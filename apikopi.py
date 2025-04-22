import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from smarthouse.persistence import SmartHouseRepository
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException
from smarthouse.persistence import SmartHouseRepository
from pathlib import Path

app = FastAPI()

def setup_database():
    project_dir = Path(__file__).parent.parent
    db_file = project_dir / "data" / "db.sql"
    return SmartHouseRepository(str(db_file.absolute()))

repo = setup_database()
smarthouse = repo.load_smarthouse_deep()



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

@app.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional



@app.get("/smarthouse/sensor/{uuid}/current")
def get_current_sensor_measurement(uuid: str):
    sensor = smarthouse.get_sensor_by_uuid(uuid)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    current_measurement = sensor.get_current_measurement()
    return {
        "uuid": sensor.uuid,
        "name": sensor.name,
        "current_measurement": current_measurement
    }
