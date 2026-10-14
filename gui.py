import sys
import threading
import customtkinter as ctk
from llm_engine import ask_llm
from tts_engine import speak_text
from stt_engine import listen_microphone
from system_controller import execute_app_command
from system_monitor import execute_monitor_command


# تنظیم تم
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class JarvisUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("J.A.R.V.I.S - دستیار صوتی دوزبانه")
        self.geometry("640x740")
        self.minsize(520, 620)
        self.configure(fg_color="#0F111A")

        # نوار وضعیت بالایی
        self.header_frame = ctk.CTkFrame(self, fg_color="#1A1D2E", corner_radius=12)
        self.header_frame.pack(fill="x", padx=16, pady=(16, 8))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="⚡ J.A.R.V.I.S  A.I",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#00D2FF",
        )
        self.title_label.pack(side="left", padx=16, pady=12)

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="آماده به خدمت 🟢",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#4ECCA3",
        )
        self.status_label.pack(side="right", padx=16, pady=12)

        # پنجره چت
        self.chat_box = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#141724",
            text_color="#E0E6ED",
            corner_radius=12,
        )
        self.chat_box.pack(fill="both", expand=True, padx=16, pady=8)
        self.chat_box.configure(state="disabled")

        self.append_message(
            "جارویس",
            "درود مهران عزیز! سیستم صوتی، پایش سخت‌افزار و هوش مصنوعی فعال است.",
        )

        # نوار پایینی
        self.input_frame = ctk.CTkFrame(self, fg_color="#1A1D2E", corner_radius=12)
        self.input_frame.pack(fill="x", padx=16, pady=(8, 16))

        # دکمه میکروفون
        self.mic_btn = ctk.CTkButton(
            self.input_frame,
            text="🎙️",
            width=46,
            height=42,
            font=ctk.CTkFont(size=18),
            fg_color="#2A2F45",
            hover_color="#3D4463",
            corner_radius=8,
            command=self.start_voice_recording,
        )
        self.mic_btn.pack(side="left", padx=(10, 4), pady=10)

        # ورودی متنی
        self.user_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="دستور خود را بگویید یا بنویسید...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#0F111A",
            border_color="#2A2F45",
            corner_radius=8,
            height=42,
        )
        self.user_entry.pack(side="left", fill="x", expand=True, padx=6, pady=10)
        self.user_entry.bind("<Return>", lambda event: self.send_text_message())

        # دکمه ارسال
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="ارسال 🚀",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=85,
            height=42,
            fg_color="#007ACC",
            hover_color="#005A9E",
            corner_radius=8,
            command=self.send_text_message,
        )
        self.send_btn.pack(side="right", padx=(4, 10), pady=10)

    def append_message(self, sender: str, message: str):
        """نمایش پیام در پنجره چت."""
        self.chat_box.configure(state="normal")
        if sender == "شما":
            self.chat_box.insert("end", f"\n👤 {sender}:\n{message}\n", "user")
        else:
            self.chat_box.insert("end", f"\n🤖 {sender}:\n{message}\n", "bot")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def set_status(self, text: str, color: str = "#4ECCA3"):
        """تغییر متن و رنگ وضعیت برنامه."""
        self.status_label.configure(text=text, text_color=color)

    def send_text_message(self):
        """پردازش پیام متنی کاربر."""
        user_text = self.user_entry.get().strip()
        if not user_text:
            return

        self.user_entry.delete(0, "end")
        self._dispatch_processing(user_text)

    def start_voice_recording(self):
        """شروع دریافت صدای کاربر."""
        threading.Thread(target=self._voice_worker, daemon=True).start()

    def _voice_worker(self):
        """دریافت و پردازش ورودی صوتی."""
        self.set_status("در حال گوش دادن... 🎙️", "#00D2FF")
        self.mic_btn.configure(fg_color="#E02424")

        spoken_text = listen_microphone()

        self.mic_btn.configure(fg_color="#2A2F45")

        if spoken_text:
            self._dispatch_processing(spoken_text)
        else:
            self.set_status("صدایی دریافت نشد ⚠️", "#FFAA00")
            self.after(2000, lambda: self.set_status("آماده به خدمت 🟢", "#4ECCA3"))

    def _dispatch_processing(self, text: str):
        """ارسال متن برای پردازش در ترد جداگانه."""
        self.append_message("شما", text)
        self.set_status("در حال تفکر... ⏳", "#FFAA00")
        self.send_btn.configure(state="disabled")

        threading.Thread(
            target=self._process_and_speak, args=(text,), daemon=True
        ).start()

    def _process_and_speak(self, prompt: str):
        """
        پردازش لایه‌ای دستورات:
        1. پایش سخت‌افزار (psutil)
        2. کنترل برنامه‌های سیستم (system_controller)
        3. ارسال به مدل زبانی (Groq/Ollama)
        """
        try:
            # ۱. اولویت اول: آیا سوال در مورد سخت‌افزار یا منابع سیستم است؟
            monitor_reply = execute_monitor_command(prompt)

            if monitor_reply:
                reply = monitor_reply
            else:
                # ۲. اولویت دوم: آیا دستور باز کردن نرم‌افزار یا سایت است؟
                system_reply = execute_app_command(prompt)
                if system_reply:
                    reply = system_reply
                else:
                    # ۳. اولویت سوم: اگر هیچ‌کدام نبود، به هوش مصنوعی بفرست
                    reply = ask_llm(prompt)

            self.append_message("جارویس", reply)

            # خواندن صوتی خروجی
            self.set_status("در حال صحبت... 🔊", "#9D4EDD")
            speak_text(reply)

        except Exception as error:
            self.append_message("خطا", f"مشکل در پردازش: {error}")
        finally:
            self.set_status("آماده به خدمت 🟢", "#4ECCA3")
            self.send_btn.configure(state="normal")


if __name__ == "__main__":
    app = JarvisUI()
    app.mainloop()
