
import requests
import time
from bs4 import BeautifulSoup

# ==== 🔧 CẤU HÌNH TELEGRAM ===
TELEGRAM_BOT_TOKEN = "8161488133:AAGMeEmgpN-pWNevnuq9V3EOjWO-f7HKF4I"
TELEGRAM_CHAT_ID = "1056379191"
CHECK_INTERVAL = 600  # Kiểm tra mỗi 10 phút
# ==============================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

SEEN_JOBS = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("❌ Lỗi gửi Telegram:", response.text)
    except Exception as e:
        print("❌ Ngoại lệ khi gửi Telegram:", e)

def scrape_upwork_jobs():
    url = "https://www.upwork.com/nx/jobs/search/?q=Vietnamese&sort=recency"

    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        job_elements = soup.select("section.up-card-section")

        jobs = []

        for job in job_elements:
            title_tag = job.find("h4")
            link_tag = job.find("a", href=True)

            if not title_tag or not link_tag:
                continue

            title = title_tag.text.strip()
            link = "https://www.upwork.com" + link_tag["href"].split("?")[0]

            if link in SEEN_JOBS:
                continue

            SEEN_JOBS.add(link)
            jobs.append({"title": title, "link": link})

        return jobs

    except Exception as e:
        print("❌ Lỗi lấy job:", e)
        return []

def main():
    while True:
        print("🔎 Đang kiểm tra job mới...")
        jobs = scrape_upwork_jobs()
        for job in jobs:
            msg = f"📢 <b>{job['title']}</b>\n🔗 {job['link']}"
            send_telegram_message(msg)
        print(f"⏱️ Đợi {CHECK_INTERVAL} giây...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
