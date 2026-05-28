from loguru import logger
from uiautomator2.exceptions import (
    UiObjectNotFoundError,
    ConnectError,
    SessionBrokenError
    
)

from automation_server import AutomationServer


def automation_run(server: AutomationServer) -> bool:

    try:

        logger.info(f"Connecting to [{server.socket}] ")

        with server: # Automatically Connects to TV and disconnects when some problem occurs
            
            logger.info(f"Connection has been Established")

            camera_retries = 0
            max_camera_tries= 3
            back_retries = 0
            max_back_tries= 5

            logger.info(f"[{server.socket}] Establishing Hik-Connect session...")
            server.start_hik_session()
            server.hik_wait()

            logger.info(f"[{server.socket}] Session attached. Allowing 30s to stabilize...")
            server.intentional_sleep(30)

            while True: 

                if server.is_hik_running() and server.is_hik_camera_open():
                    logger.info(f"[{server.socket}] Camera is now running")
                    return True 
            
                if server.is_hik_running() and server.is_hik_menu_open(): 
                      
                    if not camera_retries <= 3: 
                        logger.debug(f"[{server.socket}] Reached Maximum Tries to Run to Camera")
                        return False
                    
                    camera_retries += 1
                    logger.info(f"[{server.socket}] {camera_retries}/{max_camera_tries} attempt is left")
                    logger.info(f"[{server.socket}] Running the camera...")

                    server.start_camera()
                    server.hik_activity_wait(activity=server.hik_activity_camera)
                    
                    logger.info(f"[{server.socket}] Session attached. Allowing 15s to stabilize...")
                    server.intentional_sleep(15)

                    continue

                if not server.is_hik_running():
                    logger.debug(f"[{server.socket}] Hik Session is not running...")
                    return False 
                
                if not back_retries <= 5: 
                    logger.debug(f"[{server.socket}] Reached Maximum Tries to Press Back")
                    return False
                

                back_retries += 1        
                logger.info(f"[{server.socket}] {back_retries}/{max_back_tries} attempt is left")
                server.press_button("BACK")
                

                if server.is_activity_opened(expected_actvitiy="HomePage"): 

                    back_retries = 0
                    camera_retries=0
                    logger.info(f"[{server.socket}] Re-establishing Hik-Connect session")
                    server.start_hik_session(attach=False)
                    server.hik_wait()


                    logger.info(f"[{server.socket}] Session attached. Allowing 30s to stabilize...")
                    server.intentional_sleep(30)

                continue

                

    except ConnectError as e:
        logger.exception(f"Couldn't not establish connection with [{server.socket}]")

        return False 
    
    except UiObjectNotFoundError as e: 

        logger.exception(f"[{server.socket}] Couldn't Find the specific ID to click on")
        return False
    
    except ConnectionError as e:

        logger.exception(f"There's no connection established with [{server.socket}]") 
        return False


    except RuntimeError as e: 

        logger.exception(f"Runtime Error")
        return False
    
    except SessionBrokenError as e:
        
        logger.exception(f"Session Crashed")
        return False
    

    except Exception as e:
        
        logger.exception(f"[{server.socket}] Unhandled critical error: {e}")
        return False
    
        

