from telegram.ext import Updater, CommandHandler
import helper.codeforces as cg
import helper.handle_handler as hh
import helper
from db import db
from datetime import time, timedelta


class Bot:
    @staticmethod
    def start_bot(bot, update):
        """
        When the /start command is executed.
        This also registers the user to the db(db/users_info.json)
        :return: void
        """
        update.message.reply_text("I'm Alexa!")
        db.add_user(update.effective_user)

    def add_handlers(self):
        """
        Add all the necessary handles. This is where all your "/commands" are defined
        :return: void
        """
        self.dispatcher.add_handler(CommandHandler('start', self.start_bot))
        self.dispatcher.add_handler(CommandHandler('upcoming', self.upcoming))
        self.dispatcher.add_handler(CommandHandler('running', self.running))
        self.dispatcher.add_handler(CommandHandler('refresh', self.refresh))
        self.dispatcher.add_handler(CommandHandler('add_handle', self.add_handle, pass_args=True))
        self.dispatcher.add_handler(CommandHandler('rating_of', self.get_rating_of, pass_args=True))
        self.dispatcher.add_handler(CommandHandler('list_handles', self.list_handles))
        self.dispatcher.add_handler(CommandHandler('rem_handle', self.rem_handle, pass_args=True))
    #
    # def testing(self):
    #     print(cg.did_contest_really_end(1077))

    def __init__(self):
        """
        Starting point of Bot. Connects to the bot and schedules the necessary daemons
        :return: void
        """
        self.TOKEN = helper.get_json_token()

        self.updater = Updater(token=self.TOKEN)
        self.dispatcher = self.updater.dispatcher

        # Create a cron job that fetches the updates daily at 3:00 AM
        self.job_queue = self.updater.job_queue
        self.job_daily_update = self.job_queue.run_daily(self._3am_update_callback,
                                                         time=time(hour=3, minute=0, second=0, microsecond=0))
        self._3am_update_callback()
        self.add_handlers()

        # Continuously polls for the updates on the Telegram
        self.updater.start_polling()

        # self.testing()

    def add_alarms(self):
        """
        For each contest, schedule two jobs. One alerts for the upcoming contest,
        the other fetches the rating changes of the interested users.
        :return: void
        """
        jobs = [x.name for x in self.job_queue.jobs()]
        contest_list = cg.get_contest_time_and_id()
        for x in contest_list:
            if x["id"] not in jobs:
                # print("Adding: " + str(x["id"]))
                self.job_queue.run_once(self.alarm, when=x["date"] - timedelta(hours=1),
                                        context=x["id"], name=x["id"])

                self.job_queue.run_once(cg.contest_finished, when=x["end_time"],
                                        context={"job_queue": self.job_queue,
                                                 "id": x["id"],
                                                 "datetime": x["end_time"]}, name=str(x["id"]) + "_end")

    def _3am_update_callback(self, bot=None, job=None):
        """
        Cron job that fetches the details from the CF.
        :param bot:
        :param job:
        :return: void
        """
        # cg.write_codeforces_contest_list()
        self.add_alarms()

    @staticmethod
    def alarm(bot, job):
        """
        Send update of the upcoming contest 1 hour before
        :param bot:
        :param job:
        :return: void
        """
        message = str(job.context) + " is going to start in 1 hour!"
        people = db.get_users_list()
        for person in people:
            bot.send_message(chat_id=person, text=message)

    @staticmethod
    def upcoming(bot, update):
        """
        Called when the user executes /upcoming
        Replies the user with a list of all upcoming contests
        :param bot:
        :param update:
        :return: void
        """
        res = cg.get_upcoming_contests()
        bot.send_message(chat_id=update.message.chat_id, text=res, parse_mode="HTML")

    @staticmethod
    def running(bot, update):
        """
        Called when the user executes /running
        Replies with the list of upcoming contests
        :param bot:
        :param update:
        :return:
        """
        res = cg.get_running_contests()
        bot.send_message(chat_id=update.message.chat_id, text=res, parse_mode="HTML")

    @staticmethod
    def refresh(bot, update):
        """
        Called when the user executes /refresh
        :param bot:
        :param update:
        :return:
        """
        cg.write_codeforces_contest_list()
        res = "Updating contest list... Please wait"
        bot.send_message(chat_id=update.message.chat_id, text=res)

    @staticmethod
    def add_handle(bot, update, args):
        """
        Adds the user to the list in the db
        :param bot:
        :param update:
        :param args: The positional arguments that are sent with the message
                     args[0] should contain the desired handle
        :return:
        """
        if len(args) != 1:
            update.message.reply_text("The format is /add_handle handle_name")
        else:
            res = hh.add_handle(args[0], update.effective_user.id)
            update.message.reply_text(res)

    @staticmethod
    def get_rating_of(bot, update, args):
        """
        Called when the user executes /get_rating
        Replies with the rating of the handle in args[0]
        :param bot:
        :param update:
        :param args: args[0] should contain the desired handle
        :return:
        """
        res = hh.get_rating_of(args[0])
        update.message.reply_text(res)

    @staticmethod
    def list_handles(bot, update):
        """
        Called when the user executes /list_handles
        Get a list of handle that the user is currently following
        :param bot:
        :param update:
        :return:
        """
        res = hh.get_handle_list(str(update.effective_user.id))
        update.message.reply_text(res)

    @staticmethod
    def rem_handle(bot, update, args):
        """
        Called when the user executes /rem_handle
        Remove the handle from the interested list
        :param bot:
        :param update:
        :param args:
        :return:
        """
        res = hh.remove_handle(args[0], str(update.effective_user.id))
        update.message.reply_text(res)
