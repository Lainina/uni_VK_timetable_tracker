import requests
from src.core.vk.token import VK_TOKEN


class VkApiHandler:
    def __init__(self, token: str):
        self.token = token
        self.version = '5.131'
        self.api_url = 'https://api.vk.com/method/'

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


vk = VkApiHandler(token=VK_TOKEN)
