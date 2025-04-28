import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
CHAT_ID = config["chat_id"]
MIN_BUDGET = config.get("min_budget", 0)

# Load sent jobs
sent_jobs_file = "sent_jobs.txt"
if os.path.exists(sent_jobs_file):
    with open(sent_jobs_file, 'r') as f:
        seen_jobs = set(f.read().splitlines())
else:
    seen_jobs = set()

def send_telegram_message(bot_token, chat_id, title, description, link):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"*{title}*\n{description}",
        "parse_mode": "Markdown",
        "reply_markup": json.dumps({
            "inline_keyboard": [[
                {"text": "🔗 View Job", "url": link}
            ]]
        })
    }
    response = requests.post(url, data=payload)
    return response.json()

def get_new_upwork_jobs():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    url = "https://www.upwork.com/nx/jobs/search/?q=Vietnamese&sort=recency"
    driver.get(url)
    time.sleep(3)

    jobs = []
    try:
        job_elements = driver.find_elements(By.CSS_SELECTOR, "section.air-card-hover.job-tile-responsive")
        for job in job_elements:
            title_elem = job.find_element(By.CSS_SELECTOR, "h2 > a")
            title = title_elem.text
            link = title_elem.get_attribute("href")
            description = job.find_element(By.CSS_SELECTOR, "span.break").text

            # Budget check (optional)
            budget = 0
            try:
                budget_text = job.find_element(By.CSS_SELECTOR, "small.up-text-muted").text
                if "$" in budget_text:
                    budget = int(budget_text.replace("$", "").split()[0])
            except:
                pass  # some jobs might not have budget listed

            jobs.append({
                "title": title,
                "link": link,
                "description": description,
                "budget": budget
            })
    except Exception as e:
        print("Error while fetching jobs:", e)

    driver.quit()
    return jobs

def save_sent_job(link):
    with open(sent_jobs_file, 'a') as f:
        f.write(link + "\n")

if __name__ == "__main__":
    while True:
        jobs = get_new_upwork_jobs()
        for job in jobs:
            if job['link'] not in seen_jobs and job['budget'] >= MIN_BUDGET:
                seen_jobs.add(job['link'])
                save_sent_job(job['link'])
                send_telegram_message(BOT_TOKEN, CHAT_ID, job['title'], job['description'], job['link'])
                print(f"✅ Sent: {job['title']} (${job['budget']})")
        time.sleep(300)  # 5 phút quét lại
