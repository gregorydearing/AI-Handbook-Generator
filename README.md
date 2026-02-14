# 📚 AI Handbook Generator

An AI-powered application that processes PDF documents and generates comprehensive, structured handbooks using Retrieval-Augmented Generation (RAG) and Large Language Models.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🎯 Overview

This project demonstrates the integration of modern AI technologies to create an intelligent document processing and generation system. It combines vector databases, semantic search, and LLM-powered content generation to transform uploaded PDFs into detailed, professional handbooks.

**Live Demo Mode:** The application includes a demo mode that works immediately without API configuration, making it easy to explore the interface and workflow.

### Key Features

✅ **PDF Processing** - Robust text extraction from multiple PDF formats  
✅ **Vector Database** - ChromaDB for efficient semantic search and retrieval  
✅ **RAG System** - Context-aware responses using retrieved document chunks  
✅ **Long-Form Generation** - Iterative approach to generate 20,000+ word handbooks  
✅ **Interactive UI** - Clean Gradio web interface for easy interaction  
✅ **Demo Mode** - Works without API key for testing and demonstration  
✅ **Modular Architecture** - Separated concerns for maintainability and extensibility

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                   (Gradio Web UI)                        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                  PDF Processor                           │
│        • Text Extraction (pdfplumber + PyPDF2)          │
│        • Intelligent Chunking (overlap strategy)         │
│        • Metadata Preservation                           │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                   ChromaDB                               │
│        • Vector Storage (embeddings)                     │
│        • Semantic Search (cosine similarity)            │
│        • Efficient Retrieval (top-k queries)            │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Handbook Generator                          │
│        • Google Gemini API Integration                   │
│        • Iterative Section Generation                    │
│        • Structured Prompting (LongWriter technique)    │
│        • Demo Mode Fallback                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Google Gemini API key** (optional - app works in demo mode without it)
  - Free at [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI-Handbook-Generator.git
   cd AI-Handbook-Generator/handbook-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment (Optional - for real API)**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key:
   # GEMINI_API_KEY=your_actual_key_here
   ```
   
   **Note:** The app works in **DEMO MODE** without an API key, generating sample outputs for testing.

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser** to `http://localhost:7860`

---

## 📖 Usage

### 1. Upload Documents

- Click **"Upload PDF Files"** and select one or more PDFs
- Click **"Process PDFs"** to index the content
- Wait for confirmation that processing is complete
- View the processed documents list

### 2. Chat with Documents

Ask questions about the uploaded content:
- **"What are the main findings in this research?"**
- **"Summarize the methodology used"**
- **"What conclusions does the author draw?"**

### 3. Generate Handbooks

Use natural language to request handbook generation:
- **"Create a handbook on machine learning"**
- **"Generate a comprehensive guide about transformers"**

**What happens:**
- Analyzes all uploaded documents
- Generates structured handbook (20,000+ words in production)
- Saves to `handbooks/` directory
- Shows preview in chat

**Demo vs Production:**
- **Demo Mode** (no API key): ~2,000 word sample
- **Production Mode** (with API key): 20,000+ AI-powered handbook

---

## 🛠️ Technical Implementation

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Gradio 4.44.0 | Web UI |
| **Vector DB** | ChromaDB | Semantic search |
| **LLM** | Google Gemini 2.0 | Generation |
| **PDF Parsing** | pdfplumber, PyPDF2 | Text extraction |
| **Language** | Python 3.11 | Application logic |

### PDF Processing
- Dual extraction (pdfplumber + PyPDF2 fallback)
- Intelligent chunking (1000 words, 200 overlap)
- Vector storage with ChromaDB

### RAG System
- Semantic search with cosine similarity
- Top-k retrieval (configurable)
- Source tracking for citations

### Handbook Generation
- Iterative section-by-section approach
- Structured prompting (LongWriter technique)
- Graceful demo mode fallback

---

## 📁 Project Structure

```
AI-Handbook-Generator/
├── handbook-app/
│   ├── app.py                    # Main application
│   ├── pdf_processor.py          # PDF & vector DB
│   ├── handbook_generator.py     # LLM integration
│   ├── requirements.txt          # Dependencies
│   ├── .env.example             # Config template
│   └── handbooks/               # Generated outputs
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🎓 Skills Demonstrated

### AI/ML Engineering
- RAG architecture implementation
- Vector databases and embeddings
- LLM API integration
- Prompt engineering for long-form content

### Software Engineering
- Modular code architecture
- Error handling and graceful degradation
- Environment configuration
- Production-ready practices

---

## 🔧 Configuration

Create `.env` file:
```bash
GEMINI_API_KEY=your-api-key-here
```

Get free API key: [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## 🚧 Known Limitations

1. **Output Length:** 15-25k words (depends on source material)
2. **PDF Processing:** No OCR (digital PDFs only)
3. **Language:** Optimized for English
4. **API Limits:** Free tier has daily quotas

---

## 🔜 Future Enhancements

- [ ] Multi-language support
- [ ] OCR integration
- [ ] Export to PDF/DOCX
- [ ] User authentication
- [ ] Batch processing
- [ ] Custom templates

---

## 📄 License

MIT License - Free to use for any purpose

---

## 📧 Contact

**Greg Dearing**
- GitHub: [@gregorydearing](https://github.com/gregorydearing)
- LinkedIn: https://www.linkedin.com/in/greg-dearing-94139999/
- Email: gregory.a.dearing@gmail.com

---

⭐ **If you found this project helpful, please star it!**

*Built to demonstrate RAG architecture and LLM integration*
