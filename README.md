# Site Change Monitor — مراقب تغيّر الموقع

مشروع بايثون على مرحلتين:

1. **المرحلة 1 (Baseline):** يجلب الصفحة الرئيسية لرابط تعطيه، يستخرج النص المرئي، ويحفظ الـ Embedding المرجعي في `data/baseline.json`.
2. **المرحلة 2 (Watch):** يعمل كل دقيقة، يجلب نفس الرابط، يحسب Embedding جديدًا ويقارنه (cosine similarity) بالمرجعي. إذا نزل التشابه عن العتبة (افتراضيًا `0.98`) يطبع في الـ Terminal:
   `⚠️ يوجد تغيير / يوجد هجوم على الموقع!`

> فشل الاتصال (حجب، انقطاع شبكة، مهلة) يُطبع كرسالة منفصلة "تعذّر جلب الموقع" ولا يُعدّ تغييرًا.

## التثبيت

```bash
git clone <repo-url> && cd psc-site-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## التشغيل

**المرحلة 1** — إنشاء الـ Embedding المرجعي (مرة واحدة):

```bash
python phase1_baseline.py https://example.com
```

**المرحلة 2** — المراقبة كل دقيقة (إيقاف بـ `Ctrl+C`):

```bash
python phase2_watch.py https://example.com
```

يجب استخدام نفس الرابط ونفس الـ backend في المرحلتين.

### خيارات

| الخيار | الافتراضي | الوصف |
|---|---|---|
| `--threshold` | `0.98` | أقل تشابه مسموح قبل اعتباره تغييرًا (ارفعه لحساسية أعلى) |
| `--interval` | `60` | ثواني بين كل فحص |
| `--backend` | `hash` | `hash` تضمين محلي سريع بلا تحميل نماذج؛ `sbert` تضمين دلالي (يتطلب `pip install sentence-transformers`) |
| `--baseline-file` | `data/baseline.json` | مسار ملف المرجع |
| `--insecure` | — | تجاهل التحقق من شهادة TLS |

## ملاحظات

- الصفحات التي تتغير باستمرار (أخبار، عدّادات) قد تعطي تنبيهات كاذبة؛ خفّض `--threshold` (مثل `0.9`).
- الـ Embedding يُحسب على النص المرئي فقط (تُهمل `script` و`style`).

## الاختبارات

```bash
pytest -q
```

تستخدم خادم HTTP محلي يحاكي موقعًا ثم "يخترقه" للتأكد من اكتشاف التغيير.
