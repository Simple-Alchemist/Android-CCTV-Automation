from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from automation_server import AutomationServer 
from camera_script import automation_run
from database import NetworkDB



networks: list[tuple[str, str, int]] #name, IP and port
result = None

with NetworkDB() as ndb: 

    networks = ndb.fetch_all_network()

tv_server = dict()

for network in networks: 

    tv_server[network[0]] =  AutomationServer(network[1], network[2])


with ThreadPoolExecutor(max_workers=4) as executor: 

    ...

            


