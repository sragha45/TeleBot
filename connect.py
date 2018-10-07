from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token="631877927:AAGvbOPIwlBWthCI1_MmZ61GNB3mOa6zVjM")
dispatcher = updater.dispatcher


def start_bot(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm Alexa!")


start_handler = CommandHandler('start', start_bot)
dispatcher.add_handler(start_handler)


def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)


dispatcher.add_handler(MessageHandler(Filters.text, echo))


def to_caps(bot, update, args):
    reply_string = ''.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_string)


dispatcher.add_handler(CommandHandler('caps', to_caps, pass_args=True))


def to_caps_inline(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(InlineQueryResultArticle(
        id=update.inline_query.id,
        title='Caps',
        url='https://google.com',
        hide_url=True,
        input_message_content=InputTextMessageContent(query.upper())
    ))
    logging.info(update.inline_query.id)
    bot.answer_inline_query(update.inline_query.id, results)


dispatcher.add_handler(InlineQueryHandler(to_caps_inline))

updater.start_polling()


def auto_send(bot, job):
    bot.sendMessage(chat_id='647915079', text="Where are you?")


updater.job_queue.run_repeating(auto_send, interval=1, first=2)


