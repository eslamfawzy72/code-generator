# 🤖 AI Code Assistant

An intelligent AI-powered Code Assistant built with **FastAPI**, **Streamlit**, **LangChain**, and **Qwen 2.5**. The assistant can understand user intent, generate Python code using Retrieval-Augmented Generation (RAG), explain existing code line by line, maintain conversation memory, and execute generated code safely.

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

### 🧠 Conversation Memory
- Stores previous user requests and assistant responses.
- Supports contextual follow-up questions for both:
  - Code Generation
  - Code Explanation

### 💬 Streamlit Frontend
- Interactive chat interface
- Response streaming
- Syntax-highlighted code blocks
- Execute generated code
- Conversation history sidebar
- Clean ChatGPT-like interface

---

# 🏗 Architecture

```
                User
                  │
                  ▼
          Streamlit Frontend
                  │
                  ▼
        FastAPI Orchestrator
                  │
      ┌───────────┴────────────┐
      │                        │
      ▼                        ▼
 Intent Classifier      Memory Service
      │                        │
      └───────────┬────────────┘
                  │
      ┌───────────┴────────────┐
      │                        │
      ▼                        ▼
 Code Generator          Code Explainer
      │                        │
      ▼                        ▼
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
```

---

# 📂 Project Structure

```text
Backend/
│
├── routers/
│   └── orchestrator_router.py
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

### Frontend

- Streamlit

### AI Components

- Intent Classification
- Retrieval-Augmented Generation (RAG)
- Relevance Checking
- Code Extraction
- Code Explanation
- Conversation Memory

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
