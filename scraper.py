import requests
from bs4 import BeautifulSoup
from newspaper import Article
import openai
import streamlit as st

# Use the OpenAI API Key securely from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🧠 Option 1: GPT-powered web summarizer
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
        - Score from 0 to 100, estimating fit for InnHealthium (offering regulatory, funding, digital & AI, and GTM support in MedTech, IVD, diagnostics, digital health).

        Format:

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

# 🧪 Option 2: HTML-scraping fallback (very basic)
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
