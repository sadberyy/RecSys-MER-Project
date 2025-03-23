import logging
import pandas
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, Application, ContextTypes, ConversationHandler, MessageHandler, filters
from todobot.recommendations import get_recommendations
from todobot.config import TELEGRAM_TOKEN
from todobot.reranging import rearrange_tracks


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CHOOSING_MOOD = 0


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Список команд:\n"
                                    "/start - запуск бота\n"
                                    "/choose_mood - выбрать настроение\n"
                                    "/show_mood - показать выбранное настроение\n"
                                    "/register - ввести id (только для давних пользователей)\n"
                                    "/recommend - рекомендовать треки на основе выбранного настроения.")


async def ask_mood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("Anger", callback_data='Anger')],
        [InlineKeyboardButton("Sad", callback_data='Sad')],
        [InlineKeyboardButton("Pleasure", callback_data='Pleasure')],
        [InlineKeyboardButton("Joy", callback_data='Joy')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Как у тебя настроение сегодня?",
        reply_markup=reply_markup
    )
    return CHOOSING_MOOD


async def mood_chosen(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    mood = query.data

    context.bot_data[update.effective_user.id] = mood

    mood_text = ""

    if mood == 'Anger':
        mood_text = "Anger"
    elif mood == 'Sad':
        mood_text = "Sad"
    elif mood == 'Joy':
        mood_text = "Joy"
    elif mood == 'Pleasure':
        mood_text = "Pleasure"

    await query.message.reply_text(text=f"Вы выбрали настроение: {mood_text}")

    return ConversationHandler.END

async def show_mood(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in context.bot_data:
        chosen_mood = context.bot_data[user_id]
        await update.message.reply_text(f"Ваше текущее настроение: {chosen_mood}")
    else:
        await update.message.reply_text("Вы пока не выбрали настроение. Используйте команду /choose_mood, чтобы выбрать.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in context.bot_data:
        context.bot_data[user.id] = {'is_new': True, 'user_id': user.id, 'chosen_mood': None, "chosen_user_in_base": None}
        await update.message.reply_html(
            "Привет! Я бот для рекомендации музыки на основе настроения. Список команд:\n"
            "/choose_mood - выбрать настроение\n"
            "/show_mood - показать выбранное настроение\n"
            "/register - ввести id (только для давних пользователей)\n"
            "/recommend - рекомендовать треки на основе выбранного настроения."
            )
    else:
        await update.message.reply_html(
                "Привет! Рады видеть вас снова. Список команд:\n"
            "/choose_mood - выбрать настроение\n"
            "/show_mood - показать выбранное настроение\n"
            "/recommend - рекомендовать треки на основе выбранного настроения."
        )
        
async def recommend_tracks_by_emotion(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    print(user_id)
    if user_id in context.bot_data:
        chosen_mood = context.bot_data[user_id]
        print('chosen moode=', chosen_mood)
        if 'chosen_user_in_base' not in context.bot_data:
            context.bot_data['chosen_user_in_base'] = 0
        recommended_tracks = []

        suitable_tracks = get_recommendations(flags, user_data, context.bot_data["chosen_user_in_base"], topn = 100)
        filename = 'todobot/music_arousal_valence.csv'

        suitable_tracks = rearrange_tracks(chosen_mood, suitable_tracks)
        cnt = 1
        tracks_to_recommend = suitable_tracks[:10]
        
        for track in tracks_to_recommend.index:
            
            recommended_tracks.append(
                f"{cnt}. \"{tracks_to_recommend.loc[track, 'track_name']}\" - {tracks_to_recommend.loc[track, 'artist']}")
            cnt += 1
        message_text = f"Рекомендации треков для настроения '{chosen_mood}':\n" + "\n".join(recommended_tracks)
        await update.message.reply_text(message_text)

    else:
        await update.message.reply_text(
            "Вы пока не выбрали настроение. Используйте команду /choose_mood, чтобы выбрать.")


user_data = 0
df = pandas.read_csv("todobot/User Listening History.csv")

flags = {}


def is_user_new(from_tg_user_id: str) -> bool:
    result = df.loc[df['user_id'] == from_tg_user_id]
    if not result.empty:
        return False
    return True

async def ask_if_new_user(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="new_user_yes")],
        [InlineKeyboardButton("Нет", callback_data="new_user_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вы - новый пользователь?", reply_markup=reply_markup)

async def handle_new_user_response(update: Update, context: CallbackContext) -> None:
    user_data = update.effective_user.id
    if not update.callback_query:
        await update.message.reply_text("Используйте кнопки для выбора.")
        return

    query = update.callback_query
    await query.answer()

    if query.data == "new_user_yes":
        await query.message.reply_text("Добро пожаловать! Мы рады видеть вас! Используйте /choose_mood, чтобы выбрать настроение, а затем /recommend, чтобы получить рекомендации. ")
        flags[user_data] = True
    elif query.data == "new_user_no":
        await query.message.reply_text("Рады видеть вас снова!")
        flags[user_data] = False
        await query.message.reply_text("Введите ваш id")


async def handle_id_input(update: Update, context: CallbackContext) -> None:
    from_tg_user_id = update.message.text

    if is_user_new(from_tg_user_id):
        flags[from_tg_user_id] = True
    else:
        flags[from_tg_user_id] = False
    context.bot_data["chosen_user_in_base"] = from_tg_user_id
    await update.message.reply_text(f'Ваш id = {context.bot_data["chosen_user_in_base"]} успешно сохранён. Используйте /choose_mood, чтобы выбрать настроение, а затем /recommend, чтобы получить рекомендации.' )

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Действие отменено.')
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", ask_if_new_user))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("show_mood", show_mood))
    application.add_handler(CommandHandler("recommend", recommend_tracks_by_emotion))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id_input))
    application.add_handler(CallbackQueryHandler(handle_new_user_response, pattern="new_user_yes|new_user_no"))


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("choose_mood", ask_mood)],  
        states={
            CHOOSING_MOOD: [CallbackQueryHandler(mood_chosen)],},
        fallbacks=[CommandHandler("cancel", cancel)], 
    )

    application.add_handler(conv_handler)
    application.bot_data = {}

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
