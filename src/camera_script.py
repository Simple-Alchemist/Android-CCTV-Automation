from loguru import logger
from uiautomator2.exceptions import (
    ConnectError,
    UiAutomationNotConnectedError
)

import http.client
import time

from automation_server import AutomationServer
from config import CameraScriptConfig


logger.remove() 

# Custom Format where I'll have log displayed along with it's Socket
logger.add(
    "server.log", 
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>[{extra[socket]}]</cyan> - <level>{message}</level>",
    colorize=True,
    mode="w"
)

logger.configure(extra={"socket": "SYSTEM"})



def automation_run(server: AutomationServer, cs_config: CameraScriptConfig) -> bool:

    tv_logger = logger.bind(socket=server.socket)

    for connection_attempt in range(1, cs_config.max_connection_attempt+1):  
        tv_logger.info(f"{connection_attempt}/{cs_config.max_connection_attempt} to establish the connection")

        try:

            tv_logger.info(f"Attempt to Connect....")
        
            with server: # Automatically Connects to TV and disconnects automatically

                tv_logger.info("Connection has been Established.")
                
                for session_attempt in range(1, cs_config.max_session_attempt+1): 

                    tv_logger.info(f"{session_attempt}/{cs_config.max_session_attempt} attempts to Start the Camera")

                    cs_config.camera_tries = 0 
                    cs_config.back_tries = 0

                    try:

                        tv_logger.info("Establishing Hik-Connect session...")
                         
                        server.start_hik_session() 

                        tv_logger.info(f"Session is being attached, Allowing {cs_config.device_stabilization_time} to stabilize...")
                        time.sleep(cs_config.device_stabilization_time) 

                        while True: 

                            if server.is_hik_camera_open():

                                tv_logger.info("Camera is now running")

                                return True 
                        
                            if server.is_hik_menu_open(): 
                                
                                if cs_config.camera_tries >= cs_config.max_camera_tries: 

                                    tv_logger.info("Reached Maximum Tries to Run to Camera")

                                    server.press_button("HOME")

                                    tv_logger.info(f"Brought to in Homepage. Allowing {cs_config.press_button_time}s to stabilize...")
                                    time.sleep(cs_config.press_button_time)

                                    break
                                
                                cs_config.camera_tries += 1
                                tv_logger.info(f"{cs_config.camera_tries}/{cs_config.max_camera_tries} attempt is left")
                                tv_logger.info(f"Running the camera...")

                                server.start_camera()
                                
                                tv_logger.info(f"Camera has been put to start. Allowing {cs_config.device_stabilization_time}s to stabilize....")
                                time.sleep(cs_config.device_stabilization_time)

                                continue

                            if server.is_hik_running(): 
                            # If Hik running but the desired Activity isn't up then there's a high probability that a "install Dialogue" Poped on the screen 
                            # To fix that, It will simply Press "BACK" for max times 

                                if cs_config.back_tries >= cs_config.max_back_tries: 
                                #if it has already reached the max, then it will Press "HOME" and will Re-Try to Launch Hik-connect

                                    tv_logger.info(f"Reached Maximum Tries to Press Back")

                                    server.press_button("HOME")

                                    tv_logger.info(f"Brought to in Homepage. Allowing {cs_config.press_button_time}s to stabilize...")
                                    time.sleep(cs_config.press_button_time)

                                    break

                                cs_config.back_tries += 1        
                                tv_logger.info(f"{cs_config.back_tries}/{cs_config.max_back_tries} attempt")

                                server.press_button("BACK")

                                logger.info(f"Back Button Pressed. Allowing {cs_config.press_button_time}s to stabilize...")
                                time.sleep(cs_config.press_button_time)

                                continue

                            if not server.is_hik_running():

                                server.press_button("HOME")

                                tv_logger.info(f"Brought to in Homepage. Allowing {cs_config.press_button_time}s to stabilize...")
                                time.sleep(cs_config.press_button_time)

                                break
                        
                            continue

                    except http.client.RemoteDisconnected:
                        # If Connection is lost! then it should go to Connection Attempt Loop to re-establish Connection
                        tv_logger.exception(f"Remote end closed connection without response; Re-Connecting to the TV")

                        break
                
                    except Exception as e:
                        
                        tv_logger.exception(f"Unhandled critical error: {e}")

                        if session_attempt <= cs_config.max_session_attempt: 
                            tv_logger.info(f"Will be re-trying in {cs_config.device_stabilization_time}s.....")
                            time.sleep(cs_config.device_stabilization_time)

                            continue

                        return False  

        except (ConnectError, UiAutomationNotConnectedError) as e :

            tv_logger.exception(f"Couldn't not establish connection")


            if connection_attempt <= cs_config.max_connection_attempt: 
                tv_logger.info(f"Will be re-trying in {cs_config.network_stabilization_time}s.....")
                time.sleep(cs_config.network_stabilization_time)

                continue

            return False
        
        except Exception: 

            tv_logger.exception(f"Something went wrong")

            return False

        
    else:

        return False