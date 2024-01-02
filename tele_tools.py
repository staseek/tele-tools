import argparse
import logging

import phonenumbers
import telethon.errors.rpcerrorlist

import tools
from telethon import TelegramClient
from configparser import ConfigParser
import asyncio

from pathlib import Path

config = ConfigParser()
config.read('./config.ini')

API_ID = int(config['Telegram']['API_ID'])
API_HASH = config['Telegram']['API_HASH']

FORMATTER = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

logger = logging.getLogger('tele_tools')
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(FORMATTER)
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)
actions = dict(
        clean=tools.cleaner.Cleaner(logger=logger),
        show_dialogs=tools.show_dialogs_info.DialogInformationer(logger=logger)
        #donwload_files=tools.download_files.DownloadFiles(),
        #unremover=tools.unremover.Unremover()
    )

SESSIONS_PATH = Path('sessions')


async def main():

    parser = argparse.ArgumentParser(prog='Telegram Tools',
                                     description='Command line tool for telegram with'
                                                 ' some actions with your account')
    parser.add_argument('--session-name')
    parser.add_argument('--phone')
    subparsers = parser.add_subparsers(help='modules commands help', dest="command")

    for action_name, action_module in actions.items():
        current_action_parser = subparsers.add_parser(action_name)
        current_action_parser = action_module.arguments_fill(current_action_parser)

    args = parser.parse_args()
    if args.session_name is None and args.phone is None:
        logging.error('Not specified session_name of already used'
                      ' telegram account or phone for new login')
        exit(1)

    if args.session_name is not None and args.phone is None and not Path(args.session_name).exists():
        logging.error(f'Not exist session file {args.session_name} and'
                      f' can\'t create new - no phone specified')
        exit(1)

    if args.phone is not None:
        try:
            phonenumbers.parse(args.phone, None)
        except phonenumbers.phonenumberutil.NumberParseException as exc:
            phonenumbers.parse("+" + args.phone)

    if args.command not in actions:
        logging.critical('Unknown command action')
        exit(1)

    client = TelegramClient(str(SESSIONS_PATH / Path(args.session_name if args.session_name else args.phone)),
                            API_ID,
                            API_HASH,
                            system_version="4.16.30-vxCUSTOM",
                            device_model='iPhone 14 Pro Max',
                            app_version='0.1a')
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(args.phone)
        try:
            me = await client.sign_in(args.phone, input('Enter code: '))
            logger.info(me)
        except telethon.errors.rpcerrorlist.SessionPasswordNeededError as exc:
            logger.info('two factor is enabled')
            password = input("Enter password: ")
            me = await client.sign_in(password=password)
            logger.info(me)
    await actions[args.command].run(client, args)


if __name__ == "__main__":
    asyncio.run(main())
