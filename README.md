# ⚡ J.A.R.V.I.S - AI Desktop Assistant (Bilingual)
> دستیار صوتی و متنی هوشمند دوزبانه (فارسی / انگلیسی) تحت سیستم‌عامل Windows 11 با معماری هایبرید پردازش ابری/محلی، تله‌متری سیستم و کنترل سخت‌افزار.

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)](https://github.com/TomSchimansky/CustomTkinter)
[![Cloud LLM](https://img.shields.io/badge/Cloud%20LLM-Groq%20(Qwen3.8--27B)-orange)](https://groq.com/)
[![Local LLM](https://img.shields.io/badge/Local%20Fallback-Ollama%20(Qwen2.5--1.5B)-green)](https://ollama.com/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2011-0078D4?logo=windows&logoColor=white)](https://microsoft.com)

---

## 📖 فهرست مطالب
- [معرفی پروژه](#-معرفی-پروژه)
- [قابلیت‌های برجسته (Key Features)](#-قابلیت‌های-برجسته-key-features)
- [معماری سیستم و جریان داده (Architecture & Data Flow)](#-معماری-سیستم-و-جریان-داده-architecture--data-flow)
- [پیش‌نیازها و محیط اجرا (Prerequisites)](#-پیش‌نیازها-و-محیط-اجرا-prerequisites)
- [راهنمای نصب و راه‌اندازی گام‌به‌گام (Step-by-Step Setup)](#-راهنمای-نصب-و-راه‌اندازی-گام‌به‌گام-step-by-step-setup)
- [معرفی و وظیفه هر فایل در پروژه (File Structure & Roles)](#-معرفی-و-وظیفه-هر-فایل-در-پروژه-file-structure--roles)
- [سناریوهای تست و اعتبارسنجی (Testing & Verification)](#-سناریوهای-تست-و-اعتبارسنجی-testing--verification)
- [توسعه در آینده (Roadmap)](#-توسعه-در-آینده-roadmap)

---

## 🎯 معرفی پروژه
**J.A.R.V.I.S** یک سیستم هوش مصنوعی دسکتاپ بر پایه ویندوز ۱۱ است که با هدف ادغام مدل‌های زبانی بزرگ (LLMs) با کارکردهای بومی سیستم‌عامل (Native OS Calls) طراحی شده است. 

این پروژه با بهره‌گیری از معماری **High-Availability Hybrid Engine**، پایداری پاسخ‌گویی را به بالاترین سطح می‌رساند: پردازش‌های سریع زبانی بر بستر **Groq Cloud** و مدل پرقدرت دوزبانه `qwen/qwen3.8-27b` انجام می‌گیرند و در صورت قطعی اینترنت، با مکانیزم خودکار **Failover** پردازش روی هسته لوکال **Ollama** منتقل می‌گردد. همچنین با استفاده از خط لوله‌های پیشرفته STT و TTS مایکروسافت، تعامل کلامی پیوسته و طبیعی بین انسان و رایانه فراهم شده است.

---

## 🚀 قابلیت‌های برجسته (Key Features)

### ۱. معماری لایه‌ای با تأخیر نزدیک به صفر (Low-Latency Layered Routing)
درخواست‌های کاربر به طور مستقیم به مدل هوش مصنوعی ارسال نمی‌شوند؛ بلکه ابتدا در دو لایه فیلتر سبک و بومی سیستم ارزیابی می‌گردند تا سرعت واکنش در بالاترین سطح ممکن باشد:
1. **Hardware Telemetry Check:** پاسخ‌دهی به وضعیت پردازنده، رم و باتری در کمتر از ۵ میلی‌ثانیه.
2. **Deterministic OS Commands:** تطبیق دقیق و رگولار الگوهای باز کردن نرم‌افزارها و سایت‌ها.
3. **LLM Engine Query:** در صورتی که درخواست کاربر نیاز به تفکر تحلیلی و گفتگو داشته باشد.

### ۲. پایداری هوش مصنوعی با معماری Failover
- **مغز اصلی ابری:** مدل چندزبانه `qwen/qwen3.8-27b` روی سرورهای پردازش موازی LPU Groq با سرعت تولید تا ۳۰۰ توکن بر ثانیه.
- **مغز پشتیبان محلی:** اجرای مدل `qwen2.5:1.5b` روی Ollama بدون نیاز به اینترنت.

### ۳. شنیدار صوتی تطبیق‌پذیر (Adaptive Voice Activity Detection)
- استفاده از آستانه سکوت تطبیقی (`pause_threshold = 1.8s`) برای جلوگیری از قطع شدن زودهنگام در حین فکر کردن کاربر.
- مانیتورینگ نویز محیط به صورت داینامیک قبل از شروع ضبط.
- تفکیک و پشتیبانی هوشمندانه از دو زبان انگلیسی و فارسی.

### ۴. گفتار صوتی دوزبانه طبیعی (Neural TTS)
- ادغام مستقیم با سرورهای هوش مصنوعی صوتی Azure/Edge مایکروسافت.
- تشخیص زبان پاسخ و تغییر بلادرنگ کاراکتر صوتی:
  - زبان فارسی: صداپیشه نیورال `fa-IR-DilaraNeural`
  - زبان انگلیسی: صداپیشه نیورال `en-US-JennyNeural`

### ۵. حافظه تعاملی کوتاه‌مدت (Context-Aware Memory)
- مدیریت پنجره مکالمه به کمک ساختار داده‌ای `deque` با مکانیزم چرخش خودکار (Rolling History).
- پشتیبانی از ضمیرها، ارجاعات ضمنی و دنبال کردن تا ۱۰ پیام آخر بدون پر شدن سقف کانتکست یا اتلاف حافظه.

### ۶. مانیتورینگ منابع و کنترل بومی سیستم
- استخراج لحظه‌ای متریک‌های هسته‌های CPU، درصد مصرف RAM، فضای خالی درایو C، باتری و اسکن پراستفاده‌ترین پروسس‌های سیستم‌عامل به کمک `psutil`.

---

## 🏛 معماری سیستم و جریان داده (Architecture & Data Flow)
```mermaid
flowchart TD
User([ورودی کاربر: صدا یا متن]) --> InputDecision{نوع ورودی?}
InputDecision -->|صوتی| Mic[میکروفون: stt_engine]
Mic --> GoogleSTT[تبدیل صدا به متن - VAD 1.8s]
GoogleSTT --> RawText[متن ورودی]
InputDecision -->|متنی| RawText

RawText --> Dispatcher{تصمیم‌گیرنده دستورات در gui.py}

Dispatcher -->|۱. کلمات مانیتورینگ؟| Monitor[system_monitor.py]
Monitor --> psutil[تحلیل سخت‌افزار با psutil] --> Result[تولید پاسخ متنی]

Dispatcher -->|۲. دستور اجرای برنامه/وب؟| Controller[system_controller.py]
Controller --> NativeCall[اجرا با os.startfile / webbrowser] --> Result

Dispatcher -->|۳. سؤال گفتگویی و عمومی| LLM[llm_engine.py]
LLM --> ContextMemory[بررسی تاریخچه چت deque]
ContextMemory --> GroqCheck{ارتباط با Groq API?}
GroqCheck -->|موفق| GroqLPU[Groq Cloud: qwen3.8-27b] --> Result
GroqCheck -->|عدم دسترسی/خطا| OllamaLocal[Ollama Local: qwen2.5:1.5b] --> Result

Result --> GUI[نمایش در چت CustomTkinter]
Result --> TTS[tts_engine.py: انتخاب صدا بر اساس زبان]
TTS --> PyGame[پخش صوتی با pygame]
