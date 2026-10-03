from datetime import datetime, timedelta
import os
import random
from threading import Thread
from flask import Flask, render_template, request
from supabase import Client, create_client
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# Configuration Flask pour Render
app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get('TOKEN')
TON_ID_ADMIN = 5724620019  # ID Admin configuré

# Informations Supabase intégrées directement
SUPABASE_URL = 'https://uyruufvdezefffimcped.supabase.co/'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5cnV1ZnZkZXplZmZmaW1jcGVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNzkwMTAsImV4cCI6MjA5NzY1NTAxMH0.JNm1sOBUTvjl1m1OXmQVkOh4z5dFkDk-_qieJU1gVC8'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Images sur ton dépôt GitHub
PHOTO_HIGHER = 'IMG_6204.jpeg'  # Image verte (Higher)
PHOTO_LOWER = 'IMG_6203.jpeg'  # Image rouge (Lower)


# ==========================================
# FONCTIONS SUPABASE DIRECTES
# ==========================================
def est_valide(user_id):
  try:
    response = (
        supabase.table('users').select('*').eq('user_id', str(user_id)).execute()
    )
    data = response.data
    if data and len(data) > 0:
      user_info = data[0]
      if user_info.get('is_vip') == True or user_info.get('status') == 'active':
        return True
    return False
  except Exception as e:
    print(f'Erreur Supabase est_valide: {e}')
    return False


def ajouter_utilisateur(user_id, id_1win):
  try:
    supabase.table('users').upsert({
        'user_id': str(user_id),
        'id_1win': str(id_1win),
        'status': 'pending',
        'is_vip': False,
    }).execute()
  except Exception as e:
    print(f'Erreur Supabase ajouter_utilisateur: {e}')


def valider_utilisateur(user_id):
  try:
    supabase.table('users').update(
        {'status': 'active', 'is_vip': True}
    ).eq('user_id', str(user_id)).execute()
  except Exception as e:
    print(f'Erreur Supabase valider_utilisateur: {e}')


@app.route('/')
def home():
  return render_template('index.html')


# ==========================================
# GESTION DU BOT TELEGRAM
# ==========================================
async def start(update, context):
  user_id = update.effective_user.id

  if est_valide(user_id):
    keyboard = [[KeyboardButton('📊 OBTENIR UN SIGNAL'), KeyboardButton('📈 STATISTIQUES')]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        '🤖 **Re-bonjour ! Ton accès VIP est actif.**\n\nClique sur le bouton'
        ' ci-dessous pour obtenir ton signal 👇',
        parse_mode='Markdown',
        reply_markup=markup,
    )
  else:
    message = (
        'Bienvenue sur le bot 1win 🚀\n\n'
        'Pour débloquer tes accès, suis ces étapes :\n\n'
        '1️⃣ Inscris-toi ici : https://lkbb.cc/78634e\n'
        '2️⃣ Utilise le code promo : COK225\n'
        '3️⃣ Effectue une recharge sur ton compte.\n'
        '4️⃣ Envoie ton ID 1win ici pour validation.'
    )
    await update.message.reply_text(message)


async def handle_message(update, context):
  user_id = update.effective_user.id
  message_text = update.message.text

  if message_text == '📊 OBTENIR UN SIGNAL':
    if not est_valide(user_id):
      await update.message.reply_text(
          '⛔ **ACCÈS RESTREINT**\n\nTu dois d’abord envoyer ton ID 1win valide'
          ' pour débloquer les signaux.',
          parse_mode='Markdown',
      )
      return

    # --- CALCUL DU SIGNAL (Toutes les 7 min + Martingales) ---
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    remainder = current_minutes % 7
    next_interval_mins = (
        current_minutes + (7 - remainder)
        if remainder != 0
        else current_minutes + 7
    )

    target_hour = (next_interval_mins // 60) % 24
    target_minute = next_interval_mins % 60

    base_time = datetime.now().replace(
        hour=target_hour, minute=target_minute, second=0, microsecond=0
    )

    signal_time_str = base_time.strftime('%H:%M')
    matingal1_str = (base_time + timedelta(minutes=2)).strftime('%H:%M')
    matingal2_str = (base_time + timedelta(minutes=4)).strftime('%H:%M')
    matingal3_str = (base_time + timedelta(minutes=6)).strftime('%H:%M')

    seed = (target_hour * 60) + target_minute
    is_higher = seed % 2 == 0

    fiabilite = round(random.uniform(85.0, 99.9), 1)

    if is_higher:
      action_text = '🟢 HIGHER (HAUSSE / ACHAT)'
      tendance_emoji = '📈'
      photo_path = PHOTO_HIGHER
    else:
      action_text = '🔴 LOWER (BAISSE / VENTE)'
      tendance_emoji = '📉'
      photo_path = PHOTO_LOWER

    texte_signal = (
        f'📊 **SIGNAL TRADING ACTIF**\n\n'
        f'📍 **HEURE D’ENTRÉE:** {signal_time_str}\n'
        f'🎯 **OPTION :** {action_text}\n'
        f'{tendance_emoji} **MATINGAL 1 :** {matingal1_str}\n'
        f'{tendance_emoji} **MATINGAL 2 :** {matingal2_str}\n'
        f'{tendance_emoji} **MATINGAL 3 :** {matingal3_str}\n'
        f'⚡ **FIABILITÉ :** {fiabilite}%'
    )

    inline_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            '💻 TRADER MAINTENANT', url='https://lkbb.cc/78634e'
        )
    ]])

    with open(photo_path, 'rb') as photo:
      await context.bot.send_photo(
          chat_id=update.effective_chat.id,
          photo=photo,
          caption=texte_signal,
          parse_mode='Markdown',
          reply_markup=inline_markup,
      )
    return

  elif message_text == '📈 STATISTIQUES':
    if not est_valide(user_id):
      await update.message.reply_text('⛔ Accès restreint.')
      return
    await update.message.reply_text(
        '📊 **Statistiques :** Taux de réussite global 89% 🟢',
        parse_mode='Markdown',
    )
    return

  # Enregistrement de l'ID 1win dans Supabase
  ajouter_utilisateur(user_id, message_text)

  await update.message.reply_text(
      "ID reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅"
  )

  # Alerte Admin
  await context.bot.send_message(
      chat_id=TON_ID_ADMIN,
      text=(
          f'🚨 Nouvelle demande :\nUser ID: {user_id}\nID 1win:'
          f' {message_text}\n\nTape: /valider {user_id}'
      ),
  )


async def valider(update, context):
  if update.effective_user.id != TON_ID_ADMIN:
    return

  if context.args:
    user_id_a_valider = int(context.args[0])
    valider_utilisateur(user_id_a_valider)

    keyboard = [[KeyboardButton('📊 OBTENIR UN SIGNAL'), KeyboardButton('📈 STATISTIQUES')]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=user_id_a_valider,
        text=(
            '✅ Félicitations ! Ton ID a été validé. Tu peux maintenant'
            ' accéder aux signaux.'
        ),
        reply_markup=markup,
    )
    await update.message.reply_text(
        f'Utilisateur {user_id_a_valider} validé avec succès !'
    )


def run_web():
  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
  Thread(target=run_web).start()

  bot_app = ApplicationBuilder().token(TOKEN).build()
  bot_app.add_handler(CommandHandler('start', start))
  bot_app.add_handler(CommandHandler('valider', valider))
  bot_app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )
  bot_app.run_polling()
