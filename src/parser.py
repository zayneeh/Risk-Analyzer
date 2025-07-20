from docx import Document

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text

def segment_by_criteria(text):
    sections = {
        "background": "",
        "original_contributions": "",
        "judging": "",
        "critical_role": "",
        "media_coverage": "",
        "recommendation_letters": ""
    }
    lines = text.splitlines()
    current_section = "background"
    for line in lines:
        lower = line.lower()
        if "original contribution" in lower:
            current_section = "original_contributions"
        elif "judging" in lower:
            current_section = "judging"
        elif "critical role" in lower:
            current_section = "critical_role"
        elif "media coverage" in lower:
            current_section = "media_coverage"
        elif "recommendation" in lower:
            current_section = "recommendation_letters"
        sections[current_section] += line + "\n"
    return sections

def classify_criteria(section_name):
    mapping = {
        "original_contributions": "Criterion 6: Original Contributions",
        "judging": "Criterion 2: Judging",
        "critical_role": "Criterion 4: Critical Role",
        "media_coverage": "Criterion 7: Media Coverage",
        "recommendation_letters": "Supporting Letters",
        "background": "General Background"
    }
    return mapping.get(section_name, "Unclassified")
