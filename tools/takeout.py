import argparse
import logging
import typing
from pathlib import Path
import telethon
import json
from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.types.contacts import Contacts
from functools import reduce


async def aenumerate(asequence, start=0):
    """Asynchronously enumerate an async iterator from a given start value"""
    n = start
    async for elem in asequence:
        yield n, elem
        n += 1

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
        return parser

    async def run(self, client: telethon.TelegramClient, args) -> None:
        """

        :param client:
        :param args:
        :return:
        """

        def to_json_custom(x) -> str:
            if hasattr(x, 'to_json'):
                return json.loads(x.to_json())
            elif hasattr(x, 'to_dict'):
                return x.to_dict()
            else:
                try:
                    json.dumps(x)
                    return x
                except Exception:
                    return str(x)

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
                    async for message in client.iter_messages(dialog, wait_time=1):
                        messages_f.write(json.dumps(message, default=to_json_custom))
                        messages_f.write('\n')
                self.logger.info('downloading %s dialog %s finished ... OK ', dialog_number + 1, dialog.name)

