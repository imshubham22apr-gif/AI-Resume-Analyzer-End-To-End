import json
import fitz  # PyMuPDF
import ollama

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def screen_resume_with_llama(resume_text, job_description):
    prompt = f"""
    You are a Senior Technical Recruiter with 20 years of experience.
    Your goal is to objectively evaluate a candidate based on a Job Description (JD).

    JOB DESCRIPTION:
    {job_description}

    CANDIDATE RESUME:
    {resume_text}

    TASK:
    Analyze the resume against the JD. Look for key skills, experience levels, and project relevance.
    Be strict but fair. "React" matches "React.js". "AWS" matches "Amazon Web Services".

    OUTPUT FORMAT:
    Provide the response in valid JSON format only. Do not add any conversational text.
    structure:
    {{
        "candidate_name": "extracted name",
        "match_score": 85,
        "key_strengths": ["strength 1", "strength 2", "strength 3"],
        "missing_critical_skills": ["missing skill 1", "missing skill 2"],
        "recommendation": "Interview" or "Reject",
        "reasoning": "A 2-sentence summary of why."
    }}
    """
    
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'user', 'content': prompt},
        ])
        content = response['message']['content']
        
        # Clean JSON output in case the LLM wrapped it in markdown
        clean_json = content.replace("```json", "").replace("```", "").strip()
        
        try:
            result_data = json.loads(clean_json)
            return result_data
        except json.JSONDecodeError:
            print("Failed to parse JSON from LLM.")
            return {
                "candidate_name": "Parsing Error",
                "match_score": 0,
                "key_strengths": [],
                "missing_critical_skills": [],
                "recommendation": "Manual Review Required",
                "reasoning": "The AI provided an invalid format. Raw output: " + content
            }
            
    except Exception as e:
        print(f"Ollama Connection Error: {e}")
        return {
            "candidate_name": "Local AI Offline",
            "match_score": 0,
            "key_strengths": ["Please start Ollama"],
            "missing_critical_skills": ["Llama 3 Model"],
            "recommendation": "Error",
            "reasoning": f"Could not connect to local Ollama. Error: {str(e)}. Make sure you run 'ollama run llama3'."
        }

def analyze_resume(pdf_path, job_description):
    text = extract_text_from_pdf(pdf_path)
    
    if not job_description or job_description.strip() == "":
        job_description = "General Software Engineering or Technical role. Looking for strong fundamentals, good communication, and relevant technical skills."
        
    result = screen_resume_with_llama(text, job_description)
    return result
