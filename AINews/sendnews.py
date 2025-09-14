import requests
import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env if present (for local dev)
load_dotenv(override=True)

# ---- Environment Variables ----
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
print(GROQ_API_KEY)

# Fail fast if required secrets are missing
if not GROQ_API_KEY:
    raise RuntimeError("❌ Missing GROQ_API_KEY environment variable")
if not SENDER_EMAIL:
    raise RuntimeError("❌ Missing SENDER_EMAIL environment variable")
if not RECIPIENT_EMAIL:
    raise RuntimeError("❌ Missing RECIPIENT_EMAIL environment variable")
if not APP_PASSWORD:
    raise RuntimeError("❌ Missing APP_PASSWORD environment variable")

# ---- RSS Feeds ----
POPULAR_AI_SITES = [
    {"name": "MIT Technology Review", "rss": "https://www.technologyreview.com/feed/", "category": "Research"},
    {"name": "TechCrunch AI", "rss": "https://techcrunch.com/tag/ai/feed/", "category": "Business"},
    {"name": "Ars Technica", "rss": "https://feeds.arstechnica.com/arstechnica/technology-lab/", "category": "Technology"},
    {"name": "ZDNet AI", "rss": "https://www.zdnet.com/topic/artificial-intelligence/rss.xml", "category": "Enterprise"},
    {"name": "AI News", "rss": "https://www.artificialintelligence-news.com/feed/", "category": "Industry"},
    {"name": "Towards Data Science", "rss": "https://towardsdatascience.com/feed", "category": "Research"},
    {"name": "OpenAI Blog", "rss": "https://openai.com/blog/rss.xml", "category": "Research"},
    {"name": "Hugging Face Blog", "rss": "https://huggingface.co/blog/feed.xml", "category": "Research"},
    {"name": "AI Research", "rss": "https://www.artificialintelligence-news.com/feed/", "category": "Research"},
    {"name": "Machine Learning Mastery", "rss": "https://machinelearningmastery.com/feed/", "category": "Research"},
    {"name": "AI Weekly", "rss": "https://aiweekly.co/issues.rss", "category": "Newsletter"},
    {"name": "AI News Daily", "rss": "https://www.artificialintelligence-news.com/feed/", "category": "Industry"},
    {"name": "AI Business Weekly", "rss": "https://www.artificialintelligence-news.com/feed/", "category": "Business"},
    {"name": "AI Time Journal", "rss": "https://www.aitimejournal.com/feed/", "category": "Industry"},
    {"name": "AI Research Hub", "rss": "https://www.artificialintelligence-news.com/feed/", "category": "Research"},
]

# ---- Discover AI Sites ----
def discover_top_ai_sites():
    print("🔍 Discovering top AI news sites...")
    active_sites = []

    for site in POPULAR_AI_SITES:
        try:
            print(f"Checking {site['name']}...")
            feed = feedparser.parse(site["rss"])
            if not feed.bozo and len(feed.entries) > 0:
                recent_articles = 0
                for entry in feed.entries[:5]:
                    try:
                        if hasattr(entry, "published_parsed") and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                            if pub_date > datetime.now() - timedelta(days=7):
                                recent_articles += 1
                    except:
                        recent_articles += 1

                if recent_articles > 0:
                    site["recent_articles"] = recent_articles
                    site["total_articles"] = len(feed.entries)
                    active_sites.append(site)
                    print(f"✅ {site['name']} - {recent_articles} recent articles")
                else:
                    print(f"❌ {site['name']} - No recent articles")
            else:
                print(f"❌ {site['name']} - Invalid feed")

        except Exception as e:
            print(f"❌ {site['name']} - Error: {e}")
            continue

        time.sleep(0.5)

    active_sites.sort(key=lambda x: x["recent_articles"], reverse=True)
    top_10 = active_sites[:10]

    print(f"\n Selected top {len(top_10)} active AI news sites:")
    for i, site in enumerate(top_10, 1):
        print(f"  {i}. {site['name']} ({site['recent_articles']} recent articles)")

    return top_10

# ---- Fetch Articles ----
def fetch_top_news_from_sites(selected_sites):
    articles = []
    print(f"\n📰 Fetching top 2 articles from {len(selected_sites)} sites...")

    for i, site in enumerate(selected_sites, 1):
        try:
            print(f"[{i}/{len(selected_sites)}] Fetching from {site['name']}...")
            feed = feedparser.parse(site["rss"])
            for entry in feed.entries[:2]:
                try:
                    article = {
                        "title": entry.get("title", "No Title"),
                        "link": entry.get("link", "#"),
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", entry.get("description", "No summary available")),
                        "source": site["name"],
                        "category": site["category"],
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"  ⚠️ Error processing article: {e}")
                    continue
        except Exception as e:
            print(f"  ❌ Error fetching from {site['name']}: {e}")
            continue

        time.sleep(1)

    print(f"📈 Collected {len(articles)} articles total")
    return articles

# ---- Summarize Article ----
def summarize_article(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "user", "content": f"Summarize the following AI article in 2-3 sentences:\n\n{text}"}
        ],
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    summary = response.json()["choices"][0]["message"]["content"]
    return summary

# ---- Send Email ----
def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email error: {e}")

# ---- Generate Email Body ----
def generate_email_body(articles):
    current_date = datetime.now().strftime("%B %d, %Y")
    sources = {}
    for article in articles:
        sources.setdefault(article["source"], []).append(article)

    email_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 30px; }}
            .source {{ margin: 25px 0; }}
            .source h3 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }}
            .article {{ margin: 20px 0; padding: 20px; border-left: 5px solid #3498db; background-color: #f8f9fa; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .article-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }}
            .article-meta {{ font-size: 12px; color: #666; margin-bottom: 10px; }}
            .article-summary {{ margin: 10px 0; line-height: 1.5; }}
            .article-link {{ color: #3498db; text-decoration: none; font-weight: bold; }}
            .article-link:hover {{ text-decoration: underline; }}
            .footer {{ margin-top: 40px; padding: 20px; background-color: #f4f4f4; text-align: center; border-radius: 10px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1> AI & Gen AI News Digest</h1>
            <p>{current_date} | Top {len(articles)} Articles from {len(sources)} Sources</p>
        </div>
    """

    for source, source_articles in sources.items():
        email_body += f'<div class="source"><h3>📰 {source}</h3>'
        for article in source_articles:
            summary = summarize_article(article["summary"])
            email_body += f"""
            <div class="article">
                <div class="article-title">{article['title']}</div>
                <div class="article-meta">Category: {article['category']} | Published: {article['published']}</div>
                <div class="article-summary">{summary}</div>
                <a href="{article['link']}" class="article-link">Read full article →</a>
            </div>
            """
        email_body += "</div>"

    email_body += """
        <div class="footer">
            <p>🤖 This digest is automatically generated from top AI/Gen AI news sources</p>
            <p>Sources are dynamically selected based on recent activity and content quality</p>
        </div>
    </body>
    </html>
    """

    return email_body

# ---- Main ----
def main():
    print("🚀 Starting AI News Aggregator...")

    top_sites = discover_top_ai_sites()
    if not top_sites:
        print("❌ No active AI news sites found!")
        return

    articles = fetch_top_news_from_sites(top_sites)
    if not articles:
        print("❌ No articles found!")
        return

    print("\n📧 Generating email digest...")
    email_body = generate_email_body(articles)
    send_email("Daily AI & Gen AI News Digest", email_body)

    print("✅ Process completed successfully!")

if __name__ == "__main__":
    main()
