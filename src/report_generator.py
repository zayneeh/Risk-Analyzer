from docx import Document

def generate_report(analyzed_sections, output_path="outputs/rfe_risk_report.docx"):
    doc = Document()

    # Title
    doc.add_heading("EB-1A RFE Risk Analysis Report", 0)

    # Executive Summary
    doc.add_heading("Executive Summary", level=1)
    for entry in analyzed_sections:
        doc.add_paragraph(
            f"{entry['criteria']} ({entry['section'].replace('_', ' ').title()}): Reviewed by AI"
        )

    # Section-by-section analysis
    for entry in analyzed_sections:
        doc.add_page_break()
        doc.add_heading(entry['criteria'], level=2)
        doc.add_paragraph(f"Section: {entry['section'].replace('_', ' ').title()}")

        # Excerpt
        doc.add_heading("Petition Excerpt", level=3)
        doc.add_paragraph(entry['excerpt'], style="Intense Quote")

        # AI Feedback
        doc.add_heading("AI Legal Assessment", level=3)
        doc.add_paragraph(entry.get("llm_feedback", "No AI feedback provided."))

    # Save report
    doc.save(output_path)
