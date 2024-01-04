import argparse
import logging
import typing
from pathlib import Path
import telethon
import json


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

        def to_json_cumstom(x) -> str:
            if hasattr(x, 'to_json'):
                return x.to_json()
            elif hasattr(x, 'to_dict'):
                return json.dumps(x.to_dict(), default=to_json_cumstom)
            else:
                try:
                    return json.dumps(x)
                except Exception:
                    return str(x)

        me = await client.get_me()
        current_takeout_path = self.TAKEOUT_DIR / Path(f"{me.phone}_{me.id}")
        current_takeout_path.mkdir(parents=True, exist_ok=True)
        with open(current_takeout_path / 'me.json', 'w') as mef:
            mef.write(me.to_json())
        with open(current_takeout_path / 'dialogs.json', 'w') as dialogs_f:
            async for dialog in client.iter_dialogs():
                dialogs_f.write(json.dumps(dialog.__dict__, default=to_json_cumstom))
                dialogs_f.write('\n')

