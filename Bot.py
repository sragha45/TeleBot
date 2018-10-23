from telegram.ext import Updater, CommandHandler
import helper.codeforces as cg
import helper.handle_handler as hh
import helper
from db import db
import json

from datetime import datetime, time, timedelta


class Bot:
    @staticmethod
    def start_bot(bot, update):
        update.message.reply_text("I'm Alexa!")
        db.add_user(update.effective_user)

    def add_handlers(self):
        self.dispatcher.add_handler(CommandHandler('start', self.start_bot))
        self.dispatcher.add_handler(CommandHandler('upcoming', self.upcoming))
        self.dispatcher.add_handler(CommandHandler('running', self.running))
        self.dispatcher.add_handler(CommandHandler('refresh', self.refresh))
        self.dispatcher.add_handler(CommandHandler('add_handles', self.add_handles, pass_args=True))
        self.dispatcher.add_handler(CommandHandler('rating_of', self.get_rating_of, pass_args=True))
        self.dispatcher.add_handler(CommandHandler('list_handles', self.list_handles))

    def __init__(self):
        self.TOKEN = helper.get_json_token()

        self.updater = Updater(token=self.TOKEN)
        self.dispatcher = self.updater.dispatcher

        # Create a cron job that fetches the updates daily at 3:00 AM
        self.job_queue = self.updater.job_queue
        self.job_daily_update = self.job_queue.run_daily(self._3am_update_callback,
                                                         time=time(hour=3, minute=0, second=0, microsecond=0))
        self._3am_update_callback()
        self.add_handlers()
        self.updater.start_polling()

    def add_alarms(self):
        jobs = [x.name for x in self.job_queue.jobs()]
        contest_list = cg.get_contest_time_and_id()
        for x in contest_list:
            if x["id"] not in jobs:
                self.job_queue.run_once(self.alarm, when=x["date"] - timedelta(hours=1),
                                        context=x["id"], name=x["id"])

                self.job_queue.run_once(cg.contest_finished, when=x["end_time"],
                                        context={"job_queue": self.job_queue,
                                                 "id": x["id"],
                                                 "datetime": x["end_time"]}, name=str(x["id"]) + "_end")

    def _3am_update_callback(self, bot=None, job=None):
        cg.write_codeforces_contest_list()
        self.add_alarms()

    @staticmethod
    def alarm(bot, job):
        message = str(job.context) + " is going to start in 1 hour!"
        people = db.get_users_list()
        for person in people:
            bot.send_message(chat_id=person, text=message)

    @staticmethod
    def upcoming(bot, update):
        res = cg.get_upcoming_contests()
        bot.send_message(chat_id=update.message.chat_id, text=res, parse_mode="HTML")

    @staticmethod
    def running(bot, update):
        res = cg.get_running_contests()
        bot.send_message(chat_id=update.message.chat_id, text=res, parse_mode="HTML")

    @staticmethod
    def refresh(bot, update):
        cg.write_codeforces_contest_list()
        res = "Updating contest list... Please wait"
        bot.send_message(chat_id=update.message.chat_id, text=res)

    @staticmethod
    def add_handles(bot, update, args):
        res = hh.add_handle(args[0], update.effective_user.id)
        update.message.reply_text(res)

    @staticmethod
    def get_rating_of(bot, update, args):
        res = hh.get_rating_of(args[0])
        update.message.reply_text(res)

    @staticmethod
    def list_handles(bot, update):
        res = hh.get_handle_list(str(update.effective_user.id))
        update.message.reply_text(res)
