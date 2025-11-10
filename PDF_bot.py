import os
from flask import Flask
import threading
import telebot
from fpdf import FPDF
from docx import Document

# --- Telegram token ---
TOKEN = os.getenv("BOT_TOKEN")  # Render Environment Variables dan oling
bot = telebot.TeleBot(TOKEN)

# --- Flask server ---
app = Flask(__name__)

@app.route('/')
def index():
    return "PDF_Milliy_bot ishlamoqda ✅"

# --- PDF yaratish funksiyalari ---
def create_pdf_from_text(text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)

def read_word(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

# --- Telegram bot handlers ---
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "👋 Salom! Menga matn, Word (.docx) yoki rasm yuboring — men PDF ga aylantirib qaytaraman 📄")

@bot.message_handler(content_types=['text'])
def text_to_pdf(message):
    output_path = "text_result.pdf"
    create_pdf_from_text(message.text, output_path)
    with open(output_path, 'rb') as f:
        bot.send_document(message.chat.id, f, caption="✅ Matningiz PDF ga o‘tkazildi!")
    os.remove(output_path)

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    local_path = f"./{file_name}"
    with open(local_path, "wb") as f:
        f.write(downloaded_file)

    if file_name.endswith(".docx"):
        text = read_word(local_path)
        output_pdf = file_name.replace(".docx", ".pdf")
        create_pdf_from_text(text, output_pdf)
        with open(output_pdf, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"✅ {file_name} PDF ga o‘tkazildi!")
        os.remove(output_pdf)
    else:
        bot.reply_to(message, "❌ Faqat .docx fayllarni qabul qilaman 📄")
    os.remove(local_path)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    img_path = f"{message.chat.id}.jpg"
    pdf_path = f"{message.chat.id}.pdf"
    with open(img_path, "wb") as f:
        f.write(downloaded_file)

    pdf = FPDF()
    pdf.add_page()
    pdf.image(img_path, x=10, y=10, w=190)
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption="🖼 Rasm PDF ga aylantirildi!")

    os.remove(img_path)
    os.remove(pdf_path)

# --- Bot pollingni alohida thread-da ishga tushirish ---
def start_bot():
    bot.infinity_polling(timeout=60, long_polling_timeout=30)

threading.Thread(target=start_bot).start()

# --- Flask server porti (Render uchun) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
