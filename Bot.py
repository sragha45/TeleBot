from telegram.ext import Updater, CommandHandler
import helper.codeforces as cg
from datetime import datetime, timedelta
import set_alarms
import db.db
import json


class Bot:
    @staticmethod
    def start_bot(bot, update):
        update.message.reply_text("I'm Alexa!")
        db.db.add_user(update.effective_user)

    def add_handles(self):
        self.dispatcher.add_handler(CommandHandler('start', self.start_bot))

    def __init__(self):
        self.TOKEN = "631877927:AAGJAVZo_GBz7Gmpq0HWOB8su-kK1i_CsLI"

        self.updater = Updater(token=self.TOKEN)
        self.dispatcher = self.updater.dispatcher

        # Create a cron job that runs fetches the updates daily at 3:00 AM
        self.job_queue = self.updater.job_queue
        # self.job_daily_update = job_queue.run_daily(_3am_update_callback,
        #                                             time(hour=3, minute=0, second=0, microsecond=0))
        # self.job_daily_update = self.job_queue.run_once(_3am_update_callback, datetime.now())
        self._3am_update_callback()
        self.add_handles()
        self.updater.start_polling()

    def add_alarms(self):
            contest_list = cg.get_contest_time_and_id()
            for x in contest_list:
                self.job_queue.run_once(self.alarm, when=x[0], context=x[1], name=x[1])

    def _3am_update_callback(self, bot=None, job=None):
        # cg.get_codeforces_contest_list()
        self.add_alarms()

    @staticmethod
    def alarm(bot, job):
        message = str(job.context) + " is starting now!"
        people = db.db.get_users_list()
        for person in people:
            bot.send_message(chat_id=person, text=message)
