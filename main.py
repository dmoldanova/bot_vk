import vk_api
from flask_sslify import SSLify
from flask import Flask,request
import requests
import json
import config
import vk


app = Flask(__name__)
bot = vk_api.VkApi(token=config.TOKEN)
#session = vk.Session()
#api = vk.API(session, v=5.0)

# список user
users = {}
URL = 'https://api.telegram.org/bot{}'.format(config.TOKEN)

# список привествий
greeating = ['привет','добрый день','добрый вчер','здравствуйте']
num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# доплнительные функции!!
def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return

def check_number_phone(text):
    text_len = len(text)
    if text_len != 11:
        return False
    else:
        i = 0
        sum = 0
        while i != text_len:
            if (str(text[i]) in num) == False:
                return False
            i += 1
        return True

def handler_question(id, text):
    text_lower = str(text).lower()

    print('handler_question()')

    if users[id]['level'] == '0':
        if (text_lower in greeating) == False:
            text = 'Для начала давай поприветствуем друг друга!'
            #bot.send_text_message(id, text)
            bot.method('messages.send', {'user_id': id, 'message': text})
            users[id]['level'] = '0'
        else:
            text = 'Привет! Данный бот предназначен для сбора контактной информации.\nОставь свой номер телефона ' \
                   'и в ближайшее время наш оператор с Вами свяжется!\n' \
                   'Основные правила ввода номера телефона:\n' \
                   '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                   '\n3. В номере телефона должны быть только цифры.'
            #bot.send_text_message(id, text)
            bot.method('messages.send', {'user_id': id, 'message': text})
            users[id]['level'] = '1'
    elif users[id]['level'] == '1' or users[id]['level'] == '2':
        if text[0] != 8 and len(text) == 10:
            text = 'Номер телефона должен начинаться с 8! Еще раз скажу правила ввода номера:\n' \
                   '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                   '\n3. В номере телефона должны быть только цифры.'
            # bot.send_text_message(id, text)
            bot.method('messages.send', {'user_id': id, 'message': text})
        elif len(text_lower) != 11:
            text = 'Данный бот предназначен для сбора контактной информации.\nПомощь в написании номера телефона:\n1. ' \
                   'Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                   '\n3. В номере телефона должны быть только цифры.'
            #bot.send_text_message(id, text)
            bot.method('messages.send', {'user_id': id, 'message': text})
        else:
            if text_lower[0] != '7':
                text = 'Номер телефона должен начинаться с 8! Еще раз скажу правила ввода номера:\n' \
                       '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                       '\n3. В номере телефона должны быть только цифры.'
                #bot.send_text_message(id, text)
                bot.method('messages.send', {'user_id': id, 'message': text})
            elif check_number_phone(text_lower) == False:
                text = 'В номере должны присутствовать только цифры. Еще раз скажу правила ввода номера:\n' \
                       '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                       '\n3. В номере телефона должны быть только цифры.'
                #bot.send_text_message(id, text)
                bot.method('messages.send', {'user_id': id, 'message': text})
            else:
                if users[id]['number_mobile'] == 'no':
                    users[id]['number_mobile'] = text_lower
                    text = 'Ваш номер {} попал в базу. Ждите звонка от нашего оператора!'.format(text)
                    #bot.send_text_message(id, text)
                    bot.method('messages.send', {'user_id': id, 'message': text})
                    users[id]['level'] = '2'
                    url = 'https://api.sip7.net/cm/v2/quickcall?login={}&password={}&from={}&to={}'.format(config.login,
                                                                                                           config.pw,
                                                                                                           config.domen,
                                                                                                           text_lower)
                    r = requests.post(url)
                    print(r)
                else:
                    text = 'Ваш номер телефона поменялся на - {}'.format(text_lower)
                    users[id]['number_mobile'] = text_lower
                    #bot.send_text_message(id, text)
                    bot.method('messages.send', {'user_id': id, 'message': text})
                    users[id]['level'] = '2'
                    url = 'https://api.sip7.net/cm/v2/quickcall?login={}&password={}&from={}&to={}'.format(config.login,
                                                                                                           config.pw,
                                                                                                           config.domen,
                                                                                                           text_lower)
                    r = requests.post(url)
                    print(r)

    return

def handler_funk(id, text, id_sms):

    print(users)

    if id not in users.keys():
        print('тут!')
        users[id] = {'number_mobile': 'no', 'level':'0', 'id_sms': '0'}

    if int(id_sms) > int(users[id]['id_sms']):
        handler_question(id, text)
        users[id]['id_sms'] = id_sms

    return

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        write_json(r)

        if "type" not in r.keys():
            return "not bot"
        elif r["type"] == "confirmation":
            return config.confirmation_token
        elif r["type"] == "message_new":
            id = r["object"]["user_id"]
            id_sms = r["object"]["id"]
            text = r["object"]["body"]

            #bot.method('messages.send', {'user_id': id, 'message': "hellow"})
	    bot.method('messages.markAsRead',{'message_ids' : id})
            print('--- to (', config.num, ') ---')
            print('chat_id: ', id)
            print('text: ', text)
            handler_funk(id, text, id_sms)
            print('level: ', users[id]["level"])
            print('number_mobile: ', users[id]["number_mobile"])
            print('-------------------------')

            return "ok"

    return "Hello Bot!"

def main():
    pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')
