import logging
import argparse
import typing
import telethon
import datetime
import re

class DialogInformationer:
    module_name = 'dialog_infomartion'
    module_description = 'Show dialogs in user account'

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger('cleaner_logger')

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        return parser

    async def run(self, client: telethon.TelegramClient, args):
        self.logger.info('started getting information about dialogs module')

        for dialog in await client.get_dialogs():
            print(dialog.id, dialog.name)

        self.logger.info('finished getting information about dialogs module')
