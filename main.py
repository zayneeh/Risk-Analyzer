import os
from src.parser import extract_text_from_docx, segment_by_criteria, classify_criteria
from src.report_generator import generate_report
from src.risk_detector import analyze_section_with_llama as analyze_section
def main():
    # Load OpenAI API key from environment variable
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ ERROR: OPENAI_API_KEY not set. Please set it as an environment variable.")
        return

    # Load petition
    input_path = "sample_data/sample_petition.docx"
    if not os.path.exists(input_path):
        print(f"❌ ERROR: Petition file not found at {input_path}")
        return

    print("📄 Reading petition document...")
    raw_text = extract_text_from_docx(input_path)

    print("📚 Segmenting petition by EB-1A criteria...")
    sections = segment_by_criteria(raw_text)

    analyzed_data = []

    print("🔍 Analyzing sections for risk and compliance...")
    for section_name, content in sections.items():
        if not content.strip():
            continue  # Skip empty sections

        criteria = classify_criteria(section_name)
        llm_feedback = analyze_section(content, criteria)


        analyzed_data.append({
            "section": section_name,
            "criteria": criteria,
            "excerpt": content[:300] + "..." if len(content) > 300 else content,
            "llm_feedback": llm_feedback
        })

    print("📝 Generating final risk report...")
    generate_report(analyzed_data, output_path="outputs/rfe_risk_report.docx")
    print("✅ Done! Report saved to outputs/rfe_risk_report.docx")

if __name__ == "__main__":
    main()
