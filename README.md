# 🤖 AI Code Assistant

An intelligent AI-powered Code Assistant built with **FastAPI**, **Streamlit**, **LangChain**, and **Qwen 2.5**. The assistant can understand user intent, generate Python code using Retrieval-Augmented Generation (RAG), explain existing code line by line, maintain conversation memory, execute generated code safely, and analyze voice input to generate and execute SQL queries.

---

## ✨ Features

### 💻 Code Generation

- Generates complete Python solutions from natural language prompts.
- Uses **Retrieval-Augmented Generation (RAG)** to retrieve similar programming examples.
- Filters retrieved examples using an AI relevance checker.
- Produces clean executable Python code.
- Automatically executes generated code and returns execution results.

### 📖 Code Explanation

- Explains existing Python code.
- Provides:
  - High-level summary
  - Line-by-line explanation
  - Context-aware follow-up explanations
- Automatically extracts code from the user's prompt.
- Remembers previously explained code so users can ask follow-up questions without resending the code.

### 🎙️ Voice SQL Analysis

- Accepts **voice/audio input** from the user.
- Supports both **English and Arabic** voice input.
- Uses **Faster-Whisper** to convert speech into text.
- Sends the transcribed text directly to **Qwen 2.5** for SQL query generation.
- The LLM understands the user's intent and generates the corresponding SQL query.
- Executes the generated SQL query against the application database.
- Returns the database results to the user.
- Supports:
  - Browser voice recording
  - Audio file upload
  - Audio preview
  - Audio reset/clear
  - Arabic RTL display
  - Transcription display
  - Generated SQL display
  - Database results displayed as a table

### 🧠 Conversation Memory

- Stores previous user requests and assistant responses.
- Supports contextual follow-up questions for both:
  - Code Generation
  - Code Explanation

### 💬 Streamlit Frontend

- Interactive chat interface
- Voice SQL interface
- Response streaming
- Syntax-highlighted code blocks
- Execute generated code
- Audio recording and upload
- Audio preview
- Conversation history sidebar
- Arabic and English support
- RTL support for Arabic
- Clean ChatGPT-like interface

---

# 🏗 Architecture

## Overall Architecture

```text
                         User
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
     Streamlit Frontend          Voice SQL Page
             │                         │
             ▼                         ▼
     FastAPI Orchestrator       Voice Pipeline API
             │                         │
      ┌──────┴──────┐                  ▼
      │             │           Faster-Whisper
      ▼             ▼                  │
Intent Classifier  Memory              ▼
      │             │           Transcribed Text
      └──────┬──────┘                  │
             │                         ▼
      ┌──────┴──────────────┐   Qwen 2.5
      │                     │       │
      ▼                     ▼       ▼
Code Generator       Code Explainer
      │                     │
      ▼                     ▼
 Retrieval + RAG      Code Extraction
      │
      ▼
 Relevance Checker
      │
      ▼
 LLM Generator
      │
      ▼
 Code Execution


Voice SQL Flow:

User Voice
    │
    ▼
Streamlit Voice Interface
    │
    ▼
POST /api/v1/voice_pipeline
    │
    ▼
Faster-Whisper
    │
    ▼
Transcribed Text
    │
    ▼
Qwen 2.5
    │
    ▼
Generated SQL
    │
    ▼
SQLite Database
    │
    ▼
Query Results
    │
    ▼
Streamlit
---
# 📂 Project Structure

```text
Backend/
│
├── routers/
│   ├── orchestrator_router.py
│   └── voice_pipeline_router.py
│
├── services/
│   ├── orchestrator_service.py
│   ├── llm_classifier.py
│   ├── llm_code_generator.py
│   ├── llm_explainer.py
│   ├── llm_code_extraction_service.py
│   ├── retrieval_service.py
│   ├── relevance_checker_service.py
│   ├── prompt_builder.py
│   ├── memory_service.py
│   ├── execution_service.py
│   ├── voice_analysis_service.py
│   ├── query_generator_service.py
│   └── llm_service.py
│
├── schemas/
│
├── dto/
│
├── app.py
│
Frontend/
│
└── app.py
```

---

# 🚀 Technologies

### Backend

- FastAPI
- LangChain
- Ollama
- Qwen 2.5
- Pydantic
- Python
-  Faster-Whisper
- SQLite

### Frontend

- Streamlit

### AI Components

### AI Components

- Intent Classification
- Retrieval-Augmented Generation (RAG)
- Relevance Checking
- Code Extraction
- Code Explanation
- Conversation Memory
- Speech-to-Text
- Voice Analysis
- Natural Language to SQL
- SQL Query Generation

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/<username>/<repository>.git

cd <repository>
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start Ollama

Ensure Ollama is installed and running.

Pull the model:

```bash
ollama pull qwen2.5:3b
```

---

## 5. Start the Backend

```bash
uvicorn app:app --reload --port 8004
```

---

## 6. Start the Frontend

Open another terminal.

```bash
streamlit run app.py
```

---

# 📚 API

## POST

```
/api/v1/orchestrator
```

### Request

```json
{
  "user_prompt": "Write a function that returns the Fibonacci sequence."
}
```

---

### Generate Response

```json
{
  "generation": {
    "language": "python",
    "code": "...",
    "explanation": null
  },
  "execution": {
    "success": true,
    "stdout": "",
    "stderr": "",
    "exit_code": 0,
    "execution_time": 0.12
  }
}
```

---

### Explain Response

```json
{
  "summary": "The function returns the sum of two numbers.",
  "lines": [
    {
      "line_number": 1,
      "line": "def add(a, b):",
      "explanation": "Defines a function named add."
    }
  ]
}
```

---

# 🧪 Example Prompts

## Code Generation

```
Write a Python function to check if a string is a palindrome.
```

```
Generate a recursive implementation of merge sort.
```

```
Create a Python class representing a Bank Account.
```

---

## Code Explanation

```
Explain this code.

