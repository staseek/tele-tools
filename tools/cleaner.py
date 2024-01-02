import logging
import argparse
import typing
import telethon
import datetime
import re


class Cleaner:
    module_name = 'cleaner'
    module_description = 'Clean messages of users with some criterias'

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger('cleaner_logger')

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        parser.add_argument('--older', help='Remove message older than date')
        parser.add_argument('--newer', help='Remove messages newer than date')
        parser.add_argument('--delta', help='Remove messages not in delta in days from today (N days ago)')
        parser.add_argument('--regex', help='Remove message with regex matched')
        parser.add_argument('--chat_id', type=lambda s: [int(item) for item in s.split(',')])
        return parser

    async def run(self, client: telethon.TelegramClient, args):
        self.logger.info('started cleaning module')
        for dialog_to_clean in [x for x in await client.get_dialogs() if x.id in args.chat_id]:
            self.logger.info(f'starting clean dialog with id={dialog_to_clean.id} and name={dialog_to_clean.name}')
            messages_to_delete = []
            interval_to_delete = (None, None)
            messages_to_not_delete = set([])
            self.logger.info("starting scrapping pinned messages for saving them")
            async for message in client.iter_messages(dialog_to_clean,
                                                      filter=telethon.types.InputMessagesFilterPinned()):
                messages_to_not_delete.add(message.id)
            self.logger.info("finished scrapping pinned messages for saving them")
            async for message in client.iter_messages(dialog_to_clean):
                # print(datetime.datetime.now(datetime.timezone.utc) - message.date)
                self.logger.debug(f"processing message with id={message.id}")
                if (args.older and message.date < datetime.datetime.strptime(args.older, '%Y-%m-%d')) or \
                        (args.newer and message.date > datetime.datetime.strptime(args.newer, '%Y-%m-%d')) or \
                        (args.delta and datetime.datetime.now(
                            datetime.timezone.utc) - message.date > datetime.timedelta(days=int(args.delta))) or \
                        (args.regex and re.search(args.regex, message.text)):
                    if message.id not in messages_to_delete:
                        messages_to_delete.append(message.id)
                        if interval_to_delete[0] is None:
                            interval_to_delete = (message.date, message.date)
                        else:
                            interval_to_delete = (min(interval_to_delete[0], message.date),
                                                  max(interval_to_delete[1], message.date))
                self.logger.debug(f"processed message with id={message.id}")
                if len(messages_to_delete) > 95:
                    deleted_messages = await client.delete_messages(entity=dialog_to_clean.entity.id,
                                                                    message_ids=messages_to_delete,
                                                                    revoke=True)
                    self.logger.info(f'chunk cleared for interval from {interval_to_delete[0]}'
                                     f' till {interval_to_delete[1]}. Deleted {len(deleted_messages)} messages')
                    interval_to_delete = (None, None)
                    messages_to_delete = []
            if len(messages_to_delete) > 0:
                deleted_messages = await client.delete_messages(entity=dialog_to_clean.entity.id,
                                                                message_ids=messages_to_delete,
                                                                revoke=True)
                self.logger.info(f'last chunk cleared for interval from {interval_to_delete[0]}'
                                 f' till {interval_to_delete[1]}. Deleted {len(deleted_messages)} messages.')
                messages_to_delete = []
        self.logger.info('finished cleaning module')
