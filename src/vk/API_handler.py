import requests
from config import TEST_CHAT_ID_1
from dataclasses import dataclass


# TODO: add logging, replace all prints with logs

@dataclass
class Server:
    key: str
    server_url: str
    ts: str


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
            print('error: could not send message')
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
            print('error: could not delete message')
            return
        return

    def get_longpoll_server(self) -> Server | None:
        params = {'group_id': self.group_id,
                  'access_token': self.token,
                  'v': self.version}
        url = self.api_url + 'groups.getLongPollServer'
        response = requests.get(url=url, params=params)

        if response.json().get('error', {}):
            print('error: could not get long poll server')
            return

        server = response.json().get('response', {})

        key = server.get('key', {})
        server_url = server.get('server', {})
        ts = server.get('ts', {})

        return Server(key, server_url, ts)

    def poll(self, server: Server) -> dict[str, str | dict[str, str | int]]:
        params = {'act': 'a_check',
                  'key': server.key,
                  'ts': server.ts,
                  'wait': 25}
        response = requests.get(url=server.server_url, params=params)

        if response.json().get('failed', {}):
            print('warning: failed to get updates, trying again...')
            server = self.get_longpoll_server()

            if not server:
                print('error: could not restart server, terminating...')
                return {}

            params['key'] = server.key
            params['ts'] = server.ts

            response = requests.get(url=server.server_url, params=params)

            if response.json().get('failed', {}):
                print('error: failed to get updates twice, terminating...')
                return {}
            print('warning: connection restored')

        # TODO: format the info from response and return it
        return {'ts': '7566', 'messages': [{'peer_id': 200000002, 'message_id': 17800, 'text': 'Это тест'}]}

    def start_polling(self):
        server = self.get_longpoll_server()

        if not server:
            print('error: failed to start polling')
            return

        while True:
            updates = self.poll(server)

            if not updates:
                print('terminal error: longpoll connection terminated')
                return

            server.ts = updates['ts']
            messages = updates['messages']

            if messages:
                for message in messages:
                    pass  # TODO: handle messages somehow
