"""
Module for downloading files from chat
"""
import json
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
        parser.add_argument("--no_reload", action="store_true", help="If script founds already downloaded file - stop")
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
            metainf = None
            if not (current_directory / Path('files.meta.json')).exists():
                with open(current_directory / Path('files.meta.json'), 'w') as filesmetaf:
                    filesmetaf.write('{}')
                    filesmetaf.write('\n')
            with open(current_directory / Path('files.meta.json'), 'r') as filesmetaf:
                metainf = json.loads(filesmetaf.read())
                metainf_keys = set(metainf.keys())
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
                    key = f"{message.media.document.id}_{file_name}"
                    if key in metainf_keys and args.no_reload:
                        break
                    else:
                        metainf_keys.add(key)
                        metainf[key] = message.media.document.size

                    path = await message.download_media('{}/{}'.format(current_directory, file_name), progress_callback=progress_callback)
                    self.pbar.close()
                    downloaded_files_count += 1
            with open(current_directory / Path('files.meta.json'), 'w') as filesmetaf:
                filesmetaf.write(json.dumps(metainf, indent=4))
                filesmetaf.write('\n')

        logging.info('finished downloading files module')
