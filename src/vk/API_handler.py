import requests
from config import TEST_CHAT_ID_1
from dataclasses import dataclass
from src.core.logger.logger import logger


@dataclass
class Server:
    key: str
    server_url: str
    ts: str


@dataclass
class Message:
    peer_id: int
    message_id: int
    text: str


class VkApiHandler:
    def __init__(self, token: str, chat_id: int = TEST_CHAT_ID_1):
        self.token = token
        self.version = '5.131'
        self.api_url = 'https://api.vk.com/method/'
        self.group_id = '219138476'
        self.chat_id = chat_id

    def send_message(self, text: str, peer_id: int = 0) -> int:
        if not peer_id:
            peer_id = self.chat_id

        params = {'peer_ids': str(peer_id),
                  'random_id': '0',
                  'message': text,
                  'access_token': self.token,
                  'v': self.version}
        url = self.api_url + 'messages.send'
        response = requests.get(url=url, params=params)

        if response.json().get('error', {}):
            logger.error('Could not send message: %s', text)
            return 0

        message_id = response.json().get('response', {})[0].get('conversation_message_id', {})

        return message_id

    def delete_message(self, message_id: int, peer_id: int = 0) -> None:
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

    def poll(self, server: Server) -> (str, list[Message]):
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
        messages = []
        for update in response['updates']:
            info = update['object']['message']

            message = Message(info['peer_id'], info['conversation_message_id'], info['text'])

            messages.append(message)

        return server, messages

    def get_first_server(self) -> Server:
        try:
            server = self.get_longpoll_server()
            return server
        except RuntimeError:
            logger.critical('Failed to start polling')
            raise
