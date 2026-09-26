import os
import subprocess
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 MUSTY VIDEO COMPRESSOR\n\n"
        "Tura video kawai. Zan rage girmansa sannan in dawo maka da compressed video."
    )


async def compress_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.video:
        return

    status = await message.reply_text("⏳ Ana sauke video...")

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "input.mp4"
        out = Path(tmp) / "compressed.mp4"

        tg_file = await message.video.get_file()
        await tg_file.download_to_drive(custom_path=str(src))

        await status.edit_text("⚙️ Ana compressing video...")

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "28",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            str(out),
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0 or not out.exists():
            await status.edit_text(
                "❌ An samu matsala wajen compressing video."
            )
            return

        await status.edit_text("📤 Ana tura compressed video...")

        with out.open("rb") as video:
            await message.reply_video(
                video=video,
                caption="✅ An gama compression — MUSTY VIDEO COMPRESSOR",
            )

        await status.delete()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Tura video kawai. Bot zai compress shi sannan ya dawo maka da shi."
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(filters.VIDEO, compress_video)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
