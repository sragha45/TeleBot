from telegram.ext import Updater, CommandHandler
import getter.codeforces as cg
from datetime import datetime, time
import set_alarms
import json


def get_contest_data():
    contests = []
    with open("data/contest_list.json", "r", encoding='utf-8') as f:
        contest_list = json.load(f)
        for x in contest_list:
            date = datetime.utcfromtimestamp((x["startTimeSeconds"]))
            id = x["id"]
            contests.append((date, id))

    return contests


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

        # Create a cron job that runs fetches the updates daily at 3:00 AM
        self.job_queue = self.updater.job_queue
        # self.job_daily_update = job_queue.run_daily(cg.get_codeforces_contest_list,
        #                                             time(hour=3, minute=0, second=0, microsecond=0))
        # self.job_daily_update = job_queue.run_once(cg.get_codeforces_contest_list, datetime.now())
        self.add_alarms()
        self.add_handles()
        self.updater.start_polling()

    def add_alarms(self):
            contest_list = get_contest_data()
            for x in contest_list:
                self.job_queue.run_once(self.alarm, when=x[0], context=x[1], name=x[1])

    @staticmethod
    def alarm(bot, job):
        message = str(job.context) + " is starting now!"
        bot.send_message(chat_id='454380420', text=message)
