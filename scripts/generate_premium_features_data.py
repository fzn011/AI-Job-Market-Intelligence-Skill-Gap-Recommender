"""Generate premium feature JSON data assets."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

COMPANY_PREP_PACKS = {
    "Google": {
        "industry": "Technology",
        "headquarters": "United States",
        "hiring_focus": ["problem solving", "communication", "python", "machine learning", "system design"],
        "interview_style": "Structured technical + behavioral loops with strong emphasis on scalability and clarity.",
        "core_values": ["Focus on the user", "Think big", "Bias for action", "Data-driven decisions"],
        "typical_roles": ["Software Engineer", "Data Scientist", "Product Manager", "ML Engineer"],
        "prep_tips": [
            "Practice coding on a shared doc with clear communication.",
            "Prepare 2-3 projects with measurable impact metrics.",
            "Review system design basics even for ML roles.",
        ],
        "sample_questions": [
            "Tell me about a time you solved an ambiguous problem with data.",
            "How would you design a scalable logging pipeline?",
        ],
    },
    "bKash": {
        "industry": "Fintech",
        "headquarters": "Bangladesh",
        "hiring_focus": ["sql", "excel", "communication", "customer service", "financial products", "risk assessment"],
        "interview_style": "Mix of operational case questions, product knowledge, and customer-centric scenarios.",
        "core_values": ["Financial inclusion", "Customer trust", "Operational excellence"],
        "typical_roles": ["Data Analyst", "Business Analyst", "Risk Analyst", "Operations Executive"],
        "prep_tips": [
            "Understand mobile financial services and agent banking basics.",
            "Prepare examples showing attention to detail in reporting.",
            "Highlight experience with dashboards and KPI tracking.",
        ],
        "sample_questions": [
            "How would you monitor transaction anomaly patterns?",
            "Describe a customer complaint you resolved effectively.",
        ],
    },
    "Grameenphone": {
        "industry": "Telecommunications",
        "headquarters": "Bangladesh",
        "hiring_focus": ["communication", "customer service", "excel", "data analysis", "marketing", "network basics"],
        "interview_style": "Behavioral interviews plus domain questions on telecom products and customer lifecycle.",
        "core_values": ["Customer first", "Innovation", "Integrity"],
        "typical_roles": ["Digital Marketing Executive", "Customer Service Representative", "Data Analyst", "Business Analyst"],
        "prep_tips": [
            "Learn basic telecom product vocabulary (prepaid, postpaid, churn, ARPU).",
            "Prepare campaign or retention analysis examples.",
            "Show teamwork in high-volume customer environments.",
        ],
        "sample_questions": [
            "How would you reduce churn for prepaid users?",
            "Explain a campaign you would run for a new data package.",
        ],
    },
    "Microsoft": {
        "industry": "Technology",
        "headquarters": "United States",
        "hiring_focus": ["azure", "python", "sql", "communication", "collaboration", "problem solving"],
        "interview_style": "Growth mindset behavioral questions plus technical depth.",
        "core_values": ["Growth mindset", "Customer obsession", "Diversity and inclusion"],
        "typical_roles": ["Cloud Engineer", "Data Engineer", "Software Developer", "BI Analyst"],
        "prep_tips": [
            "Prepare STAR stories showing learning from failure.",
            "Review Azure fundamentals for cloud roles.",
            "Highlight cross-functional collaboration.",
        ],
        "sample_questions": [
            "Tell me about a time you learned a new technology quickly.",
            "How do you prioritize competing stakeholder requests?",
        ],
    },
    "BRAC": {
        "industry": "NGO / Development",
        "headquarters": "Bangladesh",
        "hiring_focus": ["communication", "report writing", "excel", "field operations", "monitoring and evaluation"],
        "interview_style": "Mission alignment, field impact, and practical program management questions.",
        "core_values": ["Empowerment", "Innovation", "Integrity", "Inclusiveness"],
        "typical_roles": ["Program Coordinator", "Monitoring Officer", "Field Officer", "Research Assistant"],
        "prep_tips": [
            "Connect your work to community impact.",
            "Prepare M&E or reporting examples.",
            "Show adaptability in resource-constrained settings.",
        ],
        "sample_questions": [
            "How would you measure success for a community program?",
            "Describe working with diverse stakeholders in the field.",
        ],
    },
    "Pathao": {
        "industry": "Technology / Logistics",
        "headquarters": "Bangladesh",
        "hiring_focus": ["operations management", "excel", "data analysis", "customer service", "logistics coordination"],
        "interview_style": "Fast-paced operational problem solving and growth metrics.",
        "core_values": ["Speed", "Customer focus", "Ownership"],
        "typical_roles": ["Operations Executive", "Business Analyst", "Supply Chain Executive", "Data Analyst"],
        "prep_tips": [
            "Prepare examples optimizing delivery or logistics KPIs.",
            "Show comfort with ambiguous startup environments.",
            "Highlight data-driven operations improvements.",
        ],
        "sample_questions": [
            "How would you improve rider allocation during peak hours?",
            "Describe a process you improved with data.",
        ],
    },
}

SALARY_BANDS = {
    "Bangladesh": {
        "Data Analyst": {"entry": "350000-550000", "mid": "550000-900000", "senior": "900000-1400000", "currency": "BDT/year"},
        "Data Scientist": {"entry": "600000-900000", "mid": "900000-1500000", "senior": "1500000-2500000", "currency": "BDT/year"},
        "Software Developer": {"entry": "400000-700000", "mid": "700000-1200000", "senior": "1200000-2000000", "currency": "BDT/year"},
        "Credit Analyst": {"entry": "350000-500000", "mid": "500000-800000", "senior": "800000-1200000", "currency": "BDT/year"},
        "Digital Marketing Executive": {"entry": "250000-400000", "mid": "400000-650000", "senior": "650000-1000000", "currency": "BDT/year"},
    },
    "United States": {
        "Data Analyst": {"entry": "65000-85000", "mid": "85000-110000", "senior": "110000-140000", "currency": "USD/year"},
        "Data Scientist": {"entry": "90000-120000", "mid": "120000-160000", "senior": "160000-220000", "currency": "USD/year"},
        "Software Developer": {"entry": "80000-110000", "mid": "110000-150000", "senior": "150000-200000", "currency": "USD/year"},
        "Machine Learning Engineer": {"entry": "110000-140000", "mid": "140000-180000", "senior": "180000-250000", "currency": "USD/year"},
    },
    "United Kingdom": {
        "Data Analyst": {"entry": "28000-35000", "mid": "35000-48000", "senior": "48000-65000", "currency": "GBP/year"},
        "Data Scientist": {"entry": "35000-45000", "mid": "45000-65000", "senior": "65000-90000", "currency": "GBP/year"},
        "Software Developer": {"entry": "30000-42000", "mid": "42000-60000", "senior": "60000-85000", "currency": "GBP/year"},
    },
    "Remote": {
        "Data Analyst": {"entry": "45000-70000", "mid": "70000-95000", "senior": "95000-130000", "currency": "USD/year"},
        "Data Scientist": {"entry": "80000-110000", "mid": "110000-150000", "senior": "150000-200000", "currency": "USD/year"},
        "Frontend Developer": {"entry": "60000-90000", "mid": "90000-120000", "senior": "120000-160000", "currency": "USD/year"},
    },
}

VOICE_INTERVIEW_RUBRIC = {
    "dimensions": ["clarity", "structure", "technical_depth", "confidence", "relevance"],
    "scale": {"1": "Needs improvement", "2": "Developing", "3": "Adequate", "4": "Strong", "5": "Excellent"},
}


def main() -> None:
    (DATA / "company_prep_packs.json").write_text(
        json.dumps(COMPANY_PREP_PACKS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DATA / "salary_bands.json").write_text(
        json.dumps(SALARY_BANDS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DATA / "voice_interview_rubric.json").write_text(
        json.dumps(VOICE_INTERVIEW_RUBRIC, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("Generated premium feature data files.")


if __name__ == "__main__":
    main()
