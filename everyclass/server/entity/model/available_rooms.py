import datetime
from dataclasses import dataclass
from typing import List

from everyclass.rpc import ensure_slots
from everyclass.rpc.entity import Entity
from everyclass.server.entity.domain import get_semester_date
from everyclass.server.utils import JSONSerializable
from everyclass.server.utils.encryption import encrypt, RTYPE_ROOM


@dataclass
class Room(JSONSerializable):
    name: str  # 教室名
    room_id: str  # 教室 ID
    room_id_encoded: str  # 编码后的教室 ID

    def __json_encode__(self):
        return {'name': self.name, 'room_id_encoded': self.room_id_encoded}

    @classmethod
    def make(cls, name: str, room_id: str):
        dct = {'name': name, 'room_id': room_id, 'room_id_encoded': encrypt(RTYPE_ROOM, room_id)}
        return cls(**ensure_slots(cls, dct))


class AvailableRooms(JSONSerializable):

    def __json_encode__(self):
        return {'rooms': self.rooms}

    def __init__(self, campus: str, building: str, date: datetime.date, time: str):
        _, week, day = get_semester_date(date)

        resp = Entity.get_available_rooms(week, f"{day + 1}{time}", campus, building)

        self.rooms: List[Room] = []
        for r in resp:
            # 反馈占用计数

            self.rooms.append(Room.make(name=r['name'], room_id=r['code']))