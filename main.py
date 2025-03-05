import os
import time
import random
import logging
import requests
import openai
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# تعيين مفاتيح API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID224589568286774SS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKENEAAQabtZB7Rd0BOyaq63AIFaooZCX360rYg04V2L4AvO3edDlBCZCvjkNa2ODYtLsk9GtPubyJbJLDpKojDpIk5nIAAsLSKvNHhUbJxQE1raCuB75Rzz9rTROPQpq3nCQuSz31SoPZAZBseLsZB4lLWoeHYYPYuQiRpx0o3T4QN96fPvmyZCpLvK2xvVDDHavuL2F7RKgMUtiOTZCqgZC6y44SsxAZD(Logging)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# التحقق من صحة المفاتيح قبل التشغيل
if not OPENAI_API_KEY or not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
    logging.error("❌ يرجى التأكد من إعداد متغيرات البيئة بشكل صحيح!")
    raise ValueError("مفاتيح API غير متوفرة!")

openai.api_key = OPENAI_API_KEY

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

def post_to_facebook(content, retries=3):
    """نشر المحتوى على فيسبوك مع إعادة المحاولة عند الفشل"""
    if not content:
        logging.warning("⚠️ لا يوجد محتوى للنشر")
        return
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed",
                params={"message": content, "access_token": FACEBOOK_ACCESS_TOKEN}
            )
            response.raise_for_status()
            post_id = response.json().get("id", "غير معروف")
            logging.info(f"✅ تم النشر بنجاح! ID: {post_id}")
            return post_id
        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ فشل النشر (محاولة {attempt}): {e}")
            time.sleep(5 * attempt)  # تأخير تصاعدي بين المحاولات
    
    logging.error("❌ فشل النشر بعد عدة محاولات!")

def main():
    """التنفيذ الرئيسي مع توليد منشورات متعددة"""
    num_posts = 3  # عدد المنشورات التي سيتم إنشاؤها ونشرها
    logging.info(f"🔄 جاري توليد {num_posts} منشورات...")
    
    for i in range(num_posts):
        logging.info(f"📌 توليد المنشور رقم {i + 1}...")
        generated_content = generate_crypto_content()
        
        if generated_content:
            logging.info(f"\n📢 المحتوى المُولد:\n{generated_content}\n{'-'*30}")
            wait_time = random.randint(20, 40)  # تأخير عشوائي بين 20-40 ثانية
            logging.info(f"⏳ انتظار {wait_time} ثانية قبل النشر...")
            time.sleep(wait_time)
            post_to_facebook(generated_content)

if __name__ == "__main__":
    main()