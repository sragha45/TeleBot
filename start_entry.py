import logging
from Bot import Bot

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == "__main__":
    bot = Bot()
