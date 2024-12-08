from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import time
import threading

app = FastAPI()

# 允许的前端地址（CORS配置）
origins = [
    "*",  # 允许的前端地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


# 房间数据模型
class Room(BaseModel):
    roomNumber: int
    isPoweredOn: bool
    currentTemperature: float
    targetTemperature: float
    mode: str  # 'Cooling' or 'Heating'
    windSpeed: str  # 'Low', 'Medium', 'High'
    costRate: float  # 每度的费用


# 模拟数据库中的5个房间
rooms = [
    Room(roomNumber=101, isPoweredOn=False, currentTemperature=32, targetTemperature=25, mode='Cooling',
         windSpeed='Medium', costRate=1),
    Room(roomNumber=102, isPoweredOn=False, currentTemperature=28, targetTemperature=25, mode='Cooling',
         windSpeed='Medium', costRate=1),
    Room(roomNumber=103, isPoweredOn=False, currentTemperature=30, targetTemperature=25, mode='Cooling',
         windSpeed='Medium', costRate=1),
    Room(roomNumber=104, isPoweredOn=False, currentTemperature=29, targetTemperature=25, mode='Cooling',
         windSpeed='Medium', costRate=1),
    Room(roomNumber=105, isPoweredOn=False, currentTemperature=35, targetTemperature=25, mode='Cooling',
         windSpeed='Medium', costRate=1)
]


# 查询房间信息
@app.get("/api/room_info", response_model=List[Room])
async def get_room_info():
    return rooms


# 开启空调
class TurnOnRequest(BaseModel):
    room_number: int


@app.post("/api/turnOn")
async def turn_on_ac(request: TurnOnRequest):
    room = next((r for r in rooms if r.roomNumber == request.room_number), None)
    if room:
        room.isPoweredOn = True
        return {"message": "空调已开启", "room": room}
    raise HTTPException(status_code=404, detail="房间不存在")


# 关闭空调
class TurnOffRequest(BaseModel):
    room_number: int


@app.post("/api/turnOff")
async def turn_off_ac(request: TurnOffRequest):
    room = next((r for r in rooms if r.roomNumber == request.room_number), None)
    if room:
        room.isPoweredOn = False
        return {"message": "空调已关闭", "room": room}
    raise HTTPException(status_code=404, detail="房间不存在")


# 设置目标温度
class SetTemperatureRequest(BaseModel):
    room_number: int
    target_temperature: float


@app.post("/api/set_temperature")
async def set_temperature(request: SetTemperatureRequest):
    room = next((r for r in rooms if r.roomNumber == request.room_number), None)
    if room:
        room.targetTemperature = request.target_temperature
        return {"message": "目标温度已设置", "room": room}
    raise HTTPException(status_code=404, detail="房间不存在")


# 设置风速
class SetWindSpeedRequest(BaseModel):
    room_number: int
    wind_speed: str


@app.post("/api/set_wind_speed")
async def set_wind_speed(request: SetWindSpeedRequest):
    room = next((r for r in rooms if r.roomNumber == request.room_number), None)
    if room:
        room.windSpeed = request.wind_speed
        return {"message": "风速已设置", "room": room}
    raise HTTPException(status_code=404, detail="房间不存在")


# 设置模式（制热/制冷）
class SetModeRequest(BaseModel):
    room_number: int
    mode: str


@app.post("/api/set_mode")
async def set_mode(request: SetModeRequest):
    room = next((r for r in rooms if r.roomNumber == request.room_number), None)
    if room:
        if request.mode not in ['Cooling', 'Heating']:
            raise HTTPException(status_code=400, detail="无效的模式")
        room.mode = request.mode
        if room.mode == 'Cooling':
            room.targetTemperature = 25  # Cooling模式下默认目标温度为25°C
        elif room.mode == 'Heating':
            room.targetTemperature = 22  # Heating模式下默认目标温度为22°C
        return {"message": "模式已设置", "room": room}
    raise HTTPException(status_code=404, detail="房间不存在")


# 温度变化逻辑（根据风速每10秒变化）
def update_temperature(room: Room):
    if not room.isPoweredOn:
        return

    if room.windSpeed == 'Low':
        room.currentTemperature -= 0.33  # 低风速下每10秒降低0.33°C
    elif room.windSpeed == 'Medium':
        room.currentTemperature -= 0.5  # 中风速下每10秒降低0.5°C
    elif room.windSpeed == 'High':
        room.currentTemperature -= 1  # 高风速下每10秒降低1°C


# 定时更新温度，每10秒钟更新一次，并打印房间状态
def temperature_update_thread():
    while True:
        time.sleep(10)  # 每10秒钟更新一次
        for room in rooms:
            update_temperature(room)

        # 每 10 秒钟打印出当前的房间数据
        print("=== 当前房间状态 ===")
        for room in rooms:
            print(f"房间 {room.roomNumber}:")
            print(f"  开关机状态: {'开机' if room.isPoweredOn else '关机'}")
            print(f"  当前温度: {room.currentTemperature:.2f} °C")
            print(f"  目标温度: {room.targetTemperature} °C")
            print(f"  风速: {room.windSpeed}")
            print(f"  模式: {room.mode}")
        print("=====================")


# 启动温度更新线程
thread = threading.Thread(target=temperature_update_thread, daemon=True)
thread.start()

# 启动 FastAPI 服务器
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
