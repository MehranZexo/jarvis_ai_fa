import os
import re
import asyncio
import edge_tts
import pygame

# تعریف صداهای استاندارد مایکروسافت
VOICE_FA = "fa-IR-DilaraNeural"  # صدای فارسی فوق‌العاده طبیعی
VOICE_EN = "en-US-JennyNeural"  # صدای انگلیسی بسیار شفاف و حرفه‌ای
OUTPUT_AUDIO_FILE = "response.mp3"


def is_primarily_english(text: str) -> bool:
    """بررسی اینکه آیا متن عموماً انگلیسی است یا فارسی"""
    # حذف کاراکترهای علائم نگارشی و اعداد برای دقت در تشخیص زبان
    clean_text = re.sub(r"[0-9\s\W_]+", "", text)
    if not clean_text:
        return False

    # کاراکترهای الفبای فارسی و عربی (یونی‌کد 0600 تا 06FF)
    persian_chars = len(re.findall(r"[\u0600-\u06FF]", clean_text))
    # کاراکترهای الفبای انگلیسی
    english_chars = len(re.findall(r"[a-zA-Z]", clean_text))

    # اگر کاراکترهای انگلیسی از فارسی بیشتر بود، انگلیسی در نظر گرفته می‌شود
    return english_chars > persian_chars


async def _synthesize_speech(text: str, output_path: str):
    """تولید فایل صوتی با انتخاب خودکار وویس مناسب زبان متن"""
    if is_primarily_english(text):
        selected_voice = VOICE_EN
        print(f"[TTS] 🎙️ شناسایی زبان انگلیسی -> استفاده از {VOICE_EN}")
    else:
        selected_voice = VOICE_FA
        print(f"[TTS] 🎙️ شناسایی زبان فارسی -> استفاده از {VOICE_FA}")

    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(output_path)


def speak(text: str):
    """تبدیل متن به گفتار و پخش آن به صورت خودکار"""
    if not text.strip():
        return

    try:
        asyncio.run(_synthesize_speech(text, OUTPUT_AUDIO_FILE))

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(OUTPUT_AUDIO_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()

        if os.path.exists(OUTPUT_AUDIO_FILE):
            os.remove(OUTPUT_AUDIO_FILE)

    except Exception as e:
        print(f"[TTS Error] ❌ خطا در تولید یا پخش صدا: {e}")


# برای سازگاری با ایمپورت gui.py
speak_text = speak

if __name__ == "__main__":
    speak_text("Hello Mahsa! Testing bilingual speech engine.")
    speak("سلام مهسا جان، حالا من به هر دو زبان مسلط هستم.")
