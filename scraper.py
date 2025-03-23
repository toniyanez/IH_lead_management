import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# -------------------------------------------
# Securely get API credentials from secrets
# -------------------------------------------
api_key = st.secrets["OPENAI_API_KEY"]
project_id = st.secrets["OPENAI_PROJECT_ID"]

# Initialize OpenAI client with project-scoped key
client = OpenAI(
    api_key=api_key,
    project=project_id
)

# -------------------------------------------
# GPT-powered company info extractor
# -------------------------------------------
def extract_info_from_url(url):
    try:
        # Step 1: Scrape main article text from the page
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        # Step 2: Ask GPT to analyze and extract structured info
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

# -------------------------------------------
# (Optional) HTML-based lead extractor
# Only works on known HTML structure
# -------------------------------------------
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