def add(a, b):
    return a + b
```

```
Explain this function line by line.
```

```
Why does it return -1?
```

```
Can you explain the recursive part in more detail?
```

---

# 🧠 Memory Examples

### User

```
Explain this code.

def add(a, b):
    return a + b
```

Assistant explains it.

Then the user asks

```
Why do we return instead of print?
```

The assistant remembers the previously explained code without requiring the user to resend it.

# 🎙️ Voice Analysis API

## POST `/api/v1/voice_pipeline`

The endpoint accepts an audio file containing a natural-language database query using `multipart/form-data`.

### Request Body

Content-Type: multipart/form-data


`audio=<audio-file>`

### Example

```bash
curl -X POST "http://127.0.0.1:8004/api/v1/voice_pipeline" \
  -F "audio=@voice_query.wav"
```

### Example Response

```json
{
  "transcription": "Show me the total number of products in each category.",
  "normalized_text": "Show me the total number of products in each category.",
  "sql": "SELECT category, COUNT(*) FROM products GROUP BY category;",
  "results": [
    {
      "category": "Electronics",
      "count": 10
    },
    {
      "category": "Books",
      "count": 7
    }
  ]
}
```
---

# 🔄 AI Pipeline

### Generation Pipeline

```
User Prompt
      │
      ▼
Intent Classification
      │
      ▼
Conversation Memory
      │
      ▼
Retrieve Examples
      │
      ▼
Relevance Checker
      │
      ▼
Prompt Builder
      │
      ▼
LLM Generation
      │
      ▼
Execute Code
      │
      ▼
Response
```

---

### Explanation Pipeline

```
User Prompt
      │
      ▼
Intent Classification
      │
      ▼
Extract Source Code
      │
      ▼
Conversation Memory
      │
      ▼
LLM Explanation
      │
      ▼
Line-by-Line Explanation
```

---
# 🎙️ Voice Analysis Pipeline

The Voice Analysis feature converts a user's spoken database request into a SQL query and executes it against the database.

```text
User Voice
    │
    ▼
Audio Recording / Upload
    │
    ▼
Voice Analysis API
    │
    ▼
Faster-Whisper
    │
    ▼
Speech-to-Text
    │
    ▼
Transcribed Text
    │
    ▼
Text Normalization
    │
    ▼
Qwen 2.5
    │
    ▼
SQL Query Generation
    │
    ▼
SQLite Database
    │
    ▼
SQL Execution
    │
    ▼
Query Results
    │
    ▼
Frontend


---

# Future Improvements

- Token streaming from the backend
- Multiple programming language support
- Persistent chat history
- User authentication
- Docker deployment
- Unit and integration tests
- Vector database support
- Better memory management
- Conversation search
- Syntax-aware code diff explanations

---

# Author

**Eslam Mohamed Fawzy**
