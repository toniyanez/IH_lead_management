import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# ----------------------------------------
# Configure OpenAI Client
# Supports classic key or project-scoped key
# ----------------------------------------

# Required: OPENAI_API_KEY in Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Optional: support org or project ID for sk-proj keys
org_id = st.secrets.get("OPENAI_ORG_ID", None)
project_id = st.secrets.get("OPENAI_PROJECT_ID", None)

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    organization=org_id,     # use if provided
    project=project_id       # use if using sk-proj key
)

# ----------------------------------------
# GPT-powered Website Info Extractor
# ----------------------------------------

def extract_info_from_url(url):
    try:
        # Step 1: Download and extract article text from homepage
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        # Step 2: Ask GPT to extract lead information
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
# Optional: HTML Pattern-Based Lead Extractor
# Only works with known HTML structure
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

