import argparse
import logging
import random
import typing
from pathlib import Path
import telethon
import json
from telethon.tl.functions.contacts import GetContactsRequest
from functools import reduce
from tools.tools import aenumerate, to_json_custom



class Takeout:
    """
    Module for saving your telegram account information
    """
    module_name = "takeout"
    module_description = "Takeout messages and other information from your telegram account"
    TAKEOUT_DIR = Path('takeout')

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger("takeout_logger")

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Fill argument parser with arguments for module
        :param parser: ArgumentParser
        :return: new ArgumentParser
        """
        parser.add_argument("--download-channels", action="store_true", help="Download channels messages. ")
        parser.add_argument("--text-only", help="Download only text infomation, no media")
        parser.add_argument('--chat_id', type=lambda s: [int(item) for item in s.split(',')])
        parser.add_argument("--max-size", type=int, help="Maximum size of downloading media in bytes")
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
        with open(current_takeout_path / 'me.json', 'w') as mef:
            mef.write(me.to_json())
        with open(current_takeout_path / 'contacts.json', 'w') as contactsf:
            contactsf.write(
                json.dumps(await client(GetContactsRequest(hash=client.api_id)),
                           default=to_json_custom)
            )

        with open(current_takeout_path / 'dialogs.json', 'w') as dialogs_f:
            dialogs_count = reduce(lambda y, x: y + (0 if x.is_channel and not args.download_channels else 1),
                                   await client.get_dialogs(), 0)
            async for dialog_number, dialog in aenumerate(client.iter_dialogs()):
                self.logger.info('downloading %s dialog started ... %s', dialog_number + 1, dialog.name)
                dialogs_f.write(json.dumps(dialog.__dict__, default=to_json_custom))
                dialogs_f.write('\n')
                current_dialog_path = current_takeout_path / Path(str(dialog.id))
                current_dialog_path.mkdir(exist_ok=True, parents=True)
                with open(current_dialog_path / 'info.json', 'w') as dialog_info_f:
                    dialog_info_f.write(json.dumps(dialog, default=to_json_custom))
                if dialog.is_channel and not args.download_channels:
                    continue
                with open(current_dialog_path / 'messages.json', 'w') as messages_f:
                    async for message_number, message in aenumerate(client.iter_messages(dialog, wait_time=1)):
                        messages_f.write(json.dumps(message, default=to_json_custom))
                        messages_f.write('\n')
                        if message.media:
                            if args.max_size and message.media.document.size > args.max_size:
                                continue
                            new_filename = Path(message.file.name if message.file and
                                                                   message.file.name
                                                else f"{str(message_number)}_{random.Random().randint(1, 1000)}")
                            self.logger.info('downloading media for message with id = %s with name %s',
                                             message.id, new_filename)
                            current_dialog_media_path = current_dialog_path / Path('media')
                            await message.download_media(file=current_dialog_media_path / new_filename)

                self.logger.info('downloading %s dialog %s finished ... OK ', dialog_number + 1, dialog.name)

