from loguru import logger


from automation_server import AutomationServer 
from camera_script import automation_run
from database import NetworkDB


networks: list[tuple[str, str, int]]

with NetworkDB() as ndb: 

    networks = ndb.fetch_all_network()




