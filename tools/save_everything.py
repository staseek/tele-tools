"""
Module for listening your telegram account and save everything (if other user delete message you will save it)
"""
import json
import logging
import argparse
import telethon
import telethon.events
import typing
from pathlib import Path
import json
import random


class SaveEverything:
    """
    Module for saving everything
    """
    module_name = 'saver'
    module_description = 'Save all new message chat'
    download_directory = Path('saver')

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger('saver_everything')

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Fill parser with arguments for current module
        :param parser:
        :return: new parser
        """
        parser.add_argument('--chat_id', type=lambda s: [int(item) for item in s.split(',')])
        return parser

    async def run(self, client: telethon.TelegramClient, args) -> None:
        """
        Module start function
        :return: None
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

        logging.info('started listening messages')
        me = await client.get_me()

        @client.on(telethon.events.NewMessage)
        async def new_message_handler(event):
            if args.chat_id is None or len(args.chat_id) == 0 or event.message.peer_id.user_id in args.chat_id:
                dialog = [x for x in await client.get_dialogs() if x.id == event.message.peer_id.user_id][0]
                current_dialog_path = self.download_directory / Path(f"{me.phone}_{me.id}") / Path(
                    f"{dialog.id}_{dialog.name}")
                current_dialog_path.mkdir(parents=True, exist_ok=True)
                message = event.message
                with open(current_dialog_path / Path("messages.txt"), 'a') as messagesf:
                    messagesf.write(json.dumps(event.message, default=to_json_custom))
                    messagesf.write("\n")
                    if message.media:
                        new_filename = Path(message.file.name if message.file and
                                                             message.file.name
                                            else f"{random.Random().randint(1, 1000)}")
                        self.logger.info('downloading media for message with id = %s with name %s',
                                     message.id, new_filename)
                        current_dialog_media_path = current_dialog_path / Path('media')
                        await message.download_media(file=current_dialog_media_path / new_filename)
        await client.run_until_disconnected()
        logging.info('finished listening messages')
