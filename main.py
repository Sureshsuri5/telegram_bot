from time import sleep
import fun
import config

bot_token=config.bot_token
base_url=f'https://api.telegram.org/bot{bot_token}'

offset=0
try:
    sleep(5)
    while True:
        offset=fun.read_msg(offset,base_url)

except KeyboardInterrupt:
    print('keyboard interrupted!')
