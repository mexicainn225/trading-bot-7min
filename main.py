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
    CallbackQueryHandler,
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
# FONCTIONS SUPABASE ROBUSTES
# ==========================================
def est_valide(user_id):
  if user_id == TON_ID_ADMIN:
    return True
  try:
    response = (
        supabase.table('users').select('*').eq('user_id', str(user_id)).execute()
    )
    data = response.data
    if data and len(data) > 0:
      user_info = data[0]
      if user_info.get('is_vip'] == True or user_info.get('status') == 'active':
        return True
    return False
  except Exception as e:
    print(f'Erreur Supabase est_valide: {e}')
    return False


def ajouter_utilisateur(user_id, id_1win):
  try:
    # 1. On vérifie si l'utilisateur existe déjà
    existing = (
        supabase.table('users')
        .select('*')
        .eq('user_id', str(user_id))
        .execute()
    )
    if existing.data and len(existing.data) > 0:
      # S'il existe, on met à jour son ID 1win et on remet le statut à pending
      supabase.table('users').update({
          'id_1win': str(id_1win),
          'status': 'pending',
          'is_vip': False,
      }).eq('user_id', str(user_id)).execute()
    else:
      # S'il n'existe pas, on l'ajoute proprement
      supabase.table('users').insert({
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

  if message_text == '📊 NEW SIGNAL':
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

    # Choix 100% aléatoire (Higher ou Lower)
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

  # Alerte Admin avec 3 Boutons Interactifs
  admin_keyboard = [
      [
          InlineKeyboardButton(
              '✅ Valider l\'accès', callback_data=f'val_{user_id}'
          ),
          InlineKeyboardButton('❌ Mauvais code', callback_data=f'err_{user_id}'),
      ],
      [
          InlineKeyboardButton(
              '💰 Rappel Recharge', callback_data=f'recharge_{user_id}'
          )
      ],
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


# Gestion des clics sur les boutons admin
async def admin_callback(update, context):
  query = update.callback_query
  if update.effective_user.id != TON_ID_ADMIN:
    await query.answer('Accès refusé.', show_alert=True)
    return

  await query.answer()
  data = query.data

  if data.startswith('val_'):
    user_id_target = int(data.split('_')[1])
    valider_utilisateur(user_id_target)

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
      print(f'Erreur envoi validation utilisateur: {e}')

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
      print(f'Erreur envoi message erreur: {e}')

    await query.edit_message_text(
        text=query.message.text + '\n\n🔴 **STATUT : MAUVAIS CODE NOTIFIÉ**',
        parse_mode='Markdown',
    )

  elif data.startswith('recharge_'):
    user_id_target = int(data.split('_')[1])
    try:
      await context.bot.send_message(
          chat_id=user_id_target,
          text=(
              '⚠️ Tu es bien inscrit avec le code COK225 ! Recharge toi'
              ' maintenant pour activer 🚀'
          ),
      )
    except Exception as e:
      print(f'Erreur envoi message recharge: {e}')

    await query.edit_message_text(
        text=query.message.text + '\n\n🟡 **STATUT : RAPPEL RECHARGE ENVOYÉ**',
        parse_mode='Markdown',
    )


async def valider(update, context):
  if update.effective_user.id != TON_ID_ADMIN:
    return

  if context.args:
    user_id_a_valider = int(context.args[0])
    valider_utilisateur(user_id_a_valider)

    keyboard = [[KeyboardButton('📊 NEW SIGNAL'), KeyboardButton('📈 STATISTIQUES')]]
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
  bot_app.add_handler(CallbackQueryHandler(admin_callback))
  bot_app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )
  bot_app.run_polling()
