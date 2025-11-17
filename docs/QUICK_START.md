# دليل الإعداد السريع 🚀

## خطوات البدء (15 دقيقة)

### 1. ⚠️ تأمين API Keys (CRITICAL!)

**احذف المفاتيح القديمة فوراً!**

1. اذهب إلى: https://www.binance.com/en/my/settings/api-management
2. احذف أي مفاتيح قديمة
3. أنشئ مفاتيح جديدة:
   - ✅ Enable: **Read Only**
   - ❌ Disable: **Trading**
   - ❌ Disable: **Withdrawals**
4. احفظ المفاتيح في مكان آمن

---

### 2. 🐍 تثبيت Python Dependencies

```bash
cd crypto-ai-trader/backend

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

---

### 3. 🔑 إعداد Environment Variables

```bash
# Copy example file
cp ../.env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**املأ هذه القيم الأساسية:**
```env
# Binance (REQUIRED)
BINANCE_API_KEY=YOUR_NEW_API_KEY
BINANCE_SECRET_KEY=YOUR_NEW_SECRET_KEY

# Email (Optional but recommended)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
NOTIFICATION_EMAIL=your_email@gmail.com

# Leave these as default for now
MIN_CONFIDENCE_SCORE=80
TARGET_PROFIT_PERCENT=3.0
STOP_LOSS_PERCENT=1.0
WATCH_COINS=BTC,ETH,BNB,SOL,ADA
```

**للحصول على Gmail App Password:**
1. اذهب إلى: https://myaccount.google.com/security
2. فعّل 2-Step Verification
3. اذهب إلى App Passwords
4. أنشئ password جديد للتطبيق

---

### 4. 🚀 تشغيل Backend

```bash
cd backend
python main.py
```

**يجب أن ترى:**
```
🚀 Starting AI Trading Signal API Server...
📊 Monitoring coins: ['BTC', 'ETH', 'BNB', 'SOL', 'ADA']
⚙️ Min confidence: 80%
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**اختبر API:**
افتح: http://localhost:8000
يجب أن ترى API documentation

---

### 5. 🎨 تثبيت Frontend

**افتح terminal جديد:**

```bash
cd crypto-ai-trader/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**يجب أن ترى:**
```
  ▲ Next.js 14.0.3
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

---

### 6. ✅ اختبار النظام

1. **افتح Dashboard:** http://localhost:3000

2. **جرب تحليل عملة:**
   - اختر "BTC" من القائمة
   - اضغط "تحليل BTC"
   - انتظر 2-3 دقائق (التدريب في المرة الأولى)

3. **تحقق من النتائج:**
   - يجب أن تظهر إشارة كاملة
   - تأكد من وجود Confidence Score
   - راجع أسباب الإشارة

---

## 🐛 حل المشاكل الشائعة

### ❌ خطأ: Module not found
```bash
# تأكد من تفعيل virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ خطأ: Binance API Error
```bash
# تحقق من:
# 1. صحة API Keys في .env
# 2. الصلاحيات (Read Only)
# 3. اتصال الإنترنت
```

### ❌ خطأ: Port already in use
```bash
# غير البورت في backend/main.py
# من 8000 إلى 8001 مثلاً
uvicorn.run(app, host="0.0.0.0", port=8001)

# وفي frontend/next.config.js:
NEXT_PUBLIC_API_URL: 'http://localhost:8001'
```

### ❌ Frontend لا يتصل بـ Backend
```bash
# تأكد من:
# 1. Backend يعمل (http://localhost:8000)
# 2. لا يوجد CORS errors في Console
# 3. الـ API URL صحيح في frontend
```

---

## 🎯 الخطوات التالية

### 1. **اختبر بـ Demo Account (مهم جداً!)**
   - افتح حساب Demo في Binance
   - اختبر الإشارات لمدة أسبوعين
   - سجل النتائج

### 2. **راقب الأداء**
   - افحص Confidence Scores
   - قارن التنبؤات بالواقع
   - سجل الملاحظات

### 3. **اضبط الإعدادات**
```env
# في .env
MIN_CONFIDENCE_SCORE=85  # ارفع للإشارات الأكثر تحفظاً
TARGET_PROFIT_PERCENT=2.5  # اخفض للأهداف الأكثر واقعية
STOP_LOSS_PERCENT=1.5  # اضبط حسب تحملك للمخاطرة
```

---

## 📊 فهم الإشارات

### ✅ إشارة جيدة:
```
Confidence: 85%+
Risk Level: LOW or MEDIUM
Reasoning: 3+ أسباب واضحة
Potential Profit: 2-5%
```

### ⚠️ إشارة متوسطة:
```
Confidence: 75-85%
Risk Level: MEDIUM
Reasoning: 2-3 أسباب
```

### ❌ تجنب:
```
Confidence: < 75%
Risk Level: HIGH
Reasoning: أسباب متضاربة
```

---

## 🔔 إعداد الإشعارات (اختياري)

### Email:
```env
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=app_password_here
NOTIFICATION_EMAIL=your@gmail.com
```

### Telegram:
1. أنشئ بوت مع [@BotFather](https://t.me/botfather)
2. احصل على Token
3. أرسل رسالة لبوتك
4. احصل على Chat ID من: https://api.telegram.org/bot<TOKEN>/getUpdates

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 🎓 نصائح مهمة

1. **لا تتعجل** - اختبر جيداً قبل المال الحقيقي
2. **ابدأ صغيراً** - 10% من رأس المال كحد أقصى
3. **التزم بـ Stop-Loss** - دائماً
4. **لا تكن عاطفياً** - ثق في التحليل أو لا تدخل
5. **تعلم باستمرار** - راقب وطوّر

---

## ✅ Checklist

- [ ] حذفت المفاتيح القديمة
- [ ] أنشأت مفاتيح جديدة (Read Only)
- [ ] ثبّت Python dependencies
- [ ] أعددت .env file
- [ ] Backend يعمل بنجاح
- [ ] Frontend يعمل بنجاح
- [ ] اختبرت تحليل عملة
- [ ] ظهرت إشارة كاملة
- [ ] فهمت كيف أقرأ الإشارات
- [ ] جاهز للاختبار على Demo

**إذا أكملت كل النقاط - تهانينا! 🎉**

**بالتوفيق! 🚀**
