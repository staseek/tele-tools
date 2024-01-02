import logging
import argparse


class Cleaner:
    module_name = 'downloader'
    module_description = 'Download files from chat'

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        parser.add_argument('--older')
        parser.add_argument('--newer')
        parser.add_argument('--regex')
        return parser

    def run(self):
        logging.info('started cleaning module')

