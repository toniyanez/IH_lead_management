import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# ✅ HARDCODED API KEY (for local/private use only)
client = OpenAI(
    api_key="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Replace with your actual key
    project="proj_7EqGQg2RKl5FeRaNsYxzC2w"                   # Replace with your actual project ID
)

def extract_info_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        prompt = f"""
        You are an assistant analyzing startup websites for potential B2B services.
        Given the homepage text below, extract:

        - Company name
        - Summary of their product or solution
        - Contact email (if mentioned)
        - Likely growth phase (choose from: pre-seed, seed, series A, series B, series C, consolidation, expansion)
        - Score from 0 to 100, estimating fit for InnHealthium (we help with regulatory, funding, AI, GTM for MedTech, IVD, digital health)

        Respond in this format:

        Company: ...
        Summary: ...
        Email: ...
        Growth Phase: ...
        Score: ...

        ---
        {text}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error extracting info from {url}:\n\n{str(e)}"

