import speech_recognition as sr


def listen_microphone() -> str:
    """
    میکروفون را باز می‌کند، نویز محیط را کالیبره می‌کند و تا زمانی که کاربر
    صحبت می‌کند گوش می‌دهد. با تشخیص ۲ ثانیه سکوت پیوسته، ضبط را پایان می‌دهد.
    """
    recognizer = sr.Recognizer()

    # 1. مدت سکوت پس از پایان صحبت برای اتمام ضبط (پیش‌فرض 0.8 بود، الان 1.8 ثانیه)
    recognizer.pause_threshold = 1.8

    # 2. زمان سکوت اضافه در انتهای صدا برای جلوگیری از بریده شدن حروف آخر کلمات
    recognizer.non_speaking_duration = 0.6

    # 3. آستانه انرژی داینامیک برای تطبیق با صدای محیط
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print("\n🎙️ در حال کالیبره کردن نویز محیط...")
            # بررسی 0.6 ثانیه اول برای فیلتر نویز پس‌زمینه
            recognizer.adjust_for_ambient_noise(source, duration=0.6)

            print("🟢 اکنون صحبت کنید (سیستم تا توقف کلام گوش می‌دهد)...")
            # timeout: حداکثر زمانی که منتظر شروع صحبت می‌ماند (اگر 7 ثانیه حرف نزدی قطع می‌شود)
            # phrase_time_limit: حداکثر طول یک جمله مستمر (مثلاً 25 ثانیه)
            audio = recognizer.listen(source, timeout=7.0, phrase_time_limit=25.0)

        print("⚡ در حال پردازش و تبدیل صدا به متن...")

        # اولویت با زبان فارسی است، در صورت عدم تشخیص مناسب انگلیسی بررسی می‌شود
        try:
            text = recognizer.recognize_google(audio, language="fa-IR")
            if text.strip():
                print(f"🗣️ گفتار تشخیص داده شده (فارسی): {text}")
                return text.strip()
        except sr.UnknownValueError:
            pass

        # تلاش مجدد با زبان انگلیسی
        try:
            text = recognizer.recognize_google(audio, language="en-US")
            if text.strip():
                print(f"🗣️ Detected Speech (English): {text}")
                return text.strip()
        except sr.UnknownValueError:
            pass

        print("⚠️ صدایی تشخیص داده نشد.")
        return ""

    except sr.WaitTimeoutError:
        print("⌛ کاربر صحبتی نکرد (Timeout).")
        return ""
    except Exception as e:
        print(f"❌ خطای STT: {e}")
        return ""


if __name__ == "__main__":
    print("تست میکروفون...")
    res = listen_microphone()
    print("نتیجه نهایی:", res)
