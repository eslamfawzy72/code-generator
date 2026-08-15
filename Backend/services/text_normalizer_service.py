from services.llm_service import LLMService
from services.sql_service import SQLiteService
from schemas.text_normalizer_response import TextNormalizationResponse


class TextNormalizer:
    SYSTEM_PROMPT = """
You are a domain-aware speech transcription correction assistant.

Your task is to correct errors in a speech-to-text transcription and
produce a clear, meaningful user question.

The transcription may contain:
- incorrectly recognized words
- phonetic errors
- missing words
- extra words
- words that sound similar to database-related terms

You will be given the database schema as context.

Rules:

1. Preserve the user's original meaning.
2. Correct likely speech-to-text errors.
3. Use the database schema to resolve ambiguous or incorrectly
   transcribed words.
4. Prefer database terms when a transcription error closely resembles
   a valid table or column name.
5. Do not invent database concepts that are not present in the schema.
6. Do not answer the user's question.
7. Do not generate SQL.
8. Do not add information that the user did not request.
9. Preserve numbers, quantities, filters, and constraints from the
   original question.
10. The user may speak Arabic or English.
11. Preserve the language of the user's question whenever possible.
12. Return ONLY the corrected question.
13. Do not include explanations, markdown, or quotation marks.

Example 1:

Database columns:
row_id
order_id
order_date
ship_date
ship_mode
customer_id
customer_name
segment
country
city
state
postal_code
region
product_id
category
sub_category
product_name
sales

Transcription:
Show total feels boy category

Corrected question:
Show total sales by category

Example 2:

Database columns:
- product_name
- sales

Transcription:
Show top five brothers by sales

Corrected question:
Show top five products by sales
"""

    def __init__(
        self,
        llm: LLMService,
        sql_service: SQLiteService,
    ):
        self.llm = llm
        self.sql_service = sql_service

    def _format_schema(self, schema: dict) -> str:
        lines = []

        for table_name, columns in schema.items():
            lines.append(f"Table: {table_name}")
            lines.append("Columns:")

            for column in columns:
                lines.append(
                    f"- {column['name']} ({column['type']})"
                )

            lines.append("")

        return "\n".join(lines)

    async def normalize(self, transcription: str) -> TextNormalizationResponse:
        if not transcription.strip():
            return TextNormalizationResponse(
                status="error",
                text=None,
                error="Transcription cannot be empty.",
            )

        try:
            schema = self.sql_service.get_schema()
            formatted_schema = self._format_schema(schema)

            user_prompt = f"""
Database Schema:

{formatted_schema}

Speech Transcription:

{transcription}

Correct the transcription while preserving the user's original meaning.
Return only the corrected user question.
"""

            response = self.llm.generate(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0,
                max_tokens=256,
            )

            if not response or not response.strip():
                return TextNormalizationResponse(
                    status="error",
                    text=None,
                    error="LLM returned an empty response.",
                )

            return TextNormalizationResponse(
                status="success",
                text=response.strip(),
            )

        except Exception as e:
            return TextNormalizationResponse(
                status="error",
                text=None,
                error=f"Error normalizing transcription: {str(e)}",
            )