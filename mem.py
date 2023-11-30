import os

from datetime import datetime, timedelta
from filelock import FileLock

START: datetime = datetime.utcnow()
O_DEATH: timedelta = timedelta(seconds=int(os.getenv("O_DEATH", 10)))
MEMORY_PATH = "/tmp/o.memory.txt"
MEMORY_LOCK_PATH = "/tmp/o.memory.lock"
MEMORY_MAX_SIZE = 4096  # bytes
MAX_STEPS = 100
STEPS = 0


def timestamp(log: str) -> str:
    return f"{datetime.utcnow().timestamp()}{log}"


def check_alive(name: str):
    global STEPS
    print(timestamp(f"{name} step {STEPS} of {MAX_STEPS}"))
    STEPS += 1
    if STEPS > MAX_STEPS:
        print(timestamp(f"{name} max steps {MAX_STEPS} exceeded"))
        return False
    if datetime.utcnow() - START > O_DEATH:
        print(timestamp(f"{name} death seconds {O_DEATH} exceeded"))
        return False
    return True


async def check_memory() -> str:
    log = ""
    if not os.path.exists(MEMORY_PATH):
        # log += timestamp("📜 Memory file not found, creating ...")
        with open(MEMORY_PATH, "w") as f:
            f.write("")
    else:
        mem_size = os.path.getsize(MEMORY_PATH)
        # log += timestamp(f"💾 Current memory size is {mem_size} bytes")
        if mem_size > MEMORY_MAX_SIZE:
            # log += timestamp(f"🗑️ Memory limit {MEMORY_MAX_SIZE} exceeded, truncating past")
            with FileLock(MEMORY_LOCK_PATH):
                with open(MEMORY_PATH, "r") as file:
                    lines = file.readlines()
                half_index = len(lines) // 2
                with open(MEMORY_PATH, "w") as file:
                    file.writelines(lines[half_index:])
    # print(log)
    return log


async def get_memory() -> (str, str):
    log = await check_memory()
    with FileLock(MEMORY_LOCK_PATH):
        with open(MEMORY_PATH, "r") as f:
            memraw = f.read()
    return log, f"Here is the robot memory (the more recent robot memories are at the bottom):\n<memory>\n{memraw}\n</memory"


async def add_memory(txt: str) -> str:
    log = await check_memory()
    with FileLock(MEMORY_LOCK_PATH):
        with open(MEMORY_PATH, "a") as f:
            f.write(timestamp(txt))
            f.write("\n")
    return log
