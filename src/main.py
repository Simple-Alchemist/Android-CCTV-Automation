from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from automation_server import AutomationServer
from camera_script import automation_run
from database import NetworkDB

tvs: dict[str, AutomationServer] = dict()
tracker: dict[Any, str] = dict()

with NetworkDB() as ndb: 

    #Creating TV Objects
    for network in ndb.fetch_all_network(): 
        
        tvs[network[0]] =  AutomationServer(network[1], network[2])

logger.info("Successfully Created TV Objects of all Networks")

with ThreadPoolExecutor(max_workers=len(tvs)) as executor: 

    
    for tv_name in tvs:
        
        logger.info("Executing Automation through Threads")
        futures = executor.submit(automation_run, tvs[tv_name])
        tracker[futures] = tv_name

    
    for completed_task in as_completed(tracker): 

        tv_name = tracker[completed_task]

        try: 
            result = completed_task.result()

            if not result: 

                logger.info(f"{tv_name} of {tvs[tv_name].socket} failed to switch on Camera")

        except Exception as e: 

            logger.exception(e)
        
