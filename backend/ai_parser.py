import re
import spacy
from pdfminer.high_level import extract_text

nlp = spacy.load('en_core_web_sm')

# A basic list of skills for keyword matching
SKILLS_DB = [
    'python', 'java', 'c++', 'c', 'c#', 'javascript', 'typescript', 'react', 'angular',
    'vue', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring boot', 'html',
    'css', 'tailwind', 'bootstrap', 'sql', 'mysql', 'postgresql', 'mongodb', 'aws',
    'azure', 'gcp', 'docker', 'kubernetes', 'machine learning', 'deep learning',
    'data science', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
    'git', 'linux', 'figma', 'ui/ux', 'agile', 'scrum', 'nlp', 'computer vision'
]

ROLES_MAP = {
    'Data Science': ['machine learning', 'data science', 'python', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'nlp', 'deep learning'],
    'Frontend Developer': ['html', 'css', 'javascript', 'typescript', 'react', 'vue', 'angular', 'tailwind', 'figma'],
    'Backend Developer': ['python', 'java', 'node.js', 'express', 'django', 'flask', 'fastapi', 'sql', 'postgresql', 'mongodb'],
    'Cloud/DevOps Engineer': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'git']
}

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_email(text):
    email = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email:
        return email[0]
    return None

def extract_mobile(text):
    phone = re.findall(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?', text)
    if phone:
        # Just grab the first sequence of numbers that looks like a phone number
        raw = re.findall(r'\+?\d[\d -]{8,12}\d', text)
        if raw:
            return raw[0]
    return None

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return None

def extract_skills(text):
    doc = nlp(text.lower())
    tokens = [token.text for token in doc if not token.is_stop]
    skills = set()
    
    # check unigrams
    for token in tokens:
        if token in SKILLS_DB:
            skills.add(token)
            
    # check bigrams (e.g. machine learning)
    text_lower = text.lower()
    for skill in SKILLS_DB:
        if " " in skill and skill in text_lower:
            skills.add(skill)
            
    return list(skills)

def predict_role_and_recommend(skills, text):
    if not skills:
        return "General", [], 30, ["Add more industry-standard keywords."], ["No detectable skills found."]
        
    role_scores = {role: 0 for role in ROLES_MAP}
    for skill in skills:
        for role, role_skills in ROLES_MAP.items():
            if skill in role_skills:
                role_scores[role] += 1
                
    predicted_role = max(role_scores, key=role_scores.get)
    if role_scores[predicted_role] == 0:
        predicted_role = "General / Unknown"
        
    recommended_skills = []
    if predicted_role in ROLES_MAP:
        recommended_skills = [s for s in ROLES_MAP[predicted_role] if s not in skills][:5]
        
    # score calculation
    score = min(100, len(skills) * 8 + 40)
    
    # Generate Strengths
    strengths = []
    if len(skills) > 5:
        strengths.append(f"Strong foundational skill set detected for {predicted_role}.")
    if re.search(r'\b(github\.com|linkedin\.com)\b', text.lower()):
        strengths.append("Professional links (GitHub/LinkedIn) are present.")
        score = min(100, score + 10)
    if re.search(r'\b(led|managed|achieved|increased|improved|optimized)\b', text.lower()):
        strengths.append("Good use of action verbs in experience descriptions.")
        score = min(100, score + 10)

    if not strengths:
        strengths.append("Clean text structure detected.")

    # Generate Improvements
    improvements = []
    if len(recommended_skills) > 0:
        improvements.append(f"Consider learning or highlighting: {', '.join(recommended_skills)} to boost {predicted_role} alignment.")
    if not re.search(r'\b(github\.com|linkedin\.com)\b', text.lower()):
        improvements.append("Add links to your LinkedIn or GitHub portfolio to increase recruiter trust.")
    
    # Bias & Quality Checks (Inspired by research)
    if not re.search(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?%?', text):
        improvements.append("Include more quantifiable achievements (numbers, percentages) to show impact.")
    
    return predicted_role, recommended_skills, score, improvements, strengths

def analyze_resume(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    
    name = extract_name(text)
    email = extract_email(text)
    mobile = extract_mobile(text)
    skills = extract_skills(text)
    
    predicted_role, recommended_skills, score, improvements, strengths = predict_role_and_recommend(skills, text)
    
    # Estimate experience based on keywords
    exp_level = "Fresher"
    if "senior" in text.lower() or "lead" in text.lower():
        exp_level = "Senior Level"
    elif "experience" in text.lower() and re.search(r'[3-9]\+?\s*years?', text.lower()):
        exp_level = "Mid Level"
        
    return {
        "name": name,
        "email": email,
        "mobile_number": mobile,
        "skills": list(skills),
        "predicted_role": predicted_role,
        "recommended_skills": recommended_skills,
        "resume_score": score,
        "experience_level": exp_level,
        "no_of_pages": 1,
        "strengths": strengths,
        "improvements": improvements
    }
