import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# ----------------------------------------
# ✅ HARDCODED OpenAI Project Credentials
# Only use for private or local development
# ----------------------------------------
API_KEY = "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"
PROJECT_ID = "proj_7EqGQg2RKl5FeRaNsYxzC2wI"

# Initialize OpenAI client with project-aware setup
client = OpenAI(
    api_key=API_KEY,
    project=PROJECT_ID,
)

# ----------------------------------------
# 🌐 AI-POWERED WEBSITE ANALYZER FUNCTION
# ----------------------------------------

def extract_info_from_url(url):
    try:
        # Step 1: Extract readable text content from URL
        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()

        if not text:
            return f"❌ No readable text found at {url}"

        # Step 2: Build GPT prompt for structured output
        prompt = f"""
        You are an assistant analyzing startup websites for potential B2B services.
        Given the homepage text below, extract:

        - Company name
        - Summary of their product or solution
        - Contact email (if mentioned)
        - Likely growth phase (choose from: pre-seed, seed, series A, series B, series C, consolidation, expansion)
        - Score from 0 to 100, estimating fit for InnHealthium (we help with regulatory, funding, AI, GTM for MedTech, IVD, and diagnostics)

        Respond in this exact format (no commentary):

        Company: ...
        Summary: ...
        Email: ...
        Growth Phase: ...
        Score: ...

        ---
        {text}
        """

        # Step 3: Send to GPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error extracting info from {url}:\n\n{str(e)}"

# ----------------------------------------
# 🔧 OPTIONAL BASIC HTML SCRAPER (fallback)
# Only use for very structured HTML pages
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
