# General Configuration
DEBUG = True

# Upload Configuration
# More information on: https://github.com/Elektroblock/StratoWeb/settings
use_webclient = True # Enables upload to chosen Server
api_key = 'XUVCHYbp2y6NMjjELjDERUQtdaLRsTsFshaJgVk585pbcWVT9PuGT7yvm2xHHMXM' # Must be the same betwene Client and Server!
server_url = "https://live.mlstrato.de"
input_filepath = 'C:/Users/Julian/PycharmProjects/MLS-receive/out/'

# local connection, to remote debug groundStation if device hosting groundstation is not reachable
# To enable connection to stratoClient, a simple Shell Program to display live Data and see the groundStation logs

use_debug_server = True
debug_server_port = 65432
debug_server_host = '127.0.0.1'
