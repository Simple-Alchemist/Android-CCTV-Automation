from loguru import logger
from uiautomator2.exceptions import (
    ConnectError,
    SessionBrokenError
    
)
import sys

from automation_server import AutomationServer


logger.remove() 

logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>[{extra[socket]}]</cyan> - <level>{message}</level>",
    colorize=True
)

logger.configure(extra={"socket": "SYSTEM"})



def automation_run(server: AutomationServer) -> bool:

    tv_logger = logger.bind(socket=server.socket)

    max_connection_attempt = 3

    for connection_attempt in range(1, max_connection_attempt+1): 

        try:

            tv_logger.info(f"Connecting....")
            
            with server: # Automatically Connects to TV and disconnects when some problem occurs

                max_session_attempt = 3
                
                for session_attempt in range(1, max_session_attempt):

                    try:

                        camera_retries = 0
                        max_camera_tries= 3
                        back_retries = 0
                        max_back_tries= 5

                        tv_logger.info("Connection has been Established")

                        tv_logger.info("Establishing Hik-Connect session...")
                        server.start_hik_session()
                        server.hik_wait()

                        tv_logger.info(f"Session attached. Allowing 30s to stabilize...")
                        server.intentional_sleep(30)

                        while True: 

                            if server.is_hik_running() and server.is_hik_camera_open():

                                tv_logger.info("Camera is now running")

                                return True 
                        
                            if server.is_hik_running() and server.is_hik_menu_open(): 
                                
                                if camera_retries <= max_camera_tries: 
                                    tv_logger.debug("Reached Maximum Tries to Run to Camera")
            
                                    return False
                                
                                camera_retries += 1
                                tv_logger.info(f"{camera_retries}/{max_camera_tries} attempt is left")
                                tv_logger.info(f"Running the camera...")

                                server.start_camera()
                                server.hik_activity_wait(activity=server.hik_activity_camera)
                                
                                tv_logger.info(f"Camera has been put to start")


                                continue

                            if not server.is_hik_running():
                                raise SessionBrokenError("Hik session is not running") 
                            
                            if back_retries <= max_back_tries: 
                                tv_logger.debug(f"Reached Maximum Tries to Press Back")
                                return False
                
                            back_retries += 1        
                            tv_logger.info(f"{back_retries}/{max_back_tries} attempt")
                            server.press_button("BACK")
                            

                            if server.is_activities_opened(expected_activities=["HomePage"]): 

                                tv_logger.info(f"Re-establishing Hik-Connect session")
                                server.restart_hik_session()
                                server.hik_wait()


                                tv_logger.info(f"Session attached. Allowing 60s to stabilize...")
                                server.intentional_sleep(60)

                            continue
                
                    except Exception as e:
                        
                        tv_logger.exception(f"[{server.socket}] Unhandled critical error: {e}")

                        if session_attempt < max_session_attempt: 
                            tv_logger.info("Will be re-trying in 30s.....")
                            server.intentional_sleep(30)

                            continue

                        return False
                

        except ConnectError as e:

            tv_logger.exception(f"Couldn't not establish connection with [{server.socket}]")


            if connection_attempt < max_connection_attempt: 
                tv_logger.info("Will be re-trying in 60s.....")
                server.intentional_sleep(60)

                continue

            return False

    else:

        return False