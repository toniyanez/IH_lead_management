import requests
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI

# HARDCODED project-scoped API key (⚠️ for private use only)
client = OpenAI(
    api_key="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",
    project="proj_7EqGQg2RKl5FeRaNsYxzC2w"
)

def extract_info_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        prompt = f"""
        You are an assistant analyzing startup websites for potential B2B services.
        Extract:
        - Company name
        - Summary
        - Contact email
        - Growth Phase
        - Score out of 100 (InnHealthium fit)
        Respond like:
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

