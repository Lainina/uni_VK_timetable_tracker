from dataclasses import dataclass

import requests

from config import TEST_CHAT_ID_1
from src.core.logger.logger import logger


@dataclass
class Server:
    key: str
    server_url: str
    ts: str


@dataclass
class EvenObject:
    peer_id: int
    message_id: int


@dataclass
class Message(EvenObject):
    text: str


@dataclass
class MessageEvent(EvenObject):
    user_id: int
    event_id: str
    payload: dict

    def __post_init__(self):
        self.command = self.payload['command']
        self.menu = self.payload.get('menu', [])


class VkApiHandler:
    def __init__(self, token: str, api_version, chat_id: int = TEST_CHAT_ID_1):
        self.token = token
        self.version = api_version
        self.api_url = 'https://api.vk.com/method/'
        self.group_id = '219138476'
        self.chat_id = chat_id

    def send_message(self, text: str, peer_id: int = None, keyboard: dict = None) -> int:
        if peer_id is None:
            peer_id = self.chat_id

        params = {'peer_ids': str(peer_id),
                  'random_id': '0',
                  'message': text,
                  'access_token': self.token,
                  'v': self.version}
        url = self.api_url + 'messages.send'

        response = requests.post(url=url, params=params, data=keyboard)

        if response.json().get('error', {}):
            logger.error('Could not send message: %s. Error: %s', text, response.json().get('error', {}))
            return 0

        message_id = response.json().get('response', {})[0].get('conversation_message_id', {})
        logger.info('Sent message: %s, id = %s', text, message_id)

        return message_id

    def edit_message(self, text: str, peer_id: int, message_id: int, keyboard: dict = None) -> None:
        params = {'peer_id': peer_id,
                  'conversation_message_id': message_id,
                  'message': text,
                  'access_token': self.token,
                  'v': self.version}

        url = self.api_url + 'messages.edit'

        response = requests.post(url=url, params=params, data=keyboard)

        if response.json().get('error', {}):
            logger.error('Could not edit message: %s. Error: %s', text, response.json().get('error', {}))
            return

        logger.debug('Edited message: %s', text)

    def send_message_event_answer(self, event: MessageEvent, event_data: dict) -> None:
        params = {'event_id': event.event_id,
                  'user_id': event.user_id,
                  'peer_id': event.peer_id,
                  'event_data': event_data,
                  'access_token': self.token,
                  'v': self.version}
        url = self.api_url + 'messages.sendMessageEventAnswer'

        response = requests.post(url=url, params=params, data=event_data)

        if response.json().get('error', {}):
            logger.error('Could not send event answer. Error: %s', response.json().get('error', {}))
            return

        logger.info('Sent event answer: %s', event_data)

    def delete_message(self, message_id: int, peer_id: int = None) -> None:
        if not peer_id:
            peer_id = self.chat_id

        params = {'peer_id': str(peer_id),
                  'cmids': str(message_id),
                  'delete_for_all': '1',
                  'access_token': self.token,
                  'v': self.version}
        url = self.api_url + 'messages.delete'
        response = requests.get(url=url, params=params)

        if response.json().get('error', {}):
            logger.error('Could not delete message: %s', str(message_id))
            return
        return

    def get_longpoll_server(self) -> Server:
        params = {'group_id': self.group_id,
                  'access_token': self.token,
                  'v': self.version}
        url = self.api_url + 'groups.getLongPollServer'
        response = requests.get(url=url, params=params)

        if response.json().get('error', {}):
            logger.error('Could not get longpoll server')
            raise RuntimeError('getLongPollServer returned error')

        server = response.json().get('response', {})

        key = server.get('key', {})
        server_url = server.get('server', {})
        ts = server.get('ts', {})

        return Server(key, server_url, ts)

    def poll(self, server: Server) -> (str, list[Message], list[MessageEvent]):
        params = {'act': 'a_check',
                  'key': server.key,
                  'ts': server.ts,
                  'wait': 25}
        response = requests.get(url=server.server_url, params=params)

        if response.json().get('failed', {}):
            logger.warning('Failed to get updates, trying again...')
            try:
                server = self.get_longpoll_server()
            except RuntimeError:
                logger.critical('Could not restart server, terminating...')
                raise

            params['key'] = server.key
            params['ts'] = server.ts

            response = requests.get(url=server.server_url, params=params)

            if response.json().get('failed', {}):
                logger.critical('Failed to get updates twice, terminating...')
                raise RuntimeError('server poll failed twice')

            logger.warning('Connection restored')

        response = response.json()

        server.ts = response['ts']
        messages, message_events = [], []
        for update in response['updates']:
            if update['type'] == 'message_new':
                info = update['object']['message']
                message = Message(info['peer_id'], info['conversation_message_id'], info['text'])
                messages.append(message)
            elif update['type'] == 'message_event':
                info = update['object']
                message_event = MessageEvent(info['peer_id'], info['conversation_message_id'],
                                             info['user_id'], info['event_id'], info['payload'])
                message_events.append(message_event)

        return server, messages, message_events

    def get_first_server(self) -> Server:
        try:
            server = self.get_longpoll_server()
            return server
        except RuntimeError:
            logger.critical('Failed to start polling')
            raise
