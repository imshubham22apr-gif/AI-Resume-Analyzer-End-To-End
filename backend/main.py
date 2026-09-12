from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ai_parser import analyze_resume
import models
from database import engine, get_db
import shutil
import os
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Velaris AI Resume Analyzer API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Resume Analyzer API"}

@app.post("/api/analyze")
async def analyze_endpoint(
    resume: UploadFile = File(...), 
    job_description: str = Form(""),
    db: Session = Depends(get_db)
):
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
        
    try:
        # Analyze the saved PDF with Job Description
        result = analyze_resume(file_path, job_description)
        
        # Save to DB (mapping new Llama3 JSON format to old DB schema to prevent migration errors)
        db_resume = models.ResumeData(
            name=result.get("candidate_name", ""),
            email="",
            mobile_number="",
            skills=json.dumps(result.get("key_strengths", [])),
            predicted_role=result.get("recommendation", ""),
            resume_score=float(result.get("match_score", 0)),
            experience_level="Reasoning: " + str(result.get("reasoning", ""))[:200],
            no_of_pages=len(result.get("layout_diagnostics", [])) or 1
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/resumes")
def get_all_resumes(db: Session = Depends(get_db)):
    return db.query(models.ResumeData).all()

