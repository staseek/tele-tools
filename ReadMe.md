# Telegram CLI tools 

Some useful scripts for work with telegram accounts with CLI.
Supports 2-fa authorization.

## How to run
1. Clone repository
2. Create virtual env ```python -m venv venv && source venv/bin/activate```
3. Install requirements ```python -m pip install -r requirements.txt```
4. Configure ```config.ini``` get this data [here](https://my.telegram.org/auth?to=apps)
```
[Telegram]
API_ID=11111
API_HASH=sdkjaksljdaisojd890qwj8d832jd
```

## Common parameters

Now there are these modules:

### Get Dialog Information module
Iterate through your dialog list and print it to stdout.

Example:
```
python3 tele_tools.py --phone %your_phone_here% show_dialogs
```
Print in stdout chat_id and chat name for all dialogs in account.

### Clean chats module

Example:
```
python3 tele_tools.py --phone %your_phone_here% clean --delta 30 --chat_id -133778221
```