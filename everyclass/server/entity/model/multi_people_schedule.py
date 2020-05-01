import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

from everyclass.server.entity import domain
from everyclass.server.utils import JSONSerializable


@dataclass
class Event(JSONSerializable):
    name: str
    room: str

    def __json_encode__(self):
        return {'name': self.name, 'room': self.room}


@dataclass
class MultiPeopleSchedule(JSONSerializable):
    schedules: List[Dict[str, Optional[Event]]]
    accessible_people: List[str]
    inaccessible_people: List[str]

    def __json_encode__(self):
        return {'schedules': self.schedules,
                'inaccessible_people': self.inaccessible_people,
                'accessible_people': self.accessible_people}

    def __init__(self, people: List[str], date: datetime.date, current_user: str):
        """多人日程展示。输入学号或教工号列表及日期，输出多人在当天的日程"""
        from everyclass.server import logger
        from everyclass.server.entity import service
        from everyclass.server.user import service as user_service

        accessible_people = []
        inaccessible_people = []

        for identifier in people:
            if user_service.has_access(identifier, current_user):
                accessible_people.append(identifier)
            else:
                inaccessible_people.append(identifier)

        self.schedules = list()

        for identifier in accessible_people:
            is_student, _ = service.get_people_info(identifier)
            semester, week, day = domain.get_semester_date(date)
            if is_student:
                cards = service.get_student_timetable(identifier, semester).cards
            else:
                cards = service.get_teacher_timetable(identifier, semester).cards

            cards = filter(lambda c: week in c.weeks and c.lesson[0] == str(day), cards)  # 用日期所属的周次和星期过滤card

            event_dict = {}
            for card in cards:
                time = card.lesson[1:5]  # "10102" -> "0102"
                if time not in event_dict:
                    event_dict[time] = Event(name=card.name, room=card.room)
                else:
                    # 课程重叠
                    logger.warning("time of card overlapped", extra={'people_identifier': identifier,
                                                                     'date': date})

            # 给没课的位置补充None
            for i in range(1, 10, 2):
                key = f"{i:02}{i + 1:02}"
                if key not in event_dict:
                    event_dict[key] = None

            self.schedules.append(event_dict)
            self.inaccessible_people = inaccessible_people
            self.accessible_people = accessible_people