# main.py
import os
import tweepy
import requests
import schedule
import time
from datetime import datetime
from configparser import ConfigParser
from openai import OpenAI

# ---------------------- تهيئة التكوين ----------------------
config = ConfigParser()
config.read('config.ini')

# ---------------------- تكامل DeepSeek API ----------------------
class DeepSeekClient:
    def __init__(self):
        self.api_key = config['API_KEYS']['deepseek_api_key']
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
    def generate_analysis(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-reasoner",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, json=data, headers=headers)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"خطأ في DeepSeek: {str(e)}")
            return None

# ---------------------- تكامل ChatGPT API ----------------------
class ChatGPTClient:
    def __init__(self):
        self.client = OpenAI(api_key=config['API_KEYS']['chatgpt_api_key'])
    
    def improve_content(self, text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user", 
                    "content": f"حوّل هذا النص إلى منشور جذاب لوسائل التواصل مع إضافة إيموجيات: {text}"
                }]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"خطأ في ChatGPT: {str(e)}")
            return None

# ---------------------- إدارة منصات التواصل ----------------------
class SocialMediaManager:
    def __init__(self):
        # تكوين تويتر
        self.twitter_auth = tweepy.OAuthHandler(
            config['TWITTER']['consumer_key'],
            config['TWITTER']['consumer_secret']
        )
        self.twitter_auth.set_access_token(
            config['TWITTER']['access_token'],
            config['TWITTER']['access_token_secret']
        )
        self.twitter_api = tweepy.API(self.twitter_auth)
    
    def post_to_twitter(self, content):
        try:
            self.twitter_api.update_status(content[:280])
            print(f"[{datetime.now()}] تم النشر على تويتر ✅")
        except Exception as e:
            print(f"خطأ في تويتر: {str(e)}")

# ---------------------- الجدولة التلقائية ----------------------
def scheduled_task():
    print(f"بدء المهمة المجدولة: {datetime.now()}")
    
    # توليد المحتوى
    deepseek = DeepSeekClient()
    raw_content = deepseek.generate_analysis(
        "اكتب تحليلًا تفصيليًا عن عملة Yeblay مع 3 أسباب للاستثمار فيها"
    )
    
    if raw_content:
        chatgpt = ChatGPTClient()
        final_content = chatgpt.improve_content(raw_content)
        
        if final_content:
            social = SocialMediaManager()
            social.post_to_twitter(final_content)

# ---------------------- التشغيل الرئيسي ----------------------
if __name__ == "__main__":
    # جدولة المهام كل 6 ساعات
    schedule.every(6).hours.do(scheduled_task)
    
    # التشغيل الفوري لأول مرة
    scheduled_task()
    
    # الحفاظ على التشغيل
    while True:
        schedule.run_pending()
        time.sleep(60)