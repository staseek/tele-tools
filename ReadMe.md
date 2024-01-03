# Telegram CLI tools 

Some useful scripts for work with telegram accounts with CLI.
It supports 2-fa authorization.

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
```
--phone %your_phone_number%
--session-name %session_name_file%
```

### Get Dialog Information module
Iterate through your dialog list and print it to stdout.
This module has no specific arguments. 

Example:
```
python3 tele_tools.py --phone %your_phone_here% show_dialogs
```
It prints to stdout chat_id and chat name for all dialogs in the account.


### Clean chats module
This module gets chat history and removes messages. (If you are admin - it removes anybody's messages if you aren't admin only your messages) 


```
--older - remove message older than date
--newer - remove messages newer than date
--delta - remove mesages not in delta days from today
--regex - remove message matched to regex
--chat_id - comma-separated chat identificitors
--dry-run - dry run. Just print messages, not delete
```

Example:
```
python3 tele_tools.py --phone %your_phone_here% clean --delta 30 --chat_id %your_chat_id_for_cleaning%
```