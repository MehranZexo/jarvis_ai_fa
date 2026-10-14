import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    models = client.models.list()
    print("✅ مدل‌های فعال روی اکانت شما:")
    for m in models.data:
        print(f" - {m.id}")
except Exception as e:
    print("❌ خطا:", e)
# این فایل کلا برای اینه که ببینید در کروگ  چنتا هوش مصنوعی دارید و کدوم بهتره من رایگان استافده کردم
