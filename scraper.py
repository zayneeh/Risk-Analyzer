import os, re, json, requests
from bs4 import BeautifulSoup
import pdfplumber
from dotenv import load_dotenv
import praw 
from datetime import datetime, timedelta

load_dotenv()
HEADERS = {"User-Agent": "Mozilla/5.0 (EB1A-Scraper)"}
BASE_URL = "https://www.uscis.gov"
USCIS_POLICY = f"{BASE_URL}/policy-manual/volume-6-part-f-chapter-2"
AAO_INDEX = f"{BASE_URL}/administrative-appeals/aao-decisions/aao-non-precedent-decisions"

RAW_AAO_DIR = "knowledge_base/raw/aao"
PROCESSED_DIR = "knowledge_base/processed"
os.makedirs(RAW_AAO_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean(text): return re.sub(r"\s+", " ", text.strip())

# 1️⃣ USCIS Policy Manual extraction
def scrape_uscis_policy():
    print("🔍 Fetching USCIS EB‑1A policy manual...")
    r = requests.get(USCIS_POLICY, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    article = soup.find("article") or soup.find("div", class_="field--name-body")
    if not article:
        print("⚠️ Couldn't find policy content.")
        return

    sections = {}
    heading = None
    for el in article.find_all(['h2','h3','h4','p','li']):
        text = clean(el.get_text())
        if el.name in ("h2","h3","h4"):
            heading = text
            sections[heading] = ""
        elif heading:
            sections[heading] += " " + text

    with open(os.path.join(PROCESSED_DIR, "uscis_policy.json"), "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
    print(f"...Extracted {len(sections)} USCIS policy sections.")

# 2️⃣ AAO PDF download and extraction
def scrape_aao_pdfs():
    print("📄 Fetching AAO non-precedent decision links...")
    r = requests.get(AAO_INDEX, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    pdfs = []
    for a in soup.select("a[href$='.pdf']"):
        title = clean(a.get_text())
        href = a['href']
        full_url = href if href.startswith("http") else BASE_URL + href
        pdfs.append((title, full_url))

    decisions = []
    for title, url in pdfs:
        safe_fn = re.sub(r'[\\/*?:"<>|]',"_", title)
        path = os.path.join(RAW_AAO_DIR, safe_fn + ".pdf")
        if not os.path.exists(path):
            print(" ↓ Downloading", title)
            resp = requests.get(url, headers=HEADERS, timeout=30)
            with open(path,"wb") as f:
                f.write(resp.content)

        text_snip = ""
        try:
            with pdfplumber.open(path) as pdf:
                text_snip = " ".join(p.extract_text() or "" for p in pdf.pages[:5])
        except Exception as e:
            print("⚠️ PDF read error:", title, e)
            continue

        decisions.append({"title": title, "url": url, "text_snippet": clean(text_snip)})

    with open(os.path.join(PROCESSED_DIR, "aao_decisions.json"), "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2, ensure_ascii=False)

    print(f"...Processed {len(decisions)} AAO decisions.")


def scrape_reddit_web():
    print("🗣 Web scraping Reddit for EB-1A posts...")
    
    posts = []
    subreddits = ["immigration", "USCIS"]
    
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/search.json?q=EB1A&sort=new&restrict_sr=1&limit=50"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers)
            print(f"...Reddit web response for r/{sub}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                sub_posts = 0
                for post_data in data['data']['children']:
                    post = post_data['data']
                    posts.append({
                        "title": post['title'],
                        "url": post['url'], 
                        "score": post['score'],
                        "text": post.get('selftext', '')[:1000],
                        "created_utc": post['created_utc'],
                        "subreddit": sub
                    })
                    sub_posts += 1
                print(f"  Found {sub_posts} posts in r/{sub}")
                    
        except Exception as e:
            print(f"Web scraping error for r/{sub}: {e}")
    
    # Save to file
    os.makedirs("knowledge_base/processed", exist_ok=True)
    with open("knowledge_base/processed/reddit_eb1a_posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(posts)} Reddit posts to file.")
    return posts

# 🧩 Main orchestrator
def run_all():
    scrape_uscis_policy()
    scrape_aao_pdfs()
    scrape_reddit_web()  # Uncomment when credentials are ready

if __name__ == "__main__":
    run_all()
