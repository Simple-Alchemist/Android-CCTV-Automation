import uiautomator2 as u2
from uiautomator2.exceptions import (
    ConnectError, 
    AppNotFoundError, 
    UiObjectNotFoundError,
    SessionBrokenError,
    DeviceError
)
from adbutils import adb, AdbError

import logging 


logger = logging.getLogger(__name__) 

class AutomationTools:
 
    
    def __init__(self, IP:str, port:str|int):
 
        self._socket = f"{IP}:{str(port)}"

        self._hik_package_name =  "com.hikvision.hikconnect"
        self._hik_activity_menu = "main.MainTabActivity"
        self._hik_activity_camera = "liveplay.mainlive.page.MainLivePlayActivity"
        self._tv_con = None 
        self._hik_con = None

    def connect(self) -> bool:

        try:

            #connect to the Device
            self._tv_con = u2.connect(self._socket)
            
            logger.info(f"Connected to {self._socket}")

            return True
            
        except ConnectError:

            logger.exception(f"Connection Failed to {self._socket}", exc_info=True)
            
            return False
        
    def start_hik_session(self) -> bool:
        
        #check whether tv_con is created (or connected)
        if self._tv_con is None: 
            logger.error(f"Connection is not established") 
            return False

        try:

            #Start the session
            self._hik_con = self._tv_con.session(package_name=self._hik_package_name, attach=True) 

            logger.info(f"Session has been started")

            return True
            
 
        except AppNotFoundError:
            
            logger.exception(f"Hik connect is not installed", exc_info=True)
            #report class error
            return False
        

        except SessionBrokenError:

            logger.exception(f"Session has been broken", exc_info=True)
            #report class error
            return False

    def is_hik_running(self):

        if self._hik_con is None:

            logger.error(f"Session hasn't started")

            return False
        
        if not self._hik_con.running(): 

            logger.error(f"Session isn't running")

            return False

        logger.info(f"Session is running")

        return True
        
    def is_hik_menu_open(self) -> bool:

        if self._hik_con is None:
            logger.error(f"Session hasn't started")
            return False

        if  not (self._hik_con.app_current()["activity"] == self._hik_activity_menu):
            #report class error
            logger.error(f"Hik-Connect Menu has not been Displayed")
            return False
            
        logger.info(f"Hik-Connect Menu has been Displayed")
            
        return True
        
    def is_hik_camera_open(self) -> bool:

        if self._hik_con is None:
            logger.error(f"Session hasn't started")
            return False

        if not self._hik_con.app_current()["activity"] == self._hik_activity_camera:

            logger.error(f"Hik-Connect Camera has not been Displayed")
            return False 
         
        logger.info(f"Hik-Connect Camera has been Displayed")
            
        return True
    
    def start_camera(self) -> bool: 

        if self._hik_con is None:
            logger.error(f"Session hasn't started")
            return False
            
        try:
            # Get more information such classname, index number and e.t.c
            layout = self._hik_con(
                resourceId="com.hikvision.hikconnect:id/background_layout"
                ) 

            if not layout.exists():
                logger.exception(f"Unable to find background layout")
                return False
            
            layout.click(timeout=30) 
            
            logger.info(f"Camera has been started")
            return True
        
        except UiObjectNotFoundError:
            logger.exception("Failed to interact with UI object", exc_info=True)
            return False
        
    def close_hik(self) -> bool: 
        
        if self._hik_con is None:
            logger.error(f"Session hasn't started")
            return False

        try:
            self._hik_con.close()

            logger.info(f"Hik-Connect has been closed")

            return True
        
        except DeviceError:
            logger.exception(f"Unable to close Hik-Connect", exc_info=True)
            return False
                
    def disconnect(self) -> bool:
        if self._tv_con is None:

            logger.error(f"Session hasn't started")
            return False

        try:
            
            adb.disconnect(self._socket, raise_error=True) 

            logger.info(f"Disconnected from {self._socket}")

            return True
        
        except AdbError:

            logger.exception(f"Adb Error, unable to disconnect", exc_info=True)
            return  False
        
    def hik_wait(self, timeout=30):

        if self._hik_con is None:
            logger.error(f"Session hasn't started")
            return False
        
        try:
            self._hik_con.app_wait(self._hik_package_name, timeout=timeout)

            return True
        except DeviceError:
            logger.exception(f"Unable to wait for app", exc_info=True)
            return False
        
    def hik_activity_wait(self,activity: str,  timeout: int = 30):

        if self._hik_con is None:
            logger.error(f"Session hasn't started")
            return False
        
        try:
            self._hik_con.wait_activity(activity=activity, timeout=timeout)
            return True
        except DeviceError:
            logger.exception(f"Unable to wait for activity", exc_info=True)
            return False
    
    @property
    def hik_package_name(self) -> str:
        return self._hik_package_name 
    
    @property
    def hik_activity_menu(self) -> str: 
        return self._hik_activity_menu
    
    @property
    def hik_activity_camera(self) -> str: 
        return self._hik_activity_camera


def automation_run(tool: AutomationTools) -> bool:

    if not tool.connect(): 
        return False 

    if not tool.start_hik_session(): 
        return False
    
    tool.hik_wait()
    tool.hik_activity_wait(tool.hik_activity_menu)

    max_tries = 3 
    attempt = 0

    while attempt<=max_tries:

        attempt+=1
        logger.info(f"{attempt}/{max_tries} attempt are left")

        if not tool.is_hik_running(): #if hik is not running
            logger.info("Hik-connect isn't running")
            
            if attempt >= max_tries: 
                logger.info("Reached Max Attempt")

                return False
            
            tool.start_hik_session() # start hik session
            tool.hik_wait()
            tool.hik_activity_wait(tool.hik_activity_menu)

            continue
        
        if tool.is_hik_camera_open():
            logger.info("Camera is already displayed")
            return True # here's the Truth!
        
        if not tool.is_hik_menu_open(): #if hik's menu is not being displayed
            logger.info("Hik-connect Menu isn't displayed")
            if attempt >= max_tries: 
                logger.info("Reached Max Attempt")
                return False 

            tool.start_hik_session()
            tool.hik_wait()
            tool.hik_activity_wait(tool.hik_activity_menu)

            continue 

        if not tool.start_camera(): 

            return False 
        
        if not tool.is_hik_camera_open(): 
            logger.info("Camera is not displayed")
            if attempt >= max_tries: 
                logger.info("Reached Max Attempt")
                return False # log it 
            
            tool.hik_activity_wait(tool.hik_activity_menu)
            tool.start_camera()
            tool.hik_activity_wait(tool.hik_activity_camera)
            continue

        continue

    return False
        
    