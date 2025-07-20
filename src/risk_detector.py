# src/mistral_decision.py

import ollama

CRITERIA_DESCRIPTIONS = {
    "Criterion 4: Critical Role": "Evidence of a leading or critical role in distinguished organizations.",
    "Criterion 6: Original Contributions": "Evidence of original contributions of major significance.",
    "Criterion 2: Judging": "Participation as a judge of the work of others.",
    "Criterion 7: Media Coverage": "Evidence of published media coverage about the individual.",
    "Supporting Letters": "Recommendation letters supporting eligibility for EB-1A.",
    "General Background": "General background or personal bio."
}

def analyze_section_with_llama(section_text, criterion_label):
    criterion_description = CRITERIA_DESCRIPTIONS.get(criterion_label, "General background evidence.")

    prompt = f"""
You are simulating a USCIS adjudicator reviewing an EB-1A petition.

Criterion:
{criterion_label}

Definition:
{criterion_description}

Petition Excerpt:
\"\"\"
{section_text}
\"\"\"

Instructions:
- Does this meet the criterion?
- What's missing?
- Suggest improvements.

Reply in bullet points.
"""

    response = ollama.chat(model="llama3", messages=[
        {"role": "user", "content": prompt}
    ])
    return response["message"]["content"]
