import ollama
import re
from difflib import SequenceMatcher

CRITERIA_DESCRIPTIONS = {
    "Criterion 2: Judging": "Participation as a judge of the work of others in the same or related field.",
    "Criterion 4: Critical Role": "Evidence of a leading or critical role in distinguished organizations.",
    "Criterion 6: Original Contributions": "Evidence of original contributions of major significance.",
    "Criterion 7: Media Coverage": "Evidence of published material in major media about the individual.",
    "Criterion 1: Scholarly Articles": "Authorship of scholarly articles in professional or major trade publications.",
    "Supporting Letters": "Recommendation letters supporting eligibility.",
    "Final Merits (Kazarian Step Two)": "Overall merits-based analysis of extraordinary ability.",
    "Intent & Benefit to U.S.": "Statement of intent and expected future benefit to the United States.",
    "General Background": "General background and personal bio information.",
    "Unclassified": "Unclassified evidence not directly tied to USCIS criteria."
}


def analyze_section_with_deepseek(section_text, criterion_label):
    print(f"🧠 Prompting Mistral for: {criterion_label}")
    criterion_description = CRITERIA_DESCRIPTIONS.get(criterion_label, "General supporting evidence.")

    section_text = section_text[:4000]

    prompt = f"""
You are simulating a USCIS EB-1A petition adjudicator.

📘 Criterion:
{criterion_label}

📖 Definition:
{criterion_description}

📄 Petition Excerpt:
\"\"\"{section_text}\"\"\"

Instructions:
1. Does this section meet the criterion? Be specific.
2. List vague, overused, or exaggerated phrases (e.g., “renowned expert”, “cutting-edge”).
3. Are the claims supported by independent third-party evidence (e.g., awards, citations, media)?
4. Recommend concrete improvements.

Return:
- Risk Analysis (in bullet points)
- Buzzwords: ["word1", "word2"]
"""

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        risk_text = response["message"]["content"]
    except Exception as e:
        return {
            "llm_feedback": f"⚠️ Mistral error during risk analysis: {e}",
            "reviewer_voice": "",
            "buzzwords": []
        }

    # Reviewer note
    persona_prompt = f"""
You are a USCIS adjudicator. Based on the following analysis, summarize your concern in 2–3 formal sentences for an internal RFE memo.

\"\"\"{risk_text}\"\"\"
"""
    try:
        persona_response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": persona_prompt}]
        )
        reviewer_voice = persona_response["message"]["content"]
    except Exception as e:
        reviewer_voice = f"(⚠️ Reviewer simulation failed: {e})"

    # Extract buzzwords
    buzzwords = extract_buzzwords_from_text(risk_text)

    return {
        "llm_feedback": risk_text.strip(),
        "reviewer_voice": reviewer_voice.strip(),
        "buzzwords": buzzwords
    }


def extract_buzzwords_from_text(text):
    matches = re.findall(r"[\"']([^\"']{3,40}?)[\"']", text)
    return list(set([m for m in matches if len(m.split()) <= 5]))


def check_letter_similarity(sections, threshold=0.85):
    letters = {k: v for k, v in sections.items() if "recommendation" in k.lower()}
    flagged = []

    names = list(letters.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]
            sim = SequenceMatcher(None, letters[a], letters[b]).ratio()
            if sim >= threshold:
                flagged.append((a, b, round(sim, 2)))
    return flagged