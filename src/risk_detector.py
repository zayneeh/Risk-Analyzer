import json, ollama
from pathlib import Path

CRITERIA_DESCRIPTIONS = {
    "Criterion 2: Judging": "Participation as a judge of the work of others in the same or related field.",
    "Criterion 4: Critical Role": "Evidence of a leading or critical role in distinguished organizations.",
    "Criterion 6: Original Contributions": "Evidence of original contributions of major significance.",
    "Criterion 7: Media Coverage": "Evidence of published material in major media about the individual.",
    "Supporting Letters": "Recommendation letters supporting eligibility.",
    "General Background": "General background and personal bio information."
}

# Paths to scraped JSON data
USCIS_PATH = Path("knowledge_base/processed/uscis_policy.json")
AAO_PATH = Path("knowledge_base/processed/aao_decisions.json")
REDDIT_PATH = Path("knowledge_base/processed/reddit_eb1a_posts.json")

def load_json(path):
    return json.load(open(path, encoding="utf-8")) if path.exists() else {}

uscis_data = load_json(USCIS_PATH)
aao_data = load_json(AAO_PATH)
reddit_data = load_json(REDDIT_PATH)

# Build context for LLM input
def get_context_for(criterion):
    usc_guidance = uscis_data.get(criterion, "")
    
    aao_snips = [entry["text_snippet"] for entry in aao_data if criterion.lower().split(":")[1].strip().lower() in entry["text_snippet"].lower()]
    reddit_snips = [post["text"] for post in reddit_data if criterion.lower().split(":")[1].strip().lower() in post["text"].lower()]
    
    aao_block = "\n- " + "\n- ".join(aao_snips[:3]) if aao_snips else "No matching AAO decisions found."
    reddit_block = "\n- " + "\n- ".join(reddit_snips[:3]) if reddit_snips else "No Reddit examples found."

    return f"""
📘 USCIS Guidance:
{usc_guidance}

📑 AAO Denial Samples:
{aao_block}

💬 Reddit Forum Reports:
{reddit_block}
"""

def analyze_section_with_deepseek(section_text, criterion_label):
    context = get_context_for(criterion_label)
    criterion_def = CRITERIA_DESCRIPTIONS.get(criterion_label, "General supporting evidence.")

    prompt = f"""
You are simulating a USCIS EB-1A petition adjudicator.

📘 Criterion:
{criterion_label}

📖 Definition:
{criterion_def}

📄 Petition Excerpt:
\"\"\"
{section_text}
\"\"\"

📚 Reference Materials:
{context}

🧠 Instructions:
- Does the excerpt meet the criterion?
- What’s weak or missing?
- Suggest improvements or stronger evidence.

Respond in bullet points.
"""

    response = ollama.chat(model="deepseek-llm:7b", messages=[
        {"role": "user", "content": prompt}
    ])
    return response["message"]["content"]
