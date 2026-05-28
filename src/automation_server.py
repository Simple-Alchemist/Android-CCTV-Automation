import uiautomator2 as u2
from uiautomator2.exceptions import (
    UiObjectNotFoundError,
)
from typing import Self, Literal

from adbutils import adb

class AutomationServer:
 
    
    def __init__(self, IP:str, port: str|int):
 
        self._socket = f"{IP}:{str(port)}"
        self._hik_package_name =  "com.hikvision.hikconnect"
        self._hik_activity_menus = [".main.MainTabActivity"] #get all the variants of it, since it varies from TV to TV
        self._hik_activity_camera = ".liveplay.mainlive.page.MainLivePlayActivity" #get all the variants of it, since it varies from TV to TV
        self._tv_con = None 
        self._hik_con = None


    def __enter__(self) -> Self:
        self.connect()

        return self
    
    def __exit__(self, exc_type, exc, tb) :
        
        self.disconnect()

    @property
    def tv_con(self) -> u2.Device: 

        if self._tv_con is None:
            raise ConnectionError("Tv Device Object hasn't been created")
        
        else: 

            return self._tv_con
        
    @property
    def hik_con(self) -> u2.Session: 

        if self._hik_con is None:
            raise ConnectionError("Hik Session Object hasn't been created")
        
        else: 

            return self._hik_con
        
    @property
    def current_activity(self) -> str|None: 

        activity = self.tv_con.app_current().get('activity', None)

        if activity is None: 
            raise RuntimeError("Can not fetch current activity")
        
        return activity

    @property
    def hik_package_name(self) -> str:
        return self._hik_package_name 
    
    @property
    def hik_activity_menus(self) -> list[str]: 
        return self._hik_activity_menus
    
    @property
    def hik_activity_camera(self) -> str: 
        return self._hik_activity_camera

    @property 
    def socket(self) -> str: 
        return self._socket
    
    def connect(self) -> None:

        #connect to the Device
        self._tv_con = u2.connect(self._socket)
            
    def start_hik_session(self, attach: bool = True) -> None:
        
        #Checking if a Hik Session is running or not
        if self._hik_con is not None: 
            raise RuntimeError("There's already a hik session running")
        
        #Start the session
        self._hik_con = self.tv_con.session(package_name=self.hik_package_name, attach=attach) 

    def restart_hik_session(self) -> None: 
        
        self.hik_con.restart()

    def is_hik_running(self) -> bool:

        return self.hik_con.running()

    def is_activity_opened(self, expected_actvitiy: str) -> bool:
        
        current_activity = self.current_activity 
        
        return current_activity == expected_actvitiy

    def is_hik_menu_open(self) -> bool:

        current_activity = self.current_activity

        return current_activity in self.hik_activity_menus
                    
    def is_hik_camera_open(self) -> bool:
        
        current_activity = self.current_activity

        return current_activity == self.hik_activity_camera
    
    def start_camera(self) -> None: 
        # Get more information such classname, index number and e.t.c
        layout = self.hik_con(
            resourceId=f"{self._hik_package_name}:id/background_layout"
            ) 

        if not layout.exists():

            raise UiObjectNotFoundError("Backgorund Layout doesn't seems to exist")
            
        layout.click(timeout=30) 
       
    def close_hik(self) -> None : 
        
        self.hik_con.close()
        self._hik_con = None

    def press_button(self, button: Literal["HOME", "BACK"]):
        
        self.tv_con.press(key=str(button))

    def intentional_sleep(self, seconds: int): 
        self.tv_con.sleep(seconds=seconds)

    def disconnect(self) :
        self.tv_con
        adb.disconnect(self._socket, raise_error=True) 

        self._tv_con = None
        self._hik_con = None
   
    def hik_wait(self, timeout=30):
        
        self.hik_con.app_wait(self._hik_package_name, timeout=timeout)
  
    def hik_activity_wait(self,activity: str,  timeout: int = 30):

        self.hik_con.wait_activity(activity=activity, timeout=timeout)
