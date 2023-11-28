import argparse
import asyncio
import base64
from collections import deque
from datetime import datetime, timedelta
import hashlib
import os
import subprocess

from pydub import AudioSegment
from pydub.playback import play
from scipy.io.wavfile import write
import sounddevice as sd

from models import import_models
from robots import import_robot

argparser = argparse.ArgumentParser()
argparser.add_argument("--model_api", type=str, default="test")
args = argparser.parse_args()

MODELS: dict = import_models(args.model_api)

async def sense() -> list:
    return await asyncio.gather(_vlm(), _stt(), _tts("observing"))


async def act(func: str, code: str, speech: str) -> list:
    return await asyncio.gather(_act(func, code), _tts(speech))


async def plan(state: str) -> [str, str, str]:
    results = await asyncio.gather(
        *[
            _llm(
                f"""
Pick a function based on the robot log. Always pick a function and provide any args required. Here are the functions:
{ROBOT['functions']}
Here is the robot log
<robotlog>
{state}
</robotlog>
Pick one of the functions and the args. Here are some example outputs:
{ROBOT['examples']}
Your response should be a single line with the chosen function code and arguments.
"""
            ),
            _llm(
                f"""
Summarize the robot log in a couple clever words, be brief but precise
Here is the robot log
<robotlog>
{state}
</robotlog>
"""
            ),
            _tts("deciding"),
        ]
    )
    func, code = results[0][1].split(",")
    speech = results[1][1]
    return func, code, speech


state = deque([f"{EMOJIS['born']} robot is alive"], maxlen=MEMORY)
while datetime.now() - BIRTHDAY < LIFESPAN:
    if len(state) >= MEMORY:
        for _ in range(FORGET):
            state.popleft()
        state.appendleft(f"{EMOJIS['forget']} memory erased")
    for s in asyncio.run(sense()):
        state.append(s)
    state_str = "\n".join([str(item) for item in state])
    print(f"*********** {EMOJIS['state']} age {datetime.now() - BIRTHDAY}")
    print(state_str)
    print(f"*********** {EMOJIS['state']}")
    func, code, speech = asyncio.run(plan(state_str))
    state.append(f"{EMOJIS['llm']} choosing function {func} {code}")
    print(f"___________{EMOJIS['plan']}")
    print(speech)
    print(func, code)
    print(f"___________{EMOJIS['plan']}")
    for s in asyncio.run(act(func, code, speech)):
        state.append(s)
