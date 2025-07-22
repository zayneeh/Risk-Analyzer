import os
from src.parser import extract_text, segment_by_criteria, classify_criteria, extract_declared_field
from src.report_generator import generate_report
from src.risk_detector import analyze_section_with_deepseek, check_letter_similarity, detect_field_inconsistencies

def main():
    input_path = "sample_data/main.pdf"
    output_path = "outputs/rfe_risk_report.docx"

    if not os.path.exists(input_path):
        print(f"❌ ERROR: Petition file not found at {input_path}")
        return

    print("📄 Reading petition document...")
    raw_text = extract_text(input_path)

    print("📚 Segmenting petition by EB-1A criteria...")
    sections = segment_by_criteria(raw_text)

    analyzed_data = []
    declared_fields = set()

    print("🤖 Analyzing each section with Mistral LLM...")
    for section_name, content in sections.items():
        if not content.strip():
            continue

        criteria = classify_criteria(section_name)
        print(f"  ➤ Evaluating: {criteria} ({section_name})")

        result = analyze_section_with_deepseek(content, criteria)

        field = extract_declared_field(content)
        if field:
            declared_fields.add(field.lower())

        analyzed_data.append({
            "section": section_name,
            "criteria": criteria,
            "excerpt": content[:300] + "..." if len(content) > 300 else content,
            "llm_feedback": result["llm_feedback"],
            "reviewer_voice": result["reviewer_voice"],
            "buzzwords": result["buzzwords"],
            "suggested_language": result.get("suggested_language", "")
        })

    print("🔁 Checking for duplicated recommendation letters...")
    similar_letters = check_letter_similarity(sections)

    print("⚠️ Checking for field of expertise inconsistencies...")
    conflicting_fields = detect_field_inconsistencies(sections)

    print("📝 Generating final DOCX report...")
    generate_report(
        analyzed_data,
        output_path=output_path,
        extra_notes={
            "similar_letters": similar_letters,
            "conflicting_fields": [f"{s}: {f}" for s, f in conflicting_fields] if conflicting_fields else []
        }
    )

    print(f"✅ Done! Report saved to: {output_path}")

if __name__ == "__main__":
    main()
