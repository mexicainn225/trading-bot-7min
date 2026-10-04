from datetime import datetime, timedelta
import os
import random
from threading import Thread
from flask import Flask, render_template, request
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# Configuration Flask pour Render
app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get('TOKEN')
TON_ID_ADMIN = 5724620019  # Ton ID Admin

# Images sur ton dépôt GitHub
PHOTO_HIGHER = 'IMG_6204.jpeg'
PHOTO_LOWER = 'IMG_6203.jpeg'

# Fichier local pour stocker les IDs validés (remplace Supabase)
FICHIER_UTILISATEURS = 'utilisateurs_valides.txt'


def charger_utilisateurs_valides():
  if not os.path.exists(FICHIER_UTILISATEURS):
    return set()
  try:
    with open(FICHIER_UTILISATEURS, 'r') as f:
      return set(int(line.strip()) for line in f if line.strip().isdigit())
  except Exception:
    return set()


def sauvegarder_utilisateur_valide(user_id):
  users = charger_utilisateurs_valides()
  users.add(int(user_id))
  with open(FICHIER_UTILISATEURS, 'w') as f:
    for uid in users:
      f.write(f'{uid}\n')


def est_valide(user_id):
  if int(user_id) == int(TON_ID_ADMIN):
    return True
  users = charger_utilisateurs_valides()
  return int(user_id) in users


@app.route('/')
def home():
  return render_template('index.html')


# ==========================================
# GESTION DU BOT TELEGRAM AVEC RESTRICTION
# ==========================================
async def start(update, context):
  user_id = update.effective_user.id

  if est_valide(user_id):
    keyboard = [[KeyboardButton('📊 NEW SIGNAL'), KeyboardButton('📈 STATISTIQUES')]]
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

  # 1. Gestion du bouton NEW SIGNAL
  if message_text == '📊 NEW SIGNAL':
    if not est_valide(user_id):
      await update.message.reply_text(
          '⛔ **ACCÈS RESTREINT**\n\nTu dois d’abord envoyer ton ID 1win valide'
          ' pour débloquer les signaux.',
          parse_mode='Markdown',
      )
      return

    # --- CALCUL DU SIGNAL ---
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

    is_higher = random.choice([True, False])
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
        f'💱 **ACTIF :** AUD/CAD (OTC)\n'
        f'📍 **HEURE D’ENTRÉE:** {signal_time_str}\n'
        f'⏳ *Place ton trade a la minute juste!*\n\n'
        f'🎯 **OPTION :** {action_text}\n'
        f'{tendance_emoji} **MARTINGALE 1 :** {matingal1_str}\n'
        f'{tendance_emoji} **MARTINGALE 2 :** {matingal2_str}\n'
        f'{tendance_emoji} **MARTINGALE 3 :** {matingal3_str}\n'
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

  # 2. Gestion du bouton STATISTIQUES
  elif message_text == '📈 STATISTIQUES':
    if not est_valide(user_id):
      await update.message.reply_text('⛔ Accès restreint.')
      return
    await update.message.reply_text(
        '📊 **Statistiques :** Taux de réussite global 89% 🟢',
        parse_mode='Markdown',
    )
    return

  # 3. Si déjà validé
  if est_valide(user_id):
    keyboard = [[KeyboardButton('📊 NEW SIGNAL'), KeyboardButton('📈 STATISTIQUES')]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        '✅ Ton accès est déjà actif ! Utilise les boutons ci-dessous 👇',
        reply_markup=markup,
    )
    return

  # 4. Envoi de l'ID 1win à l'admin pour validation
  await update.message.reply_text(
      "ID reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅"
  )

  admin_keyboard = [
      [
          InlineKeyboardButton(
              '✅ Valider l\'accès', callback_data=f'val_{user_id}'
          ),
          InlineKeyboardButton('❌ Mauvais code', callback_data=f'err_{user_id}'),
      ]
  ]
  admin_markup = InlineKeyboardMarkup(admin_keyboard)

  await context.bot.send_message(
      chat_id=TON_ID_ADMIN,
      text=(
          f'🚨 **Nouvelle demande :**\n'
          f'👤 User ID: `{user_id}`\n'
          f'🆔 ID 1win: `{message_text}`'
      ),
      parse_mode='Markdown',
      reply_markup=admin_markup,
  )


# Gestion des clics admin
async def admin_callback(update, context):
  query = update.callback_query
  if update.effective_user.id != TON_ID_ADMIN:
    await query.answer('Accès refusé.', show_alert=True)
    return

  await query.answer()
  data = query.data

  if data.startswith('val_'):
    user_id_target = int(data.split('_')[1])
    sauvegarder_utilisateur_valide(user_id_target)

    keyboard = [[KeyboardButton('📊 NEW SIGNAL'), KeyboardButton('📈 STATISTIQUES')]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    try:
      await context.bot.send_message(
          chat_id=user_id_target,
          text=(
              '✅ Félicitations ! Ton ID a été validé. Tu peux maintenant'
              ' accéder aux signaux.'
          ),
          reply_markup=markup,
      )
    except Exception as e:
      print(f'Erreur envoi validation: {e}')

    await query.edit_message_text(
        text=query.message.text + '\n\n🟢 **STATUT : VALIDÉ & ACTIVÉ**',
        parse_mode='Markdown',
    )

  elif data.startswith('err_'):
    user_id_target = int(data.split('_')[1])
    try:
      await context.bot.send_message(
          chat_id=user_id_target,
          text='❌ Ce ID n’est pas inscrit avec le code COK225.',
      )
    except Exception as e:
      print(f'Erreur envoi erreur: {e}')

    await query.edit_message_text(
        text=query.message.text + '\n\n🔴 **STATUT : REFUSÉ**',
        parse_mode='Markdown',
    )


def run_web():
  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
  Thread(target=run_web).start()

  bot_app = ApplicationBuilder().token(TOKEN).build()
  bot_app.add_handler(CommandHandler('start', start))
  bot_app.add_handler(CallbackQueryHandler(admin_callback))
  bot_app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )
  bot_app.run_polling()
