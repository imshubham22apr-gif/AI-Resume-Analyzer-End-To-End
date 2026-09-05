from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
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
async def analyze_endpoint(resume: UploadFile = File(...), db: Session = Depends(get_db)):
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
        
    try:
        # Analyze the saved PDF
        result = analyze_resume(file_path)
        
        # Save to DB
        db_resume = models.ResumeData(
            name=result.get("name", ""),
            email=result.get("email", ""),
            mobile_number=result.get("mobile_number", ""),
            skills=json.dumps(result.get("skills", [])),
            predicted_role=result.get("predicted_role", ""),
            resume_score=result.get("resume_score", 0),
            experience_level=result.get("experience_level", ""),
            no_of_pages=result.get("no_of_pages", 0)
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

