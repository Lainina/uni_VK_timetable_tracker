from src.database.database import Timetable


class RedemptionBot:
    def __init__(self):
        self.schedule = Timetable("timetable.json")

    def send_message(self, chat_id: str, text: str):
        pass

    def delete_message(self, chat_id: str, message_id: str):
        pass
