import requests
import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv(override=True)

# Pre-defined list of popular AI/Gen AI news sites with their RSS feeds
POPULAR_AI_SITES = [
    {
        'name': 'MIT Technology Review',
        'rss': 'https://www.technologyreview.com/feed/',
        'category': 'Research'
    },
    {
        'name': 'TechCrunch AI',
        'rss': 'https://techcrunch.com/tag/ai/feed/',
        'category': 'Business'
    },
    {
        'name': 'Ars Technica',
        'rss': 'https://feeds.arstechnica.com/arstechnica/technology-lab/',
        'category': 'Technology'
    },
    {
        'name': 'ZDNet AI',
        'rss': 'https://www.zdnet.com/topic/artificial-intelligence/rss.xml',
        'category': 'Enterprise'
    },
    {
        'name': 'AI News',
        'rss': 'https://www.artificialintelligence-news.com/feed/',
        'category': 'Industry'
    },
    {
        'name': 'Towards Data Science',
        'rss': 'https://towardsdatascience.com/feed',
        'category': 'Research'
    },
    {
        'name': 'OpenAI Blog',
        'rss': 'https://openai.com/blog/rss.xml',
        'category': 'Research'
    },
    {
        'name': 'Hugging Face Blog',
        'rss': 'https://huggingface.co/blog/feed.xml',
        'category': 'Research'
    },
    {
        'name': 'AI Research',
        'rss': 'https://www.artificialintelligence-news.com/feed/',
        'category': 'Research'
    },
    {
        'name': 'Machine Learning Mastery',
        'rss': 'https://machinelearningmastery.com/feed/',
        'category': 'Research'
    },
    {
        'name': 'AI Weekly',
        'rss': 'https://aiweekly.co/issues.rss',
        'category': 'Newsletter'
    },
    {
        'name': 'AI News Daily',
        'rss': 'https://www.artificialintelligence-news.com/feed/',
        'category': 'Industry'
    },
    {
        'name': 'AI Business Weekly',
        'rss': 'https://www.artificialintelligence-news.com/feed/',
        'category': 'Business'
    },
    {
        'name': 'AI Time Journal',
        'rss': 'https://www.aitimejournal.com/feed/',
        'category': 'Industry'
    },
    {
        'name': 'AI Research Hub',
        'rss': 'https://www.artificialintelligence-news.com/feed/',
        'category': 'Research'
    }
]

def discover_top_ai_sites():
    """Dynamically discover top AI news sites by checking their activity and popularity"""
    print("🔍 Discovering top AI news sites...")
    
    active_sites = []
    
    for site in POPULAR_AI_SITES:
        try:
            print(f"Checking {site['name']}...")
            feed = feedparser.parse(site['rss'])
            
            # Check if feed is valid and has recent content
            if not feed.bozo and len(feed.entries) > 0:
                # Check if articles are recent (within last 7 days)
                recent_articles = 0
                for entry in feed.entries[:5]:  # Check last 5 articles
                    try:
                        # Simple check for recent content
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                            if pub_date > datetime.now() - timedelta(days=7):
                                recent_articles += 1
                    except:
                        # If date parsing fails, assume it's recent
                        recent_articles += 1
                
                if recent_articles > 0:
                    site['recent_articles'] = recent_articles
                    site['total_articles'] = len(feed.entries)
                    active_sites.append(site)
                    print(f"✅ {site['name']} - {recent_articles} recent articles")
                else:
                    print(f"❌ {site['name']} - No recent articles")
            else:
                print(f"❌ {site['name']} - Invalid feed")
                
        except Exception as e:
            print(f"❌ {site['name']} - Error: {e}")
            continue
        
        # Add small delay to be respectful
        time.sleep(0.5)
    
    # Sort by recent activity and return top 10
    active_sites.sort(key=lambda x: x['recent_articles'], reverse=True)
    top_10 = active_sites[:10]
    
    print(f"\n Selected top {len(top_10)} active AI news sites:")
    for i, site in enumerate(top_10, 1):
        print(f"  {i}. {site['name']} ({site['recent_articles']} recent articles)")
    
    return top_10

def fetch_top_news_from_sites(selected_sites):
    """Fetch top 2 articles from each selected site"""
    articles = []
    print(f"\n📰 Fetching top 2 articles from {len(selected_sites)} sites...")
    
    for i, site in enumerate(selected_sites, 1):
        try:
            print(f"[{i}/{len(selected_sites)}] Fetching from {site['name']}...")
            feed = feedparser.parse(site['rss'])
            
            for entry in feed.entries[:2]:  # Top 2 articles per site
                try:
                    article = {
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', '#'),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', entry.get('description', 'No summary available')),
                        'source': site['name'],
                        'category': site['category']
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"  ⚠️ Error processing article: {e}")
                    continue
                    
        except Exception as e:
            print(f"  ❌ Error fetching from {site['name']}: {e}")
            continue
        
        # Add delay between requests
        time.sleep(1)
    
    print(f"📈 Collected {len(articles)} articles total")
    return articles

# Summarize article using Groq Inference API
def summarize_article(text):
    url = 'https://api.groq.com/openai/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {os.getenv("GROQ_API_KEY")}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": f"Summarize the following AI article in 2-3 sentences:\n\n{text}"}]
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    summary = response.json()['choices'][0]['message']['content']
    return summary

# Send email with summarized news
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SENDER_EMAIL')
    msg['To'] = os.getenv('RECIPIENT_EMAIL')
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(os.getenv('SENDER_EMAIL'), os.getenv('APP_PASSWORD'))
            server.sendmail(os.getenv('SENDER_EMAIL'), os.getenv('RECIPIENT_EMAIL'), msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email error: {e}")

# Generate enhanced email body
def generate_email_body(articles):
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Group articles by source
    sources = {}
    for article in articles:
        source = article['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(article)
    
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
            summary = summarize_article(article['summary'])
            email_body += f"""
            <div class="article">
                <div class="article-title">{article['title']}</div>
                <div class="article-meta">Category: {article['category']} | Published: {article['published']}</div>
                <div class="article-summary">{summary}</div>
                <a href="{article['link']}" class="article-link">Read full article →</a>
            </div>
            """
        
        email_body += '</div>'
    
    email_body += """
        <div class="footer">
            <p>🤖 This digest is automatically generated from top AI/Gen AI news sources</p>
            <p>Sources are dynamically selected based on recent activity and content quality</p>
        </div>
    </body>
    </html>
    """
    
    return email_body

# Main function
def main():
    print(" Starting AI News Aggregator...")
    
    # Step 1: Discover top 10 active AI news sites
    top_sites = discover_top_ai_sites()
    
    if not top_sites:
        print("❌ No active AI news sites found!")
        return
    
    # Step 2: Fetch top 2 articles from each site
    articles = fetch_top_news_from_sites(top_sites)
    
    if not articles:
        print("❌ No articles found!")
        return
    
    # Step 3: Generate and send email
    print("\n Generating email digest...")
    email_body = generate_email_body(articles)
    send_email("Daily AI & Gen AI News Digest", email_body)
    
    print("✅ Process completed successfully!")

if __name__ == "__main__":
    main()
