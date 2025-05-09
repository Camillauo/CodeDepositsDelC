import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from smarthouse.persistence import SmartHouseRepository

app = FastAPI()


def setup_database():
    project_dir = Path(__file__).parent.parent
    db_file = project_dir / "data" / "db.sql"
    return SmartHouseRepository(str(db_file.absolute()))

repo = setup_database()
smarthouse = repo.load_smarthouse_deep()


class MeasurementInput(BaseModel):
    value: float

class ActuatorUpdate(BaseModel):
    state: str



@app.get("/smarthouse/")
def get_smarthouse():
    return {
        "floors": len(smarthouse.get_floors()),
        "rooms": len(smarthouse.get_rooms()),
        "devices": len(smarthouse.get_devices()),
        "area": smarthouse.get_area()
    }

@app.get("/smarthouse/floor")
def get_floors():
    return [{"floor_id": f.id, "rooms": len(f.rooms)} for f in smarthouse.get_floors()]

@app.get("/smarthouse/floor/{fid}")
def get_floor(fid: int):
    floor = smarthouse.get_floor_by_id(fid)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return {
        "floor_id": floor.id,
        "area": floor.get_area(),
        "rooms": [r.name for r in floor.rooms]
    }

@app.get("/smarthouse/floor/{fid}/room")
def get_rooms_in_floor(fid: int):
    floor = smarthouse.get_floor_by_id(fid)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return [{"room_id": r.id, "name": r.name, "area": r.area} for r in floor.rooms]

@app.get("/smarthouse/floor/{fid}/room/{rid}")
def get_room(fid: int, rid: int):
    floor = smarthouse.get_floor_by_id(fid)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    room = next((r for r in floor.rooms if r.id == rid), None)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "room_id": room.id,
        "name": room.name,
        "area": room.area,
        "devices": [d.name for d in room.devices]
    }

@app.get("/smarthouse/device")
def get_all_devices():
    return [{
        "uuid": d.uuid,
        "name": d.name,
        "type": d.device_type,
        "manufacturer": d.manufacturer
    } for d in smarthouse.get_devices()]

@app.get("/smarthouse/device/{uuid}")
def get_device(uuid: str):
    device = smarthouse.get_device_by_uuid(uuid)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        "uuid": device.uuid,
        "name": device.name,
        "type": device.device_type,
        "manufacturer": device.manufacturer
    }



@app.get("/smarthouse/sensor/{uuid}/current")
def get_current_sensor_measurement(uuid: str):
    sensor = smarthouse.get_sensor_by_uuid(uuid)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    current = sensor.get_current_measurement()
    return {
        "uuid": sensor.uuid,
        "name": sensor.name,
        "current_measurement": current
    }

@app.post("/smarthouse/sensor/{uuid}/current")
def add_sensor_measurement(uuid: str, measurement: MeasurementInput):
    sensor = smarthouse.get_sensor_by_uuid(uuid)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    sensor.add_measurement(measurement.value)
    return {"status": "added", "value": measurement.value}

@app.get("/smarthouse/sensor/{uuid}/values")
def get_sensor_values(uuid: str, limit: Optional[int] = None):
    sensor = smarthouse.get_sensor_by_uuid(uuid)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    values = sensor.get_measurements()
    if limit:
        values = values[-limit:]
    return values

@app.delete("/smarthouse/sensor/{uuid}/oldest")
def delete_oldest_measurement(uuid: str):
    sensor = smarthouse.get_sensor_by_uuid(uuid)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    removed = sensor.remove_oldest_measurement()
    return {"removed": removed}



@app.get("/smarthouse/actuator/{uuid}/current")
def get_actuator_state(uuid: str):
    actuator = smarthouse.get_actuator_by_uuid(uuid)
    if not actuator:
        raise HTTPException(status_code=404, detail="Actuator not found")
    return {
        "uuid": actuator.uuid,
        "state": actuator.get_state()
    }

@app.put("/smarthouse/device/{uuid}")
def update_actuator_state(uuid: str, update: ActuatorUpdate):
    actuator = smarthouse.get_actuator_by_uuid(uuid)
    if not actuator:
        raise HTTPException(status_code=404, detail="Actuator not found")
    actuator.set_state(update.state)
    return {
        "status": "updated",
        "new_state": update.state
    }


@app.get("/hello")
async def hello():
    return {"message": "Hello, World!"}
