import os
import re
from docx import Document
from PyPDF2 import PdfReader
import ollama


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or '' for page in reader.pages)

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def run_llm_classification(paragraph):
    prompt = f"""
You are helping classify segments of a USCIS EB-1A petition.

Below is a paragraph. Return the most appropriate category for this content from the list:
- background
- original_contributions
- authorship
- judging
- critical_role
- media_coverage
- final_merits
- statement_of_intent
- recommendation_letters
- other

Paragraph:
\"\"\"{paragraph}\"\"\"

Respond only with the category label. Do not include extra explanation.
"""
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response['message']['content'].strip().lower()


def segment_by_criteria(text):
    segments = {
        "background": "",
        "original_contributions": "",
        "authorship": "",
        "judging": "",
        "critical_role": "",
        "media_coverage": "",
        "final_merits": "",
        "statement_of_intent": "",
        "recommendation_letters": "",
        "other": ""
    }

    pattern_to_key = {
        r"summary of .*?achievements|biography|background|education|career overview": "background",
        r"evidence of original.*?contribution|scientific contribution|developed.*?framework|novel work|patent": "original_contributions",
        r"authorship of scholarly articles|published.*?(journal|conference|paper)|citations": "authorship",
        r"judg(e|ing) the work|peer review|review(ed|er) for": "judging",
        r"critical role|leading role|executive|director|organized|led the": "critical_role",
        r"media coverage|featured in|press|interviewed by|news outlet": "media_coverage",
        r"final merits|extraordinary ability|risen to the very top|kazarian": "final_merits",
        r"statement .*?plans|intend.*?continue|future research|benefit.*?united states|contribute.*?US": "statement_of_intent",
        r"recommendation letter|supporting letter|reference letter|this letter.*?recommend": "recommendation_letters"
    }

    paragraphs = re.split(r"\n{2,}", text)
    for idx, para in enumerate(paragraphs):
        para_clean = para.strip()
        if not para_clean:
            continue

        matched = False
        for pattern, key in pattern_to_key.items():
            if re.search(pattern, para_clean, re.IGNORECASE):
                segments[key] += para_clean + "\n\n"
                matched = True
                break

        if not matched:
            try:
                predicted_key = run_llm_classification(para_clean)
                if predicted_key not in segments:
                    predicted_key = "other"
                segments[predicted_key] += para_clean + "\n\n"
                print(f"🤖 LLM classified paragraph #{idx+1} as: {predicted_key}")
            except Exception as e:
                print(f"❌ LLM failed on paragraph #{idx+1}: {e}")
                segments["other"] += para_clean + "\n\n"

    return segments


def classify_criteria(section_name):
    mapping = {
        "original_contributions": "Criterion 6: Original Contributions",
        "authorship": "Criterion 1: Scholarly Articles",
        "judging": "Criterion 2: Judging",
        "critical_role": "Criterion 4: Critical Role",
        "media_coverage": "Criterion 7: Media Coverage",
        "recommendation_letters": "Supporting Letters",
        "final_merits": "Final Merits (Kazarian Step Two)",
        "statement_of_intent": "Intent & Benefit to U.S.",
        "background": "General Background",
        "other": "Unclassified"
    }
    return mapping.get(section_name, "Unclassified")


def extract_declared_field(text):
    patterns = [
        r"(?:expert|specialist|leader|authority)\s+(?:in|on|within)\s+(?:the field of\s+)?([A-Za-z\s\-&]+)",
        r"(?:field of study|area of expertise)\s+(?:is|includes)?\s*([A-Za-z\s\-&]+)",
        r"(?:research|focus|discipline)\s+(?:is|in)\s+([A-Za-z\s\-&]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None
