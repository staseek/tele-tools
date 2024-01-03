"""
Module for cleaning cloud chats
"""
import logging
import argparse
import typing
import datetime
import re
import telethon
import pytz
from tzlocal import get_localzone

class Cleaner:
    """
    Module for cleaning cloud chats
    """
    module_name = 'cleaner'
    module_description = 'Clean messages of users with some criterias'

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger('cleaner_logger')

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Fill argument parser with arguments for module
        :param parser: ArgumentParser
        :return: new ArgumentParser
        """
        parser.add_argument('--older', help='Remove message older than date')
        parser.add_argument('--newer', help='Remove messages newer than date')
        parser.add_argument('--delta', help='Remove messages not in delta in days from today (N days ago)')
        parser.add_argument('--regex', help='Remove message with regex matched')
        parser.add_argument('--chat_id', type=lambda s: [int(item) for item in s.split(',')])
        parser.add_argument('--dry-run', action="store_true", help="Dry run. Just print messages, not delete")
        return parser

    async def run(self, client: telethon.TelegramClient, args) -> None:
        """
        Main run module functions
        :param client: initialized TelegramClient
        :param args: parsed arguments
        :return: None
        """
        local_tz = get_localzone()
        self.logger.info('started cleaning module')
        for dialog_to_clean in [x for x in await client.get_dialogs() if x.id in args.chat_id]:
            self.logger.info('starting clean dialog with id=%s and name=%s', dialog_to_clean.id,
                             dialog_to_clean.name)
            messages_to_delete = []
            messages_to_delete_full = []
            interval_to_delete = (None, None)
            # messages_to_not_delete = set([])
            # self.logger.info("starting scrapping pinned messages for saving them")
            # async for message in client.iter_messages(dialog_to_clean,
            #                                           filter=telethon.types.InputMessagesFilterPinned()):
            #     messages_to_not_delete.add(message.id)
            # self.logger.info("finished scrapping pinned messages for saving them")
            async for message in client.iter_messages(dialog_to_clean, wait_time=1):
                # self.logger.debug(f"processing message with id={message.id}")
                if (args.older and message.date <
                    datetime.datetime.strptime(args.older, '%Y-%m-%d').replace(tzinfo=local_tz)) or \
                        (args.newer and message.date >
                         datetime.datetime.strptime(args.newer, '%Y-%m-%d').replace(tzinfo=local_tz)) or \
                        (args.delta and datetime.datetime.now(
                            datetime.timezone.utc) - message.date > datetime.timedelta(days=int(args.delta))) or \
                        (args.regex and re.search(args.regex, message.text)):
                    if message.id not in messages_to_delete:
                        messages_to_delete.append(message.id)
                        messages_to_delete_full.append(message)
                        if interval_to_delete[0] is None:
                            interval_to_delete = (message.date, message.date)
                        else:
                            interval_to_delete = (min(interval_to_delete[0], message.date),
                                                  max(interval_to_delete[1], message.date))
                # self.logger.debug(f"processed message with id={message.id}")
                if len(messages_to_delete) > 95:
                    if args.dry_run:
                        print('here')
                        for message_d in messages_to_delete_full:
                            print(message_d.id, message_d.date, message_d.text)
                    else:
                        deleted_messages = await client.delete_messages(entity=dialog_to_clean.entity.id,
                                                                        message_ids=messages_to_delete,
                                                                        revoke=True)
                        self.logger.info('chunk cleared for interval from %s till %s. Deleted %s messages',
                                     interval_to_delete[0], interval_to_delete[1], deleted_messages[0].pts_count)
                    interval_to_delete = (None, None)
                    messages_to_delete = []
                    messages_to_delete_full = []
            if len(messages_to_delete) > 0:
                if args.dry_run:
                    for message_d in messages_to_delete_full:
                        print(message_d.id, message_d.date, message_d.text)
                else:
                    deleted_messages = await client.delete_messages(entity=dialog_to_clean.entity.id,
                                                                message_ids=messages_to_delete,
                                                                revoke=True)
                    self.logger.info('chunk cleared for interval from %s till %s. Deleted %s messages',
                                 interval_to_delete[0], interval_to_delete[1], deleted_messages[0].pts_count)
                messages_to_delete = []
                messages_to_delete_full = []
        self.logger.info('finished cleaning module')
