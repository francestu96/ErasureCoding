from events import NodeOffline, NodeFail, ServerOffline, ServerFail, UploadComplete, DownloadComplete, StatisticsCollector
from utils import exp_rv
from heapq import heappush

class State:
    def __init__(self, N, K, NODE_UPTIME, NODE_DOWNTIME, NODE_LIFETIME, SERVER_UPTIME, SERVER_DOWNTIME, SERVER_LIFETIME, UPLOAD_DURATION, DOWNLOAD_DURATION):
        self.t = 0  # seconds
        self.node_online = True  # the node starts online
        self.server_online = [True] * N  # servers all start online
        self.remote_blocks = [[False] * N] * N  # no server starts having their block
        self.local_blocks = [True] * N  # flags each locally owned block
        #consts
        self.N = N
        self.K = K
        self.NODE_UPTIME = NODE_UPTIME
        self.NODE_DOWNTIME = NODE_DOWNTIME
        self.NODE_LIFETIME = NODE_LIFETIME
        self.SERVER_UPTIME = SERVER_UPTIME
        self.SERVER_DOWNTIME = SERVER_DOWNTIME
        self.SERVER_LIFETIME = SERVER_LIFETIME
        self.UPLOAD_DURATION = UPLOAD_DURATION
        self.DOWNLOAD_DURATION = DOWNLOAD_DURATION
        # we need to access current events for uploads and download
        # terminations, in case we need to cancel them because the
        # node or one of the servers went offline
        self.current_upload = self.current_download = None
        
        self.events = []  # event queue

        # we add to the event queue the first events of node going
        # offline or failing
        self.schedule(exp_rv(NODE_UPTIME), NodeOffline())
        self.schedule(exp_rv(NODE_LIFETIME), NodeFail())

        # same, for each of the servers
        for i in range(N):
            self.schedule(exp_rv(SERVER_UPTIME), ServerOffline(i))
            self.schedule(exp_rv(SERVER_LIFETIME), ServerFail(i))

        # we now decide what the next upload will be
        self.schedule_next_upload()

    def schedule(self, delay, event):
        """Add an event to the event queue after the required delay."""
        
        heappush(self.events, (self.t + delay, event))

    def schedule_next_upload(self):
        """Schedule the next upload, if any."""

        # if the node is online, upload a possessed local block to an online
        # server that doesn't have it (if possible)
        if self.node_online:
            local_idxs = [i for i in range(len(self.local_blocks)) if self.local_blocks[i]]
            remotes = []
            for remote in self.remote_blocks:
                remotes.append([i for i in range(len(remote)) if remote[i]])

            for remote_idx, remote_server in enumerate(remotes):
                for i in local_idxs:
                    if(i not in remote_server and self.server_online[i]):
                        event = UploadComplete(remote_idx, i)
                        self.current_upload = event
                        self.schedule(exp_rv(self.UPLOAD_DURATION), event)
                        return

    def schedule_next_download(self):
        """Schedule the next download, if any."""

        # if the node is online, download a remote block the node doesn't
        # have from an online server which has it (if possible)
        if self.node_online:
            rbs = []
            for i in range(len(self.remote_blocks)):
                for j in range(len(self.remote_blocks[i])):
                    if len(rbs) > i:
                        rbs[i] = self.remote_blocks[j][i] or rbs[i]
                    else:
                        rbs.append(self.remote_blocks[j][i])

            remote_idxs = [i for i in range(len(rbs)) if rbs[i]]
            local_idxs = [i for i in range(len(self.remote_blocks)) if self.local_blocks[i]]
            for i in remote_idxs:
                if(i not in local_idxs and self.server_online[i]):
                    event = DownloadComplete(i)
                    self.current_download = event
                    self.schedule(exp_rv(self.DOWNLOAD_DURATION), event)
                    return

    def check_game_over(self):
        """Did we lose enough redundancy that we can't recover data?"""

        # check if we have at least K blocks saved, either locally or remotely
        lbs, rbs_array = self.local_blocks, self.remote_blocks
        rbs = []
        for i in range(len(rbs_array)):
            for j in range(len(rbs_array[i])):
                if len(rbs) > i:
                    rbs[i] = rbs_array[j][i] or rbs[i]
                else:
                    rbs.append(rbs_array[j][i])

        blocks_saved = [lb or rb for lb, rb in zip(lbs, rbs)]
        if sum(blocks_saved) < self.K:
            raise GameOver

class GameOver(Exception):
    """Not enough redundancy in the system, data is lost."""
    pass