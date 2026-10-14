import asyncio
import edge_tts
import pygame
import os
import time

# صدای خانم دلارا (fa-IR-DilaraNeural) یا آقا فرید (fa-IR-FaridNeural)
VOICE = "fa-IR-DilaraNeural"
OUTPUT_FILE = "test_voice.mp3"


async def speak_persian(text: str):
    print(f"🎙️ در حال تولید گفتار: '{text}' ...")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT_FILE)

    # پخش با pygame بدون مسدود کردن خروجی
    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    print("✅ پخش با موفقیت انجام شد.")


if __name__ == "__main__":
    test_text = (
        "سلام مهران جان! من جارویس هستم، دستیار صوتی هوشمند شما. همه‌چیز عالی کار می‌کنه!"
    )
    asyncio.run(speak_persian(test_text))
