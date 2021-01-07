#!/usr/bin/env python3

from consts import DATA_SIZE, K, UPLOAD_SPEED, DOWNLOAD_SPEED, MAXT, YEAR, DAY
from state import State, GameOver
from utils import log
from heapq import heappop
import matplotlib.pyplot as plt
import sys
        
state = State()
events = state.events

try:
    while events:
        t, event = heappop(events)
        if t > MAXT:
            break

        state.t = t
        event.process(state)
except GameOver:
    log(state, "Game over")
    print(f"Game over after {t/YEAR:.2f} years!")
else:  # no exception
    print(f"Data safe for {t/YEAR:.2f} years!")

finally:
    # Plot
    plt.plot(state.plot_time, state.plot_servers, label="Online servers")
    plt.plot(state.plot_time, state.plot_locals, label="Available local blocks")
    plt.plot(state.plot_time, state.plot_remote, label="Available remote blocks")

    plt.ylim(0, 11)
    plt.xlim(0, MAXT / YEAR)
    plt.ylabel('Number of blocks/servers available')
    plt.xlabel('Time')
    plt.legend(loc="lower right")
    plt.show()