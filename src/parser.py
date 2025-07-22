import os
import re
from docx import Document
from PyPDF2 import PdfReader

# === TEXT EXTRACTION ===

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


# === SEMANTIC SEGMENTATION ===

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
        r"summary of .*?achievements|biography|background": "background",
        r"evidence of original.*?contribution|scientific contribution|created .*? model": "original_contributions",
        r"authorship of scholarly articles|published.*?(journal|conference)": "authorship",
        r"judg(e|ing) the work|review(ed|er) for|peer review": "judging",
        r"critical role|leading role|president of|organized|led the": "critical_role",
        r"media coverage|featured in|press|interviewed by": "media_coverage",
        r"final merits|extraordinary ability|risen to the very top": "final_merits",
        r"statement .*?plans|intend.*?continue|future research|permanent residence": "statement_of_intent",
        r"recommendation letter|supporting letter|reference letter|professor .*?states": "recommendation_letters"
    }

    paragraphs = re.split(r"\n{2,}", text)
    current_key = "other"

    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            continue

        matched = False
        for pattern, key in pattern_to_key.items():
            if re.search(pattern, para_clean, re.IGNORECASE):
                current_key = key
                matched = True
                break

        segments[current_key] += para_clean + "\n\n"

    return segments


# === CRITERIA LABEL MAPPER ===

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
