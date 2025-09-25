# راهنمای تنظیم Reddit OAuth

برای فعال‌سازی دانلود از Reddit، باید یک اپلیکیشن Reddit OAuth ایجاد کنید:

## مراحل تنظیم:

### 1. ایجاد Reddit App
1. به [Reddit Developer Console](https://www.reddit.com/prefs/apps) بروید
2. روی **"Create App"** یا **"Create Another App"** کلیک کنید
3. فرم را پر کنید:
   - **Name**: `Telegram Download Bot` (یا هر نام دلخواه)
   - **App type**: `web app` را انتخاب کنید
   - **Description**: `Bot for downloading Reddit content` (اختیاری)
   - **About URL**: خالی بگذارید (اختیاری)
   - **Redirect URI**: `http://localhost:8080/reddit/callback`

### 2. دریافت اطلاعات OAuth
پس از ایجاد اپلیکیشن:
- **Client ID**: رشته کوتاه زیر نام اپلیکیشن (مثل: `abc123def456`)
- **Client Secret**: رشته طولانی در قسمت "secret"

### 3. تنظیم فایل .env
در فایل `.env` مقادیر زیر را تنظیم کنید:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

### 4. راه‌اندازی
1. ربات را مجدداً راه‌اندازی کنید
2. دستور `/reddit_login` را در ربات ارسال کنید
3. روی دکمه "ورود به Reddit" کلیک کنید
4. اجازه دسترسی به ربات را بدهید
5. حالا می‌توانید لینک‌های Reddit را ارسال کنید

## نکات مهم:
- این تنظیمات فقط یک بار لازم است
- هر کاربر باید یک بار وارد حساب Reddit خود شود
- توکن‌های احراز هویت در حافظه ربات ذخیره می‌شوند
- اگر ربات restart شود، باید مجدداً login کنید

## عیب‌یابی:
- اگر خطای 403 دریافت کردید، مطمئن شوید که Client ID و Secret درست تنظیم شده‌اند
- اگر صفحه callback باز نمی‌شود، بررسی کنید که پورت 8080 آزاد باشد
- اگر مشکلی داشتید، ربات را restart کنید و مجدداً تلاش کنید
