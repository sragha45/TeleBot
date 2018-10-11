from telegram.ext import Updater, CommandHandler
import getter.codeforces as cg
from datetime import time


class Bot:
    @staticmethod
    def start_bot(bot, update):
        update.message.reply_text("I'm Alexa!")

    def add_handles(self):
        self.dispatcher.add_handler(CommandHandler('start', self.start_bot))

    def __init__(self):
        self.TOKEN = "631877927:AAGJAVZo_GBz7Gmpq0HWOB8su-kK1i_CsLI"

        self.updater = Updater(token=self.TOKEN)
        self.dispatcher = self.updater.dispatcher

        job_queue = self.updater.job_queue
        self.job_daily_update = job_queue.run_daily(cg.get_codeforces_contest_list,
                                                    time(hour=3, minute=0, second=0, microsecond=0))

        self.add_handles()
        self.updater.start_polling()

