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
    raise ValueError(f"Unsupported file type: {ext}")

def extract_text_from_pdf(file_path):
    return "\n".join(page.extract_text() or '' for page in PdfReader(file_path).pages)

def extract_text_from_docx(file_path):
    return "\n".join(para.text for para in Document(file_path).paragraphs)

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def run_local_llm(prompt: str) -> str:
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

def classify_paragraph(paragraph: str) -> str:
    prompt = f"""
Classify this paragraph into one of the following EB-1A categories:
- Background
- Original Contributions
- Authorship
- Judging
- Critical Role
- Media Coverage
- Final Merits
- Statement of Intent
- Recommendation Letter
- Other

Return ONLY the category name.

Paragraph:
\"\"\"
{paragraph}
\"\"\"
"""
    response = run_local_llm(prompt)
    return response.strip().lower()

def segment_by_criteria(text):
    print("🧠 Segmenting paragraphs using LLM classification...")
    categories = {
        "background": "",
        "original contributions": "",
        "authorship": "",
        "judging": "",
        "critical role": "",
        "media coverage": "",
        "final merits": "",
        "statement of intent": "",
        "recommendation letter": "",
        "other": ""
    }
    for para in re.split(r"\n{2,}", text):
        if not para.strip():
            continue
        try:
            category = classify_paragraph(para)
            key = category.lower()
            if key not in categories:
                key = "other"
            categories[key] += para.strip() + "\n\n"
        except Exception as e:
            print(f"❌ Failed to classify paragraph: {e}")
            categories["other"] += para.strip() + "\n\n"
    return categories

def classify_criteria(section_name):
    map = {
        "original contributions": "Criterion 6: Original Contributions",
        "authorship": "Criterion 1: Scholarly Articles",
        "judging": "Criterion 2: Judging",
        "critical role": "Criterion 4: Critical Role",
        "media coverage": "Criterion 7: Media Coverage",
        "recommendation letter": "Supporting Letters",
        "final merits": "Kazarian Step Two",
        "statement of intent": "Intent and U.S. Benefit",
        "background": "General Background",
        "other": "Unclassified"
    }
    return map.get(section_name.lower(), "Unclassified")

def extract_declared_field(text):
    match = re.search(r"(?:field of (?:study|expertise|research)\s*[:\-]?\s*)([A-Za-z &\-]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None
