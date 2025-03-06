#!/bin/bash
# تثبيت المتطلبات
pip install -r requirements.txt
# تشغيل FastAPI باستخدام uvicorn
uvicorn server:app --host 0.0.0.0 --port 10000