import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# ✅ Secure key access from secrets.toml
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    project=st.secrets["OPENAI_PROJECT_ID"]
)

def extract_info_from_url(url):
    try:
        # Scrape main content
        article = Article(url)
        article.download()
        article.parse()
        main_text = article.text.strip()

        # Additional scraping
        extra = ""
        try:
            soup = BeautifulSoup(requests.get(url, timeout=10).content, 'html.parser')
            title = soup.title.string if soup.title else ""
            metas = " ".join([m.get("content", "") for m in soup.find_all("meta")])
            h1s = " ".join([h.get_text() for h in soup.find_all("h1")])
            paragraphs = " ".join([p.get_text() for p in soup.find_all("p")[:10]])
            extra = f"{title}\n{metas}\n{h1s}\n{paragraphs}"
        except:
            pass

        content = f"{main_text}\n\n{extra}"

        prompt = f"""
        Analyze this startup homepage and extract:

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
        return {"error": f"❌ Error extracting info from {url}: {str(e)}"}

