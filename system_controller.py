import os
import subprocess
import webbrowser
import re

# نگاشت برنامه‌ها به دستورات اجرایی ویندوز
# کلیدها: لیست کلمات کلیدی مختلف برای هر برنامه
PROGRAMS_MAP = {
    ("notepad", "نوت پد", "نوتپد", "نت پد", "نتپد", "یادداشت"): "notepad.exe",
    ("calc", "calculator", "ماشین حساب", "حساب"): "calc.exe",
    ("chrome", "کروم", "گوگل کروم"): "chrome",
    ("edge", "ایج", "مایکروسافت ایج"): "msedge",
    ("cmd", "ترمینال", "کامند پرامپت", "سی ام دی"): "cmd.exe",
    ("task manager", "تسک منیجر", "مدیریت وظایف"): "taskmgr.exe",
    ("explorer", "فایل منیجر", "مای کامپیوتر", "پوشه"): "explorer.exe",
    ("paint", "نقاشی", "پینت"): "mspaint.exe",
}

# نگاشت وب‌سایت‌ها
WEBSITES_MAP = {
    ("google", "گوگل"): "https://www.google.com",
    ("youtube", "یوتیوب"): "https://www.youtube.com",
    ("github", "گیت هاب", "گیت‌هاب"): "https://www.github.com",
    ("digikala", "دیجی کالا", "دیجیکالا"): "https://www.digikala.com",
}


def normalize_text(text: str) -> str:
    """یکسان‌سازی حروف فارسی، حذف نیم‌فاصله‌ها و کاراکترهای اضافه"""
    if not text:
        return ""
    text = text.lower()
    # تبدیل ی و ک عربی به فارسی
    text = text.replace("ي", "ی").replace("ك", "ک")
    # حذف نیم‌فاصله
    text = text.replace("\u200c", " ").replace("\u200b", " ")
    # حذف اعراب و علائم نگارشی
    text = re.sub(r"[^\w\s]", " ", text)
    # یکی کردن فاصله‌های متوالی
    text = re.sub(r"\s+", " ", text).strip()
    return text


def execute_app_command(raw_text: str) -> str:
    """
    بررسی می‌کند آیا دستور مربوط به باز کردن نرم‌افزار یا سایتی هست یا نه.
    در صورت اجرا، پیام موفقیت برمی‌گرداند؛ در غیر این صورت None.
    """
    text = normalize_text(raw_text)

    # کلمات کلیدی مربوط به قصد «باز کردن»
    trigger_words = [
        "باز کن",
        "بازکن",
        "اجرا کن",
        "اجراکن",
        "open",
        "launch",
        "run",
        "برو به",
        "برو توی",
    ]

    is_open_intent = any(trigger in text for trigger in trigger_words)

    # ۱. بررسی وب‌سایت‌ها
    for aliases, url in WEBSITES_MAP.items():
        for alias in aliases:
            clean_alias = normalize_text(alias)
            # اگر اسم سایت گفته شده بود و کلمه باز کردن هم بود (یا صرفاً اسم سایت معروف گفته شد)
            if clean_alias in text and (
                is_open_intent or f"برو به {clean_alias}" in text
            ):
                webbrowser.open(url)
                return f"در حال باز کردن {alias.capitalize()} در مرورگر شما هستم."

    # ۲. بررسی برنامه‌های ویندوز
    for aliases, target in PROGRAMS_MAP.items():
        for alias in aliases:
            clean_alias = normalize_text(alias)
            # اگر اسم برنامه در متن بود
            if clean_alias in text:
                try:
                    # روش اول: استفاده از startfile (بهترین روش در ویندوز ۱۱)
                    os.startfile(target)
                except Exception:
                    # روش فال‌بک: اجرای دستور در بک‌گراند
                    subprocess.Popen(target, shell=True)

                return f"نرم‌افزار {alias.capitalize()} با موفقیت باز شد."

    return None


if __name__ == "__main__":
    # تست دستی چند حالت
    test_cases = [
        "نت پد را باز کن",
        "لطفا نوت‌پد رو بازکن",
        "open calculator please",
        "ماشین حساب باز کن",
        "یوتیوب را باز کن",
    ]
    for tc in test_cases:
        print(f"تست: '{tc}' -> پاسخ: {execute_app_command(tc)}")
