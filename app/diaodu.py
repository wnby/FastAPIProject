from pydantic import BaseModel
import datetime
from collections import deque
import asyncio
import threading
from backend_py.scheduler.schedule_struct import ScheduleItem, DBQueueItem, ScheduleTask
from backend_py.sql_utils import DetailedRecord, User
from backend_py.scheduler.schedule_cache import ScheduleCache
from backend_py.sql_utils.db_utils import summarize_bill
from loguru import logger

# 线程安全的队列
schedule_task_queue: deque[ScheduleTask] = deque([])  # 用于任务队列
task_queue_lock = threading.Lock()

# 服务队列和等待队列的大小
serving_queue_size = 10  # 假设最多有10个房间同时服务
serving_queue: deque[ScheduleItem] = deque([], maxlen=serving_queue_size)
waiting_queue_size = 20  # 假设最多有20个房间在等待
waiting_queue: deque[ScheduleItem] = deque([], maxlen=waiting_queue_size)

# 数据库持久化队列
db_queue: deque[DBQueueItem] = deque([])

# 缓存
schedule_cache = ScheduleCache()

# 记录时间
last_step_time: datetime.datetime = None


def query_serving_queue(log_level: str = "debug"):
    global serving_queue, waiting_queue
    served_rooms = [item.room_number for item in serving_queue]
    waited_rooms = [item.room_number for item in waiting_queue]
    if log_level == "debug":
        logger.debug(f"Serving queue: {served_rooms}, Waiting queue: {waited_rooms}")
    return served_rooms, waited_rooms


async def add_record(item: ScheduleItem):
    """将服务记录持久化到数据库"""
    room_number = item.room_number
    duration = item.end_time - item.start_time
    bill_rate = {"low": 0.1, "medium": 0.2, "high": 0.3}

    user = await User.filter(room_number=room_number).first()
    if user:
        user_name = user.name  # 获取用户名
    else:
        logger.error(f"Room {room_number} has no associated user. Using 'Guest'.")
        user_name = "Guest"  # 默认用户名为 'Guest'

    amount = (duration.total_seconds() / 60) * bill_rate.get(item.last_speed, 0)  # 按分钟计费

    # 持久化到 DetailedRecord 表
    await DetailedRecord.create(
        user_name=user_name,
        room_number=room_number,
        serving_speed=item.last_speed,
        start_time=item.start_time,
        end_time=item.end_time,
        amount=amount
    )
    logger.info(f"Recorded charge for room {room_number}: {user_name}, {amount:.2f} USD")


async def handle_task_queue():
    """处理调度队列中的任务"""
    global schedule_task_queue, schedule_cache, db_queue, waiting_queue, serving_queue
    with task_queue_lock:
        while len(schedule_task_queue) > 0:
            task = schedule_task_queue.popleft()

            room_number = task.room_number
            op_type = task.op_type
            op_value = task.op_value

            if op_type == "temperature":
                # 调整温度
                schedule_cache.update_temperature(str(room_number), op_value)
                db_queue.append(DBQueueItem(room_number=room_number, op_type=op_type, op_value=op_value))

            elif op_type == "speed":
                # 调整风速
                schedule_cache.update_speed(str(room_number), op_value)

            elif op_type == "off":
                # 关闭房间
                schedule_cache.remove_room(str(room_number))
                for item in serving_queue:
                    if item.room_number == room_number:
                        item.end_time = datetime.datetime.now()
                        await add_record(item)  # 记录服务结束
                        serving_queue.remove(item)
                        break
                for item in waiting_queue:
                    if item.room_number == room_number:
                        waiting_queue.remove(item)
                        break

            else:
                logger.error(f"Unknown operation type: {op_type}")


async def step_queue():
    """执行队列步骤，处理服务中的房间"""
    global serving_queue, waiting_queue
    if len(serving_queue) == 0 and len(waiting_queue) == 0:
        return  # 没有任务，不进行任何处理

    if len(waiting_queue) > 0 and len(serving_queue) < serving_queue_size:
        # 从等待队列移一个房间到服务队列
        join_item = waiting_queue.popleft()
        join_item.start_time = datetime.datetime.now()  # 更新开始时间
        serving_queue.append(join_item)

    if len(serving_queue) > 0:
        # 服务队列的第一个房间处理完毕，移除并记录
        leaving_item = serving_queue.popleft()
        leaving_item.end_time = datetime.datetime.now()  # 结束时间
        await add_record(leaving_item)  # 持久化记录
        if len(waiting_queue) > 0:
            # 继续处理等待队列
            next_item = waiting_queue.popleft()
            next_item.start_time = datetime.datetime.now()
            serving_queue.append(next_item)


async def step():
    """调度任务执行一步"""
    await handle_task_queue()  # 处理调度队列中的任务
    await step_queue()  # 执行队列步骤
    query_serving_queue(log_level="debug")  # 查询并打印当前的服务和等待队列状态


def scheduler_thread_func():
    global last_step_time
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    last_step_time = datetime.datetime.now()

    while True:
        now_time = datetime.datetime.now()
        if (now_time - last_step_time).total_seconds() >= 1:
            loop.run_until_complete(step())  # 每秒执行一次
            last_step_time = now_time
        else:
            loop.run_until_complete(asyncio.sleep(0.2))  # 避免CPU过于繁忙
