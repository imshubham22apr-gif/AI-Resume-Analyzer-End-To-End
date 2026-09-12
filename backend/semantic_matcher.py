"""
semantic_matcher.py - Skill Ontology & Two-Stage Semantic Matcher
Performs canonical skill normalization (ESCO/O*NET inspired Knowledge Graph)
and n-gram cosine similarity matching against Job Requirements.
"""
import re
from typing import Dict, List, Set, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Canonical Knowledge Graph & Taxonomy (ESCO/O*NET inspired)
TECH_ONTOLOGY: Dict[str, Dict[str, Any]] = {
    "kubernetes": {
        "canonical": "Kubernetes",
        "aliases": ["k8s", "kube", "kubernetes cluster"],
        "category": "Container Orchestration",
        "parents": ["Cloud Native", "DevOps"]
    },
    "docker": {
        "canonical": "Docker",
        "aliases": ["containerization", "containers", "docker-compose", "dockerfile"],
        "category": "Containerization",
        "parents": ["DevOps"]
    },
    "react": {
        "canonical": "React.js",
        "aliases": ["reactjs", "react.js", "react native"],
        "category": "Frontend Frameworks",
        "parents": ["JavaScript Ecosystem"]
    },
    "next.js": {
        "canonical": "Next.js",
        "aliases": ["nextjs", "next js"],
        "category": "Fullstack Frameworks",
        "parents": ["React.js", "JavaScript Ecosystem"]
    },
    "typescript": {
        "canonical": "TypeScript",
        "aliases": ["ts"],
        "category": "Programming Languages",
        "parents": ["JavaScript Ecosystem"]
    },
    "python": {
        "canonical": "Python",
        "aliases": ["py", "python3", "fastapi", "django", "flask"],
        "category": "Programming Languages",
        "parents": ["Backend Engineering"]
    },
    "aws": {
        "canonical": "Amazon Web Services (AWS)",
        "aliases": ["amazon web services", "ec2", "s3", "lambda", "cloudwatch", "iam", "eks"],
        "category": "Cloud Infrastructure",
        "parents": ["Cloud Computing"]
    },
    "gcp": {
        "canonical": "Google Cloud Platform (GCP)",
        "aliases": ["google cloud", "bigquery", "cloud run", "gke"],
        "category": "Cloud Infrastructure",
        "parents": ["Cloud Computing"]
    },
    "postgresql": {
        "canonical": "PostgreSQL",
        "aliases": ["postgres", "psql"],
        "category": "Relational Databases",
        "parents": ["Databases"]
    },
    "mongodb": {
        "canonical": "MongoDB",
        "aliases": ["mongo", "nosql database"],
        "category": "NoSQL Databases",
        "parents": ["Databases"]
    },
    "redis": {
        "canonical": "Redis",
        "aliases": ["caching", "in-memory store"],
        "category": "In-Memory Caching",
        "parents": ["Databases"]
    },
    "machine learning": {
        "canonical": "Machine Learning",
        "aliases": ["ml", "deep learning", "nlp", "computer vision", "llm", "transformers", "pytorch", "tensorflow"],
        "category": "Artificial Intelligence",
        "parents": ["Data Science & AI"]
    },
    "ci/cd": {
        "canonical": "CI/CD",
        "aliases": ["continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"],
        "category": "DevOps & Automation",
        "parents": ["DevOps"]
    },
    "system design": {
        "canonical": "System Design",
        "aliases": ["microservices", "distributed systems", "high availability", "scalability", "event-driven architecture"],
        "category": "Software Architecture",
        "parents": ["Architecture"]
    }
}


def extract_canonical_skills(text: str) -> Dict[str, Any]:
    """
    Scans text against the canonical skill ontology using boundary-aware regex matching.
    Resolves acronyms like 'k8s' -> 'Kubernetes' and maps to categories.
    """
    text_lower = text.lower()
    matched_canonical: Set[str] = set()
    categories_covered: Set[str] = set()

    for skill_key, data in TECH_ONTOLOGY.items():
        all_terms = [skill_key] + data.get("aliases", [])
        for term in all_terms:
            # Word boundary matching to avoid false positives (e.g. 'ts' matching 'its')
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(term) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, text_lower):
                matched_canonical.add(data["canonical"])
                categories_covered.add(data["category"])
                break

    return {
        "skills": matched_canonical,
        "categories": categories_covered
    }


def compute_semantic_alignment(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Calculates two-stage semantic alignment:
    1. Canonical Ontology Skill Coverage (ESCO/O*NET inspired)
    2. Sub-linear N-gram Cosine Similarity (TF-IDF vector space)
    """
    # 1. Ontology-based Entity Extraction & Coverage
    resume_entities = extract_canonical_skills(resume_text)
    jd_entities = extract_canonical_skills(jd_text)

    jd_skills = jd_entities["skills"]
    resume_skills = resume_entities["skills"]

    if jd_skills:
        matched_skills = resume_skills.intersection(jd_skills)
        missing_skills = jd_skills - resume_skills
        ontology_coverage = (len(matched_skills) / len(jd_skills)) * 100.0
    else:
        # If JD has no explicit ontology keywords, fallback to general skill volume
        matched_skills = resume_skills
        missing_skills = set()
        ontology_coverage = min(100.0, len(resume_skills) * 15.0) if resume_skills else 50.0

    # 2. Textual Semantic Cosine Similarity (TF-IDF with 1-2 ngrams and sublinear scaling)
    semantic_cosine = 50.0
    if resume_text.strip() and jd_text.strip():
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                sublinear_tf=True,
                max_features=2500
            )
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            cos_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            # Scale cosine similarity (which rarely exceeds 0.70 in text) to a 0-100 score
            calibrated_cos = min(100.0, (cos_sim / 0.65) * 100.0)
            semantic_cosine = round(calibrated_cos, 1)
        except Exception:
            semantic_cosine = 50.0

    # 3. Composite Calibrated Score: 60% Ontology Skill Coverage + 40% Textual Semantic Cosine
    composite_score = round((0.60 * ontology_coverage) + (0.40 * semantic_cosine), 1)
    composite_score = max(0.0, min(100.0, composite_score))

    return {
        "composite_score": composite_score,
        "ontology_coverage_pct": round(ontology_coverage, 1),
        "semantic_cosine_score": semantic_cosine,
        "canonical_skills_matched": sorted(list(matched_skills)),
        "missing_critical_skills": sorted(list(missing_skills)),
        "categories_represented": sorted(list(resume_entities["categories"]))
    }
