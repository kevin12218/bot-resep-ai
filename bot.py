import os
import telebot
from google import genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()

# --- BLOK DEBUGGING TINGKAT DEWA ---
print("=== CEK VARIABEL DARI RAILWAY ===")
daftar_kunci = list(os.environ.keys())
print(f"Apakah ada kata GEMINI di Railway? : {any('GEMINI' in k for k in daftar_kunci)}")
print(f"Apakah ada kata TELEGRAM di Railway? : {any('TELEGRAM' in k for k in daftar_kunci)}")
print("=================================")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ MESIN BERHENTI: Railway benar-benar tidak mengirimkan GEMINI_API_KEY ke Python!")
    exit() # Mematikan sistem dengan aman tanpa pesan error panjang
else:
    print("✅ GEMINI_API_KEY berhasil ditangkap!")

if not TELEGRAM_BOT_TOKEN:
    print("❌ MESIN BERHENTI: Railway tidak mengirimkan TELEGRAM_BOT_TOKEN!")
    exit()

# Setup AI & Bot
client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ... (biarkan sisa kode di bawahnya tetap sama seperti sebelumnya) ...

# Ini yang terjadi kalau Anda ketik /start di Telegram
@bot.message_handler(commands=['start'])
def send_welcome(message):
    teks_sapaan = (
        "🍳 *Halo! Saya AI Chef pribadi Anda.* 🍳\n\n"
        "Kirimkan 1 pesan sekaligus yang berisi:\n"
        "1. Bahan yang ada di kulkas\n"
        "2. Tipe masakan (Sehat / Normal)\n"
        "3. Target minimal protein\n\n"
        "*Contoh ketik di chat:*\n"
        "Ayam, telur, brokoli. Mau yang sehat, minimal protein 40g ya."
    )
    bot.reply_to(message, teks_sapaan, parse_mode="Markdown")

# Ini yang terjadi kalau Anda membalas chat ke bot
@bot.message_handler(func=lambda message: True)
def handle_resep(message):
    # Memberikan notifikasi bahwa AI sedang memproses
    msg_loading = bot.reply_to(message, "⏳ *AI Chef sedang meracik resep untuk Anda...*", parse_mode="Markdown")
    
    user_input = message.text
    
    # Instruksi pintar ke AI
    prompt = f"""
    Pengguna meminta resep dengan detail pesan berikut: "{user_input}"
    
    Tugas Anda:
    1. Analisa bahan dan preferensi (sehat/normal) dari pesan pengguna.
    2. CEK TARGET PROTEIN: Jika pengguna menyebutkan angka target protein, modifikasi takaran bahan agar mencapai target tersebut. 
    3. Jika pengguna TIDAK menyebutkan target protein, buatkan porsi normal saja (1-2 porsi).
    4. Gunakan bahan yang disebutkan, ditambah bumbu dasar dapur standar.
    
    Format jawaban WAJIB persis seperti ini:
    
    NAMA MASAKAN: [Berikan nama yang menarik]
    TINGKAT KESULITAN: [MUDAH / SEDANG / SULIT] (Beri alasan singkat)
    CATATAN PROTEIN: [Jika ada target: "Tercapai (X gram)" / Jika tidak ada target: "Porsi standar tanpa target spesifik"]
    
    BAHAN & BUMBU:
    - [List bahan dan takarannya]
    
    CARA MEMBUAT:
    1. [Langkah 1]
    2. [Langkah 2]
    
    INFO NUTRISI (Estimasi per porsi):
    - Kalori: [X] kcal
    - Protein: [X] gram
    """
    
    try:
        # Meminta jawaban dari Gemini AI
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        # Menghapus pesan "sedang meracik" dan menggantinya dengan resep
        bot.delete_message(chat_id=message.chat.id, message_id=msg_loading.message_id)
        bot.reply_to(message, response.text.strip())
        
    except Exception as e:
        bot.reply_to(message, f"❌ Maaf, sistem AI sedang error: {e}")

# Perintah agar bot selalu hidup dan siap membalas chat
print("Bot Resep sudah menyala! Silakan buka aplikasi Telegram Anda dan chat bot-nya.")
bot.polling(none_stop=True)

print("Mancing Railway")
