"""
Module for downloading files from chat
"""
import logging
import argparse


class FilesDownloader:
    """
    Module for downloading files from chat
    """
    module_name = 'downloader'
    module_description = 'Download files from chat'

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Fill parser with arguments for current module
        :param parser:
        :return: new parser
        """
        parser.add_argument('--chat_id', type=lambda s: [int(item) for item in s.split(',')])
        return parser

    def run(self) -> None:
        """
        Module start function
        :return: None
        """
        logging.info('started cleaning module')
