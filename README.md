# Risk-Analyzer


**VisaCompanion** is a local tool that helps legal professionals and EB-1A petitioners identify weaknesses in their immigration petition drafts before submission. It simulates a USCIS adjudicator’s feedback using a lightweight open-source language model — **DeepSeek LLM 7B** — running locally via **Ollama**.

---

## Features

- AI-powered analysis of EB-1A petition content  
- Section-by-section feedback modeled after USCIS RFE criteria  
- Professional `.docx` report generation  
- Runs entirely offline — no internet or API keys required

---

## Folder Structure

```
Risk-Analyzer/
├── main.py                    # Main orchestrator script
├── sample_data/
│   └── sample_petition.docx   # Petition input file (editable by you)
├── outputs/
│   └── rfe_risk_report.docx   # Final Word report with feedback
├── src/
│   ├── parser.py              # Handles file reading and sectioning
│   ├── deepseek_decision.py  # Uses DeepSeek-LLM to analyze each section
│   └── report_generator.py   # Generates and formats the output report
├── requirements.txt           # Python dependencies
└── README.md
```

---

## Requirements

- Python 3.8 or higher  
- Ollama (to run the LLM locally)  
- At least 8 GB of RAM  
- Microsoft Word or Google Docs (to open output files)

---

## Setup Instructions

### 1. Install Ollama

Download the installer from:  
[https://ollama.com/download](https://ollama.com/download)  
Install and restart your terminal (or PowerShell) afterward.

---

### 2. Pull the DeepSeek LLM

In your terminal or PowerShell, run:

```bash
ollama pull deepseek-llm:7b
```

To start the model, open a **new terminal window** and run:

```bash
ollama run deepseek-llm:7b
```

Keep this terminal running. It hosts the LLM in the background while your tool runs.

---

### 3. Install Python Dependencies

In your main project folder, run:

```bash
pip install -r requirements.txt
```

This will install `python-docx`, which is used to read and generate `.docx` files.

---

## How to Use the Tool

### Step 1: Add Your Petition Draft

Save your `.docx` petition draft inside the `sample_data/` folder.  
Make sure the document has clear headings like:

```
Original Contributions  
Judging  
Critical Role  
Media Coverage  
Recommendation Letters
```

### Step 2: Run the Script

In your terminal, from the root of the project, run:

```bash
python main.py
```

### Step 3: Review the Results

After completion, the feedback report will be saved at:

```
outputs/rfe_risk_report.docx
```

Open it in Microsoft Word or Google Docs to view the analysis.

---

## What the Output Includes

Each analyzed section contains:

- The EB-1A criterion name  
- Your original petition content  
- AI-generated insights:
  - Weaknesses in evidence or phrasing
  - Missing elements that may trigger RFE
  - Suggestions to strengthen the section

---

## Why Use DeepSeek LLM?

- Open-source and free to use  
- Runs locally — no internet or API key needed  
- Strong performance for legal-style feedback  
- Compatible with Ollama on Windows, macOS, and Linux

---

## Troubleshooting

| Problem                          | Suggested Fix                                               |
|----------------------------------|-------------------------------------------------------------|
| `ollama not recognized`          | Ensure Ollama is installed and your terminal was restarted |
| Model isn’t responding           | Make sure `ollama run deepseek-llm:7b` is still running     |
| Output file not created          | Ensure the petition isn’t empty and has section headers     |
| Python crashes or lags           | Close unused apps — you may be low on memory (8 GB minimum) |
| Getting coder model responses    | Double-check you're using `deepseek-llm:7b`, not `deepseek-coder` |

---

## Future Plans

- Add support for `.pdf` petitions  
- Allow toggling between multiple LLMs (e.g. DeepSeek vs LLaMA)  
- Add prediction confidence scores  
- Suggest templates for missing sections

---

## Disclaimer

This tool is intended for educational and research use only.  
It does **not** provide legal advice and should not be relied on for official immigration decisions.  
Always consult a licensed immigration attorney before submitting your petition.

---

## Credits

- [DeepSeek LLM](https://huggingface.co/deepseek-ai)  
- [Ollama](https://ollama.com/)  
- [USCIS EB-1A Policy Manual](https://www.uscis.gov/policy-manual/volume-6-part-f-chapter-2)
