"""
fetch_insights.py
يشتغل كل ساعتين عبر GitHub Actions (.github/workflows/insights-check.yml).
يجيب عدد المتابعين وعدد المنشورات من Instagram Graph API ويضيفهم
كسطر جديد بـ data/insights_log.json (يحتفظ بآخر 500 قراءة بس حتى ما يكبر الملف).
"""
import json
import os
from datetime import datetime, timezone

from instagram_api import InstagramAPI

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "insights_log.json")
MAX_ENTRIES = 500


def main():
    ig = InstagramAPI()
    summary = ig.get_account_summary()

    if "error" in summary:
        print(f"❌ فشلت مراجعة الحساب: {summary['error'].get('message')}")
        raise SystemExit(1)

    entry = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "followers_count": summary.get("followers_count", 0),
        "media_count": summary.get("media_count", 0),
        "username": summary.get("username", ""),
    }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = []

    log.append(entry)
    log = log[-MAX_ENTRIES:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print(f"✅ تمت المراجعة — متابعين: {entry['followers_count']}, منشورات: {entry['media_count']}")


if __name__ == "__main__":
    main()
