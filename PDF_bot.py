import os
import telebot
from telebot import types
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

TOKEN = "7873155083:AAETF8a_BBiglQ8Kkj5-AgWQh4g7nYiZQUE"  # <-- bu yerga tokeningizni yozing
bot = telebot.TeleBot(TOKEN)

# PDF saqlanadigan vaqtinchalik papka
if not os.path.exists("temp"):
    os.mkdir("temp")

# --- FUNKSIYA: matndan PDF yaratish ---
def text_to_pdf(text, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    text_obj = c.beginText(40, 800)
    for line in text.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.save()

# --- FUNKSIYA: DOCX dan PDF yaratish ---
def docx_to_pdf(docx_path, pdf_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    text_to_pdf(text, pdf_path)

# --- FUNKSIYA: rasmni PDF ga o‘tkazish ---
def image_to_pdf(image_path, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    image = ImageReader(image_path)
    c.drawImage(image, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=True)
    c.save()

# --- START komandasi ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📝 Matnni PDF qilish")
    btn2 = types.KeyboardButton("🖼️ Rasmni PDF qilish")
    btn3 = types.KeyboardButton("📄 Word yoki TXT faylni PDF qilish")
    markup.add(btn1, btn2, btn3)
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum! 👋\nQaysi turdagi ma’lumotni PDF formatga o‘tkazmoqchisiz?",
        reply_markup=markup
    )

# --- Tugma tanlanganda javob ---
@bot.message_handler(func=lambda message: message.text in [
    "📝 Matnni PDF qilish",
    "🖼️ Rasmni PDF qilish",
    "📄 Word yoki TXT faylni PDF qilish"
])
def ask_for_input(message):
    if message.text == "📝 Matnni PDF qilish":
        bot.send_message(message.chat.id, "✏️ Matningizni yuboring.")
    elif message.text == "🖼️ Rasmni PDF qilish":
        bot.send_message(message.chat.id, "📷 Rasm yuboring (1 dona).")
    elif message.text == "📄 Word yoki TXT faylni PDF qilish":
        bot.send_message(message.chat.id, "📎 Word (.docx) yoki TXT fayl yuboring.")

# --- Rasm qabul qilish ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)

    img_path = f"temp/{message.chat.id}.jpg"
    pdf_path = f"temp/{message.chat.id}.pdf"

    with open(img_path, 'wb') as f:
        f.write(downloaded)

    image_to_pdf(img_path, pdf_path)
    with open(pdf_path, 'rb') as f:
        bot.send_document(message.chat.id, f, caption="📄 Rasm PDF formatda tayyor!")

    os.remove(img_path)
    os.remove(pdf_path)

# --- Word yoki TXT fayl qabul qilish ---
@bot.message_handler(content_types=['document'])
def handle_doc(message):
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name
    file_ext = file_name.lower().split('.')[-1]

    downloaded = bot.download_file(file_info.file_path)

    doc_path = f"temp/{file_name}"
    pdf_name = file_name.rsplit('.', 1)[0] + ".pdf"
    pdf_path = f"temp/{pdf_name}"

    with open(doc_path, 'wb') as f:
        f.write(downloaded)

    if file_ext == "docx":
        docx_to_pdf(doc_path, pdf_path)
    elif file_ext == "txt":
        with open(doc_path, 'r', encoding='utf-8') as f:
            text = f.read()
        text_to_pdf(text, pdf_path)
    else:
        bot.reply_to(message, "❌ Faqat .docx yoki .txt fayllarni qabul qilaman.")
        os.remove(doc_path)
        return

    with open(pdf_path, 'rb') as f:
        bot.send_document(message.chat.id, f, caption=f"✅ {pdf_name} PDF formatda tayyor!")

    os.remove(doc_path)
    os.remove(pdf_path)

# --- Matnni PDF qilish ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    # "/start" komandasini qayta PDF qilmaslik
    if message.text.startswith("/start"):
        return

    text = message.text.strip()
    if not text:
        bot.reply_to(message, "❗ Iltimos, matn kiriting.")
        return

    pdf_name = "matn.pdf"
    pdf_path = f"temp/{pdf_name}"
    text_to_pdf(text, pdf_path)

    with open(pdf_path, 'rb') as f:
        bot.send_document(message.chat.id, f, caption="✅ Matningiz PDF formatda tayyor!")

    os.remove(pdf_path)

# --- Botni ishga tushirish ---
print("🤖 Bot ishga tushdi...")
bot.infinity_polling()
