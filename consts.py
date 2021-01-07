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
NODE_LIFETIME = 300 * DAY  # average time before node crashes and loses data
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