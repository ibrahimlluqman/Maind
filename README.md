# AI Social Scheduler — نسخة GitHub (مجانية بالكامل)

هذا كل الي تحتاجه يشتغل بدون سيرفر حقيقي: **GitHub Pages** للواجهة،
**GitHub Actions** بدل الـ Cron، و**ملفات JSON** بدل قاعدة بيانات MySQL.

## 1) أنشئ الريبو

1. سوّي ريبو جديد على GitHub (خاص أو عام — الخاص أفضل لأنه يحتوي بيانات حسابك).
2. ارفع كل محتويات هذا المجلد لجذر الريبو (نفس البنية بالضبط).

## 2) فعّل GitHub Pages

Settings → Pages → Source: اختر branch `main` و folder `/ (root)` → Save.
بعد دقيقة أو دقيقتين رح يصير موقعك شغال على:
`https://<اسم_حسابك>.github.io/<اسم_الريبو>/`

## 3) اربط رابط الويب بالبيانات الحقيقية

افتح `index.html`، أول سطر بالـ `<script>` بالأعلى:

```js
const REPO = { owner: "ibrahimlluqman", name: "REPLACE_WITH_YOUR_REPO_NAME" };
```

بدّل `REPLACE_WITH_YOUR_REPO_NAME` باسم الريبو الي سويته. بعدها الواجهة رح تجيب
تلقائيًا بيانات `data/scheduled_posts.json` و`data/insights_log.json` الحقيقية
بدل البيانات التجريبية، وتحدثها كل ٥ دقايق.

## 4) جهّز حساب Instagram Business + تطبيق Meta

- حساب Instagram لازم يكون **Business** أو **Creator** ومربوط بصفحة Facebook.
- سوّي تطبيق على developers.facebook.com، أضف منتج **Instagram Graph API**.
- اعمل OAuth تسجيل دخول مرة وحدة يدويًا واحصل على **long-lived access token**
  (صالح ٦٠ يوم، يحتاج تجديد دوري — نگدر نضيف سكربت تجديد تلقائي لاحقًا لو تريد).
- احصل على **IG_USER_ID** (معرف حساب Instagram Business).

## 5) أضف الـ Secrets بالريبو

Settings → Secrets and variables → Actions → New repository secret:

| الاسم | القيمة |
|---|---|
| `IG_ACCESS_TOKEN` | الـ long-lived token |
| `IG_USER_ID` | معرف حساب Instagram |

## 6) فعّل الصلاحيات

Settings → Actions → General → Workflow permissions → اختر **Read and write permissions**
(بدونها الـ workflow ما يگدر يعمل commit للتحديثات).

## 7) جرّب

- Actions تبويب → اختر workflow → **Run workflow** يدويًا للتجربة الأولى بدل ما تستنى الجدول.
- `publish-scheduled-posts.yml` يشتغل كل ٥ دقايق تلقائيًا.
- `insights-check.yml` يشتغل كل ساعتين تلقائيًا.

## كيف تضيف منشور جديد

الطريقة الأبسط الحين: افتح `data/scheduled_posts.json` مباشرة من واجهة GitHub
بالمتصفح (زر القلم ✏️) وأضف عنصر جديد بنفس الشكل:

```json
{
  "id": 3,
  "content_type": "image",
  "caption": "...",
  "hashtags": "#...",
  "media_path": "media/my-photo.jpg",
  "scheduled_time_utc": "2026-09-20T18:00:00Z",
  "status": "pending",
  "attempts": 0,
  "last_error": null,
  "published_media_id": null
}
```

ارفع الصورة/الفيديو لمجلد `media/` أول، وتأكد `scheduled_time_utc` بتوقيت **UTC**
(بغداد = UTC+3، يعني لو تريدها 8:30 مساءً ببغداد، تكتب 17:30 بالملف).

> لاحقًا نگدر نبني نموذج "Create Post" بالواجهة يضيف هذا تلقائيًا عبر GitHub API
> بدل التعديل اليدوي — گلي إذا تريدها.

## ⚠️ القيود المهمة الي لازم تعرفها

- **الدقة الزمنية**: GitHub Actions أقل جدول مدعوم هو كل ٥ دقايق، وبأوقات الزحمة
  ممكن يتأخر ١٠-١٥ دقيقة إضافية. مو دقة سيرفر مخصص، بس مقبولة لشخص واحد.
- **الوسائط لازم تكون بالريبو نفسه** (أو أي رابط HTTPS عام ثاني) — GitHub عنده حد
  أقصى ~100 ميجا للملف الواحد و~1 گيگا موصى فيه لكامل الريبو المجاني.
- **التوكن الطويل الأمد ينتهي كل ٦٠ يوم** — لازم تجدده يدويًا (أو نضيف سكربت
  تجديد تلقائي لاحقًا).
- **الحماية**: ما فيه صفحة تسجيل دخول بالواجهة، فإذا الريبو "عام" أي شخص يگدر
  يشوف بيانات منشوراتك (مو التوكن — هذا محمي بالـ Secrets). خلّي الريبو **Private**
  إذا تريد خصوصية، وفعّل GitHub Pages يشتغل حتى مع الريبو الخاص (متاح مجانًا).
