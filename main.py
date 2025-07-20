import os
from src.parser import extract_text_from_docx, segment_by_criteria, classify_criteria
from src.report_generator import generate_report
from src.risk_detector import analyze_section_with_deepseek as analyze_section

def main():
    input_path = "sample_data/sample_petition.docx"
    output_path = "outputs/rfe_risk_report.docx"

    # Check for input file
    if not os.path.exists(input_path):
        print(f"❌ ERROR: Petition file not found at {input_path}")
        return

    print("📄 Reading petition document...")
    raw_text = extract_text_from_docx(input_path)

    print("📚 Segmenting petition by EB-1A criteria...")
    sections = segment_by_criteria(raw_text)

    analyzed_data = []

    print("🤖 Analyzing each section with DeepSeek LLM...")
    for section_name, content in sections.items():
        if not content.strip():
            continue  # skip empty sections

        criteria = classify_criteria(section_name)
        print(f"  ➤ Evaluating: {criteria} ({section_name})")

        try:
            llm_feedback = analyze_section(content, criteria)
        except Exception as e:
            llm_feedback = f"[Error from DeepSeek model: {e}]"

        analyzed_data.append({
            "section": section_name,
            "criteria": criteria,
            "excerpt": content[:300] + "..." if len(content) > 300 else content,
            "llm_feedback": llm_feedback
        })

    print("📝 Generating final DOCX report...")
    generate_report(analyzed_data, output_path=output_path)
    print(f"✅ Done! Report saved to: {output_path}")

if __name__ == "__main__":
    main()