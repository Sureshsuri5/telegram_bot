import requests
import qrcode
import json
import sqlite
from sqlite import mark_sold
import datetime

prices={
    'AHA':30,'PRIME':40,'GEMINI':150
}
def get_date():
    current_date=datetime.date.today()
    return current_date

def get_time():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return current_time

#read messages/updates
def read_msg(offset,url):
    params={
        'offset':offset
    }

    read=requests.get(url+'/getUpdates',params=params)
    data=read.json()
    for result in data['result']:
        global name
        if 'message' in result:
            global msg
            if 'text' in result['message']:
                msg=result['message']['text']
                chat_id=result['message']['chat']['id']
                message_id=result['message']['message_id']
                name=result['message']['from']['first_name']
                if msg == '/start':
                    inline_keyboard(url,chat_id,name)
                elif msg.isdigit():
                    send_qr(url, chat_id,msg)
                else:
                    send_msg(url,'invalid entry',chat_id)
        elif 'callback_query' in result:
            callback=result['callback_query']
            button=callback['data']
            chat_id=callback['message']['chat']['id']
            message_id=callback['message']['message_id']
            match button:
                case 'browse_services':
                    delete_message(url, chat_id, message_id)
                    browse_services(url,chat_id)
                case 'developer':
                    delete_message(url, chat_id, message_id)
                    developer(url,chat_id)
                case 'my_funds':
                    delete_message(url, chat_id, message_id)
                    my_funds(url,chat_id)
                case 'my_orders':
                    my_orders(url,chat_id)
                case 'support':
                    delete_message(url,chat_id,message_id)
                    support(url,chat_id)
                case 'back':
                    delete_message(url, chat_id, message_id)
                    inline_keyboard(url,chat_id,name)
                case 'add_funds':
                    send_msg(url,'enter funds:',chat_id)
                case 'aha':
                    verify_funds(url,chat_id,'AHA')
                case 'prime':
                    verify_funds(url,chat_id,'PRIME')
                case 'gemini':
                    verify_funds(url, chat_id, 'GEMINI')
    if data['result']:
        return data['result'][-1]['update_id']+1

#send messages
def send_msg(url,text,chat_id):
        data={
            'chat_id':chat_id,
            'text':text
        }
        requests.post(url+'/sendMessage',data=data)

def delete_message(url,chat_id,message_id):
    params={
        'chat_id':chat_id,
        'message_id':message_id
    }
    requests.post(url+'/deleteMessage',params=params)

def browse_services(url,chat_id):
    params = {
        "chat_id": chat_id,
        "text": '<tg-emoji emoji-id="5064552201955836789">😀</tg-emoji> Choose Your Product:',
        "parse_mode": "HTML",
        'reply_markup': {
            'inline_keyboard': [
                [{'text': f'Aha 1m ({sqlite.count_stock('AHA')})', 'callback_data': 'aha'}],
                [{'text': f'Prime 1m ({sqlite.count_stock('PRIME')})', 'callback_data': 'prime'}],
                [{'text':f'Gemini 18m ({sqlite.count_stock('GEMINI')})','callback_data':'gemini'}],
                [{'text': '⬅️Back', 'callback_data': 'back'}]

            ]
        }
    }

    requests.post(url+'/sendMessage',json=params)


def my_funds(url,chat_id):
    available_funds=sqlite.fetch_funds(chat_id)
    payload={
        'chat_id': chat_id,
        'text':f'Your available funds : {available_funds}',
        'reply_markup':{
            'inline_keyboard':[
                [
                    {'text':'➕ Add Funds','callback_data':'add_funds'}
                ],
                [
                    {'text':'⬅️ Back','callback_data':'back'}
                ]
            ]
        }
    }
    requests.post(url+'/sendMessage',json=payload)

def add_funds(url,chat_id):
    params={
        'chat_id':chat_id,
        'text':'enter amount to add:'
    }
    requests.post(url+'/sendMessage',params=params)

def my_orders(url,chat_id):
    orders=sqlite.get_order(chat_id)
    if not orders:
        params={
            'chat_id':chat_id,
            'text':'not ordered yet'
        }
        requests.post(url+'/sendMessage',params=params)
    history = ''
    for order in orders:
        product,price,date,time=order
        history+=f'📦Product: {product}\n💸Price: {price}\n📅Date: {date}\n🕑Time: {time}\n-------------------------------------\n\n'
    params={
        'chat_id':chat_id,
        'text':history
    }
    requests.post(url+'/sendMessage',params=params)


