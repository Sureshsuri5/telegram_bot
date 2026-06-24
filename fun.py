import requests

def read_msg(offset,url):
    params={
        'offset':offset
    }
    read=requests.get(url+'/getUpdates',params=params)
    data=read.json()
    for result in data['result']:
        send_msg(url)

    if data['result']:
        return data['result'][-1]['update_id']+1

def send_msg(url):

        data={
            'chat_id':-1004455504188,
            'text':'hello'
        }
        send=requests.post(url+'/sendMessage',data=data)

