import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# ----------------------------------------
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
# 🌐 Enhanced AI-Powered Website Scraper
# ----------------------------------------

def extract_info_from_url(url):
    try:
        # 1. Try newspaper3k article parsing
        article = Article(url)
        article.download()
        article.parse()
        main_text = article.text.strip()

        # 2. Fallback scrape: Get title, meta, H1s, and body text
        extra_content = ""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else ""
            metas = " ".join([meta.get("content", "") for meta in soup.find_all("meta")])
            h1s = " ".join([h.get_text() for h in soup.find_all("h1")])
            paragraphs = " ".join([p.get_text() for p in soup.find_all("p")[:10]])
            extra_content = f"{title}\n{metas}\n{h1s}\n{paragraphs}"
        except Exception:
            pass

        # Combine everything
        content = f"{main_text}\n\n{extra_content}"

        # GPT Prompt
        prompt = f"""
        You are an assistant analyzing MedTech, IVD, or HealthTech startup websites.
        Given the homepage content below, extract:

        - Company name
        - Summary of product or solution
        - Contact email (if found)
        - Growth Phase (pre-seed, seed, series A, B, C, consolidation, expansion)
        - Score from 0-100 (fit for InnHealthium: funding, regulatory, GTM, AI)
        - A brief summary to add as a CRM comment (1-2 sentences)

        Format:
        Company: ...
        Summary: ...
        Email: ...
        Growth Phase: ...
        Score: ...
        Comments: ...

        ---
        {content}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        output = response.choices[0].message.content.strip()

        # Convert to dictionary
        result = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip().lower()] = value.strip()

        return {
            "company": result.get("company", ""),
            "summary": result.get("summary", ""),
            "email": result.get("email", ""),
            "growth_phase": result.get("growth phase", "").lower(),
            "score": int(result.get("score", "0")),
            "comments": result.get("comments", "")
        }

    except Exception as e:
        return {
            "error": f"❌ Error extracting info from {url}: {str(e)}"
        }