def verify_funds(url,chat_id,product_name):
    available_funds=sqlite.fetch_funds(chat_id)
    if available_funds>=prices[product_name]:
        deliver_products(url,chat_id,product_name)
        update_funds(url,chat_id,product_name)
    else:
        payload={
            'chat_id':chat_id,
            'text':'Insufficient Funds ',
            'reply_markup':{
                'inline_keyboard':[
                    [{'text':'➕ Add Funds','callback_data':'add_funds'}]
                ]
            }
        }
        requests.post(url+'/sendMessage',json=payload)


def deliver_products(url,chat_id,product_name):
    cred=sqlite.get_credentials(product_name)
    if cred is None:
        params={
            'chat_id':chat_id,
            'text':'sorry out of stock 🥲'
        }
        requests.post(url+'/sendMessage',params=params)
    else:
        if product_name=='GEMINI':
            id,link=cred
            message = f"✅ Order Successful!\n\nProduct:{product_name}\n\n📦 Jio Gemini AI Pro 18m\n\n{link}"
            param = {
                'chat_id': chat_id,
                'text': message
            }
            send = requests.post(url + '/sendMessage', params=param)
            mark_sold(id, product_name)
            date = get_date()
            time = get_time()
            sqlite.store_order(chat_id, product_name, prices[product_name], date, time)
        else:
            id,mail,password=cred
            message=f"CREDENTIALS:\n{mail}:{password}"
            param={
                'chat_id':chat_id,
                'text':message
            }
            send=requests.post(url+'/sendMessage',params=param)
            mark_sold(id,product_name)
            date=get_date()
            time=get_time()
            sqlite.store_order(chat_id,product_name,prices[product_name],date,time)

def update_funds(url,chat_id,product_name):
    amount=prices[product_name]
    sqlite.update_funds(amount,chat_id)

def support(url,chat_id):
    payload={
        'chat_id':chat_id,
        'text':f'''<tg-emoji emoji-id=5238025132177369293>😊</tg-emoji> Need Help?\n
Contact our support team directly:''',
        'parse_mode':'HTML',
        'reply_markup':{
            'inline_keyboard':[
                [{'text':'🧑‍💻Contact Support','url':'https://t.me/ottmakerz'}],
                [{'text':'⬅️ Back','callback_data':'back'}]
            ]
        }
    }
    send=requests.post(url+'/sendMessage',json=payload)


def developer(url,chat_id):
    params={
        'chat_id':chat_id,
        'text':'<tg-emoji emoji-id=5193188976436977891>😊</tg-emoji>developer: @ottmakerz',
        'parse_mode':'HTML',
        'reply_markup': {
        'inline_keyboard':[
            [{'text':'⬅️ Back','callback_data':'back'}]
            ]
    }
    }


    requests.post(url+'/sendMessage',json=params)

def inline_keyboard(url,chat_id,name):
    payload={
        'chat_id':chat_id,
        'text':f'<tg-emoji emoji-id="5377660214096974712">😀</tg-emoji>Welcome to Ott Sales Hub!\n\n Hey {name} <tg-emoji emoji-id="5413694143601842851">😀</tg-emoji>\n\nWe offer premium digital products at the best prices. Fast, secure, and fully automated delivery.\n\nChoose an option below to continue ! <tg-emoji emoji-id="5294010026585777874">😀</tg-emoji>',
        'parse_mode':'HTML',
        'reply_markup':
            {
            'inline_keyboard':
            [   #row:1
                [
                {'text':'🛒 Browse Services','callback_data':'browse_services'}
                ],

                #row:2
                [
                    {'text':'🪪 My Funds','callback_data':'my_funds' },
                    {'text':'📓 My Orders','callback_data':'my_orders'}
                ],

                #row:3
                [
                    {'text':'🎧 Support','callback_data':'support'}
                ],
                #row:4
                [
                    {'text':'🧑‍💻 Developer','callback_data':'developer'}
                ]

            ]
    }
    }
    requests.post(url+'/sendMessage',json=payload)

#generate and send qr for taking payments
def send_qr(base_url,chat_id,amount):
    amount=int(amount)
    upi='suresh.ottmaker@fam'
    name='Suresh Amarakonda'
    url=f'upi://pay?pa={upi}&pn={name}&am={amount}'
    file_path='qr_code.png'
    qr=qrcode.QRCode()
    qr.add_data(url)
    img=qr.make_image()
    img.save(file_path)
    with open('qr_code.png','rb') as photo:
        file={
            'photo':photo
        }
        parameter={
            'chat_id':chat_id,
            'caption':f'Name:{name}\nPay:₹{amount}\n\nNote:payments are manually verified by sending screenshot here'
        }
        requests.post(base_url+'/sendPhoto',params=parameter,files=file)
    sqlite.add_users(chat_id,amount)






