from flask import Flask, request
import logging
import json

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
                                                                                       'Готов пройти квест "Побег из тюрьмы"?'
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

                    res['response']['text'] = 'Ты уже прошел квест!'
                    res['end_session'] = True

                else:

                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)

            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            elif req['request']['original_utterance'].lower() == 'помощь':
                res['response']['text'] = 'Привет. Это квест побег из тюрьмы, здесь тебе придется думать логично, так как любое неправильное действие от тебя - ты проиграешь игру. Готов?'
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
                res['response']['text'] = 'Привет. Это квест побег из тюрьмы, здесь тебе придется думать логично, так как любое неправильное действие от тебя - ты проиграешь игру. Готов?'
        else:

            play_game(res, req)


def play_game(res, req):

    user_id = req['session']['user_id']

    res['response']['card']['title'] = 'Вы находитесь в камере для заключенных, охранник повел вас в столовую, как вы пойдете?'
    res['response']['buttons'] = [
        {
            'title': 'Смирно',
            'hide': True
        },
        {
            'title': 'Попытаюсь вырваться',
            'hide': True
        },
        {
            'title': 'Помощь',
            'hide': True
        }
    ]
    if req == 'Смирно':

        res['response']['text'] = 'Вы прошли в столовую. Здесь есть несколько выходов, куда вы пойдете?'
        res['response']['buttons'] = [
            {
                'title': 'Прямо',
                'hide': True

            },
            {
                'title': 'Налево',
                'hide': True

            },
            {
                'title': 'Направо',
                'hide': True

            },
            {
                'title': 'Помощь',
                'hide': True
            }
        ]
        if req == 'Прямо':

            res['response']['text'] = 'Вы увидели небо и солнце, ослепляющее своими лучами ваши глаза. Впереди вы видите главный выход их тюрьмы, а слева тропинка ведет ко двору, что вы будете делать?'
            res['response']['buttons'] = [
                {
                    'title': 'К выходу',
                    'hide': True

                },
                {
                    'title': 'Во двор',
                    'hide': True

                },
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]

            if req == 'Во двор':

                res['response']['text'] = 'Вы увидели двух заключенных, один строго режима, другой среднего, к кому подойдете поговорить?'
                res['response']['buttons'] = [
                    {
                        'title': 'К строгому',
                        'hide': True

                    },
                    {
                        'title': 'К среднему',
                        'hide': True

                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                    }
                ]

                if req == 'К среднему':

                    res['response'][
                        'text'] = 'Вы рассказываете ему про план побега. Он готовит для вас нужные инструменты и вы спокойно сбегаете из тюрьмы.'
                    res['response'][
                        'text'] = 'Поздравляю, вы выйграли! Концовка №1'
                    return

                else:

                    res['response'][
                        'text'] = 'You died. Вы говорите ему про свой план побега, но он рассказывает про это охранникам, так как злой из-за того, что его посадили сюда ни за что.'
                    res['response']['buttons'] = [
                        {
                            'title': 'Помощь',
                            'hide': True
                        }
                    ]
                    return

            else:

                res['response']['text'] = 'You died. Охранники увидели, как вы направляетесь к выходу - Попытка побега.'
                return

        if req == 'Налево':

            res['response']['text'] = 'You died. Вы увидели, как вашего брата бьют, вступились за него и вас посадили'
            return

        if req == 'Направо':

            res['response']['text'] = 'Вы нашли большой блок камер. К заключенному с каким режимом вы подойдете, чтобы обговорить побег?'
            res['response']['buttons'] = [
                {
                    'title': 'К легкому',
                    'hide': True

                },
                {
                    'title': 'К среднему',
                    'hide': True

                },
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]
            if req == 'К строгому':

                res['response'][
                    'text'] = 'Вы рассказываете ему про план побега. Он готовит для вас нужные инструменты и вы спокойно сбегаете из тюрьмы.'
                res['response'][
                    'text'] = 'Поздравляю, вы выйграли! Концовка №2'
                return

            else:

                res['response'][
                    'text'] = 'You died. Он был крысой.'
                return

    else:

        res['response']['text'] = 'You died. Охранник посадил вас в карцер'
        return



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