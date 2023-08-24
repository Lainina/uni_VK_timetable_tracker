import requests
from src.core.vk.token import VK_TOKEN
# TODO: add logging, replace all prints with logs


class VkApiHandler:
    def __init__(self, token: str):
        self.token = token
        self.version = '5.131'
        self.api_url = 'https://api.vk.com/method/'
        self.group_id = '219138476'

    def send_message(self, text: str, peer_id=2000000002) -> int:
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

    def delete_message(self, peer_id: int, message_id: int) -> None:
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

    def get_longpoll_server(self) -> dict[str, str]:
        params = {'group_id': self.group_id,
                  'access_token': self.token,
                  'v': self.version}
        url = self.api_url + 'groups.getLongPollServer'
        response = requests.get(url=url, params=params)

        if response.json().get('error', {}):
            print('error: could not get long poll server')
            return {}

        return response.json().get('response', {})

    def poll(self, key: str, server_url: str, ts: str) -> dict:
        params = {'act': 'a_check',
                  'key': key,
                  'ts': ts,
                  'wait': 25}
        response = requests.get(url=server_url, params=params)

        if response.json().get('failed', {}):
            print('warning: failed to get updates, trying again...')
            server = self.get_longpoll_server()

            if not server:
                print('error: could not restart server, terminating...')
                return {}

            params.update(server)
            server_url = params.pop('server')
            response = requests.get(url=server_url, params=params)

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

        key = server.get('response', {}).get('key', {})
        server_url = server.get('response', {}).get('server', {})
        ts = server.get('response', {}).get('ts', {})

        while True:
            updates = self.poll(key, server_url, ts)

            if not updates:
                print('terminal error: longpoll connection terminated')
                return

            ts = updates['ts']
            messages = updates['messages']

            if messages:
                for message in messages:
                    pass    # TODO: handle messages somehow


vk = VkApiHandler(token=VK_TOKEN)
