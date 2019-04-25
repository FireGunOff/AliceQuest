from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():

    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):

    user_id = req['session']['user_id']

    if req['session']['new']:

        res['response']['text'] = 'Привет! Назови свое имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False
        }

        return

    first_name = get_first_name(req)

    if sessionStorage[user_id]['first_name'] is None:

        if first_name is None:
            res['response']['text'] = 'Не раслышала имя. Повтори!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = 'Приятно познакомиться, ' + first_name.title() + '. Я Алиса. ' \
                                                                                       'Хочешь пройти квест "Побег из тюрьмы"?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True

                },
                {
                    'title': 'Нет',
                    'hide': True

                },
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]

    else:

        if not sessionStorage[user_id]['game_started']:

            if 'да' in req['request']['nlu']['tokens']:

                if len(sessionStorage[user_id]['guessed_cities']) == 3:

                    res['response']['text'] = 'Ты отгадал все города!'
                    res['end_session'] = True

                else:

                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)

            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            elif req['request']['original_utterance'].lower() == 'помощь':
                res['response']['text'] = 'Привет. В этом квесте тебе придется сбежать из тюрьмы используя свой интеллект и интуицую.'
            else:
                res['response']['text'] = 'Не понял ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True

                    },
                    {
                        'title': 'Нет',
                        'hide': True

                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                    }
                ]
        elif req['request']['original_utterance'].lower() == 'помощь':
                res['response']['text'] = 'Привет. В этом квесте тебе придется сбежать из тюрьмы используя свой интеллект и интуицую.'
        else:

            play_game(res, req)


def play_game(res, req):

    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']

    if attempt == 1:
        res['response']['card'] = {}
        res['response']['card']['title'] = 'Вы находитесь в камере'
        res['response']['buttons'] = [
            {
                'title': 'Пойти на выход из камеры',
                'hide': True
            },
            {
                'title': 'Остаться в камере',
                'hide': True
            },
            {
                'title': 'Помощь',
                'hide': True
            }
        ]

    else:

        if get_city(req) == 'Пойти на выход из камеры':

            res['response']['text'] = 'Впереди стоолвая'
            res['response']['buttons'] = [
                {
                    'title': 'Влево',
                    'hide': True

                },
                {
                    'title': 'Вправо',
                    'hide': True

                },
                {
                    'title': 'Вниз',
                    'hide': True

                },
                {
                    'title': 'Вверх',
                    'hide': True

                },
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]
            sessionStorage[user_id]['game_started'] = False
            return

        else:

            res['response']['text'] = 'Неправильно'
            if attempt == 3:
                res['response']['text'] = 'You died'

    sessionStorage[user_id]['attempt'] += 1



def get_city(req):

    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.GEO':

            if 'city' in entity['value'].keys():
                return entity['value']['city']
            else:
                return None

    return None


def get_first_name(req):

    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.FIO':

            if 'first_name' in entity['value'].keys():
                return entity['value']['first_name']
            else:
                return None
    return None


if __name__ == '__main__':
    app.run()