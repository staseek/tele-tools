import logging
import argparse


class Unrem:
    module_name = 'unremover'
    module_description = 'Listen all messages from '

    def arguments_fill(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        parser.add_argument('--older')
        parser.add_argument('--newer')
        parser.add_argument('--regex')
        return parser

    def run(self):
        raise NotImplementedError("this module not implemented yet")

