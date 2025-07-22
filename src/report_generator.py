from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from matplotlib import pyplot as plt
import tempfile
import os
import ollama


def run_local_llm(prompt: str) -> str:
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']


def generate_report(sections, output_path, extra_notes=None):
    doc = Document()

    # Title Page
    doc.add_heading("EB-1A Petition Risk Analysis Report", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Generated via VisaCompanion Prototype\n", style='Intense Quote').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # TOC
    doc.add_paragraph("Table of Contents", style='Heading 1')
    doc.add_paragraph("To update links in Word: Right-click and select 'Update Field'.")
    doc.add_page_break()

    # Executive Summary
    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph("This report analyzes the submitted EB-1A petition against recognized criteria. Each section includes a simulated USCIS-style evaluation and suggested improvements. A visual timeline and LLM-generated final assessment are provided.")
    doc.add_page_break()

    # Section-by-Section Feedback
    risk_scores = {}
    for entry in sections:
        doc.add_heading(entry['criteria'], level=2)
        doc.add_paragraph(entry['excerpt'], style='Quote')
        doc.add_paragraph(f"Risk Level: {entry['risk']}", style='Intense Quote')
        doc.add_paragraph("Reviewer Comments:\n" + entry['reviewer_voice'])
        doc.add_paragraph("Suggested Language:\n" + entry['suggested_language'])
        if entry['buzzwords']:
            doc.add_paragraph("Flagged Buzzwords: " + ", ".join(entry['buzzwords']))
        risk_scores[entry['criteria']] = entry['risk']
        doc.add_page_break()

    # Risk Timeline Chart
    doc.add_heading("Risk Timeline Chart", level=1)
    chart_path = _plot_risk_chart(risk_scores)
    doc.add_picture(chart_path, width=Inches(6))
    os.remove(chart_path)
    doc.add_page_break()

    # Final LLM Risk Assessment
    doc.add_heading("Final Reviewer Summary", level=1)
    final_prompt = _build_final_prompt(sections, extra_notes)
    final_summary = run_local_llm(final_prompt)
    doc.add_paragraph(final_summary.strip())
    doc.add_page_break()

    # Save DOCX
    doc.save(output_path)

def _plot_risk_chart(risk_dict):
    levels = {"Low": 1, "Medium": 2, "High": 3}
    items = list(risk_dict.items())
    labels = [i[0] for i in items]
    values = [levels.get(i[1], 0) for i in items]

    plt.figure(figsize=(10, 4))
    plt.barh(labels, values)
    plt.title("Section Risk Levels")
    plt.xlabel("Risk Level")
    plt.yticks(fontsize=8)
    tmpfile = tempfile.mktemp(suffix=".png")
    plt.tight_layout()
    plt.savefig(tmpfile)
    plt.close()
    return tmpfile

def _build_final_prompt(section_data, notes):
    bullets = "\n".join([
        f"- {item['criteria']}: {item['risk']}" for item in section_data
    ])
    note_summary = ""
    if notes:
        if notes.get("similar_letters"):
            note_summary += f"\n\n{len(notes['similar_letters'])} recommendation letters appear very similar."
        if notes.get("conflicting_fields"):
            note_summary += f"\n\nMultiple fields of expertise were found: {', '.join(notes['conflicting_fields'])}"

    return f"""
You are a USCIS adjudicator reviewing an EB-1A petition.

Summarize the overall strengths and weaknesses of the case based on the following risk scores and red flags.

Risk Summary:
{bullets}

Other notes:
{note_summary}

Write a concluding memo-style paragraph that reflects whether the petition is strong overall, borderline, or likely to trigger RFE. Use neutral and factual tone.
"""
