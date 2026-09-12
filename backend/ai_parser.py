"""
ai_parser.py - Enterprise-Grade Talent Intelligence Parser & Evaluator
Orchestrates Layout-Aware PDF Parsing, Anti-Cheat & Adversarial Defense,
Canonical Skill Ontology Matching, and LLM Reasoning.
"""
import os
import re
import json
try:
    import ollama
except ImportError:
    ollama = None
import requests
from layout_parser import parse_pdf_layout_aware
from anti_cheat import scan_for_adversarial_tampering
from semantic_matcher import compute_semantic_alignment


def extract_fallback_name(text: str) -> str:
    """
    Heuristically extracts candidate name from the top header lines of the resume.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        # Filter out common section titles or contact lines
        if any(keyword in line.lower() for keyword in ["resume", "curriculum", "email", "phone", "http", "page", "profile", "summary"]):
            continue
        # Check if line looks like a person's name (2-4 capitalized words, no numbers/symbols)
        words = line.split()
        if 2 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            return line
    return "Candidate"


def screen_with_llm(resume_text: str, job_description: str, anti_cheat_result: dict, semantic_result: dict) -> dict:
    """
    Prompts local Llama3 model with quarantined, structured context.
    Falls back gracefully to deterministic NLP metrics if Ollama is unreachable.
    """
    matched_skills_str = ", ".join(semantic_result.get("canonical_skills_matched", [])) or "None identified"
    missing_skills_str = ", ".join(semantic_result.get("missing_critical_skills", [])) or "None identified"

    prompt = f"""
    You are a Lead Talent AI Evaluator at an enterprise hiring lab.
    Evaluate the candidate resume objectively against the Target Job Description.

    TARGET JOB DESCRIPTION:
    {job_description[:2000]}

    CANDIDATE RESUME (Layout-Parsed):
    {resume_text[:3000]}

    PRE-COMPUTED DETERMINISTIC SIGNALS:
    - Canonical Skills Detected: {matched_skills_str}
    - Missing Critical Skills: {missing_skills_str}
    - Ontology Alignment Coverage: {semantic_result.get('ontology_coverage_pct', 0)}%
    - Cosine Semantic Similarity: {semantic_result.get('semantic_cosine_score', 0)}%

    INSTRUCTIONS:
    1. Extract candidate full name from header.
    2. Provide an overall fit score (0-100).
    3. List 3 key strengths with specific context from work experience.
    4. List missing skills or experience gaps.
    5. State final recommendation: "Interview" or "Reject".
    6. Provide a 2-sentence objective reasoning.

    OUTPUT FORMAT:
    Provide strict valid JSON only, without any markdown fences or conversational text:
    {{
        "candidate_name": "Full Name",
        "match_score": 85,
        "key_strengths": ["Strength 1 with metric", "Strength 2", "Strength 3"],
        "missing_critical_skills": ["Skill 1", "Skill 2"],
        "recommendation": "Interview",
        "reasoning": "Two-sentence summary explanation."
    }}
    """

    try:
        content = ""
        if ollama is not None:
            response = ollama.chat(
                model='llama3',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.1}
            )
            content = response['message']['content']
        else:
            # Fallback to direct HTTP endpoint on Ollama
            res = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=10
            )
            if res.status_code == 200:
                content = res.json().get("message", {}).get("content", "")
            else:
                raise RuntimeError(f"Ollama HTTP returned status {res.status_code}")

        clean_json = content.replace("```json", "").replace("```", "").strip()
        parsed_data = json.loads(clean_json)
        return parsed_data
    except Exception as e:
        # Graceful deterministic fallback if Ollama is unavailable
        fallback_name = extract_fallback_name(resume_text)
        sem_score = semantic_result.get("composite_score", 50.0)
        rec = "Interview" if sem_score >= 65 else "Reject"
        
        strengths = [f"Verified competency in: {s}" for s in semantic_result.get("canonical_skills_matched", [])[:3]]
        if not strengths:
            strengths = ["General domain experience detected"]

        missing = [f"Missing required proficiency: {s}" for s in semantic_result.get("missing_critical_skills", [])[:3]]
        if not missing:
            missing = ["No major critical gaps identified"]

        return {
            "candidate_name": fallback_name,
            "match_score": sem_score,
            "key_strengths": strengths,
            "missing_critical_skills": missing,
            "recommendation": rec,
            "reasoning": f"Automated semantic evaluation scored candidate at {sem_score}% alignment based on ontology mapping and text cosine similarity.",
            "_fallback_mode": True
        }


def analyze_resume(pdf_path: str, job_description: str = "") -> dict:
    """
    Main pipeline entry point.
    Executes:
    1. Multi-column layout-aware text reconstruction
    2. Invisible font and prompt injection anti-cheat audit
    3. ESCO/O*NET skill ontology and vector cosine similarity
    4. Structured LLM reasoning or deterministic fallback
    5. Calibrated penalty application for adversarial attempts
    """
    if not job_description or not job_description.strip():
        job_description = (
            "Software Engineer / Developer with strong fundamentals in backend or frontend engineering, "
            "distributed systems, APIs, cloud infrastructure, and databases."
        )

    # Step 1: Layout-Aware Parsing
    layout_result = parse_pdf_layout_aware(pdf_path)
    resume_text = layout_result.get("text", "")

    # Step 2: Adversarial & Anti-Cheat Scan
    anti_cheat_result = scan_for_adversarial_tampering(pdf_path, resume_text)

    # Step 3: Two-Stage Semantic & Ontology Matchmaking
    semantic_result = compute_semantic_alignment(resume_text, job_description)

    # Step 4: LLM Evaluation with Context Guardrail
    llm_result = screen_with_llm(resume_text, job_description, anti_cheat_result, semantic_result)

    # Step 5: Score Calibration & Penalty Deductions
    base_score = float(llm_result.get("match_score", semantic_result.get("composite_score", 50.0)))
    penalty = anti_cheat_result.get("penalty_score", 0)
    final_score = max(0.0, min(100.0, round(base_score - penalty, 1)))

    recommendation = llm_result.get("recommendation", "Review")
    reasoning = llm_result.get("reasoning", "")

    # If critical tampering is detected, override recommendation and flag candidate
    if anti_cheat_result.get("is_compromised", False):
        if anti_cheat_result.get("audit_status") == "CRITICAL_ATTACK_DETECTED" or penalty >= 50:
            recommendation = "Reject (Adversarial Tampering Detected)"
            reasoning = (
                f"[SECURITY ALERT] Candidate resume was flagged for adversarial tampering "
                f"({anti_cheat_result.get('audit_status')}). Detected {anti_cheat_result.get('white_text_count')} "
                f"white-font keyword injection(s) and {anti_cheat_result.get('prompt_injections_found')} prompt injection attempts. "
                + reasoning
            )
        else:
            reasoning = (
                f"[CAUTION] Potential keyword stuffing detected ({anti_cheat_result.get('audit_status')}). "
                f"A penalty of -{penalty} points was applied. "
                + reasoning
            )

    # Format final payload for frontend compatibility + extended diagnostic payload
    return {
        "candidate_name": llm_result.get("candidate_name", "Candidate"),
        "match_score": final_score,
        "key_strengths": llm_result.get("key_strengths", []),
        "missing_critical_skills": llm_result.get("missing_critical_skills", []),
        "recommendation": recommendation,
        "reasoning": reasoning,
        # Enhanced enterprise diagnostics
        "anti_cheat_audit": {
            "status": anti_cheat_result.get("audit_status"),
            "is_compromised": anti_cheat_result.get("is_compromised"),
            "penalty_applied": penalty,
            "white_text_detected": anti_cheat_result.get("white_text_count", 0),
            "prompt_injections": anti_cheat_result.get("prompt_injections_found", 0)
        },
        "layout_diagnostics": layout_result.get("diagnostics", []),
        "ontology_alignment": {
            "coverage_pct": semantic_result.get("ontology_coverage_pct"),
            "semantic_cosine": semantic_result.get("semantic_cosine_score"),
            "canonical_skills": semantic_result.get("canonical_skills_matched"),
            "categories": semantic_result.get("categories_represented")
        }
    }
