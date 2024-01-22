from pathlib import Path
import typing
import logging
import argparse
import telethon
from tools.tools import aenumerate

class ScrapeDialogsUser:
    """
    Module for saving your telegram account information
    """
    module_name = "scrape_dialog_users"
    module_description = "Scrape all dialogs and their users"
    TAKEOUT_DIR = Path('dialogs_to_users')

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger("takeout_logger")

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Fill argument parser with arguments for module
        :param parser: ArgumentParser
        :return: new ArgumentParser
        """
        return parser

    async def run(self, client: telethon.TelegramClient, args) -> None:
        """

        :param client:
        :param args:
        :return:
        """
        me = await client.get_me()
        current_takeout_path = self.TAKEOUT_DIR / Path(f"{me.phone}_{me.id}")
        current_takeout_path.mkdir(parents=True, exist_ok=True)
        async for dialog_number, dialog in aenumerate(client.iter_dialogs()):
            pass