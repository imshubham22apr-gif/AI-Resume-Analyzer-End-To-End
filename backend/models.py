from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class ResumeData(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    mobile_number = Column(String)
    skills = Column(Text)
    predicted_role = Column(String)
    resume_score = Column(Float)
    experience_level = Column(String)
    no_of_pages = Column(Integer)
