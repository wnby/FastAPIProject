from tortoise import Tortoise
from tortoise.functions import Sum
from app.config import bupt_hotel_config
from app.sql_utils.schema import Room, DetailedRecord

DATABASE_URL = "sqlite:///D:/pycharm/FastAPIProject/app/hotel_management.db"


async def init_db():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["app.sql_utils.schema"]}
    )
    await Tortoise.generate_schemas()

    # 初始化房间数据
    room_count = await Room.all().count()
    if room_count == 0:
        # 如果数据库为空，则初始化房间
        for i in range(1, bupt_hotel_config.hotel_layers + 1):
            for j in range(1, bupt_hotel_config.room_per_layer + 1):
                room_number_int = i * 100 + j
                await Room.create(
                    room_number=room_number_int,  # 房间号
                    status='available'            # 默认房间状态是 'available'
                )

async def close_db():
    await Tortoise.close_connections()

async def summarize_bill(room_number: int, client_name: str) -> float:
    result = await DetailedRecord.filter(room_number=room_number, user_name=client_name).annotate(total_amount=Sum('amount')).first()
    if result:
        return result.total_amount
    return -1.0
