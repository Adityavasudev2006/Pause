# Pause - AI Resume Builder

Pause is an AI-powered resume builder that transforms your experience into job-ready resumes using Google's Gemini and LangChain. Just enter your professional details—Pause handles the writing, formatting, and tone to help you stand out. Fast, smart, and tailored to your dream role.

🔗 **[Live Demo](https://pause-33il.onrender.com/)** (Note: The application may take up to 50 seconds to load due to hosting constraints on the free tier.)

## Features

- **AI-Powered Content Generation**: Automatically writes compelling summary, experience, and skills sections based on your input.
- **Context-Aware Generation**: Utilizes a RAG (Retrieval-Augmented Generation) approach with resume templates for high-quality, relevant content.
- **Customizable Tone & Style**: Tailor your resume's tone (e.g., Professional, Creative, Corporate) to match the job you're applying for.
- **Simple & Fast**: Go from raw details to a polished resume in minutes.
- **Editable Output**: Review, edit, and copy the generated resume content directly from the user-friendly interface.
- **Responsive UI**: Clean and intuitive interface built with Bootstrap, accessible on any device.

## Tech Stack

- **Frontend**: HTML, CSS (Bootstrap)
- **Backend**: Python, Flask
- **AI/LLM**: Google Gemini (`gemini-1.5-flash-001`) via LangChain
- **Embeddings**: `models/embedding-001` via `GoogleGenerativeAIEmbeddings`
- **Vector Store**: FAISS (for RAG)
- **Environment Management**: `python-dotenv`

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/pause-ai-resume-builder.git
cd pause-ai-resume-builder
