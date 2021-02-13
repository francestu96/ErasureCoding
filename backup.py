#!/usr/bin/env python3

from state import State, GameOver
from utils import log
from heapq import heappop
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import sys
import numpy as np

KB = 1024 # bytes
MB = 1024 ** 2  # bytes
GB = 1024 ** 3  # bytes
MINUTE = 60
HOUR = 60 * 60  # seconds
DAY = 24 * HOUR  # seconds
YEAR = 365 * DAY


### SYSTEM PARAMETERS

N = 10 # number of servers storing data
K = 9 # number of blocks needed to recover data

# parameters about the node backing up the data
NODE_LIFETIME = 100 * DAY  # average time before node crashes and loses data
NODE_UPTIME = 8 * HOUR  # average time spent online by the node
NODE_DOWNTIME = 16 * HOUR  # average time spent offline
DATA_SIZE = 100 * GB  # amount of data to backup
UPLOAD_SPEED = 500 * KB  # node's speed, per second
DOWNLOAD_SPEED = 2 * MB  # per second

# parameters as before, for the server
SERVER_LIFETIME = 365 * DAY
SERVER_UPTIME = 30 * DAY
SERVER_DOWNTIME = 2 * HOUR

# length of the simulation
MAXT = 100 * YEAR

BLOCK_SIZE = DATA_SIZE / K
UPLOAD_DURATION = BLOCK_SIZE / UPLOAD_SPEED
DOWNLOAD_DURATION = BLOCK_SIZE / DOWNLOAD_SPEED

# for k in range(K, N):
plot_speed = []
plot_time = []
for upload_speed, download_speed in zip(range(10*KB, UPLOAD_SPEED + 10*KB, 10*KB), range(40*KB, DOWNLOAD_SPEED + 40*KB, 40*KB)):
    UPLOAD_DURATION = BLOCK_SIZE / upload_speed
    DOWNLOAD_DURATION = BLOCK_SIZE / download_speed

    state = State(N, K, NODE_UPTIME, NODE_DOWNTIME, NODE_LIFETIME, SERVER_UPTIME, SERVER_DOWNTIME, SERVER_LIFETIME, UPLOAD_DURATION, DOWNLOAD_DURATION)
    events = state.events

    try:
        while events:
            t, event = heappop(events)
            if t > MAXT:
                break

            state.t = t
            event.process(state)
    except GameOver:
        log(state, upload_speed/KB, download_speed/MB, K, YEAR, "Game over")
        print(f"Game over after {t/YEAR:.2f} years!")
    else:
        print(f"Data safe for {t/YEAR:.2f} years!")
    finally:
        plot_time.append(t/YEAR)
        plot_speed.append((upload_speed + upload_speed) / 2 / KB)

plt.barh(plot_speed, plot_time, height=10, label=f"Redundancy: {N/K:.2f}")

plt.xlabel("Years")
plt.ylabel("Avg KB speed")
plt.title(f'Simulation of {MAXT/YEAR:.0f} years')
plt.xlim(0, MAXT/YEAR)
plt.legend()
plt.show()
