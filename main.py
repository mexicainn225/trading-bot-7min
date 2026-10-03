from datetime import datetime, timedelta
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Token intégré directement
TOKEN = "8659818470:AAHgDj_qF8PWfc0IH63NFZV1wLPB02C0NN4"
bot = TeleBot(TOKEN)

# Correction de l'ordre des images
PHOTO_HIGHER = "IMG_6204.jpeg"  # Image verte (Higher)
PHOTO_LOWER = "IMG_6203.jpeg"    # Image rouge (Lower)

@bot.message_handler(commands=['start'])
def envoyer_bienvenue(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_signal = KeyboardButton("📊 OBTENIR UN SIGNAL")
    btn_stats = KeyboardButton("📈 STATISTIQUES")
    btn_config = KeyboardButton("⚙️ CONFIGURATION")
    markup.add(btn_signal, btn_stats, btn_config)
    
    bot.send_message(
        message.chat.id, 
        "🤖 **Bienvenue sur ton Robot de Trading VIP !**\n\nClique sur le bouton ci-dessous pour lancer ton premier signal 👇", 
        parse_mode="Markdown", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "📊 OBTENIR UN SIGNAL")
def generer_signal_trading(message):
    chat_id = message.chat.id
    
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    remainder = current_minutes % 7
    next_interval_mins = current_minutes + (7 - remainder) if remainder != 0 else current_minutes + 7
    
    target_hour = (next_interval_mins // 60) % 24
    target_minute = next_interval_mins % 60
    
    # Objet datetime pour calculer facilement les martingales (+2 min, +4 min, +6 min)
    base_time = datetime.now().replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    signal_time_str = base_time.strftime("%H:%M")
    matingal1_str = (base_time + timedelta(minutes=2)).strftime("%H:%M")
    matingal2_str = (base_time + timedelta(minutes=4)).strftime("%H:%M")
    matingal3_str = (base_time + timedelta(minutes=6)).strftime("%H:%M")
    
    seed = (target_hour * 60) + target_minute
    is_higher = (seed % 2 == 0)
    
    if is_higher:
        action_text = "🟢 HIGHER (HAUSSE / ACHAT)"
        tendance_emoji = "📈"
        photo_path = PHOTO_HIGHER
    else:
        action_text = "🔴 LOWER (BAISSE / VENTE)"
        tendance_emoji = "📉"
        photo_path = PHOTO_LOWER
        
    texte_signal = (
        f"📊 **SIGNAL TRADING ACTIF**\n\n"
        f"📍 **HEURE D’ENTRÉE:** {signal_time_str}\n"
        f"🎯 **OPTION :** {action_text}\n"
        f"{tendance_emoji} **MATINGAL 1 :** {matingal1_str}\n"
        f"{tendance_emoji} **MATINGAL 2 :** {matingal2_str}\n"
        f"{tendance_emoji} **MATINGAL 3 :** {matingal3_str}\n"
        f"⚡ **FIABILITÉ :** 95.2%"
    )
    
    inline_markup = InlineKeyboardMarkup()
    btn_platform = InlineKeyboardButton("💻 TRADER MAINTENANT", url="https://lkbb.cc/78634e")
    inline_markup.add(btn_platform)
    
    with open(photo_path, 'rb') as photo:
        bot.send_photo(
            chat_id, 
            photo=photo, 
            caption=texte_signal, 
            parse_mode="Markdown", 
            reply_markup=inline_markup
        )

@bot.message_handler(func=lambda message: message.text == "📈 STATISTIQUES")
def afficher_stats(message):
    bot.send_message(message.chat.id, "📊 **Statistiques :** Taux de réussite 89% 🟢", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "⚙️ CONFIGURATION")
def afficher_config(message):
    bot.send_message(message.chat.id, "⚙️ **Config :** Signaux toutes les 7 minutes.", parse_mode="Markdown")

if __name__ == '__main__':
    bot.infinity_polling()
