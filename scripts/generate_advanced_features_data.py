"""Generate JSON data assets for advanced CareerCompass features."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SKILL_SYNONYMS = {
    "javascript": ["js", "javascript", "ecmascript", "node", "nodejs", "node.js"],
    "typescript": ["ts", "typescript"],
    "python": ["python", "py", "python3"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "t-sql", "pl/sql"],
    "power bi": ["power bi", "powerbi", "power-bi", "pbi"],
    "machine learning": ["machine learning", "ml", "machine-learning"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "docker": ["docker", "containerization", "containers"],
    "fastapi": ["fastapi", "fast api"],
    "react": ["react", "reactjs", "react.js"],
    "excel": ["excel", "ms excel", "microsoft excel", "spreadsheet"],
    "figma": ["figma", "figma design"],
    "communication": ["communication", "communicator", "verbal communication", "written communication"],
    "problem solving": ["problem solving", "problem-solving", "analytical thinking"],
    "llm": ["llm", "large language model", "large language models", "gpt"],
    "rag": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "aws": ["aws", "amazon web services", "amazon aws"],
    "git": ["git", "github", "gitlab", "version control"],
    "tableau": ["tableau", "tableau desktop"],
    "seo": ["seo", "search engine optimization", "search engine optimisation"],
    "crm": ["crm", "salesforce", "hubspot crm", "customer relationship management"],
    "autocad": ["autocad", "auto cad", "cad"],
    "project planning": ["project planning", "project management", "pm"],
    "data visualization": ["data visualization", "data visualisation", "dataviz", "data viz"],
    "nlp": ["nlp", "natural language processing"],
    "kubernetes": ["kubernetes", "k8s", "kube"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
}

INTERVIEW_QUESTIONS = {
    "python": [
        "Explain the difference between a list and a tuple in Python.",
        "How do you handle missing values in a pandas DataFrame?",
        "Describe a Python project where you improved code performance.",
    ],
    "sql": [
        "Write a query to find duplicate records in a table.",
        "Explain the difference between INNER JOIN and LEFT JOIN.",
        "How would you optimize a slow SQL query?",
    ],
    "machine learning": [
        "Explain bias-variance tradeoff with an example.",
        "How do you evaluate a classification model beyond accuracy?",
        "Describe a time you deployed an ML model to production.",
    ],
    "communication": [
        "Tell me about a time you explained a technical result to a non-technical stakeholder.",
        "How do you handle disagreement in a team project?",
    ],
    "excel": [
        "What Excel functions do you use most for financial analysis?",
        "How do you build a dynamic dashboard in Excel?",
    ],
    "docker": [
        "Explain the difference between a Docker image and a container.",
        "How would you dockerize a Python web application?",
    ],
    "figma": [
        "Walk me through your UI design process from research to prototype.",
        "How do you maintain consistency using design systems in Figma?",
    ],
    "customer service": [
        "Describe a difficult customer situation and how you resolved it.",
        "How do you prioritize tickets during peak volume?",
    ],
    "financial analysis": [
        "Walk me through a financial ratio analysis you have performed.",
        "How do you assess credit risk for a new borrower profile?",
    ],
    "lesson planning": [
        "How do you design a lesson for mixed-ability students?",
        "Describe how you measure learning outcomes after a unit.",
    ],
    "_role_behavioral": {
        "Data Analyst": [
            "Describe a dashboard you built and the business decision it enabled.",
            "How do you validate data quality before reporting?",
        ],
        "Software Developer": [
            "Describe a bug you debugged under time pressure.",
            "How do you approach code reviews?",
        ],
        "Credit Analyst": [
            "How do you balance speed and accuracy in credit assessments?",
        ],
        "UI/UX Designer": [
            "Tell me about a design iteration based on user feedback.",
        ],
    },
}

LEARNING_RESOURCES = {
    "python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "documentation", "provider": "Python.org"},
        {"title": "freeCodeCamp Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "type": "course", "provider": "freeCodeCamp"},
    ],
    "sql": [
        {"title": "SQLBolt Interactive Tutorial", "url": "https://sqlbolt.com/", "type": "tutorial", "provider": "SQLBolt"},
        {"title": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "tutorial", "provider": "Mode"},
    ],
    "machine learning": [
        {"title": "scikit-learn User Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "type": "documentation", "provider": "scikit-learn"},
        {"title": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "type": "course", "provider": "Google"},
    ],
    "power bi": [
        {"title": "Microsoft Power BI Learning", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi", "type": "course", "provider": "Microsoft"},
    ],
    "docker": [
        {"title": "Docker Getting Started", "url": "https://docs.docker.com/get-started/", "type": "documentation", "provider": "Docker"},
    ],
    "fastapi": [
        {"title": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com/", "type": "documentation", "provider": "FastAPI"},
    ],
    "excel": [
        {"title": "Excel Easy Tutorials", "url": "https://www.excel-easy.com/", "type": "tutorial", "provider": "Excel Easy"},
    ],
    "figma": [
        {"title": "Figma Learn Hub", "url": "https://www.figma.com/resource-library/", "type": "tutorial", "provider": "Figma"},
    ],
    "seo": [
        {"title": "Google Search Central SEO Guide", "url": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide", "type": "documentation", "provider": "Google"},
    ],
    "communication": [
        {"title": "Coursera Communication Skills (Audit Free)", "url": "https://www.coursera.org/courses?query=communication%20skills", "type": "course", "provider": "Coursera"},
    ],
    "rag": [
        {"title": "LangChain RAG Tutorial", "url": "https://python.langchain.com/docs/tutorials/rag/", "type": "tutorial", "provider": "LangChain"},
    ],
    "financial analysis": [
        {"title": "Corporate Finance Institute Free Resources", "url": "https://corporatefinanceinstitute.com/resources/", "type": "tutorial", "provider": "CFI"},
    ],
    "customer service": [
        {"title": "HubSpot Customer Service Training", "url": "https://www.hubspot.com/resources/courses/customer-service", "type": "course", "provider": "HubSpot"},
    ],
}

GAMIFICATION_BADGES = [
    {"badge_id": "first_gap_analysis", "title": "Gap Spotter", "description": "Complete your first skill gap analysis.", "criteria": "gap_analyses>=1"},
    {"badge_id": "five_gap_analyses", "title": "Career Tracker", "description": "Complete 5 skill gap analyses.", "criteria": "gap_analyses>=5"},
    {"badge_id": "skill_growth_10", "title": "Skill Climber", "description": "Achieve 10% skill growth between analyses.", "criteria": "skill_growth>=10"},
    {"badge_id": "first_job_match", "title": "Job Matcher", "description": "Run your first job description match.", "criteria": "job_matches>=1"},
    {"badge_id": "first_interview_prep", "title": "Interview Ready", "description": "Generate interview questions for a role.", "criteria": "interview_preps>=1"},
    {"badge_id": "first_resume_bullets", "title": "Bullet Crafter", "description": "Generate ATS resume bullets.", "criteria": "resume_bullets>=1"},
    {"badge_id": "first_career_action", "title": "Action Taker", "description": "Mark a career action as completed.", "criteria": "completed_actions>=1"},
    {"badge_id": "three_completed_actions", "title": "Momentum Builder", "description": "Complete 3 career actions.", "criteria": "completed_actions>=3"},
    {"badge_id": "cv_comparison", "title": "CV Optimizer", "description": "Compare two CV versions.", "criteria": "cv_comparisons>=1"},
    {"badge_id": "pdf_export", "title": "Report Pro", "description": "Export a PDF career report.", "criteria": "pdf_exports>=1"},
    {"badge_id": "multilingual", "title": "Global Explorer", "description": "Switch the UI to Bengali.", "criteria": "language_bn_used>=1"},
    {"badge_id": "data_import", "title": "Data Curator", "description": "Import job data via CSV or connector.", "criteria": "data_imports>=1"},
]

REGIONS = ["Global", "Bangladesh", "United Kingdom", "United States", "Remote"]

REGIONAL_PROFILES = {
    "Bangladesh": {
        "Data & AI": {
            "Data Analyst": {
                "core_skills": ["excel", "sql", "power bi", "python", "communication"],
                "helpful_skills": ["statistics", "reporting", "stakeholder management"],
                "notes": "Excel and Power BI are especially common in Bangladesh analytics roles.",
            },
            "Bank Officer": {
                "core_skills": ["banking operations", "customer onboarding", "excel", "communication", "kyc"],
                "helpful_skills": ["financial products", "regulatory compliance"],
                "notes": "Retail and corporate banking onboarding workflows are common.",
            },
        },
        "Banking & Finance": {
            "Credit Analyst": {
                "core_skills": ["financial analysis", "credit analysis", "excel", "risk assessment", "communication"],
                "helpful_skills": ["regulatory compliance", "financial reporting"],
                "notes": "Credit assessment memos and Excel models are standard deliverables.",
            },
        },
    },
    "United Kingdom": {
        "Data & AI": {
            "Data Analyst": {
                "core_skills": ["sql", "python", "power bi", "data visualization", "stakeholder management"],
                "helpful_skills": ["statistics", "a/b testing", "communication"],
                "notes": "Stakeholder communication and GDPR-aware reporting are valued.",
            },
        },
        "Software & IT": {
            "Full Stack Developer": {
                "core_skills": ["javascript", "react", "node.js", "sql", "git"],
                "helpful_skills": ["docker", "testing", "agile"],
                "notes": "Agile delivery and testing practices are commonly expected.",
            },
        },
    },
    "United States": {
        "Data & AI": {
            "Machine Learning Engineer": {
                "core_skills": ["python", "machine learning", "docker", "aws", "sql"],
                "helpful_skills": ["mlflow", "fastapi", "feature engineering"],
                "notes": "Cloud deployment and MLOps tooling are frequently listed.",
            },
        },
        "Marketing & Sales": {
            "Digital Marketing Executive": {
                "core_skills": ["google analytics", "seo", "sem", "content marketing", "crm"],
                "helpful_skills": ["copywriting", "conversion optimization"],
                "notes": "Performance marketing and analytics integration are common.",
            },
        },
    },
    "Remote": {
        "Software & IT": {
            "Frontend Developer": {
                "core_skills": ["html", "css", "javascript", "react", "git"],
                "helpful_skills": ["typescript", "communication", "documentation"],
                "notes": "Async communication and documentation skills are critical for remote roles.",
            },
        },
        "Customer Support": {
            "Technical Support Specialist": {
                "core_skills": ["troubleshooting", "communication", "ticketing systems", "documentation"],
                "helpful_skills": ["crm", "product knowledge", "empathy"],
                "notes": "Clear written communication across time zones is essential.",
            },
        },
    },
}

I18N_EN = {
    "app_name": "CareerCompass",
    "app_tagline": "Job Market Intelligence & Skill Gap Analyzer",
    "nav_overview": "Job Market Overview",
    "nav_skills": "Skill Demand Analysis",
    "nav_cv_gap": "CV Skill Gap Analyzer",
    "nav_recommendations": "Project & Career Actions",
    "nav_clustering": "Role Clustering",
    "nav_import": "Data Import",
    "nav_explorer": "Career Explorer",
    "nav_job_match": "Job Match Dashboard",
    "nav_toolkit": "Career Toolkit",
    "dataset_source": "Dataset source",
    "language": "Language",
    "analyze": "Analyze",
    "download": "Download",
    "match_score": "Match Score",
    "missing_skills": "Missing Skills",
    "matched_skills": "Matched Skills",
    "learning_resources": "Learning Resources",
    "interview_questions": "Interview Questions",
    "resume_bullets": "Resume Bullets",
    "progress_tracker": "Progress Tracker",
    "skill_growth": "Skill Growth",
    "badges": "Badges",
    "time_series": "Skill Demand Over Time",
    "public_connectors": "Public Data Connectors",
    "honest_note": "Results are guidance, not hiring guarantees.",
}

I18N_BN = {
    "app_name": "ক্যারিয়ারকম্পাস",
    "app_tagline": "চাকরির বাজার বিশ্লেষণ ও দক্ষতা ফাঁক বিশ্লেষক",
    "nav_overview": "চাকরির বাজার পর্যালোচনা",
    "nav_skills": "দক্ষতা চাহিদা বিশ্লেষণ",
    "nav_cv_gap": "সিভি দক্ষতা ফাঁক বিশ্লেষক",
    "nav_recommendations": "প্রজেক্ট ও ক্যারিয়ার অ্যাকশন",
    "nav_clustering": "রোল ক্লাস্টারিং",
    "nav_import": "ডেটা ইমপোর্ট",
    "nav_explorer": "ক্যারিয়ার এক্সপ্লোরার",
    "nav_job_match": "জব ম্যাচ ড্যাশবোর্ড",
    "nav_toolkit": "ক্যারিয়ার টুলকিট",
    "dataset_source": "ডেটাসেট সোর্স",
    "language": "ভাষা",
    "analyze": "বিশ্লেষণ করুন",
    "download": "ডাউনলোড",
    "match_score": "ম্যাচ স্কোর",
    "missing_skills": "অনুপস্থিত দক্ষতা",
    "matched_skills": "মিলে যাওয়া দক্ষতা",
    "learning_resources": "শেখার রিসোর্স",
    "interview_questions": "ইন্টারভিউ প্রশ্ন",
    "resume_bullets": "রেজুমে বুলেট",
    "progress_tracker": "অগ্রগতি ট্র্যাকার",
    "skill_growth": "দক্ষতা বৃদ্ধি",
    "badges": "ব্যাজ",
    "time_series": "সময়ের সাথে দক্ষতা চাহিদা",
    "public_connectors": "পাবলিক ডেটা কানেক্টর",
    "honest_note": "ফলাফল নির্দেশনা মাত্র, নিয়োগের garanti নয়।",
}


def main() -> None:
    (DATA / "skill_synonyms.json").write_text(
        json.dumps(SKILL_SYNONYMS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DATA / "interview_questions.json").write_text(
        json.dumps(INTERVIEW_QUESTIONS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DATA / "learning_resources.json").write_text(
        json.dumps(LEARNING_RESOURCES, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DATA / "gamification_badges.json").write_text(
        json.dumps(GAMIFICATION_BADGES, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    regional = {"regions": REGIONS, "profiles": REGIONAL_PROFILES}
    (DATA / "career_taxonomies" / "regional_profiles.json").write_text(
        json.dumps(regional, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    i18n_dir = DATA / "i18n"
    i18n_dir.mkdir(parents=True, exist_ok=True)
    (i18n_dir / "en.json").write_text(json.dumps(I18N_EN, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (i18n_dir / "bn.json").write_text(json.dumps(I18N_BN, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DATA / "user_progress").mkdir(parents=True, exist_ok=True)
    progress_file = DATA / "user_progress" / "progress.json"
    if not progress_file.exists():
        progress_file.write_text(
            json.dumps({"gap_history": [], "stats": {}, "completed_actions": [], "badges_earned": []}, indent=2)
            + "\n",
            encoding="utf-8",
        )
    print("Generated advanced feature data files.")


if __name__ == "__main__":
    main()
