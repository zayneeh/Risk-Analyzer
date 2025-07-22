import ollama

CRITERIA_DESCRIPTIONS = {
    "Criterion 2: Judging": "Participation as a judge of the work of others in the same or related field.",
    "Criterion 4: Critical Role": "Evidence of a leading or critical role in distinguished organizations.",
    "Criterion 6: Original Contributions": "Evidence of original contributions of major significance.",
    "Criterion 7: Media Coverage": "Evidence of published material in major media about the individual.",
    "Supporting Letters": "Recommendation letters supporting eligibility.",
    "General Background": "General background and personal bio information."
}

def analyze_section_with_deepseek(section_text, criterion_label):
    print(f"🧠 Prompting DeepSeek for: {criterion_label}")

    criterion_description = CRITERIA_DESCRIPTIONS.get(criterion_label, "General supporting evidence.")

    # Truncate overly long sections (tokens ≈ characters / 4)
    section_text = section_text[:4000]

    prompt = f"""
You are simulating a USCIS EB-1A petition adjudicator.

📘 Criterion:
{criterion_label}

📖 Definition:
{criterion_description}

📄 Petition Excerpt:
\"\"\"
{section_text}
\"\"\"

Instructions:
- Does this section meet the criterion?
- What's weak or missing?
- Suggest improvements or documentation that would help.

Reply in clear bullet points.
"""

    try:
        response = ollama.chat(model="deepseek-llm:7b", messages=[
            {"role": "user", "content": prompt}
        ])
        print("✅ DeepSeek returned a response.")
        return response["message"]["content"]
    except Exception as e:
        print(f"❌ DeepSeek failed: {e}")
        return f"⚠️ DeepSeek LLM error: {e}"
