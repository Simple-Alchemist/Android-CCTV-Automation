from automation_server import AutomationServer
from loguru import logger

def automation_run(server: AutomationServer) -> bool:
    tool: AutomationServer = AutomationServer("123", "124")

    try:
        logger.info(f"Connection to {server.socket} ")
        with server:
            
            server.start_hik_session(attach=True)
            server.hik_wait()
            server.intentional_sleep(10)

            while True:
                if server.is_hik_running() and server.is_hik_camera_open():
                    return True 
            
                if server.is_hik_running() and server.is_hik_menu_open(): 

                    server.start_camera()
                    server.hik_activity_wait(server.hik_activity_camera)  
                    server.intentional_sleep(10)
                    continue

                if not server.is_hik_running():
                    return False 
                
                
                server.press_button("BACK")

                if not server.is_activity_opened(expected_actvitiy="HomePage"): 
                    
                    continue

                else:
                    server.start_hik_session(attach=False) 
                    server.hik_wait()
                    server.intentional_sleep(10)
                    continue

                
                

    except:
        ...
