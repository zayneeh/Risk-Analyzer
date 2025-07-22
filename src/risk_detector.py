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
2. Identify vague, generic, or overused phrases (e.g., “renowned expert”, “leading figure”) and list them under "Buzzwords".
3. Determine if claims are independently verifiable.
4. Recommend improvements or additional evidence.
5. Provide improved draft language for the petition (1–2 paragraphs) under "Suggested Language".

Return in the following format:

Risk Analysis:
- [bullet point 1]
...

Buzzwords: ["word1", "word2", ...]

Reviewer Voice:
[Memo summary]

Suggested Language:
[Improved paragraph]
"""

    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        llm_output = response["message"]["content"]
    except Exception as e:
        return {
            "llm_feedback": f"⚠️ Mistral error during risk analysis: {e}",
            "reviewer_voice": "",
            "buzzwords": [],
            "suggested_language": ""
        }

    feedback, buzzwords, reviewer_voice, suggestion = parse_llm_risk_output(llm_output)
    return {
        "llm_feedback": feedback,
        "reviewer_voice": reviewer_voice,
        "buzzwords": buzzwords,
        "suggested_language": suggestion
    }

def parse_llm_risk_output(text):
    risk_lines = []
    buzzwords = []
    reviewer_voice = ""
    suggested_text = ""
    in_risk = in_review = in_suggest = False

    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("risk analysis:"):
            in_risk, in_review, in_suggest = True, False, False
            continue
        elif line.lower().startswith("buzzwords:"):
            in_risk = in_review = in_suggest = False
            buzzwords_line = line.partition(":")[2].strip()
            try:
                buzzwords = eval(buzzwords_line)
            except:
                buzzwords = re.findall(r'"(.*?)"', buzzwords_line)
            continue
        elif line.lower().startswith("reviewer voice:"):
            in_risk, in_review, in_suggest = False, True, False
            continue
        elif line.lower().startswith("suggested language:"):
            in_risk, in_review, in_suggest = False, False, True
            continue

        if in_risk and line.startswith("-"):
            risk_lines.append(line)
        elif in_review:
            reviewer_voice += line + " "
        elif in_suggest:
            suggested_text += line + " "

    return "\n".join(risk_lines).strip(), buzzwords, reviewer_voice.strip(), suggested_text.strip()

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

def detect_field_inconsistencies(all_texts):
    declared_fields = []
    pattern = r"(?:field of study|area of expertise|discipline|specialist in)\s+(?:is|includes|in)?\s*([A-Za-z\s\-&]+)"
    for section, text in all_texts.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            declared_fields.append((section, match.group(1).strip()))

    if len(set(field for _, field in declared_fields)) > 1:
        return declared_fields
    return []
