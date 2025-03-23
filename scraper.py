import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# ----------------------------------------
# 🛠️ API key hardcoded (use with caution)
# ----------------------------------------
client = OpenAI(
    api_key="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",  # Replace with your key
    project="proj_7EqGQg2RKl5FeRaNsYxzC2w"              # Replace with your project ID if using sk-proj
)

# ----------------------------------------
# GPT-powered Company Info Extractor
# ----------------------------------------
def extract_info_from_url(url):
    try:
        # Extract text content from the page
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
        - Score from 0 to 100, estimating fit for InnHealthium (regulatory, funding, digital & AI, and go-to-market support in MedTech, IVD, digital health)

        Respond in this format (no explanations):

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

# ----------------------------------------
# Optional HTML scraper for known page layouts
# ----------------------------------------
def scrape_leads_from_url(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        companies = []

        for tag in soup.find_all("div", class_="company"):
            name = tag.find("h2").text
            website = tag.find("a")['href']
            email = tag.find("span", class_="email").text
            summary = tag.find("p").text
            companies.append((name, website, email, "Unknown", summary, "seed", 50, "", ""))

        return companies
    except Exception as e:
        print(f"Scraping error: {e}")
        return []
