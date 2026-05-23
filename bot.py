import os
import django
import telebot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import BotLoginSession, CustomUser
from django.utils import timezone
from django.conf import settings

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Проверяем, есть ли параметр login_<token>
    args = message.text.split()
    if len(args) > 1 and args[1].startswith('login_'):
        token = args[1][6:]   # убираем "login_"
        try:
            session = BotLoginSession.objects.get(token=token, status='pending')
            if session.is_expired():
                session.status = 'expired'
                session.save()
                bot.reply_to(message, "Срок действия ссылки истёк, попробуйте ещё раз.")
                return
            # Получаем telegram_id и создаём/обновляем пользователя
            tg_id = message.from_user.id
            user, created = CustomUser.objects.get_or_create(
                telegram_id=tg_id,
                defaults={
                    'first_name': message.from_user.first_name or '',
                    'last_name': message.from_user.last_name or '',
                    'username': message.from_user.username or '',
                    'auth_date': timezone.now(),
                }
            )
            # Обновляем сессию
            session.user = user
            session.status = 'ready'
            session.save()
            bot.reply_to(message, "Вход выполнен, вернитесь в приложение!")
        except BotLoginSession.DoesNotExist:
            bot.reply_to(message, "Неверный код входа.")
    else:
        bot.reply_to(message, "Добро пожаловать! Этот бот для входа в EggsTapping.")

if __name__ == '__main__':
    bot.polling(none_stop=True)