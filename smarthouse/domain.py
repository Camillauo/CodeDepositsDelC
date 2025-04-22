from datetime import datetime
from random import random
from typing import List, Optional, Union
from abc import abstractmethod


class Measurement:


    def __init__(self, timestamp: str, value: float, unit: str) -> None:
        self.timestamp = timestamp
        self.value = value
        self.unit = unit


class Device:

    def __init__(self, id: str, model_name: str, supplier: str, device_type: str):
        self.id = id
        self.model_name = model_name
        self.supplier = supplier
        self.device_type = device_type
        self.room: Optional[Room] = None

    def get_device_type(self) -> str:
        return self.device_type

    @abstractmethod
    def is_actuator(self) -> bool:
        pass

    @abstractmethod
    def is_sensor(self) -> bool:
        pass


class Sensor(Device):

    def __init__(self, id: str, model_name: str, supplier: str, device_type: str, unit: str = ""):
        super().__init__(id, model_name, supplier, device_type)
        self.unit = unit

    def is_sensor(self) -> bool:
        return True

    def is_actuator(self) -> bool:
        return False

    def last_measurement(self) -> Measurement:
        return Measurement(datetime.now().isoformat(), random() * 10, self.unit)


class Actuator(Device):

    def __init__(self, id: str, model_name: str, supplier: str, device_type: str):
        super().__init__(id, model_name, supplier, device_type)
        self.state: Union[float, bool] = False

    def is_actuator(self) -> bool:
        return True

    def is_sensor(self) -> bool:
        return False

    def turn_on(self, target_value: Optional[float] = None):
        if target_value:
            self.state = target_value
        else:
            self.state = True

    def turn_off(self):
        self.state = False

    def is_active(self) -> bool:
        return self.state is not False


class ActuatorWithSensor(Actuator, Sensor):

    def __init__(self, id: str, model_name: str, supplier: str, device_type: str):
        super().__init__(id, model_name, supplier, device_type)

    def is_actuator(self) -> bool:
        return True

    def is_sensor(self) -> bool:
        return True


class Floor:

    def __init__(self, level):
        self.level = level
        self.rooms = []


class Room:

    def __init__(self, floor: Floor, room_size: float, room_name: Optional[str]):
        self.floor = floor
        self.room_size = room_size
        self.room_name = room_name
        self.devices: List[Device] = []


class SmartHouse:


    def __init__(self) -> None:
        self.floors: List[Floor] = []

    def register_floor(self, level: int) -> Floor:

        floor = Floor(level)
        self.floors.append(floor)
        return floor

    def register_room(self, floor: Floor, room_size: float, room_name: Optional[str] = None) -> Room:

        room = Room(floor, room_size, room_name)
        floor.rooms.append(room)
        return room

    def get_floors(self) -> List[Floor]:

        return self.floors

    def get_rooms(self) -> List[Room]:

        result = []
        for f in self.floors:
            result.extend(f.rooms)
        return result

    def get_area(self) -> float:

        result = 0.0
        for r in self.get_rooms():
            result += r.room_size
        return result

    def register_device(self, room: Room, device: Device):

        old_room = device.room
        if old_room:
            old_room.devices.remove(device)
        room.devices.append(device)
        device.room = room

    def get_devices(self) -> List[Device]:

        result = []
        for r in self.get_rooms():
            result.extend(r.devices)
        return result

    def get_device_by_id(self, device_id: str) -> Optional[Device]:

        for d in self.get_devices():
            if d.id == device_id:
                return d
        return None
