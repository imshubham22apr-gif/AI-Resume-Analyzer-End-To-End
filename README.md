# 🚀 AI Resume Analyzer (Velaris Engine)

A full-stack, AI-powered application designed to process unstructured resume data into structured insights. Using advanced Natural Language Processing (NLP), this system predicts ideal career roles, scores candidate profiles, and generates actionable optimization pathways.

## ✨ Features

- **Intelligent Parsing Engine:** Extracts key skills, contact info, and experience levels using SpaCy and PDFMiner.
- **Career Trajectory Prediction:** Maps extracted skills to industry-standard roles to predict the best-fit career.
- **Candidate Matrix & Scoring:** Grades resumes out of 100 based on keyword density, action verbs, and structure.
- **Actionable Enhancements:** Generates explicit "Core Strengths" and "Areas for Improvement" (e.g., detecting missing quantifiable metrics or professional links).
- **Cyber-Editorial UI:** Modern, immersive frontend built with Next.js, Framer Motion, and a WebGL particle background.

## 🛠️ Tech Stack

**Frontend:**
- Next.js (App Router)
- Tailwind CSS
- Framer Motion
- Axios & Lucide React

**Backend:**
- FastAPI (Python)
- SQLAlchemy (SQLite)
- SpaCy (`en_core_web_sm`) & `pdfminer.six`
- Uvicorn

## 🚀 Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/imshubham22apr-gif/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```
The backend will run on `http://localhost:8000`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will run on `http://localhost:3000`.

## ☁️ Deployment

- **Backend (Render):** Connect this repo to Render.com using the included `render.yaml` Blueprint.
- **Frontend (Vercel):** Connect this repo to Vercel. Add `NEXT_PUBLIC_API_URL` environment variable pointing to your deployed backend URL.

## 📄 License
This project is open-source and available under the MIT License.
