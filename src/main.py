from loguru import logger
from collections import deque


from automation_tool import AutomationTools, automation_run
from database import NetworkDB


network_db = NetworkDB()

network_db.connect_db()

networks: deque[tuple[str, int]]  = network_db.fetch_all_network()

for network in networks: 
    
    IP = network[0]
    port = network[1] 

    tool = AutomationTools(IP=IP, port=port)

    status =  automation_run(tool=tool) 

    
    if status is False: 

        logger.info(f"Appending {IP}:{port} to the list")

    else: 
        logger.info(f"Successfully switched on Camera of {IP}:{port}")


network_db.close()
