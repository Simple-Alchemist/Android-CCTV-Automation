from loguru import logger
from uiautomator2.exceptions import (
    ConnectError,
    SessionBrokenError
    
)
import time
import sys

from automation_server import AutomationServer
from config import CameraScriptConfig


logger.remove() 

logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>[{extra[socket]}]</cyan> - <level>{message}</level>",
    colorize=True
)

logger.configure(extra={"socket": "SYSTEM"})



def automation_run(server: AutomationServer, cs_config: CameraScriptConfig) -> bool:

    tv_logger = logger.bind(socket=server.socket)

    for connection_attempt in range(1, cs_config.max_connection_attempt+1): 

        try:

            tv_logger.info(f"Connecting....")
            
            with server: # Automatically Connects to TV and disconnects when some problem occurs

        
                for session_attempt in range(1, cs_config.max_session_attempt+1):

                    try:

                        tv_logger.info("Connection has been Established")

                        if server.is_activities_opened(expected_package=cs_config.dream_page_package,expected_activities=[cs_config.dream_page_activity]):
                                
                                tv_logger.info("Currently in Dream Activity")
                                server.press_button("HOME")

                                tv_logger.info(f"Brought to in Homepage. Allowing {cs_config.press_button_time}s to stabilize...")
                                time.sleep(cs_config.press_button_time)


                        tv_logger.info("Establishing Hik-Connect session...")
                        server.start_hik_session()
                        server.hik_wait()

                        tv_logger.info(f"Session attached. Allowing {cs_config.device_stabilization_time} to stabilize...")
                        time.sleep(cs_config.device_stabilization_time) 

                        while True: 

                            if server.is_hik_camera_open():

                                tv_logger.info("Camera is now running")

                                return True 
                        
                            if server.is_hik_menu_open(): 
                                
                                if cs_config.camera_tries >= cs_config.max_camera_tries: 
                                    tv_logger.debug("Reached Maximum Tries to Run to Camera")
            
                                    return False
                                
                                cs_config.camera_tries += 1
                                tv_logger.info(f"{cs_config.camera_tries}/{cs_config.max_camera_tries} attempt is left")
                                tv_logger.info(f"Running the camera...")

                                server.start_camera()
                                server.hik_activity_wait(activity=server.hik_activity_camera)
                                
                                tv_logger.info(f"Camera has been put to start. Allowing {cs_config.device_stabilization_time}s to stabilize....")
                                time.sleep(cs_config.device_stabilization_time)


                                continue

                            if not server.is_activities_opened(expected_package=server.hik_package_name, expected_activities=server.hik_activity_menus):
                                
                                tv_logger.info(f"Another Activity is running - {server.current_app_info['activity']} ")
                                server.press_button("HOME")
                                tv_logger.info(f"Home Button Pressed. Allowing {cs_config.press_button_time}s to stabilize") 
                                time.sleep(cs_config.press_button_time)

                            if not server.is_hik_running():
                                raise SessionBrokenError("Hik session is not running")
                            
                            if cs_config.back_tries >= cs_config.max_back_tries: 

                                tv_logger.debug(f"Reached Maximum Tries to Press Back")

                                return False
                
                            cs_config.back_tries += 1        
                            tv_logger.info(f"{cs_config.back_tries}/{cs_config.max_back_tries} attempt")
                            server.press_button("BACK")
                            logger.info(f"Back Button Pressed. Allowing {cs_config.press_button_time}s to stabilize...")
                            time.sleep(cs_config.press_button_time)
                            

                            if server.is_activities_opened(expected_package=cs_config.home_page_package, expected_activities=[cs_config.home_page_activity]): 

                                tv_logger.info(f"Re-establishing Hik-Connect session")
                                server.start_hik_session(attach=False)
                                server.hik_wait()

                                tv_logger.info(f"Session attached. Allowing {cs_config.device_stabilization_time}s to stabilize...")
                                time.sleep(cs_config.device_stabilization_time)

                            continue
                
                    except Exception as e:
                        
                        tv_logger.exception(f"[{server.socket}] Unhandled critical error: {e}")

                        if session_attempt <= cs_config.max_session_attempt: 
                            tv_logger.info(f"Will be re-trying in {cs_config.device_stabilization_time}s.....")
                            time.sleep(cs_config.device_stabilization_time)

                            continue

                        return False
                

        except ConnectError as e:

            tv_logger.exception(f"Couldn't not establish connection with [{server.socket}]")


            if connection_attempt <= cs_config.max_connection_attempt: 
                tv_logger.info(f"Will be re-trying in {cs_config.network_stabilization_time}s.....")
                time.sleep(cs_config.network_stabilization_time)

                continue

            return False

    else:

        return False