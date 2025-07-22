# Risk-Analyzer


**VisaCompanion** is a local tool that helps legal professionals and EB-1A petitioners identify weaknesses in their immigration petition drafts before submission. It simulates a USCIS adjudicator’s feedback using a lightweight open-source language model **mistral**  running locally via **Ollama**.

---

## Features

- AI-powered analysis of EB-1A petition content  
- Section-by-section feedback modeled after USCIS RFE criteria  
- 📄 Supports `.docx`, `.pdf`, and `.txt` files  
- Runs entirely offline — no internet or API keys required

---

## Folder Structure

```
Risk-Analyzer/
├── main.py # Analyzer pipeline
├── scraper.py # Downloads USCIS, AAO, Reddit data
├── sample_data/ # Petition input file(s)
├── outputs/ # Final Word report + chart
├── knowledge_base/
│ ├── raw/aao/ # Downloaded AAO decision PDFs
│ └── processed/ # Extracted JSON knowledge
├── src/
│ ├── parser.py
│ ├── risk_detector.py
│ └── report_generator.py
├── requirements.txt
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



### Build the Knowledge Base

Before you run the analyzer, you **must scrape** the official EB-1A resources into the local knowledge base.

```bash
python scraper.py
```

### 1. Install Ollama

Download the installer from:  
[https://ollama.com/download](https://ollama.com/download)  
Install and restart your terminal (or PowerShell) afterward.

---

### 2. Pull the Mistral LLM

In your terminal or PowerShell, run:

```bash
ollama pull mistral
```

To start the model, open a **new terminal window** and run:

```bash
ollama run mistral
```

Keep this terminal running. It hosts the LLM in the background while your tool runs.

---

### 3. Install Python Dependencies

In your main project folder, run:

```bash
pip install -r requirements.txt
```

This will install all dependencies .

---

## How to Use the Tool

### Step 1: Add Your Petition Draft

Save your `.docx` or `.pdf` petition draft inside the `sample_data/` folder.  


### Step 2: Run the Script

In your terminal, from the root of the project, run:

```bash
python main.py
```
This will take a whileee

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


## Credits


- [Ollama](https://ollama.com) 
- [Mistral](https://ollama.com/library/mistral) 
- [USCIS EB-1A Policy Manual](https://www.uscis.gov/policy-manual/volume-6-part-f-chapter-2)
