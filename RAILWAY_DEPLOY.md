# نشر واءم على Railway — دليل خطوة بخطوة

بنية النشر:

```
GitHub  ──►  Railway
                ├── Frontend  (Next.js)              → https://waaem.ai
                ├── Backend   (FastAPI)              → API الداخلي
                ├── Volume    (ChromaDB + SQLite)    → تخزين دائم
                └── GROQ_API_KEY  (سرّي)
```

الواجهة والخلفية تُنشران من نفس المستودع (repo واحد). المتصفح يطلب `/api/*` على نطاق الواجهة،
وNext.js يمرّرها داخلياً إلى الخلفية (لا حاجة لإعداد CORS).

---

## 0) قبل البدء
- حساب على **GitHub** وحساب على **[railway.com](https://railway.com)** (تسجيل الدخول عبر GitHub — الخطة المجانية كافية للبداية).
- مفتاح **Groq** جاهز (`GROQ_API_KEY`).
- امتلاك النطاق **waaem.ai** (من أي مسجّل نطاقات) — مطلوب فقط لخطوة النطاق المخصّص.

---

## 1) ارفع المشروع إلى مستودع GitHub جديد

من مجلد المشروع `WAAEM` (المستودع المحلي والريموت مُعدّان بالفعل، والوجهة `NoraAbdullah33/WAAEM`):

```bash
cd /Users/lamia/Desktop/WAAEM
git push -u origin main
```

> ملاحظة: ملف `backend/.env` (وفيه مفتاح Groq) وقاعدة ChromaDB (73MB) **مستثناة تلقائياً** من الرفع.
> سيُبنى KB على Railway داخل الـ Volume عند أول تشغيل.

---

## 2) أنشئ مشروع Railway واربط المستودع

1. Railway → **New Project** → **Deploy from GitHub repo** → اختر مستودع `waaem`.
2. Railway سيكتشف المستودع. سننشئ **خدمتين** من نفس المستودع.

### خدمة الخلفية (Backend)
1. الخدمة الأولى: **Settings → Root Directory** = `backend`
2. Railway يقرأ `backend/railway.json` تلقائياً (يبني عبر Dockerfile ويشغّل uvicorn على `$PORT`).
3. **Settings → Networking → Generate Domain** (سنستخدم رابطه في الواجهة).

### خدمة الواجهة (Frontend)
1. داخل نفس المشروع: **New → GitHub Repo** → نفس المستودع `waaem`.
2. **Settings → Root Directory** = `frontend`
3. Railway يقرأ `frontend/railway.json` (Dockerfile، مخرجات standalone).

---

## 3) أضف الـ Volume (تخزين ChromaDB الدائم)

على **خدمة الخلفية**:
1. **Settings → Volumes → New Volume**
2. **Mount path** = `/app/knowledge_base`
3. احفظ. هذا الـ Volume يحفظ قاعدة المتجهات (ChromaDB) وقاعدة SQLite بشكل دائم عبر عمليات إعادة النشر.

---

## 4) متغيّرات البيئة (Environment Variables)

على **خدمة الخلفية** → **Variables** → أضف:

| المتغيّر | القيمة |
|---|---|
| `GROQ_API_KEY` | `gsk_...` (مفتاحك — سرّي) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `ENVIRONMENT` | `production` |
| `KB_AUTO_BUILD` | `true` |
| `KB_UPDATE_INTERVAL_HOURS` | `168` |
| `KB_DIR` | `/app/knowledge_base` |
| `CHROMA_DIR` | `/app/knowledge_base/chroma` |
| `DATABASE_URL` | `sqlite+aiosqlite:////app/knowledge_base/waaem.db` |
| `UPLOAD_DIR` | `/app/uploads` |
| `CORS_ORIGINS` | `*` |

على **خدمة الواجهة** → **Variables** → أضف:

| المتغيّر | القيمة |
|---|---|
| `BACKEND_URL` | رابط خدمة الخلفية العام، مثال: `https://waaem-backend-production.up.railway.app` |

> `BACKEND_URL` = الرابط الذي وَلّدته في الخطوة 2 (خدمة الخلفية). يقرأه `next.config.ts` وقت التشغيل لتمرير `/api/*`.

---

## 5) أول نشر

- بعد ضبط المتغيّرات، Railway يعيد النشر تلقائياً.
- **الخلفية** تعمل فوراً، وتبدأ ببناء قاعدة المعرفة (تنزيل ٧٠ وثيقة رسمية + الفهرسة) **في الخلفية** داخل الـ Volume — يستغرق ذلك ~١٠ دقائق أول مرة فقط. أثناءها قد يقول التحليل "قاعدة المعرفة فارغة"؛ انتظر حتى يكتمل.
- تحقّق: افتح `https://<backend-domain>/api/health` → يجب أن يزيد `kb_chunks` تدريجياً حتى ~٤٩٨٠.
- بعد اكتمال البناء، قاعدة المعرفة محفوظة دائماً في الـ Volume (لن تُعاد إلا عند التحديث الأسبوعي).

---

## 6) النطاق المخصّص waaem.ai

على **خدمة الواجهة**:
1. **Settings → Networking → Custom Domain** → أدخل `waaem.ai` (و`www.waaem.ai` إن أردت).
2. Railway يعطيك هدف **CNAME** (مثل `xxxx.up.railway.app`).
3. عند مسجّل النطاق (DNS): أضف سجلّاً:
   - للنطاق الجذر `waaem.ai`: استخدم **ALIAS/ANAME** (أو "CNAME flattening" إن دعمه مزوّدك مثل Cloudflare) يشير إلى هدف Railway.
   - للـ `www`: سجل **CNAME** يشير إلى نفس الهدف.
4. Railway يُصدر شهادة **HTTPS** تلقائياً خلال دقائق.

> إن كان نطاقك على **Cloudflare**: أضف CNAME للجذر (Cloudflare يدعم التسطيح)، واضبط وضع SSL على **Full**.

---

## الصيانة والتكاليف
- **مجاني للبداية**: خطة Railway المجانية/التجريبية تكفي؛ راقب الاستهلاك، ورقِّ الخطة عند الحاجة للتشغيل الدائم بلا إيقاف.
- **تحديث الكود**: أي `git push` إلى `main` يعيد النشر تلقائياً.
- **تحديث الأنظمة**: المُحدّث الأسبوعي يعيد فحص المصادر الرسمية ويحدّث الـ Volume.
- **السرّية**: لا تضع `GROQ_API_KEY` في الكود أبداً — فقط في Variables على Railway.

## استكشاف الأخطاء
- التحليل يقول "قاعدة المعرفة فارغة" → البناء لم يكتمل بعد؛ راقب `/api/health` حتى ترتفع `kb_chunks`.
- الواجهة تُظهر خطأ اتصال → تأكّد أن `BACKEND_URL` في خدمة الواجهة يطابق رابط الخلفية العام.
- بطء أول طلب بعد خمول → في الخطة المجانية قد تُوقَف الخدمة مؤقتاً وتستيقظ عند أول زيارة.
