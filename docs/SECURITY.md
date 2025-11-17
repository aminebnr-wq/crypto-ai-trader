# ⚠️ تحذيرات الأمان المهمة

## 🚨 CRITICAL SECURITY WARNINGS

### 1. API Keys Security

**أنت شاركت API Keys معي في المحادثة!**

#### ⚠️ يجب عليك فعل هذا الآن:

1. **احذف المفاتيح القديمة فوراً:**
   ```
   API Key: 6ujc4J9Q24X0CbUNAQKS0efin0LsYKXB847TyDW6zxol8gyZCLQVsVW7YCLJlO6Q
   Secret Key: YesFSYICfDtlnPc2qWohxDuGLp6XtSWIRHo5uDvYdfphCR4ARc42aJBBOw5CxIKc
   ```
   
2. **اذهب إلى Binance → API Management**
3. **Revoke/Delete هذه المفاتيح**
4. **أنشئ مفاتيح جديدة بصلاحيات محدودة**

#### ✅ الصلاحيات الآمنة:
- ✅ **Enable Reading** فقط
- ❌ **Disable Trading**
- ❌ **Disable Withdrawals**
- ❌ **Disable Transfers**

---

### 2. Environment Variables

**لا تشارك `.env` أبداً!**

#### ❌ خطر:
```bash
# DON'T DO THIS!
git add .env
git commit -m "add config"
git push
```

#### ✅ صحيح:
```bash
# .env is in .gitignore
# Only use .env.example for sharing
```

---

### 3. GitHub/Git

**قبل رفع الكود:**

```bash
# تأكد من وجود .gitignore
cat .gitignore

# يجب أن يحتوي على:
# .env
# .env.local
# *.pyc
# __pycache__/
```

---

### 4. Production Deployment

#### على Railway/Render/Heroku:

1. **استخدم Environment Variables في لوحة التحكم**
2. **لا تضع المفاتيح في الكود**
3. **فعّل IP Whitelist في Binance**

#### على Vercel (Frontend):

```bash
# Set environment variables:
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

---

### 5. IP Security

**في Binance API Settings:**

1. **IP Restrictions** → Restrict access to specific IPs
2. **أضف IP سيرفرك فقط**
3. **لا تستخدم "Unrestricted"**

---

### 6. Two-Factor Authentication

**دائماً فعّل 2FA على:**
- ✅ Binance Account
- ✅ GitHub Account
- ✅ Email Account
- ✅ أي حساب مالي

---

### 7. Monitoring

**راقب API Activity:**

1. Binance → API Management → Activity Log
2. تحقق من أي نشاط مشبوه
3. احذف المفاتيح فوراً إذا شككت

---

### 8. Best Practices

```python
# ❌ NEVER do this:
API_KEY = "6ujc4J9Q24X0CbUNAQKS..."

# ✅ ALWAYS do this:
from config import settings
API_KEY = settings.BINANCE_API_KEY
```

---

## 🔒 Security Checklist

قبل الإنتاج، تأكد من:

- [ ] حذفت المفاتيح القديمة المشاركة
- [ ] أنشأت مفاتيح جديدة (Read Only)
- [ ] `.env` في `.gitignore`
- [ ] لا يوجد مفاتيح في الكود
- [ ] فعّلت 2FA على Binance
- [ ] أضفت IP Restrictions
- [ ] استخدمت Environment Variables في Production
- [ ] راجعت API Activity Log
- [ ] لم أشارك المفاتيح مع أحد
- [ ] غيرت Passwords بشكل دوري

---

## ⚠️ إذا تعرضت للاختراق:

1. **احذف API Keys فوراً**
2. **غير كلمة مرور Binance**
3. **تحقق من النشاط المالي**
4. **غير كلمات مرور Email**
5. **اتصل بدعم Binance**
6. **فعّل Security Features**

---

## 📞 Binance Security Support

- Support: https://www.binance.com/en/support
- Security Alerts: security@binance.com
- 24/7 Live Chat

---

**Remember: أمانك المالي مسؤوليتك!**

**🔐 Stay Safe! 🔐**
