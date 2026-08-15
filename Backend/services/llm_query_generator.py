import json

from services.llm_service import LLMService
from services.sql_service import SQLiteService
from schemas.sql_generation_response import SQLGenerationResponse
class LLMQueryGenerator:
    def __init__(self, llm: LLMService, sql_service: SQLiteService):
        self.llm = llm
        self.sql_service = sql_service

    SYSTEM_PROMPT = """
  You are an expert SQLite SQL generation assistant.

Your task is to convert a user's natural language question into a valid SQLite SELECT query.

The database schema will be provided in the user prompt.

Requirements:

- Use ONLY the tables and columns from the provided schema.
- Never invent tables or columns.
- Generate ONLY valid SQLite syntax.
- Quote identifiers only when required by SQLite.
- Do not assume relationships between tables unless they can be inferred from the schema.
- If aggregation is requested, use appropriate SQL aggregate functions.
- If sorting is requested, use ORDER BY.
- If limiting results is requested (e.g., "top 5"), use LIMIT.
- If date filtering is requested, use SQLite-compatible date functions.
- Generate ONLY read-only SELECT statements.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH, TRUNCATE, PRAGMA, or any statement that modifies the database.
- The user's question may be written in English or Arabic.
- Understand both languages, but always use the exact table and column names from the schema in the generated SQL.
- Do not wrap SQL inside markdown.
- Do not explain your reasoning.
- Do not include comments.
- Return only a JSON object matching this schema:

{
  "status": "success",
  "sql": "<SQLite SELECT statement>",
  "error": null
}

If a valid query cannot be generated because the request references missing tables, missing columns, or cannot be answered using the provided schema, return:

{
  "status": "error",
  "sql": null,
  "error": "<clear explanation>"
}
IMPORTANT:

The database contains column names with spaces.

You MUST copy every table and column name exactly as it appears.

If a column contains spaces, you MUST surround it with double quotes.

Examples:

Schema:
Product Name

Correct:
SELECT "Product Name" FROM sales;

Incorrect:
SELECT Product_Name FROM sales;

Incorrect:
SELECT ProductName FROM sales;
Before generating SQL:

1. Identify the requested operation.
2. Verify every table and column exists in the schema.
3. If any table or column does not exist, return an error.
4. Otherwise generate the SQL.

SQLite Dialect Requirements

- Generate SQL that is compatible with SQLite ONLY.
- Never use SQL Server syntax.
- Never use MySQL-specific syntax.
- Never use PostgreSQL-specific syntax.
- Use LIMIT instead of TOP.
- Use double quotes only when identifiers require quoting.
- Use SQLite-compatible date functions.
- Every generated query must execute successfully in SQLite.

Do not expose your reasoning.
Return only the final JSON.
"""

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
    def generate_query(self, user_prompt: str) -> SQLGenerationResponse:
        schema= self.sql_service.get_schema()
        formatted_schema = self._format_schema(schema)
        user_prompt_with_schema = f"""
Database Schema:

{formatted_schema}

User Question:
{user_prompt}
"""
        if not user_prompt.strip():
            return SQLGenerationResponse(
                status="error",
                sql=None,
                error="User question cannot be empty.",
            )
        try:
            response = self.llm.generate(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=user_prompt_with_schema,
                temperature=0,
                max_tokens=512,
            )
        except Exception as e:
            return SQLGenerationResponse(
                status="error",
                sql=None,
                error=f"Error generating SQL query: {str(e)}",
            )
        try:
            response_json = json.loads(response)
            
            return SQLGenerationResponse.model_validate(response_json)
        except Exception as e:
            return SQLGenerationResponse(
                status="error",
                sql=None,
                error=f"Error parsing LLM response: {str(e)}",
            )
            