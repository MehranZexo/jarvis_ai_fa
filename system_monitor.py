import os
import re

import psutil


def _normalize_text(text: str) -> str:
    """یکسان‌سازی حروف فارسی و فاصله‌ها."""
    text = text.lower()
    text = text.replace("ي", "ی")
    text = text.replace("ك", "ک")
    text = text.replace("\u200c", " ")
    text = text.replace("\u200f", " ")

    return re.sub(r"\s+", " ", text).strip()


def _is_english(text: str) -> bool:
    """تشخیص ساده زبان انگلیسی."""
    return not re.search(r"[\u0600-\u06FF]", text)


def _format_gb(value: int) -> str:
    """تبدیل بایت به گیگابایت."""
    return f"{value / (1024**3):.1f} GB"


def _get_windows_drive() -> str:
    """پیدا کردن درایوی که ویندوز روی آن نصب است."""
    if os.name == "nt":
        system_drive = os.environ.get("SystemDrive", "C:")
        return system_drive + "\\"

    return "/"


def _cpu_report(english: bool) -> str:
    cpu_usage = psutil.cpu_percent(interval=0.7)
    cpu_count = psutil.cpu_count(logical=True)

    frequency_text = ""
    frequency = psutil.cpu_freq()

    if frequency and frequency.current:
        frequency_text = f" | {frequency.current / 1000:.2f} GHz"

    if english:
        return (
            f"CPU usage: {cpu_usage:.1f}%\nLogical cores: {cpu_count}{frequency_text}"
        )

    return (
        f"مصرف پردازنده: {cpu_usage:.1f}%\n"
        f"تعداد هسته‌های منطقی: {cpu_count}{frequency_text}"
    )


def _memory_report(english: bool) -> str:
    memory = psutil.virtual_memory()

    used = _format_gb(memory.used)
    total = _format_gb(memory.total)
    available = _format_gb(memory.available)

    if english:
        return (
            f"RAM usage: {memory.percent:.1f}%\n"
            f"Used: {used} of {total}\n"
            f"Available: {available}"
        )

    return (
        f"مصرف حافظه RAM: {memory.percent:.1f}%\n"
        f"مصرف‌شده: {used} از {total}\n"
        f"حافظه آزاد: {available}"
    )


def _disk_report(english: bool) -> str:
    drive = _get_windows_drive()
    disk = psutil.disk_usage(drive)

    used = _format_gb(disk.used)
    total = _format_gb(disk.total)
    free = _format_gb(disk.free)

    if english:
        return (
            f"System drive: {drive}\n"
            f"Disk usage: {disk.percent:.1f}%\n"
            f"Used: {used} of {total}\n"
            f"Free space: {free}"
        )

    return (
        f"درایو سیستم: {drive}\n"
        f"مصرف دیسک: {disk.percent:.1f}%\n"
        f"مصرف‌شده: {used} از {total}\n"
        f"فضای آزاد: {free}"
    )


def _battery_report(english: bool) -> str:
    battery = psutil.sensors_battery()

    if battery is None:
        if english:
            return (
                "Battery information is not available. This may be a desktop computer."
            )

        return "اطلاعات باتری در دسترس نیست. احتمالاً سیستم شما دسکتاپ است."

    percentage = battery.percent
    power_status = "Plugged in" if battery.power_plugged else "Running on battery"

    if battery.secsleft not in (
        psutil.POWER_TIME_UNLIMITED,
        psutil.POWER_TIME_UNKNOWN,
    ):
        minutes_left = battery.secsleft // 60

        if english:
            return (
                f"Battery level: {percentage:.1f}%\n"
                f"Status: {power_status}\n"
                f"Estimated remaining time: {minutes_left} minutes"
            )

        return (
            f"درصد باتری: {percentage:.1f}%\n"
            f"وضعیت: {power_status}\n"
            f"زمان تقریبی باقی‌مانده: {minutes_left} دقیقه"
        )

    if english:
        return f"Battery level: {percentage:.1f}%\nStatus: {power_status}"

    return f"درصد باتری: {percentage:.1f}%\nوضعیت: {power_status}"


