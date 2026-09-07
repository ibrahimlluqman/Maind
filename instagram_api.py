"""
غلاف بسيط حول Instagram Graph API — يُستخدم من سكربتات GitHub Actions.
يقرأ التوكن ومعرف الحساب من متغيرات البيئة (تُمرَّر من GitHub Secrets).
"""
import os
import time
import requests

GRAPH_API_VERSION = "v20.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class InstagramAPI:
    def __init__(self):
        self.token = os.environ["IG_ACCESS_TOKEN"]
        self.ig_user_id = os.environ["IG_USER_ID"]

    def _get(self, path, params=None):
        params = params or {}
        params["access_token"] = self.token
        r = requests.get(f"{BASE_URL}/{path}", params=params, timeout=30)
        return r.json()

    def _post(self, path, data=None):
        data = data or {}
        data["access_token"] = self.token
        r = requests.post(f"{BASE_URL}/{path}", data=data, timeout=30)
        return r.json()

    def create_image_container(self, image_url: str, caption: str) -> dict:
        return self._post(f"{self.ig_user_id}/media", {
            "image_url": image_url,
            "caption": caption,
        })

    def create_video_container(self, video_url: str, caption: str, is_reel: bool) -> dict:
        return self._post(f"{self.ig_user_id}/media", {
            "media_type": "REELS" if is_reel else "VIDEO",
            "video_url": video_url,
            "caption": caption,
        })

    def get_container_status(self, creation_id: str) -> dict:
        return self._get(creation_id, {"fields": "status_code"})

    def wait_until_ready(self, creation_id: str, tries: int = 10, delay: int = 8) -> bool:
        for _ in range(tries):
            time.sleep(delay)
            status = self.get_container_status(creation_id)
            code = status.get("status_code")
            if code == "FINISHED":
                return True
            if code == "ERROR":
                return False
        return False

    def publish_container(self, creation_id: str) -> dict:
        return self._post(f"{self.ig_user_id}/media_publish", {"creation_id": creation_id})

    def get_account_summary(self) -> dict:
        return self._get(self.ig_user_id, {"fields": "followers_count,media_count,name,username"})
