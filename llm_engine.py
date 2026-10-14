import os
import time
from collections import deque
from dotenv import load_dotenv

from groq import Groq
import requests

load_dotenv()

# =========================
# تنظیمات
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "qwen/qwen3.8-27b"

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:1.5b"

# حافظه کوتاه‌مدت: تعداد پیام‌ها (role-based)
# 10 پیام یعنی تقریباً 5 رفت‌وبرگشت
MAX_HISTORY_MESSAGES = 10

# محدودیت کاراکتر برای اینکه پرامپت بیش از حد بزرگ نشود
MAX_HISTORY_CHARS = 8000

SYSTEM_PROMPT = (
    "You are J.A.R.V.I.S, a bilingual assistant (Persian and English) on Windows 11. "
    "Reply in the user's language. Be concise and accurate. "
    "If the user asks to control Windows or open apps/websites, the app may execute it.\n\n"
    "تو جارویس هستی، دستیار دوزبانه فارسی/انگلیسی در ویندوز 11. "
    "در زبان کاربر پاسخ بده، دقیق و کوتاه."
)

# =========================
# حافظه مکالمه
# =========================
# deque برای حافظه چرخشی عالی است
_chat_history = deque(maxlen=MAX_HISTORY_MESSAGES)


def reset_memory():
    """پاک کردن حافظه مکالمه (در صورت نیاز)."""
    _chat_history.clear()


def _trim_history_by_chars(messages, max_chars: int):
    """
    اگر مجموع کاراکترها زیاد شد، از اول حذف می‌کند تا زیر سقف بماند.
    """
    total = sum(len(m.get("content", "")) for m in messages)
    if total <= max_chars:
        return messages

    trimmed = list(messages)
    while trimmed and total > max_chars:
        removed = trimmed.pop(0)
        total -= len(removed.get("content", ""))

    return trimmed


def _build_messages(user_text: str):
    """
    پیام‌ها را برای مدل آماده می‌کند:
    system + history + new user message
    """
    base = [{"role": "system", "content": SYSTEM_PROMPT}]
    history = list(_chat_history)
    combined = base + history + [{"role": "user", "content": user_text}]

    # محدودیت کاراکتر
    combined = _trim_history_by_chars(combined, MAX_HISTORY_CHARS)

    return combined


def _save_turn(user_text: str, assistant_text: str):
    """
    ذخیره یک رفت‌وبرگشت در حافظه (بدون system).
    """
    _chat_history.append({"role": "user", "content": user_text})
    _chat_history.append({"role": "assistant", "content": assistant_text})


# =========================
# Groq
# =========================
def _ask_groq(messages):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing in .env")

    client = Groq(api_key=GROQ_API_KEY)

    # chat.completions برای Groq
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=700,
    )
    return resp.choices[0].message.content.strip()


# =========================
# Ollama
# =========================
def _ask_ollama(messages):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.4},
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return (data.get("message", {}) or {}).get("content", "").strip()


# =========================
# API اصلی پروژه
# =========================
def ask_llm(user_text: str) -> str:
    """
    ورودی کاربر را با حافظه کوتاه‌مدت به مدل می‌دهد.
    اول Groq، در صورت خطا Ollama.
    """
    messages = _build_messages(user_text)

    # اول Groq
    try:
        t0 = time.time()
        answer = _ask_groq(messages)
        dt = (time.time() - t0) * 1000
        # می‌توانی بعداً این dt را لاگ کنی
    except Exception as groq_error:
        # Failover به Ollama
        try:
            t0 = time.time()
            answer = _ask_ollama(messages)
            dt = (time.time() - t0) * 1000
        except Exception as ollama_error:
            # هر دو شکست خوردند
            raise RuntimeError(
                f"Groq failed: {groq_error} | Ollama failed: {ollama_error}"
            )

    # ذخیره در حافظه
    _save_turn(user_text, answer)
    return answer
