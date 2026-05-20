import logging
from collections import deque


from automation_tool import AutomationTools, automation_run
from database import NetworkDB


logging.basicConfig(
    level=logging.INFO,
    filename='automation.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__) 


network_db = NetworkDB()

if not network_db.connect_db(): 

    ... 

networks: deque[tuple[str, int]]  = network_db.fetch_all_network()

for network in networks: 
    
    IP = network[0]
    port = network[1] 

    tool = AutomationTools(IP=IP, port=port)

    popped_network = networks.popleft()

    status =  automation_run(tool=tool) 

    
    if status is False: 

        networks.append(popped_network)
        logger.info(f"Appending {IP}:{port} to the list")

    else: 
        logger.info(f"Successfully switched on Camera of {IP}:{port}")


network_db.close()


        











    