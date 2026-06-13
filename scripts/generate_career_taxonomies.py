"""Generate career taxonomy JSON files for CareerCompass."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "career_taxonomies"

CATEGORY_FILES = {
    "Data & AI": "data_ai_skills.json",
    "Software & IT": "software_it_skills.json",
    "Banking & Finance": "banking_finance_skills.json",
    "Business & Administration": "business_admin_skills.json",
    "Marketing & Sales": "marketing_sales_skills.json",
    "Design & Creative": "design_creative_skills.json",
    "Education & Teaching": "education_teaching_skills.json",
    "Healthcare": "healthcare_skills.json",
    "Engineering": "engineering_skills.json",
    "Customer Support": "customer_support_skills.json",
    "Operations & Project Management": "operations_project_management_skills.json",
    "General Entry-Level Jobs": "general_entry_level_skills.json",
}

TAXONOMIES = {
    "Data & AI": {
        "technical_skills": [
            "python", "sql", "pandas", "numpy", "machine learning", "scikit-learn",
            "power bi", "tableau", "data visualization", "statistics", "nlp", "llm",
            "rag", "docker", "fastapi", "mlflow", "excel", "etl", "spark", "aws",
            "feature engineering", "a/b testing", "deep learning", "pytorch", "tensorflow",
        ],
        "domain_skills": [
            "business analysis", "customer analytics", "risk analytics", "product analytics",
            "forecasting", "experiment design", "data governance", "reporting",
        ],
        "soft_skills": [
            "communication", "problem solving", "stakeholder management", "critical thinking",
            "collaboration", "storytelling with data", "attention to detail",
        ],
    },
    "Software & IT": {
        "technical_skills": [
            "javascript", "typescript", "python", "java", "html", "css", "react",
            "node.js", "sql", "git", "docker", "kubernetes", "aws", "rest api",
            "testing", "linux", "ci/cd", "mongodb", "postgresql", "agile",
        ],
        "domain_skills": [
            "system design", "debugging", "code review", "software architecture",
            "api design", "security basics", "performance optimization",
        ],
        "soft_skills": [
            "communication", "problem solving", "teamwork", "time management",
            "documentation", "collaboration", "adaptability",
        ],
    },
    "Banking & Finance": {
        "technical_skills": [
            "excel", "financial analysis", "credit analysis", "risk assessment",
            "financial reporting", "accounting", "budgeting", "sql", "power bi",
            "financial modeling", "sap", "tally", "quickbooks",
        ],
        "domain_skills": [
            "banking operations", "loan processing", "regulatory compliance",
            "customer onboarding", "anti money laundering", "financial products",
            "investment analysis", "portfolio management", "kyc",
        ],
        "soft_skills": [
            "attention to detail", "communication", "client relationship management",
            "problem solving", "integrity", "analytical thinking", "confidentiality",
        ],
    },
    "Business & Administration": {
        "technical_skills": [
            "excel", "microsoft office", "google workspace", "power bi", "sql",
            "crm software", "erp systems", "data entry", "scheduling tools",
        ],
        "domain_skills": [
            "office administration", "hr operations", "recruitment support",
            "business analysis", "process improvement", "vendor management",
            "meeting coordination", "policy compliance", "inventory management",
        ],
        "soft_skills": [
            "communication", "organization", "time management", "multitasking",
            "professionalism", "conflict resolution", "team coordination",
        ],
    },
    "Marketing & Sales": {
        "technical_skills": [
            "google analytics", "seo", "sem", "social media marketing", "crm",
            "email marketing", "content marketing", "canva", "hubspot",
            "salesforce", "meta ads", "google ads", "copywriting",
        ],
        "domain_skills": [
            "market research", "brand management", "lead generation",
            "customer acquisition", "sales pipeline", "campaign planning",
            "conversion optimization", "competitive analysis",
        ],
        "soft_skills": [
            "communication", "persuasion", "creativity", "negotiation",
            "presentation skills", "relationship building", "resilience",
        ],
    },
    "Design & Creative": {
        "technical_skills": [
            "figma", "adobe photoshop", "adobe illustrator", "ui design",
            "ux design", "wireframing", "prototyping", "visual design",
            "design systems", "after effects", "sketch", "invision",
        ],
        "domain_skills": [
            "user research", "brand identity", "social media design",
            "mobile app design", "web design", "typography", "color theory",
            "accessibility design",
        ],
        "soft_skills": [
            "creativity", "communication", "collaboration", "attention to detail",
            "presentation skills", "feedback acceptance", "visual storytelling",
        ],
    },
    "Education & Teaching": {
        "technical_skills": [
            "lesson planning", "curriculum design", "assessment design",
            "google classroom", "microsoft teams", "lms", "presentation tools",
            "educational technology", "online teaching tools",
        ],
        "domain_skills": [
            "subject knowledge", "classroom management", "student assessment",
            "differentiated instruction", "parent communication", "academic coordination",
            "learning outcomes", "education policy basics",
        ],
        "soft_skills": [
            "communication", "patience", "empathy", "organization",
            "leadership", "creativity", "conflict resolution",
        ],
    },
    "Healthcare": {
        "technical_skills": [
            "patient care", "vital signs monitoring", "medical records",
            "electronic health records", "lab procedures", "infection control",
            "medication administration", "first aid", "cpr",
        ],
        "domain_skills": [
            "clinical documentation", "healthcare compliance", "patient safety",
            "public health basics", "health education", "triage",
            "care coordination", "medical terminology",
        ],
        "soft_skills": [
            "empathy", "communication", "attention to detail", "teamwork",
            "stress management", "compassion", "professional ethics",
        ],
    },
    "Engineering": {
        "technical_skills": [
            "autocad", "solidworks", "matlab", "project estimation",
            "quality control", "technical drawing", "site supervision",
            "safety standards", "materials knowledge", "measurement tools",
        ],
        "domain_skills": [
            "structural analysis", "electrical systems", "mechanical systems",
            "construction management", "maintenance planning", "iso standards",
            "environmental compliance", "cost estimation",
        ],
        "soft_skills": [
            "problem solving", "communication", "teamwork", "attention to detail",
            "project coordination", "safety awareness", "analytical thinking",
        ],
    },
    "Customer Support": {
        "technical_skills": [
            "crm", "ticketing systems", "live chat tools", "phone support",
            "email support", "knowledge base management", "troubleshooting",
            "product documentation", "help desk software",
        ],
        "domain_skills": [
            "customer service", "complaint handling", "escalation management",
            "sla management", "customer onboarding support", "feedback collection",
            "support analytics", "product knowledge",
        ],
        "soft_skills": [
            "communication", "empathy", "patience", "active listening",
            "problem solving", "conflict resolution", "professionalism",
        ],
    },
    "Operations & Project Management": {
        "technical_skills": [
            "project planning", "ms project", "jira", "asana", "excel",
            "process mapping", "supply chain basics", "inventory tracking",
            "kpi tracking", "budget tracking", "risk register",
        ],
        "domain_skills": [
            "operations management", "logistics coordination", "vendor coordination",
            "resource planning", "quality assurance", "continuous improvement",
            "stakeholder reporting", "procurement support",
        ],
        "soft_skills": [
            "leadership", "communication", "organization", "problem solving",
            "negotiation", "decision making", "time management",
        ],
    },
    "General Entry-Level Jobs": {
        "technical_skills": [
            "microsoft office", "data entry", "typing", "email communication",
            "basic computer skills", "cash handling", "inventory management",
            "scheduling", "filing systems",
        ],
        "domain_skills": [
            "customer service", "office support", "retail operations",
            "reception duties", "record keeping", "basic reporting",
            "front desk management", "order processing",
        ],
        "soft_skills": [
            "communication", "reliability", "punctuality", "teamwork",
            "adaptability", "customer focus", "willingness to learn",
        ],
    },
}

ROLE_PROFILES = {
    "Data & AI": {
        "Data Analyst": {
            "level": "Entry to Mid",
            "core_skills": ["sql", "excel", "power bi", "python", "data visualization"],
            "helpful_skills": ["statistics", "pandas", "stakeholder management"],
            "typical_outputs": ["dashboards", "reports", "business insights"],
            "recommended_actions": ["build a dashboard portfolio", "practice SQL case studies"],
        },
        "Data Scientist": {
            "level": "Mid",
            "core_skills": ["python", "sql", "machine learning", "statistics", "pandas"],
            "helpful_skills": ["scikit-learn", "a/b testing", "communication"],
            "typical_outputs": ["models", "experiments", "insights reports"],
            "recommended_actions": ["build an end-to-end ML project", "document experiment results"],
        },
        "Machine Learning Engineer": {
            "level": "Mid to Senior",
            "core_skills": ["python", "machine learning", "docker", "mlflow", "sql"],
            "helpful_skills": ["fastapi", "aws", "feature engineering"],
            "typical_outputs": ["deployed models", "pipelines", "monitoring dashboards"],
            "recommended_actions": ["build an ML API deployment project", "practice MLOps workflows"],
        },
        "AI Engineer": {
            "level": "Mid",
            "core_skills": ["python", "llm", "rag", "fastapi", "docker"],
            "helpful_skills": ["nlp", "mlflow", "aws"],
            "typical_outputs": ["AI applications", "RAG systems", "API services"],
            "recommended_actions": ["build a RAG document assistant", "deploy an AI API"],
        },
        "BI Analyst": {
            "level": "Entry to Mid",
            "core_skills": ["power bi", "sql", "excel", "data visualization", "reporting"],
            "helpful_skills": ["tableau", "business analysis", "stakeholder management"],
            "typical_outputs": ["BI dashboards", "KPI reports", "executive summaries"],
            "recommended_actions": ["create a sales KPI dashboard", "practice DAX/SQL reporting"],
        },
        "Data Engineer": {
            "level": "Mid",
            "core_skills": ["python", "sql", "etl", "spark", "aws"],
            "helpful_skills": ["docker", "airflow", "data governance"],
            "typical_outputs": ["data pipelines", "warehouse models", "quality checks"],
            "recommended_actions": ["build an ETL pipeline project", "document data lineage"],
        },
    },
    "Software & IT": {
        "Frontend Developer": {
            "level": "Entry to Mid",
            "core_skills": ["html", "css", "javascript", "react", "git"],
            "helpful_skills": ["typescript", "testing", "responsive design"],
            "typical_outputs": ["web interfaces", "component libraries", "UI prototypes"],
            "recommended_actions": ["build a responsive portfolio site", "create a React component library"],
        },
        "Backend Developer": {
            "level": "Mid",
            "core_skills": ["python", "sql", "rest api", "git", "postgresql"],
            "helpful_skills": ["docker", "testing", "system design"],
            "typical_outputs": ["APIs", "database schemas", "service modules"],
            "recommended_actions": ["build a REST API with auth", "add automated tests"],
        },
        "Full Stack Developer": {
            "level": "Mid",
            "core_skills": ["javascript", "react", "node.js", "sql", "rest api"],
            "helpful_skills": ["docker", "aws", "git"],
            "typical_outputs": ["full web apps", "deployed products", "documentation"],
            "recommended_actions": ["build a full-stack CRUD app", "deploy to cloud"],
        },
        "QA Tester": {
            "level": "Entry to Mid",
            "core_skills": ["testing", "bug reporting", "agile", "documentation"],
            "helpful_skills": ["automation basics", "sql", "communication"],
            "typical_outputs": ["test cases", "bug reports", "regression plans"],
            "recommended_actions": ["create a test plan portfolio", "practice API testing"],
        },
        "IT Support Specialist": {
            "level": "Entry",
            "core_skills": ["troubleshooting", "linux", "networking basics", "documentation"],
            "helpful_skills": ["customer service", "security basics", "ticketing systems"],
            "typical_outputs": ["support tickets resolved", "knowledge base articles"],
            "recommended_actions": ["build a troubleshooting guide", "practice help desk scenarios"],
        },
        "DevOps Engineer": {
            "level": "Mid to Senior",
            "core_skills": ["docker", "kubernetes", "ci/cd", "linux", "aws"],
            "helpful_skills": ["python", "monitoring", "security basics"],
            "typical_outputs": ["pipelines", "infrastructure configs", "deployment automation"],
            "recommended_actions": ["set up CI/CD for a sample app", "document infra as code"],
        },
    },
    "Banking & Finance": {
        "Bank Officer": {
            "level": "Entry to Mid",
            "core_skills": ["banking operations", "customer onboarding", "excel", "communication"],
            "helpful_skills": ["kyc", "financial products", "regulatory compliance"],
            "typical_outputs": ["account opening files", "customer service reports"],
            "recommended_actions": ["prepare a customer onboarding process summary", "practice product comparison notes"],
        },
        "Credit Analyst": {
            "level": "Entry to Mid",
            "core_skills": ["financial analysis", "credit analysis", "risk assessment", "excel"],
            "helpful_skills": ["sql", "power bi", "regulatory compliance"],
            "typical_outputs": ["credit reports", "risk summaries", "financial analysis notes"],
            "recommended_actions": ["prepare a credit risk case study", "build an Excel financial workbook"],
        },
        "Financial Analyst": {
            "level": "Mid",
            "core_skills": ["financial modeling", "excel", "financial reporting", "budgeting"],
            "helpful_skills": ["sql", "power bi", "accounting"],
            "typical_outputs": ["forecasts", "variance reports", "investment memos"],
            "recommended_actions": ["build a 3-statement model", "create a budget variance dashboard"],
        },
        "Accounts Officer": {
            "level": "Entry to Mid",
            "core_skills": ["accounting", "excel", "financial reporting", "tally"],
            "helpful_skills": ["quickbooks", "attention to detail", "reconciliation"],
            "typical_outputs": ["ledgers", "month-end reports", "reconciliation sheets"],
            "recommended_actions": ["practice journal entry case studies", "build a reconciliation checklist"],
        },
        "Risk Analyst": {
            "level": "Mid",
            "core_skills": ["risk assessment", "financial analysis", "excel", "regulatory compliance"],
            "helpful_skills": ["sql", "power bi", "anti money laundering"],
            "typical_outputs": ["risk reports", "compliance summaries", "monitoring dashboards"],
            "recommended_actions": ["prepare a risk assessment case study", "document compliance controls"],
        },
        "Compliance Officer": {
            "level": "Mid",
            "core_skills": ["regulatory compliance", "anti money laundering", "kyc", "documentation"],
            "helpful_skills": ["financial products", "communication", "audit support"],
            "typical_outputs": ["compliance checklists", "audit responses", "policy summaries"],
            "recommended_actions": ["create a compliance checklist", "prepare an AML scenario analysis"],
        },
    },
    "Business & Administration": {
        "Admin Officer": {
            "level": "Entry",
            "core_skills": ["office administration", "microsoft office", "organization", "communication"],
            "helpful_skills": ["scheduling tools", "data entry", "vendor management"],
            "typical_outputs": ["schedules", "office reports", "coordination logs"],
            "recommended_actions": ["create an office operations SOP", "build a scheduling template pack"],
        },
        "HR Executive": {
            "level": "Entry to Mid",
            "core_skills": ["hr operations", "recruitment support", "communication", "microsoft office"],
            "helpful_skills": ["crm software", "policy compliance", "interview coordination"],
            "typical_outputs": ["candidate pipelines", "onboarding checklists", "HR reports"],
            "recommended_actions": ["build a recruitment tracker", "create an onboarding checklist"],
        },
        "Business Analyst": {
            "level": "Mid",
            "core_skills": ["business analysis", "excel", "process improvement", "communication"],
            "helpful_skills": ["sql", "power bi", "stakeholder management"],
            "typical_outputs": ["requirements docs", "process maps", "impact analyses"],
            "recommended_actions": ["prepare a process improvement case study", "create a requirements template"],
        },
        "Operations Executive": {
            "level": "Entry to Mid",
            "core_skills": ["operations management", "excel", "process improvement", "kpi tracking"],
            "helpful_skills": ["vendor management", "inventory tracking", "reporting"],
            "typical_outputs": ["operations reports", "SOPs", "KPI dashboards"],
            "recommended_actions": ["map an end-to-end process", "build a KPI tracker in Excel"],
        },
        "Office Coordinator": {
            "level": "Entry",
            "core_skills": ["meeting coordination", "organization", "communication", "scheduling"],
            "helpful_skills": ["google workspace", "vendor coordination", "multitasking"],
            "typical_outputs": ["meeting agendas", "event plans", "coordination calendars"],
            "recommended_actions": ["create an event planning checklist", "build a meeting agenda template"],
        },
    },
    "Marketing & Sales": {
        "Digital Marketing Executive": {
            "level": "Entry to Mid",
            "core_skills": ["social media marketing", "google analytics", "content marketing", "seo"],
            "helpful_skills": ["copywriting", "canva", "email marketing"],
            "typical_outputs": ["campaign reports", "content calendars", "analytics summaries"],
            "recommended_actions": ["run a mock digital campaign", "build a content calendar portfolio"],
        },
        "SEO Specialist": {
            "level": "Mid",
            "core_skills": ["seo", "google analytics", "content marketing", "keyword research"],
            "helpful_skills": ["sem", "copywriting", "technical seo basics"],
            "typical_outputs": ["SEO audits", "ranking reports", "optimization plans"],
            "recommended_actions": ["perform an SEO audit case study", "create an optimization roadmap"],
        },
        "Sales Executive": {
            "level": "Entry to Mid",
            "core_skills": ["sales pipeline", "communication", "lead generation", "crm"],
            "helpful_skills": ["negotiation", "presentation skills", "market research"],
            "typical_outputs": ["sales decks", "pipeline reports", "client proposals"],
            "recommended_actions": ["create a sales pitch deck", "build a CRM pipeline case study"],
        },
        "Content Marketer": {
            "level": "Entry to Mid",
            "core_skills": ["content marketing", "copywriting", "seo", "social media marketing"],
            "helpful_skills": ["canva", "email marketing", "analytics"],
            "typical_outputs": ["blog posts", "campaign copy", "editorial calendars"],
            "recommended_actions": ["build a content portfolio", "write a campaign case study"],
        },
        "Social Media Manager": {
            "level": "Entry to Mid",
            "core_skills": ["social media marketing", "content marketing", "canva", "analytics"],
            "helpful_skills": ["copywriting", "community management", "paid ads basics"],
            "typical_outputs": ["content plans", "engagement reports", "brand campaigns"],
            "recommended_actions": ["create a 30-day content plan", "design a campaign mockup"],
        },
        "Brand Executive": {
            "level": "Mid",
            "core_skills": ["brand management", "market research", "communication", "campaign planning"],
            "helpful_skills": ["copywriting", "presentation skills", "competitive analysis"],
            "typical_outputs": ["brand guidelines", "campaign briefs", "positioning docs"],
            "recommended_actions": ["create a brand identity mock project", "prepare a positioning statement"],
        },
    },
    "Design & Creative": {
        "Graphic Designer": {
            "level": "Entry to Mid",
            "core_skills": ["adobe photoshop", "adobe illustrator", "visual design", "typography"],
            "helpful_skills": ["brand identity", "social media design", "creativity"],
            "typical_outputs": ["posters", "social graphics", "brand assets"],
            "recommended_actions": ["build a branding portfolio", "create a social media design pack"],
        },
        "UI/UX Designer": {
            "level": "Mid",
            "core_skills": ["figma", "ui design", "ux design", "wireframing", "prototyping"],
            "helpful_skills": ["user research", "design systems", "accessibility design"],
            "typical_outputs": ["UI case studies", "prototypes", "design systems"],
            "recommended_actions": ["create a mobile app UI case study", "redesign a landing page in Figma"],
        },
        "Motion Designer": {
            "level": "Mid",
            "core_skills": ["after effects", "visual design", "storyboarding", "adobe illustrator"],
            "helpful_skills": ["adobe photoshop", "brand identity", "presentation skills"],
            "typical_outputs": ["motion graphics", "animated explainers", "social video assets"],
            "recommended_actions": ["create a 30-second motion reel", "animate a product explainer"],
        },
        "Brand Designer": {
            "level": "Mid",
            "core_skills": ["brand identity", "visual design", "figma", "typography"],
            "helpful_skills": ["adobe illustrator", "presentation skills", "user research"],
            "typical_outputs": ["logo systems", "brand guides", "marketing kits"],
            "recommended_actions": ["build a brand identity mock project", "document a brand style guide"],
        },
        "Product Designer": {
            "level": "Mid to Senior",
            "core_skills": ["figma", "ux design", "user research", "prototyping", "design systems"],
            "helpful_skills": ["ui design", "accessibility design", "collaboration"],
            "typical_outputs": ["product flows", "design specs", "usability findings"],
            "recommended_actions": ["create an end-to-end product case study", "run a usability test summary"],
        },
    },
    "Education & Teaching": {
        "School Teacher": {
            "level": "Entry to Mid",
            "core_skills": ["lesson planning", "classroom management", "subject knowledge", "communication"],
            "helpful_skills": ["assessment design", "educational technology", "patience"],
            "typical_outputs": ["lesson plans", "assessments", "student progress reports"],
            "recommended_actions": ["create a lesson plan portfolio", "record a short teaching demo"],
        },
        "Physics Teacher": {
            "level": "Entry to Mid",
            "core_skills": ["subject knowledge", "lesson planning", "assessment design", "communication"],
            "helpful_skills": ["classroom management", "experiment design", "curriculum design"],
            "typical_outputs": ["lab plans", "worksheets", "assessment rubrics"],
            "recommended_actions": ["build a physics lab portfolio", "create assessment materials"],
        },
        "Mathematics Teacher": {
            "level": "Entry to Mid",
            "core_skills": ["subject knowledge", "lesson planning", "assessment design", "communication"],
            "helpful_skills": ["differentiated instruction", "problem solving", "classroom management"],
            "typical_outputs": ["problem sets", "lesson sequences", "assessment sheets"],
            "recommended_actions": ["create a topic-wise worksheet pack", "design a diagnostic assessment"],
        },
        "English Teacher": {
            "level": "Entry to Mid",
            "core_skills": ["subject knowledge", "lesson planning", "communication", "assessment design"],
            "helpful_skills": ["creative writing", "classroom management", "feedback skills"],
            "typical_outputs": ["reading guides", "writing prompts", "assessment rubrics"],
            "recommended_actions": ["build a writing skills module", "create a reading comprehension pack"],
        },
        "Academic Coordinator": {
            "level": "Mid",
            "core_skills": ["academic coordination", "curriculum design", "communication", "organization"],
            "helpful_skills": ["assessment design", "stakeholder reporting", "leadership"],
            "typical_outputs": ["academic calendars", "program reports", "quality reviews"],
            "recommended_actions": ["prepare an academic calendar plan", "create a program review template"],
        },
        "Online Course Instructor": {
            "level": "Entry to Mid",
            "core_skills": ["online teaching tools", "lesson planning", "communication", "presentation tools"],
            "helpful_skills": ["lms", "video recording", "student engagement"],
            "typical_outputs": ["course modules", "video lessons", "quizzes"],
            "recommended_actions": ["record a mini-course module", "build a course outline portfolio"],
        },
    },
    "Healthcare": {
        "Nurse": {
            "level": "Entry to Mid",
            "core_skills": ["patient care", "vital signs monitoring", "medication administration", "communication"],
            "helpful_skills": ["electronic health records", "infection control", "empathy"],
            "typical_outputs": ["care plans", "patient notes", "handover reports"],
            "recommended_actions": ["prepare a patient care case study", "practice clinical documentation"],
        },
        "Medical Assistant": {
            "level": "Entry",
            "core_skills": ["patient care", "vital signs monitoring", "medical records", "communication"],
            "helpful_skills": ["appointment scheduling", "infection control", "first aid"],
            "typical_outputs": ["patient intake forms", "clinical support logs"],
            "recommended_actions": ["create a patient intake workflow", "practice vital signs documentation"],
        },
        "Healthcare Administrator": {
            "level": "Mid",
            "core_skills": ["healthcare compliance", "medical records", "operations management", "communication"],
            "helpful_skills": ["budget tracking", "staff coordination", "reporting"],
            "typical_outputs": ["admin reports", "compliance checklists", "scheduling plans"],
            "recommended_actions": ["build a clinic operations checklist", "prepare a compliance summary"],
        },
        "Lab Technician": {
            "level": "Entry to Mid",
            "core_skills": ["lab procedures", "quality control", "medical terminology", "attention to detail"],
            "helpful_skills": ["infection control", "documentation", "equipment maintenance"],
            "typical_outputs": ["lab reports", "quality logs", "sample tracking records"],
            "recommended_actions": ["create a lab SOP sample", "practice result reporting format"],
        },
        "Public Health Officer": {
            "level": "Mid",
            "core_skills": ["public health basics", "health education", "data collection", "communication"],
            "helpful_skills": ["report writing", "community outreach", "program coordination"],
            "typical_outputs": ["health campaigns", "survey reports", "awareness materials"],
            "recommended_actions": ["design a community health campaign", "prepare a survey analysis report"],
        },
    },
    "Engineering": {
        "Civil Engineer": {
            "level": "Mid",
            "core_skills": ["autocad", "structural analysis", "project estimation", "site supervision"],
            "helpful_skills": ["construction management", "safety standards", "cost estimation"],
            "typical_outputs": ["drawings", "site reports", "cost estimates"],
            "recommended_actions": ["prepare a structural design case study", "create a site inspection checklist"],
        },
        "Electrical Engineer": {
            "level": "Mid",
            "core_skills": ["electrical systems", "technical drawing", "safety standards", "troubleshooting"],
            "helpful_skills": ["autocad", "project coordination", "maintenance planning"],
            "typical_outputs": ["circuit designs", "maintenance plans", "inspection reports"],
            "recommended_actions": ["document an electrical maintenance plan", "create a load calculation case study"],
        },
        "Mechanical Engineer": {
            "level": "Mid",
            "core_skills": ["solidworks", "mechanical systems", "materials knowledge", "quality control"],
            "helpful_skills": ["matlab", "project estimation", "iso standards"],
            "typical_outputs": ["CAD models", "maintenance schedules", "quality reports"],
            "recommended_actions": ["build a CAD portfolio piece", "prepare a quality inspection report"],
        },
        "Site Engineer": {
            "level": "Entry to Mid",
            "core_skills": ["site supervision", "construction management", "safety standards", "communication"],
            "helpful_skills": ["autocad", "project coordination", "quality control"],
            "typical_outputs": ["daily site reports", "progress logs", "safety checklists"],
            "recommended_actions": ["create a daily site report template", "prepare a safety audit checklist"],
        },
        "Quality Engineer": {
            "level": "Mid",
            "core_skills": ["quality control", "iso standards", "process improvement", "documentation"],
            "helpful_skills": ["statistical analysis basics", "audit support", "problem solving"],
            "typical_outputs": ["inspection reports", "CAPA documents", "quality dashboards"],
            "recommended_actions": ["prepare a quality audit case study", "build a defect tracking log"],
        },
    },
    "Customer Support": {
        "Customer Service Representative": {
            "level": "Entry",
            "core_skills": ["customer service", "communication", "active listening", "crm"],
            "helpful_skills": ["complaint handling", "product knowledge", "patience"],
            "typical_outputs": ["resolved tickets", "customer feedback summaries"],
            "recommended_actions": ["create a support response template pack", "practice complaint scenarios"],
        },
        "Call Center Agent": {
            "level": "Entry",
            "core_skills": ["phone support", "communication", "customer service", "active listening"],
            "helpful_skills": ["crm", "multitasking", "conflict resolution"],
            "typical_outputs": ["call summaries", "resolution logs", "QA scorecards"],
            "recommended_actions": ["practice call handling scripts", "build a resolution tracking sheet"],
        },
        "Client Support Executive": {
            "level": "Entry to Mid",
            "core_skills": ["email support", "customer service", "crm", "communication"],
            "helpful_skills": ["escalation management", "documentation", "product knowledge"],
            "typical_outputs": ["support emails", "client updates", "knowledge base articles"],
            "recommended_actions": ["create a client onboarding FAQ", "write knowledge base samples"],
        },
        "Technical Support Specialist": {
            "level": "Mid",
            "core_skills": ["troubleshooting", "technical documentation", "communication", "ticketing systems"],
            "helpful_skills": ["product knowledge", "remote support tools", "problem solving"],
            "typical_outputs": ["troubleshooting guides", "resolved technical tickets"],
            "recommended_actions": ["build a troubleshooting guide", "document common issue resolutions"],
        },
    },
    "Operations & Project Management": {
        "Project Coordinator": {
            "level": "Entry to Mid",
            "core_skills": ["project planning", "communication", "organization", "stakeholder reporting"],
            "helpful_skills": ["jira", "excel", "meeting coordination"],
            "typical_outputs": ["project schedules", "status reports", "meeting minutes"],
            "recommended_actions": ["create a project tracker template", "prepare a status report sample"],
        },
        "Project Manager": {
            "level": "Mid to Senior",
            "core_skills": ["project planning", "risk register", "stakeholder reporting", "leadership"],
            "helpful_skills": ["budget tracking", "jira", "negotiation"],
            "typical_outputs": ["project plans", "risk logs", "delivery reports"],
            "recommended_actions": ["build a full project plan case study", "create a risk register sample"],
        },
        "Operations Manager": {
            "level": "Mid to Senior",
            "core_skills": ["operations management", "kpi tracking", "process improvement", "leadership"],
            "helpful_skills": ["vendor management", "budget tracking", "continuous improvement"],
            "typical_outputs": ["operations dashboards", "SOP updates", "efficiency reports"],
            "recommended_actions": ["map an operations workflow", "build a KPI dashboard in Excel"],
        },
        "Supply Chain Executive": {
            "level": "Mid",
            "core_skills": ["supply chain basics", "inventory tracking", "vendor coordination", "excel"],
            "helpful_skills": ["logistics coordination", "procurement support", "kpi tracking"],
            "typical_outputs": ["inventory reports", "supplier evaluations", "delivery schedules"],
            "recommended_actions": ["create an inventory tracking model", "prepare a supplier scorecard"],
        },
        "Logistics Coordinator": {
            "level": "Entry to Mid",
            "core_skills": ["logistics coordination", "inventory tracking", "communication", "scheduling"],
            "helpful_skills": ["vendor coordination", "excel", "problem solving"],
            "typical_outputs": ["shipment schedules", "delivery logs", "exception reports"],
            "recommended_actions": ["build a shipment tracking sheet", "document a delivery escalation process"],
        },
    },
    "General Entry-Level Jobs": {
        "Office Assistant": {
            "level": "Entry",
            "core_skills": ["office support", "data entry", "communication", "organization"],
            "helpful_skills": ["microsoft office", "scheduling", "filing systems"],
            "typical_outputs": ["filing records", "support logs", "schedules"],
            "recommended_actions": ["create an office filing system guide", "build a daily task checklist"],
        },
        "Receptionist": {
            "level": "Entry",
            "core_skills": ["front desk management", "communication", "scheduling", "customer service"],
            "helpful_skills": ["multitasking", "professionalism", "basic computer skills"],
            "typical_outputs": ["visitor logs", "appointment schedules", "call summaries"],
            "recommended_actions": ["prepare a front desk SOP", "create a visitor management template"],
        },
        "Retail Assistant": {
            "level": "Entry",
            "core_skills": ["retail operations", "customer service", "cash handling", "communication"],
            "helpful_skills": ["inventory management", "product knowledge", "teamwork"],
            "typical_outputs": ["sales summaries", "stock checks", "customer feedback notes"],
            "recommended_actions": ["practice customer service scenarios", "create a product knowledge sheet"],
        },
        "Data Entry Operator": {
            "level": "Entry",
            "core_skills": ["data entry", "typing", "attention to detail", "basic computer skills"],
            "helpful_skills": ["excel", "quality control", "time management"],
            "typical_outputs": ["clean datasets", "entry logs", "accuracy reports"],
            "recommended_actions": ["complete a data cleaning practice task", "build a data validation checklist"],
        },
        "Junior Executive": {
            "level": "Entry",
            "core_skills": ["communication", "organization", "report writing", "microsoft office"],
            "helpful_skills": ["meeting coordination", "basic reporting", "teamwork"],
            "typical_outputs": ["meeting notes", "status updates", "support documents"],
            "recommended_actions": ["prepare a weekly report template", "create a meeting notes sample pack"],
        },
    },
}


def _action(
    action_id: str,
    title: str,
    category: str,
    action_type: str,
    difficulty: str,
    estimated_time: str,
    skills_covered: list[str],
    description: str,
    deliverables: list[str],
    portfolio_value: str,
) -> dict:
    return {
        "action_id": action_id,
        "title": title,
        "category": category,
        "action_type": action_type,
        "difficulty": difficulty,
        "estimated_time": estimated_time,
        "skills_covered": skills_covered,
        "description": description,
        "deliverables": deliverables,
        "portfolio_value": portfolio_value,
    }


CAREER_ACTIONS = [
    _action("da_dashboard", "Build a Sales Dashboard in Power BI", "Data & AI", "Portfolio Project", "Intermediate", "2-3 weeks", ["power bi", "sql", "data visualization"], "Create an end-to-end sales analytics dashboard with KPIs, filters, and executive summary.", ["Power BI file", "SQL queries", "README with screenshots"], "Demonstrates BI and business storytelling skills."),
    _action("da_sql", "Complete 30 SQL Query Practice Problems", "Data & AI", "Practice Task", "Beginner", "1-2 weeks", ["sql", "data analysis"], "Solve realistic SQL problems covering joins, aggregations, window functions, and filtering.", ["SQL solution notebook", "problem set summary"], "Shows strong analytical SQL fundamentals."),
    _action("da_excel", "Build an Excel KPI Tracker", "Data & AI", "Portfolio Project", "Beginner", "1 week", ["excel", "reporting"], "Design a dynamic Excel workbook with KPI tabs, charts, and automated summaries.", ["Excel workbook", "usage guide"], "Practical for analyst and business roles."),
    _action("ds_ml", "Build an End-to-End ML Classification Project", "Data & AI", "Portfolio Project", "Intermediate", "3-4 weeks", ["python", "machine learning", "scikit-learn"], "Train, evaluate, and document a classification model with clear business context.", ["GitHub repo", "model evaluation report"], "Core data science portfolio piece."),
    _action("ai_rag", "Build a Document Intelligence RAG System", "Data & AI", "Portfolio Project", "Advanced", "3-5 weeks", ["rag", "llm", "python", "fastapi"], "Create a retrieval-augmented QA app over a document collection with API endpoint.", ["GitHub repo", "demo video", "architecture diagram"], "Strong signal for AI engineer roles."),
    _action("ai_mlops", "MLOps Experiment Tracking Project", "Data & AI", "Portfolio Project", "Advanced", "2-4 weeks", ["mlflow", "docker", "python"], "Track experiments, package a model, and document reproducible training runs.", ["MLflow runs", "Docker setup", "README"], "Shows production-minded ML workflow."),
    _action("de_etl", "Build an ETL Pipeline with Validation", "Data & AI", "Portfolio Project", "Intermediate", "2-3 weeks", ["etl", "python", "sql"], "Ingest, clean, validate, and load sample data with logging and quality checks.", ["pipeline code", "data quality report"], "Demonstrates data engineering fundamentals."),
    _action("sw_frontend", "Build a Responsive Portfolio Website", "Software & IT", "Portfolio Project", "Beginner", "1-2 weeks", ["html", "css", "javascript", "react"], "Create a polished personal site with projects, about section, and contact form.", ["Live demo link", "GitHub repo"], "Essential for developer job applications."),
    _action("sw_api", "Build a REST API with Authentication", "Software & IT", "Portfolio Project", "Intermediate", "2-3 weeks", ["python", "rest api", "postgresql", "docker"], "Implement CRUD endpoints, auth, tests, and deployment-ready structure.", ["API repo", "Postman collection", "README"], "Shows backend engineering capability."),
    _action("sw_testing", "Create a Manual + Automated Test Plan", "Software & IT", "Case Study", "Beginner", "1 week", ["testing", "documentation", "agile"], "Document test cases and add basic automated checks for a sample web app.", ["Test plan doc", "automation scripts"], "Useful for QA and developer roles."),
    _action("sw_devops", "Set Up CI/CD for a Sample App", "Software & IT", "Portfolio Project", "Advanced", "2 weeks", ["ci/cd", "docker", "git"], "Configure automated build, test, and deploy pipeline for a small project.", ["Pipeline config", "deployment notes"], "Demonstrates DevOps readiness."),
    _action("sw_fullstack", "Build a Full-Stack CRUD Application", "Software & IT", "Portfolio Project", "Intermediate", "3-4 weeks", ["react", "node.js", "sql", "rest api"], "Create a complete app with frontend, backend, database, and documentation.", ["GitHub monorepo", "demo deployment"], "Strong full-stack portfolio evidence."),
    _action("fin_credit", "Prepare a Credit Risk Case Study", "Banking & Finance", "Case Study", "Intermediate", "1-2 weeks", ["credit analysis", "financial analysis", "excel"], "Analyze a hypothetical borrower profile and write a credit recommendation memo.", ["Case study PDF", "Excel model"], "Directly relevant for banking analyst roles."),
    _action("fin_excel", "Build an Excel Financial Analysis Workbook", "Banking & Finance", "Portfolio Project", "Beginner", "1 week", ["excel", "financial reporting", "budgeting"], "Create income/expense analysis with charts, assumptions, and summary dashboard.", ["Excel file", "methodology notes"], "Practical finance skill demonstration."),
    _action("fin_aml", "Create an AML Compliance Checklist", "Banking & Finance", "Domain Knowledge", "Intermediate", "1 week", ["anti money laundering", "regulatory compliance", "kyc"], "Document red flags, verification steps, and escalation workflow for AML review.", ["Checklist PDF", "scenario examples"], "Shows compliance awareness."),
    _action("fin_model", "Build a 3-Statement Financial Model", "Banking & Finance", "Portfolio Project", "Advanced", "2-3 weeks", ["financial modeling", "excel", "financial analysis"], "Link income statement, balance sheet, and cash flow with assumptions tab.", ["Excel model", "assumptions doc"], "High-value finance portfolio artifact."),
    _action("fin_onboard", "Prepare a Customer Onboarding Process Summary", "Banking & Finance", "Case Study", "Beginner", "3-5 days", ["customer onboarding", "banking operations", "communication"], "Map onboarding steps, required documents, and service standards.", ["Process flow", "SOP document"], "Useful for bank officer applications."),
    _action("biz_hr", "Build a Recruitment Tracker in Excel", "Business & Administration", "Tool Practice", "Beginner", "3-5 days", ["hr operations", "excel", "recruitment support"], "Track candidates, interview stages, and hiring status with simple dashboards.", ["Excel tracker", "user guide"], "Demonstrates HR operations skills."),
    _action("biz_ba", "Prepare a Process Improvement Case Study", "Business & Administration", "Case Study", "Intermediate", "1-2 weeks", ["business analysis", "process improvement", "communication"], "Identify bottlenecks, propose improvements, and estimate impact.", ["Case study report", "process map"], "Strong business analyst portfolio piece."),
    _action("biz_admin", "Create an Office Operations SOP Pack", "Business & Administration", "Resume Improvement", "Beginner", "1 week", ["office administration", "organization", "documentation"], "Document daily office routines, filing, scheduling, and vendor coordination.", ["SOP pack", "checklists"], "Shows operational readiness."),
    _action("mkt_seo", "Perform an SEO Audit Case Study", "Marketing & Sales", "Case Study", "Intermediate", "1-2 weeks", ["seo", "google analytics", "content marketing"], "Audit a sample website and propose prioritized SEO improvements.", ["Audit report", "action plan"], "Demonstrates digital marketing analysis."),
    _action("mkt_campaign", "Run a Mock Digital Campaign", "Marketing & Sales", "Portfolio Project", "Beginner", "1-2 weeks", ["social media marketing", "content marketing", "canva"], "Plan, create assets, and report on a hypothetical campaign with metrics framework.", ["Campaign plan", "creative assets", "report"], "Shows campaign execution skills."),
    _action("mkt_sales", "Create a Sales Pitch Deck", "Marketing & Sales", "Portfolio Project", "Beginner", "1 week", ["sales pipeline", "presentation skills", "communication"], "Design a persuasive pitch deck for a product with objection handling notes.", ["Pitch deck", "talk track"], "Directly useful for sales interviews."),
    _action("mkt_crm", "Build a CRM Pipeline Case Study", "Marketing & Sales", "Case Study", "Intermediate", "1 week", ["crm", "lead generation", "sales pipeline"], "Simulate lead stages, conversion rates, and follow-up strategy in a CRM-style sheet.", ["Pipeline model", "strategy notes"], "Shows sales operations understanding."),
    _action("mkt_content", "Build a 30-Day Content Calendar", "Marketing & Sales", "Portfolio Project", "Beginner", "1 week", ["content marketing", "social media marketing", "copywriting"], "Plan themed posts, captions, and channel mix for a brand.", ["Content calendar", "sample posts"], "Practical content marketing artifact."),
    _action("des_ui", "Create a Mobile App UI Case Study", "Design & Creative", "Portfolio Project", "Intermediate", "2-3 weeks", ["figma", "ui design", "ux design", "prototyping"], "Design user flows, wireframes, and high-fidelity screens with rationale.", ["Figma file", "case study PDF"], "Core UX/UI portfolio deliverable."),
    _action("des_brand", "Build a Brand Identity Mock Project", "Design & Creative", "Portfolio Project", "Intermediate", "2 weeks", ["brand identity", "visual design", "adobe illustrator"], "Create logo, color palette, typography, and sample brand applications.", ["Brand guide", "mockups"], "Shows branding capability."),
    _action("des_landing", "Redesign a Landing Page in Figma", "Design & Creative", "Portfolio Project", "Beginner", "1 week", ["figma", "web design", "wireframing"], "Improve layout, hierarchy, and CTA clarity for an existing page concept.", ["Before/after screens", "design notes"], "Quick, high-impact design portfolio piece."),
    _action("des_motion", "Create a 30-Second Motion Reel", "Design & Creative", "Portfolio Project", "Advanced", "2-3 weeks", ["after effects", "visual design", "storyboarding"], "Produce a short animated reel showcasing transitions and brand motion.", ["Video reel", "project breakdown"], "Differentiates motion design candidates."),
    _action("edu_lesson", "Create a Lesson Plan Portfolio", "Education & Teaching", "Portfolio Project", "Beginner", "1-2 weeks", ["lesson planning", "assessment design", "communication"], "Prepare structured lesson plans with objectives, activities, and assessments.", ["Lesson plan pack", "rubric samples"], "Essential for teaching applications."),
    _action("edu_demo", "Record a 5-Minute Teaching Demo", "Education & Teaching", "Interview Preparation", "Beginner", "3-5 days", ["communication", "classroom management", "subject knowledge"], "Record a concise lesson segment demonstrating clarity and engagement.", ["Video demo", "lesson script"], "Strong interview differentiator for teachers."),
    _action("edu_assess", "Build a Student Assessment Sheet Pack", "Education & Teaching", "Tool Practice", "Beginner", "1 week", ["assessment design", "curriculum design", "subject knowledge"], "Create formative and summative assessments aligned to learning outcomes.", ["Assessment pack", "marking guide"], "Shows assessment design skill."),
    _action("edu_online", "Record a Mini Online Course Module", "Education & Teaching", "Portfolio Project", "Intermediate", "2 weeks", ["online teaching tools", "lesson planning", "presentation tools"], "Produce one module with slides, quiz, and learner outcomes.", ["Video module", "quiz", "outline"], "Useful for online instructor roles."),
    _action("health_care", "Prepare a Patient Care Case Study", "Healthcare", "Case Study", "Intermediate", "1 week", ["patient care", "clinical documentation", "communication"], "Document a hypothetical patient scenario with care plan and handover notes.", ["Case study", "care plan template"], "Demonstrates clinical thinking."),
    _action("health_compliance", "Build a Clinic Operations Checklist", "Healthcare", "Domain Knowledge", "Beginner", "3-5 days", ["healthcare compliance", "infection control", "patient safety"], "Create daily compliance and safety checklist for a clinic setting.", ["Checklist PDF", "SOP notes"], "Shows operational healthcare awareness."),
    _action("health_lab", "Create a Lab SOP Sample", "Healthcare", "Tool Practice", "Intermediate", "1 week", ["lab procedures", "quality control", "documentation"], "Write standard operating procedure for sample collection and reporting.", ["SOP document", "quality log template"], "Relevant for lab technician roles."),
    _action("health_campaign", "Design a Community Health Campaign", "Healthcare", "Portfolio Project", "Intermediate", "2 weeks", ["public health basics", "health education", "communication"], "Plan awareness campaign with target audience, channels, and metrics.", ["Campaign plan", "awareness materials"], "Shows public health program skills."),
    _action("eng_civil", "Prepare a Structural Design Case Study", "Engineering", "Case Study", "Advanced", "2-3 weeks", ["structural analysis", "autocad", "project estimation"], "Analyze loads, propose design approach, and estimate materials.", ["Design report", "CAD sketches"], "Engineering portfolio depth."),
    _action("eng_electrical", "Document an Electrical Maintenance Plan", "Engineering", "Case Study", "Intermediate", "1-2 weeks", ["electrical systems", "maintenance planning", "safety standards"], "Create preventive maintenance schedule and inspection checklist.", ["Maintenance plan", "checklist"], "Practical electrical engineering artifact."),
    _action("eng_quality", "Prepare a Quality Audit Case Study", "Engineering", "Case Study", "Intermediate", "1-2 weeks", ["quality control", "iso standards", "process improvement"], "Conduct mock audit, identify defects, and propose corrective actions.", ["Audit report", "CAPA plan"], "Strong for quality engineer roles."),
    _action("eng_site", "Create a Daily Site Report Template", "Engineering", "Tool Practice", "Beginner", "3-5 days", ["site supervision", "construction management", "documentation"], "Design template for progress, manpower, materials, and safety observations.", ["Report template", "sample entries"], "Useful for site engineer roles."),
    _action("cs_templates", "Create a Support Response Template Pack", "Customer Support", "Tool Practice", "Beginner", "3-5 days", ["customer service", "communication", "email support"], "Write templates for common inquiries, escalations, and follow-ups.", ["Template pack", "tone guide"], "Directly applicable in support interviews."),
    _action("cs_scenarios", "Practice Complaint Resolution Scenarios", "Customer Support", "Interview Preparation", "Beginner", "1 week", ["complaint handling", "conflict resolution", "empathy"], "Role-play difficult customer cases and document resolution steps.", ["Scenario scripts", "resolution notes"], "Builds confidence for support interviews."),
    _action("cs_kb", "Build a Knowledge Base Article Sample", "Customer Support", "Portfolio Project", "Beginner", "1 week", ["knowledge base management", "technical documentation", "troubleshooting"], "Write clear help articles with steps, screenshots, and FAQs.", ["KB articles", "style guide"], "Shows documentation and support skills."),
    _action("cs_technical", "Build a Troubleshooting Guide", "Customer Support", "Portfolio Project", "Intermediate", "1-2 weeks", ["troubleshooting", "technical documentation", "product knowledge"], "Create tiered troubleshooting flow for common product issues.", ["Troubleshooting guide", "escalation matrix"], "Strong for technical support roles."),
    _action("ops_project", "Build a Full Project Plan Case Study", "Operations & Project Management", "Case Study", "Intermediate", "2 weeks", ["project planning", "risk register", "stakeholder reporting"], "Define scope, timeline, resources, risks, and communication plan.", ["Project plan", "Gantt chart", "risk log"], "Core PM portfolio deliverable."),
    _action("ops_kpi", "Build a KPI Dashboard in Excel", "Operations & Project Management", "Tool Practice", "Beginner", "1 week", ["kpi tracking", "excel", "operations management"], "Track operational KPIs with trends, targets, and exception flags.", ["Excel dashboard", "metric definitions"], "Practical operations artifact."),
    _action("ops_supply", "Create an Inventory Tracking Model", "Operations & Project Management", "Tool Practice", "Intermediate", "1-2 weeks", ["inventory tracking", "supply chain basics", "excel"], "Model stock levels, reorder points, and supplier lead times.", ["Tracking model", "process notes"], "Shows supply chain fundamentals."),
    _action("ops_process", "Map an End-to-End Operations Workflow", "Operations & Project Management", "Case Study", "Beginner", "1 week", ["process mapping", "operations management", "continuous improvement"], "Document current-state process and identify improvement opportunities.", ["Process map", "improvement plan"], "Demonstrates operational analysis."),
    _action("ops_risk", "Create a Project Risk Register Sample", "Operations & Project Management", "Tool Practice", "Intermediate", "1 week", ["risk register", "project planning", "stakeholder reporting"], "Identify risks, likelihood, impact, owners, and mitigation actions.", ["Risk register", "mitigation plan"], "Essential PM skill demonstration."),
    _action("entry_office", "Create an Office Filing System Guide", "General Entry-Level Jobs", "Resume Improvement", "Beginner", "3-5 days", ["office support", "organization", "filing systems"], "Document filing conventions, naming rules, and retrieval process.", ["Filing guide", "folder structure"], "Shows administrative readiness."),
    _action("entry_retail", "Practice Customer Service Scenarios", "General Entry-Level Jobs", "Interview Preparation", "Beginner", "3-5 days", ["customer service", "communication", "retail operations"], "Prepare responses for common retail customer situations.", ["Scenario Q&A", "service standards"], "Interview prep for retail roles."),
    _action("entry_data", "Complete a Data Cleaning Practice Task", "General Entry-Level Jobs", "Practice Task", "Beginner", "1 week", ["data entry", "excel", "attention to detail"], "Clean a messy dataset, fix errors, and produce validation summary.", ["Clean dataset", "validation report"], "Demonstrates accuracy and computer skills."),
    _action("entry_reception", "Prepare a Front Desk SOP", "General Entry-Level Jobs", "Domain Knowledge", "Beginner", "3-5 days", ["front desk management", "communication", "scheduling"], "Document visitor handling, call routing, and appointment management.", ["Front desk SOP", "call script"], "Useful for receptionist roles."),
    _action("entry_report", "Prepare a Weekly Report Template", "General Entry-Level Jobs", "Tool Practice", "Beginner", "3-5 days", ["report writing", "microsoft office", "organization"], "Create a simple weekly status report format with sections and examples.", ["Report template", "sample report"], "Shows professional communication."),
    _action("soft_comm", "Improve Professional Communication Skills", "Business & Administration", "Soft Skill Development", "Beginner", "2 weeks", ["communication", "presentation skills", "professionalism"], "Practice email writing, meeting updates, and concise verbal summaries.", ["Email samples", "presentation outline"], "Cross-functional career skill."),
    _action("soft_negotiation", "Practice Negotiation Scenarios", "Marketing & Sales", "Soft Skill Development", "Intermediate", "1-2 weeks", ["negotiation", "persuasion", "communication"], "Work through salary, vendor, and client negotiation role-play scenarios.", ["Scenario notes", "strategy checklist"], "Useful for sales and business roles."),
    _action("cert_excel", "Complete an Excel Certification Prep Plan", "Banking & Finance", "Certification", "Beginner", "3-4 weeks", ["excel", "financial reporting", "data analysis"], "Follow structured study plan for Excel proficiency certification.", ["Study plan", "practice exercises"], "Adds credible finance/admin skill proof."),
    _action("cert_cloud", "Complete a Cloud Fundamentals Study Plan", "Software & IT", "Certification", "Beginner", "4-6 weeks", ["aws", "cloud basics", "security basics"], "Study core cloud concepts with hands-on labs and summary notes.", ["Study notes", "lab screenshots"], "Entry path for cloud/DevOps careers."),
    _action("cert_analytics", "Complete a Google Analytics Practice Track", "Marketing & Sales", "Certification", "Beginner", "2-3 weeks", ["google analytics", "seo", "conversion optimization"], "Practice analytics setup, reporting, and campaign measurement exercises.", ["Analytics report samples", "study log"], "Digital marketing credential pathway."),
    _action("resume_tailor", "Tailor Your Resume for a Target Role", "General Entry-Level Jobs", "Resume Improvement", "Beginner", "3-5 days", ["communication", "organization", "report writing"], "Rewrite resume bullets to match target role skills and outputs.", ["Tailored resume", "bullet mapping sheet"], "Immediate job-search impact."),
    _action("interview_star", "Prepare STAR Method Interview Answers", "General Entry-Level Jobs", "Interview Preparation", "Beginner", "1 week", ["communication", "problem solving", "professionalism"], "Draft structured answers for behavioral interview questions.", ["STAR answer bank", "practice recordings"], "Cross-role interview preparation."),
    _action("domain_banking", "Study Core Banking Products Overview", "Banking & Finance", "Domain Knowledge", "Beginner", "1-2 weeks", ["financial products", "banking operations", "customer onboarding"], "Summarize savings, loans, cards, and onboarding requirements.", ["Product comparison notes", "quiz sheet"], "Foundation for banking interviews."),
    _action("domain_health", "Study Medical Terminology Basics", "Healthcare", "Domain Knowledge", "Beginner", "2 weeks", ["medical terminology", "patient care", "clinical documentation"], "Learn common prefixes, suffixes, and clinical terms with flashcards.", ["Flashcard deck", "glossary"], "Entry healthcare knowledge boost."),
    _action("domain_edtech", "Explore Educational Technology Tools", "Education & Teaching", "Domain Knowledge", "Beginner", "1-2 weeks", ["educational technology", "lms", "online teaching tools"], "Compare LMS platforms and document classroom integration ideas.", ["Tool comparison", "integration plan"], "Modern teaching readiness."),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    for category, filename in CATEGORY_FILES.items():
        path = OUT / filename
        with path.open("w", encoding="utf-8") as fh:
            json.dump(TAXONOMIES[category], fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    with (OUT / "role_profiles.json").open("w", encoding="utf-8") as fh:
        json.dump(ROLE_PROFILES, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    with (OUT / "career_action_templates.json").open("w", encoding="utf-8") as fh:
        json.dump(CAREER_ACTIONS, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    role_count = sum(len(roles) for roles in ROLE_PROFILES.values())
    print(f"Generated {len(CATEGORY_FILES)} taxonomy files")
    print(f"Generated role_profiles.json with {role_count} roles")
    print(f"Generated career_action_templates.json with {len(CAREER_ACTIONS)} actions")


if __name__ == "__main__":
    main()
