import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN


bot = telegram.Bot(token=TOKEN)

data = {}


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Что необходимо напомнить?\n\n" +
                                                                    "/put чтобы создать новое напоминание.\n" +
                                                                    "Например /put убраться в саду")


start_handler = CommandHandler("start", start)


def put(update, context):
    user_input = update.message.text
    try:
        cache_message = user_input.partition(" ")[2]
        if cache_message == "":
            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите название напоминания после /put")
        else:
            data["key"] = cache_message
            context.bot.send_message(chat_id=update.effective_chat.id, text="Хорошо, через какое время вы хотите установить напоминание?\n\n" +
                                                                            "/set чтобы установить таймер" +
                                                                            " в следующем формате: 5н 2д 3ч 20м 3с\n "
                                                                            "Например /set 30с или /set 1ч 30м")
    except (IndexError, ValueError):
        update.message.reply_text("/put чтобы создать новое напоминание.\n" +
                                  "Например /put убраться в саду")


put_handler = CommandHandler("put", put)


def set(update, context):
    try:
        user_input = update.message.text
        if isValid(user_input.split()):
            time_set = user_input.split()[1:]
            time_in_seconds = seconds(time_set)
            context.job_queue.run_once(call_back_time, time_in_seconds, context=update.message.chat_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Напоминание успешно установлено")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Недопустимое время!")
    except (IndexError, ValueError):
        update.message.reply_text("/set чтобы установить таймер" +
                                  " в следующем формате: 5н 2д 3ч 20м 3с\n "
                                  "Например /set 30с или /set 1ч 30м")


set_handler = CommandHandler("set", set)


def isValid(time_list):
    for time in time_list:
        if len(time) > 1:
            unit = time[len(time) - 1]
            number = time[:len(time) - 1]
            if unit == 'н' or unit == 'д' or unit == 'ч' or unit == 'м' or unit == 'с':
                if str.isdigit(number):
                    return True
    return False


def seconds(time_list):
    time_in_seconds = 0
    for time in time_list:
        if 'н' in time:
            time_in_seconds += (int(time[:len(time) - 1]) * 604800)
        elif 'д' in time:
            time_in_seconds += (int(time[:len(time) - 1]) * 86400)
        elif 'ч' in time:
            time_in_seconds += (int(time[:len(time) - 1]) * 3600)
        elif 'м' in time:
            time_in_seconds += (int(time[:len(time) - 1]) * 60)
        else:
            time_in_seconds += int(time[:len(time) - 1])
    return time_in_seconds


def call_back_time(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=context.job.context, text=data["key"])


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(put_handler)
    dispatcher.add_handler(set_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
