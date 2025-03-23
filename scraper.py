import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# ✅ Hardcoded OpenAI project key (only for private/local use!)
client = OpenAI(
    api_key="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",  # Replace with your key
    project="proj_7EqGQg2RKl5FeRaNsYxzC2wI"                  # Replace with your project ID
)

def extract_info_from_url(url):
    try:
        # Extract visible text from homepage using newspaper3k
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        # GPT prompt
        prompt = f"""
        You are an assistant analyzing startup websites for potential B2B services.
        Given the homepage text below, extract:

        - Company name
        - Summary of their product or solution
        - Contact email (if mentioned)
        - Likely growth phase (choose from: pre-seed, seed, series A, series B, series C, consolidation, expansion)
        - Score from 0 to 100, estimating fit for InnHealthium (which offers regulatory, funding, AI, and go-to-market support in MedTech, IVD, digital health)

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


