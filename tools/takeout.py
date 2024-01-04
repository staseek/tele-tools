import argparse
import logging
import typing
from pathlib import Path
import telethon
import json
from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.types.contacts import Contacts

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
        return parser

    async def run(self,client: telethon.TelegramClient, args) -> None:
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
            async for dialog in client.iter_dialogs():
                dialogs_f.write(json.dumps(dialog.__dict__, default=to_json_custom))
                dialogs_f.write('\n')
                current_dialog_path = current_takeout_path / Path(str(dialog.id))
                current_dialog_path.mkdir(exist_ok=True, parents=True)
                async for message in client.iter_messages(dialog, wait_time=1):
                    pass


