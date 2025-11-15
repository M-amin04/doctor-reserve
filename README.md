🏥 سیستم رزرواسیون دکتر (Doctor Reservation System)
یک سیستم کامل برای رزرو آنلاین نوبت دکتر با قابلیت‌های پیشرفته

https://img.shields.io/badge/Django-5.0-green
https://img.shields.io/badge/React-18-blue
https://img.shields.io/badge/DRF-3.15-red
https://img.shields.io/badge/PostgreSQL-15-blue

✨ ویژگی‌های اصلی
🔧 بک‌اند (Django + DRF)
🔐 احراز هویت پیشرفته با Token Authentication

👨‍⚕️ مدیریت کامل دکترها با تخصص‌های مختلف

📅 سیستم رزرو نوبت هوشمند

⭐ سیستم نظرات و امتیازدهی

📊 پنل ادمین قدرتمند

📚 مستندات کامل API با Swagger

⚛️ فرانت‌اند (React)
🎨 طراحی مدرن و ریسپانسیو

🔍 جستجوی پیشرفته دکترها

📱 رابط کاربری حرفه‌ای

🔄 مدیریت state با React Hooks

🚀 شروع سریع
پیش‌نیازها
Python 3.8+

Node.js 14+

PostgreSQL

نصب و راه‌اندازی
۱. کلون کردن پروژه
bash
git clone <repository-url>
cd Reserve
۲. راه‌اندازی بک‌اند
bash
# ایجاد virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# نصب requirements
pip install -r requirements.txt

# تنظیمات دیتابیس
python manage.py makemigrations
python manage.py migrate

# ایجاد سوپریوزر
python manage.py createsuperuser



🛠️ تکنولوژی‌ها
بک‌اند
Django 5.0 - فریمورک اصلی

Django REST Framework - API

django-cors-headers - مدیریت CORS

drf-spectacular - مستندات API

PostgreSQL - دیتابیس

فرانت‌اند
React 18 - کتابخونه اصلی

React Router - مسیریابی

Axios - درخواست‌های HTTP

CSS3 - استایل‌دهی

👥 نقش‌های کاربری
👨‍💼 بیمار - رزرو نوبت، ثبت نظر

👨‍⚕️ دکتر - مدیریت نوبت‌ها، مشاهده نظرات

🔧 ادمین - مدیریت کامل سیستم

📱 صفحات اصلی
🏠 صفحه اصلی - لیست دکترها با قابلیت جستجو

🔐 ورود/ثبت‌نام - احراز هویت کاربران

👨‍⚕️ پروفایل دکتر - اطلاعات کامل دکتر

📅 نوبت‌های من - مدیریت نوبت‌های کاربر

⭐ نظرات - مشاهده و ثبت نظرات

🚀 Deploy
تولید
bash
# جمع‌آوری static files
python manage.py collectstatic

# تنظیم DEBUG=False
# تنظیم دیتابیس production
# تنظیم ALLOWED_HOSTS
🤝 مشارکت
Fork the project

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 لایسنس
این پروژه تحت لایسنس MIT منتشر شده است.

📞 پشتیبانی
برای گزارش باگ یا پیشنهاد feature جدید، لطفاً یک issue جدید ایجاد کنید.

ساخته شده با ❤️ توسط تیم توسعه