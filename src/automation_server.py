import uiautomator2 as u2
from adbutils import adb
from uiautomator2.exceptions import (
    UiObjectNotFoundError,
)

from typing import Self, Literal, Any
from threading import BoundedSemaphore

from config import AutomationServerConfig



class AutomationServer:

    start_camera_bound = BoundedSemaphore(1)

    def __init__(self, as_config: AutomationServerConfig ):

        self._config = as_config
        self._socket:str = f"{self._config.IP}:{self._config.port}"

        self._tv_con: None | u2.Device = None 
        self._hik_con: None | u2.Session = None


    def __enter__(self) -> Self:

        self.connect()

        return self
 
    def __exit__(self, exc_type, exc, tb):
        
        self.disconnect()

    @property
    def tv_con(self) -> u2.Device: 

        if self._tv_con is None:
            raise RuntimeError("Tv Device Object hasn't been created")
        
        else: 

            return self._tv_con
        
    @property
    def hik_con(self) -> u2.Session: 

        if self._hik_con is None:
            raise RuntimeError("Hik Session Object hasn't been created")
        
        else: 

            return self._hik_con
        
    @property
    def current_app_info(self) -> dict[str, Any]: 

        app_current =  self.tv_con.app_current()
        app_current.pop('pid')
        return app_current

    @property
    def hik_package_name(self) -> str:

        return self._config.hik_package_name
    
    @property
    def hik_activity_menus(self) -> list[str]: 

        return self._config.hik_activity_menus
    
    @property
    def hik_activity_camera(self) -> str: 
        return self._config.hik_activity_camera

    @property 
    def socket(self) -> str: 
        return self._socket
    
    def connect(self) -> None:

        #connect to the Device
        self._tv_con = u2.connect(self._socket)
            
    def start_hik_session(self, attach: bool = True) -> None:
        
        #Start the session
        self._hik_con = self.tv_con.session(package_name=self.hik_package_name, attach=attach) 

    def restart_hik_session(self) -> None: 
        
        self.hik_con.restart()

    def is_hik_running(self) -> bool:

        return self.hik_con.running()

    def is_activities_opened(self, expected_package: str, expected_activities: list[str]) -> bool:
        
        current_app_info = self.current_app_info
        
        return True if current_app_info['package']==expected_package and current_app_info['activity'] in expected_activities else False

    def is_hik_menu_open(self) -> bool:

        return self.is_activities_opened(
            expected_package=self.hik_package_name,
            expected_activities=self.hik_activity_menus
            )
                    
    def is_hik_camera_open(self) -> bool:

        return self.is_activities_opened(
            expected_package=self.hik_package_name, 
            expected_activities=[self.hik_activity_camera]
            )
    
    def start_camera(self) -> None: #Network Heavy Work

        # Get more information such classname, index number and e.t.c
        # Or Use Xpath!
        with AutomationServer.start_camera_bound:

            layout = self.hik_con(
                resourceId=f"{self._config.hik_package_name}:id/background_layout"
                ) 

            if not layout.exists():

                raise UiObjectNotFoundError("Backgorund Layout doesn't seems to exist")
                
            layout.click() 
       
    def close_hik(self) -> None : 
        
        self.hik_con.close()
        self._hik_con = None

    def press_button(self, button: Literal["HOME", "BACK"]):
        
        self.tv_con.press(key=button)

    def disconnect(self):

        self.tv_con
        adb.disconnect(self._socket, raise_error=True) 

        self._tv_con = None
        self._hik_con = None
        
    def hik_wait(self, timeout=30):
        
        self.hik_con.app_wait(self._config.hik_package_name, timeout=timeout)
  
    def hik_activity_wait(self,activity: str,  timeout: int = 30):

        self.hik_con.wait_activity(activity=activity, timeout=timeout)