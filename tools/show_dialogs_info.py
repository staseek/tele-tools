"""
Module printing dialog information to stdout
"""
import argparse
import logging
import typing
import telethon


class DialogInformationer:
    """
    Class of worker
    """
    module_name = 'dialog_information'
    module_description = 'Show dialogs in user account'

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger('cleaner_logger')

    @staticmethod
    def arguments_fill(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Function filling arguments for argument parserr
        :param parser:
        :return:
        """
        return parser

    async def run(self, client: telethon.TelegramClient, _) -> None:
        """
        Function running module
        :param client: TelegramClient already initialized
        :param args: arguments
        :return: None
        """
        self.logger.info('started getting information about dialogs module')

        for dialog in await client.get_dialogs():
            print(dialog.id, dialog.name)

        self.logger.info('finished getting information about dialogs module')
