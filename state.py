from events import NodeOffline, NodeFail, ServerOffline, ServerFail, UploadComplete, DownloadComplete, StatisticsCollector
from consts import K, N, NODE_UPTIME, NODE_LIFETIME, SERVER_UPTIME, SERVER_LIFETIME, UPLOAD_DURATION, DOWNLOAD_DURATION, MAXT, YEAR
from utils import exp_rv
from heapq import heappush

class State:
    def __init__(self):
        self.t = 0  # seconds
        self.node_online = True  # the node starts online
        self.server_online = [True] * N  # servers all start online
        self.remote_blocks = [False] * N  # no server starts having their block
        self.local_blocks = [True] * N  # flags each locally owned block
        self.plot_time = []
        self.plot_servers = []
        self.plot_locals = []
        self.plot_remote = []

        # we need to access current events for uploads and download
        # terminations, in case we need to cancel them because the
        # node or one of the servers went offline
        self.current_upload = self.current_download = None
        
        self.events = [(YEAR, StatisticsCollector())]  # event queue

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
        if self.node_online:
            for i in range(len(self.remote_blocks)):
                if not self.remote_blocks[i] and self.local_blocks[i] and self.server_online[i]:
                    self.current_upload = UploadComplete(i)
                    self.schedule(exp_rv(UPLOAD_DURATION),self.current_upload)
                    break
        # upload to server that doesn't have it (if possible)
        #raise NotImplementedException

    def schedule_next_download(self):
        """Schedule the next download, if any."""

        # if the node is online, download a remote block the node doesn't
        # have from an online server which has it (if possible)
        if self.node_online:
            for i in range(len(self.remote_blocks)):
                if self.remote_blocks[i] and not self.local_blocks[i] and self.server_online[i]:
                    self.current_download = DownloadComplete(i)
                    self.schedule(exp_rv(DOWNLOAD_DURATION),self.current_download)
                    break
        #raise NotImplementedException

    def check_game_over(self):
        """Did we lose enough redundancy that we can't recover data?"""

        # check if we have at least K blocks saved, either locally or remotely
        lbs, rbs = self.local_blocks, self.remote_blocks
        blocks_saved = [lb or rb for lb, rb in zip(lbs, rbs)]
        if sum(blocks_saved) < K:
            raise GameOver

class GameOver(Exception):
    """Not enough redundancy in the system, data is lost."""
    pass