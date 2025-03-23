import openai
import requests
from newspaper import Article

openai.api_key = "YOUR_OPENAI_API_KEY"

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
        - Score from 0 to 100, estimating fit for InnHealthium (which offers regulatory, funding, digital & AI, and go-to-market support in MedTech, IVD, digital health).

        Respond in this format:

        Company: ...
        Summary: ...
        Email: ...
        Growth Phase: ...
        Score: ...

        ---
        {text}
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        return response['choices'][0]['message']['content']

    except Exception as e:
        return f"Error extracting info from {url}: {str(e)}"
