from utils import exp_rv, get_true_len
from heapq import heappush

class ServerEvent:
    """Class with a self.server attribute."""
    
    def __init__(self, server):
        self.server = server

    def __str__(self):  # function to get a pretty printed name for the event
        return f'{self.__class__.__name__}({self.server})'

        
class UploadComplete(ServerEvent):
    """An upload is completed."""
    def process(self, state):
        if state.current_upload is not self:
            #print("upload was interrupted")
            # this upload was interrupted, we ignore this event
            return
        state.remote_blocks[self.server] = True
        state.schedule_next_upload()

        
class DownloadComplete(ServerEvent):
    """A download is completed."""
    
    def process(self, state):
        if state.current_download is not self:
            #print("Download was interrupted")
            # download interrupted
            return
        lb = state.local_blocks
        lb[self.server] = True
        if sum(lb) >= state.K:  # we have enough data to reconstruct all blocks
            state.local_blocks = [True] * state.N
        else:
            state.schedule_next_download()


class NodeOnline:
    """Our node went online."""
    
    def process(self, state):
        # mark the node as online
        state.node_online = True
        # schedule next upload and download
        state.schedule_next_upload()
        state.schedule_next_download()
        # schedule the next offline event
        state.schedule(exp_rv(state.NODE_UPTIME), NodeOffline())

class NodeOffline:
    """Our node went offline."""
    
    def process(self, state):
        # mark the node as offline
        state.node_online = False
        # cancel current upload and download
        state.current_upload = state.current_download = None
        # schedule the next online event
        state.schedule(exp_rv(state.NODE_DOWNTIME), NodeOnline())
    
        
class NodeFail(NodeOffline):
    """Our node failed and lost all its data."""
    
    def process(self, state):
        # mark all local blocks as lost
        state.local_blocks = [False] * state.N
        state.check_game_over()
        state.schedule(exp_rv(state.NODE_LIFETIME), NodeFail())
        super().process(state)

        
class ServerOnline(ServerEvent):
    """A server that was offline went back online."""
    
    def process(self, state):
        server = self.server
        # mark the server as back online
        state.server_online[server] = True
        # schedule the next server offline event
        state.schedule(exp_rv(state.SERVER_UPTIME), ServerOffline(server))
        # if the node was not uploading/downloading,
        # schedule new uploads/downloads to/from them
        cu = state.current_upload
        if cu is None:
            state.schedule_next_upload()
        cd = state.current_download
        if cd is None:
            state.schedule_next_download()
    
class ServerOffline(ServerEvent):
    # u can implement the possibility to schedule another upload and download
    """A server went offline."""
    
    def process(self, state):
        server = self.server
        # mark the server as offline
        state.server_online[server] = False
        # schedule the next server online event
        state.schedule(exp_rv(state.SERVER_DOWNTIME), ServerOnline(server))

        # interrupt any current uploads/downloads to this server
        
        cu = state.current_upload
        if cu is not None and cu.server == server:
            state.current_upload = None

        cd = state.current_download
        if cd is not None and cd.server == server:
            state.current_download = None

            
class ServerFail(ServerOffline):
    """A server failed and lost its data."""
    
    def process(self, state):
        state.remote_blocks[self.server] = False
        state.check_game_over()
        state.schedule(exp_rv(state.SERVER_LIFETIME), ServerFail(self.server))
        super().process(state)


class StatisticsCollector:
    def process(self, state, YEAR):
        state.plot_time.append(state.t / YEAR)
        state.plot_servers.append(get_true_len(state.server_online))
        state.plot_locals.append(get_true_len(state.local_blocks))
        state.plot_remote.append(get_true_len(state.remote_blocks))
        heappush(state.events, (state.t + YEAR, StatisticsCollector()))