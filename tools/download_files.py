"""
Module for downloading files from chat
"""
import logging
import argparse
import telethon
import typing
from pathlib import Path
import tqdm

class FilesDownloader:
    """
    Module for downloading files from chat
    """
    module_name = 'downloader'
    module_description = 'Download files from chat'
    download_directory = Path('files')

    def __init__(self, logger: typing.Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger('downloader_files_logger')
        self.prev_curr = 0
        self.pbar = None

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Fill parser with arguments for current module
        :param parser:
        :return: new parser
        """
        parser.add_argument('--chat_id', type=lambda s: [int(item) for item in s.split(',')])
        parser.add_argument('--depth', type=int, help="Search depth")
        return parser

    async def run(self, client: telethon.TelegramClient, args) -> None:
        """
        Module start function
        :return: None
        """

        logging.info('started downloading files module')
        me = await client.get_me()
        for dialog in [x for x in await client.get_dialogs() if x.id in args.chat_id]:
            downloaded_files_count = 0
            current_directory = self.download_directory / Path(f"{me.phone}_{me.id}") / Path(f"{dialog.id}_{dialog.name}")
            current_directory.mkdir(parents=True, exist_ok=True)
            async for message in client.iter_messages(dialog):
                if not message.media:
                    continue
                if downloaded_files_count >= args.depth:
                    break
                self.pbar = tqdm.tqdm(total=message.document.size, unit='B', unit_scale=True)
                self.prev_curr = 0

                def progress_callback(current, total):
                    self.pbar.update(current - self.prev_curr)
                    self.prev_curr = current

                file_name = message.media.document.attributes[0].file_name
                # print(message.media.document)
                path = await message.download_media('{}/{}'.format(current_directory, file_name),
                                                   progress_callback=progress_callback)
                self.pbar.close()
                downloaded_files_count += 1


        logging.info('finished downloading files module')
