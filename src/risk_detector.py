import openai
import os

# Set your API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Basic USCIS EB-1A Criteria descriptions for LLM grounding
CRITERIA_DESCRIPTIONS = {
    "Criterion 1": "National or international prizes/awards for excellence.",
    "Criterion 2": "Membership in associations requiring outstanding achievement.",
    "Criterion 3": "Published material about the individual in major media or professional publications.",
    "Criterion 4": "Participation as a judge of the work of others in the field.",
    "Criterion 5": "Original contributions of major significance in the field.",
    "Criterion 6": "Authorship of scholarly articles.",
    "Criterion 7": "Work displayed at exhibitions or showcases.",
    "Criterion 8": "Leading or critical role in distinguished organizations.",
    "Criterion 9": "High salary or remuneration compared to peers.",
    "Criterion 10": "Commercial success in the performing arts.",
    "Supporting Letters": "Recommendation letters from experts or collaborators.",
    "General Background": "Background and personal information about the petitioner."
}

def analyze_section_with_openai(section_text, criterion_label):
    """
    Uses OpenAI GPT-4 to analyze a section of a petition and assess RFE risk.

    Args:
        section_text (str): The text from one section of the petition.
        criterion_label (str): One of the USCIS EB-1A criteria labels.

    Returns:
        str: Bullet-point analysis from the AI reviewer.
    """

    criterion_description = CRITERIA_DESCRIPTIONS.get(criterion_label, "General supporting evidence.")

    prompt = f"""
You are acting as a USCIS adjudicator and immigration legal expert.
Your task is to evaluate whether the following petition excerpt satisfies the EB-1A immigration criterion: "{criterion_label}".

📝 Criterion Definition:
"{criterion_description}"

📄 Petition Excerpt:
\"\"\"
{section_text}
\"\"\"

Based on USCIS standards, answer the following:
1. Does the evidence clearly meet the criterion?
2. What (if anything) is weak or missing?
3. How could this be improved to avoid an RFE?

Provide your answer in clear, structured bullet points with legal reasoning.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can use "gpt-3.5-turbo" for cost/speed tradeoffs
            messages=[
                {"role": "system", "content": "You are a legal assistant for U.S. immigration attorneys."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error generating OpenAI response: {e}]"