def _process_report(english: bool) -> str:
    processes = []

    for process in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            info = process.info

            name = info.get("name") or "Unknown"
            pid = info.get("pid") or 0
            memory_percent = info.get("memory_percent") or 0.0

            processes.append(
                {
                    "name": name,
                    "pid": pid,
                    "memory_percent": memory_percent,
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(key=lambda item: item["memory_percent"], reverse=True)

    top_processes = processes[:5]

    if english:
        lines = ["Top processes by RAM usage:"]

        for item in top_processes:
            lines.append(
                f"- {item['name']} | "
                f"PID: {item['pid']} | "
                f"RAM: {item['memory_percent']:.1f}%"
            )

        return "\n".join(lines)

    lines = ["پردازه‌های پرمصرف بر اساس RAM:"]

    for item in top_processes:
        lines.append(
            f"- {item['name']} | "
            f"PID: {item['pid']} | "
            f"RAM: {item['memory_percent']:.1f}%"
        )

    return "\n".join(lines)


def _system_summary(english: bool) -> str:
    cpu_usage = psutil.cpu_percent(interval=0.7)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(_get_windows_drive())

    if english:
        return (
            "System status:\n"
            f"- CPU usage: {cpu_usage:.1f}%\n"
            f"- RAM usage: {memory.percent:.1f}%\n"
            f"- Disk usage: {disk.percent:.1f}%"
        )

    return (
        "وضعیت کلی سیستم:\n"
        f"- مصرف CPU: {cpu_usage:.1f}%\n"
        f"- مصرف RAM: {memory.percent:.1f}%\n"
        f"- مصرف دیسک: {disk.percent:.1f}%"
    )


def execute_monitor_command(user_text: str):
    """
    تشخیص و اجرای دستورات مربوط به وضعیت سخت‌افزار و سیستم‌عامل.

    اگر متن مربوط به مانیتورینگ سیستم نباشد، مقدار None برمی‌گرداند
    تا برنامه بتواند آن را به system_controller یا LLM ارسال کند.
    """
    text = _normalize_text(user_text)
    english = _is_english(user_text)

    process_keywords = [
        "پردازه",
        "پردازه ها",
        "پردازش",
        "پردازش ها",
        "برنامه های در حال اجرا",
        "برنامه‌های در حال اجرا",
        "برنامه سنگین",
        "برنامه های سنگین",
        "process",
        "processes",
        "running programs",
        "task manager",
        "top processes",
    ]

    battery_keywords = [
        "باتری",
        "شارژ لپ تاپ",
        "شارژ لپ‌تاپ",
        "وضعیت شارژ",
        "battery",
        "battery status",
        "battery level",
        "power status",
    ]

    cpu_keywords = [
        "cpu",
        "سی پی یو",
        "پردازنده",
        "پردازشگر",
        "مصرف پردازنده",
        "cpu usage",
        "processor usage",
    ]

    memory_keywords = [
        "ram",
        "رم",
        "حافظه رم",
        "مصرف رم",
        "memory usage",
        "ram usage",
        "system memory",
    ]

    disk_keywords = [
        "دیسک",
        "فضای دیسک",
        "هارد",
        "درایو",
        "فضای هارد",
        "storage",
        "disk",
        "disk usage",
        "hard drive",
        "c drive",
    ]

    summary_keywords = [
        "وضعیت سیستم",
        "وضعیت کلی سیستم",
        "منابع سیستم",
        "مشخصات سیستم",
        "سیستم چطوره",
        "بررسی سیستم",
        "system status",
        "system resources",
        "hardware status",
        "computer status",
        "pc status",
        "how is my computer",
    ]

    try:
        if any(keyword in text for keyword in process_keywords):
            return _process_report(english)

        if any(keyword in text for keyword in battery_keywords):
            return _battery_report(english)

        if any(keyword in text for keyword in cpu_keywords):
            return _cpu_report(english)

        if any(keyword in text for keyword in memory_keywords):
            return _memory_report(english)

        if any(keyword in text for keyword in disk_keywords):
            return _disk_report(english)

        if any(keyword in text for keyword in summary_keywords):
            return _system_summary(english)

    except Exception as error:
        if english:
            return f"Unable to read system information: {error}"

        return f"خواندن اطلاعات سیستم با خطا مواجه شد: {error}"

    return None
