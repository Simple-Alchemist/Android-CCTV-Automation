from dataclasses import dataclass, field

@dataclass(kw_only=True)
class AutomationServerConfig:

    IP: str
    port: int |str = field(default="5555")
    hik_package_name: str = field(default="com.hikvision.hikconnect", repr=False)
    hik_activity_menus: list[str] = field(default_factory=list, repr=False)
    hik_activity_camera: list[str] = field(default_factory=list, repr=False)

    def __post_init__(self):
        
        self.hik_activity_camera.extend(['.liveplay.mainlive.page.MainLivePlayActivity'])
        self.hik_activity_menus.extend([".main.MainTabActivity"])


@dataclass(kw_only=True)
class CameraScriptConfig:

    max_connection_attempt: int = field(default=3)
    max_session_attempt: int = field(default=4)
    back_tries: int = field(default=0, init=False)   
    max_back_tries: int = field(default=5)

    press_button_time: int = field(default=5)
    
    device_stabilization_time: int = field(default=60)
    network_stabilization_time: int = field(default=120)

