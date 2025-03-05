import os
import time
import random
import logging
import threading
import requests
import openai
from dotenv import load_dotenv
from fastapi import FastAPI

# تحميل متغيرات البيئة
load_dotenv()

# تعيين مفاتيح API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

# إعداد سجل الأحداث (Logging)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# التحقق من صحة المفاتيح قبل التشغيل
if not OPENAI_API_KEY or not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
    logging.error("❌ يرجى التأكد من إعداد متغيرات البيئة بشكل صحيح!")
    raise ValueError("مفاتيح API غير متوفرة!")

# تعيين مفتاح OpenAI
openai.api_key = OPENAI_API_KEY

# إنشاء تطبيق FastAPI
app = FastAPI()

def generate_crypto_content():
    """توليد محتوى عن العملة الرقمية باستخدام الذكاء الاصطناعي"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": "اكتب منشورًا عربيًا قصيرًا (3-4 أسطر) عن عملة DeepSeek الرقمية مع إضافة إيموجيز وهاشتاغات. ركز على:\n- تحليل فني للسوق\n- ابتكارات المشروع\n- أخبار حديثة"
            }]
        )
        content = response.choices[0].message["content"].strip()
        logging.info("✅ تم توليد المحتوى بنجاح!")
        return content
    except openai.error.OpenAIError as e:
        logging.error(f"❌ خطأ في توليد المحتوى: {e}")
    except Exception as e:
        logging.error(f"❌ خطأ غير متوقع: {e}")
    return None

def post_to_facebook(content):
    """نشر المحتوى على فيسبوك"""
    if not content:
        logging.warning("⚠️ لا يوجد محتوى للنشر")
        return {"error": "No content generated"}
    
    try:
        response = requests.post(
            f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed",
            params={"message": content, "access_token": FACEBOOK_ACCESS_TOKEN}
        )
        response.raise_for_status()
        post_id = response.json().get("id", "غير معروف")
        logging.info(f"✅ تم النشر بنجاح! ID: {post_id}")
        return {"status": "success", "post_id": post_id}
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ فشل النشر: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
def home():
    return {"message": "🚀 API تعمل بنجاح على Vercel!"}

@app.get("/generate-and-post")
def generate_and_post():
    """توليد منشور جديد ونشره"""
    logging.info("🔄 جاري توليد المنشور...")
    content = generate_crypto_content()
    
    if content:
        wait_time = random.randint(5, 10)  # تأخير عشوائي بين 5-10 ثوانٍ
        logging.info(f"⏳ انتظار {wait_time} ثوانٍ قبل النشر...")
        time.sleep(wait_time)
        return post_to_facebook(content)
    
    return {"status": "error", "message": "Failed to generate content"}

def auto_post():
    """تنفيذ نشر تلقائي عند تشغيل التطبيق"""
    logging.info("🚀 بدء التشغيل... توليد منشور تلقائي الآن!")
    generate_and_post()

# تشغيل النشر التلقائي في الخلفية عند بدء التشغيل
threading.Thread(target=auto_post, daemon=True).start()