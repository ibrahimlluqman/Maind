"""
publish_scheduled.py
يشتغل كل 5 دقايق عبر GitHub Actions (.github/workflows/publish-scheduled-posts.yml).
يقرأ data/scheduled_posts.json، ينشر أي بوست حان وقته عبر Instagram Graph API،
ويحدّث حالته بنفس الملف (يُحفظ بعدين عبر git commit من داخل الـ workflow).
"""
import json
import os
from datetime import datetime, timezone

from instagram_api import InstagramAPI

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "scheduled_posts.json")


def raw_media_url(media_path: str) -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "")  # مثال: ibrahimlluqman/scheduler
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{media_path}"


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        posts = json.load(f)

    ig = InstagramAPI()
    now = datetime.now(timezone.utc)
    changed = False

    for post in posts:
        if post["status"] != "pending":
            continue
        scheduled_time = datetime.fromisoformat(post["scheduled_time_utc"].replace("Z", "+00:00"))
        if scheduled_time > now:
            continue

        changed = True
        caption = (post.get("caption") or "") + "\n\n" + (post.get("hashtags") or "")
        media_url = raw_media_url(post["media_path"])
        is_video = post["content_type"] in ("video", "reel")

        try:
            if is_video:
                container = ig.create_video_container(media_url, caption, post["content_type"] == "reel")
            else:
                container = ig.create_image_container(media_url, caption)

            if "error" in container:
                raise RuntimeError(container["error"].get("message", "خطأ غير معروف عند إنشاء الـ container"))

            creation_id = container["id"]

            if is_video:
                ready = ig.wait_until_ready(creation_id)
                if not ready:
                    raise RuntimeError("فشلت معالجة الفيديو على خوادم Meta (timeout أو ERROR)")

            result = ig.publish_container(creation_id)
            if "error" in result:
                raise RuntimeError(result["error"].get("message", "خطأ غير معروف عند النشر"))

            post["status"] = "published"
            post["published_media_id"] = result.get("id")
            post["last_error"] = None
            print(f"✅ نُشر البوست #{post['id']}")

        except Exception as e:
            post["attempts"] = post.get("attempts", 0) + 1
            post["last_error"] = str(e)
            # بعد 3 محاولات فاشلة نوقف إعادة المحاولة التلقائية
            if post["attempts"] >= 3:
                post["status"] = "failed"
            print(f"❌ فشل البوست #{post['id']}: {e}")

    if changed:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
    else:
        print("لا توجد منشورات مستحقة الآن.")


if __name__ == "__main__":
    main()
