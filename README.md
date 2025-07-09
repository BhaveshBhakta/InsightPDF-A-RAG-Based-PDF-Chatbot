# InsightPDF — Chat with Your PDF Using Groq LLaMA 3.3

> **Upload any PDF and interact with its content conversationally using Groq's LLaMA 3.3 and ChromaDB-powered retrieval.**

---

## Overview

**InsightPDF** is a powerful AI-driven web application that enables users to:

- Upload any PDF file (e.g., research paper, legal doc, technical manual)
- Ask natural language questions about the content
- Get accurate answers along with **source-based references**

Built on **Groq’s ultra-fast LLaMA 3.3-70B model**, this project showcases how **Retrieval-Augmented Generation (RAG)** can bring conversational intelligence to static documents.

---

## Project Flow

![coldemailpng](https://github.com/user-attachments/assets/bee6b885-004e-48b8-9867-c32fb2df798d)



##  Key Features

-  Upload any PDF document via browser
-  Chat with the document using **LLaMA 3.3** via **Groq API**
-  Stores and retrieves document context with **ChromaDB**
-  Multi-turn memory using LangChain’s ConversationBufferMemory
-  Source-aware responses with preview snippets
-  Fast, reliable, and production-ready backend using Flask

---

##  Tech Stack

| Layer           | Tools & Libraries                                 |
|-----------------|---------------------------------------------------|
| **LLM Backend** | Groq API, LLaMA 3.3 (70B - Versatile)             |
| **Vector Store**| ChromaDB, HuggingFace MiniLM Embeddings           |
| **Frameworks**  | LangChain, Flask                                  |
| **PDF Parsing** | PyPDF2                                            |
| **Frontend**    | HTML, CSS (Inter font), Vanilla JavaScript        |
| **Hosting**     | Flask Server + render             |

---

##  UI Preview
![Screenshot 2025-07-09 182020](https://github.com/user-attachments/assets/69268c12-5fda-4748-83e7-6ad25c846565)

---

##  Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/BhaveshBhakta/InsightPDF-A-RAG-Based-PDF-Chatbot.git
cd InsightPDF-A-RAG-Based-PDF-Chatbot
````

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variable

Create a `.env` file or export manually:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the App

```bash
python app.py
```
---

## Folder Structure

```
InsightPDF/
├── app.py                    # Flask API endpoints
├── pdf_chatbot.py            # LLM, embeddings, vectorstore logic
├── test_pdfchat.py           # Test pdf chatbot
├── uploaded_pdfs/            # Uploaded PDF files
├── chroma_db/                # Persistent vector database
├── templates/
│   └── index.html            # Frontend page
├── static/
│   ├── css/style.css
│   └── js/script.js
├── requirements.txt
└── README.md
```

---

## Why This Project?

InsightPDF highlights:

* Practical use of **GenAI** and **RAG** techniques
* Real-world application of **LLMs for document Q\&A**
* Strong understanding of **LLM orchestration**, **vector stores**, and **stateful conversation**
* Clean frontend + scalable backend = portfolio-ready project

Use it to impress recruiters and hiring managers with your ability to build and deploy **AI-powered applications**.

---

## Security Notes

* No user data or files are stored permanently
* Groq API key is accessed securely via environment variable
* Chroma collections reset on each upload to ensure clean context

---

##  Author

**Bhavesh Bhakta**
🔗 [LinkedIn](https://www.linkedin.com/in/bhavesh-bhakta/)
💻 [GitHub](https://github.com/BhaveshBhakta)
