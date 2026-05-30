from dataclasses import dataclass, field

@dataclass(kw_only=True)
class AutomationServerConfig:

    IP: str
    port: int |str = field(default="5555")
    hik_package_name: str = field(default="com.hikvision.hikconnect")
    hik_activity_menus: list[str] = field(default_factory=list)
    hik_activity_camera: str = ".liveplay.mainlive.page.MainLivePlayActivity" 

    def __post_init__(self):
        
        self.hik_activity_menus.append(".main.MainTabActivity")


@dataclass(kw_only=True)
class CameraScriptConfig:

    max_connection_attempt: int = field(default=3)
    max_session_attempt: int = field(default=3)
    max_camera_tries: int = field(default=3)
    max_back_tries: int = field(default=5)

    press_button_time: int = field(default=15)
    device_stabilization_time: int = field(default=30)
    network_stabilization_time: int = field(default=60)

    dream_page_package: str = field(default="com.google.android.backdrop")
    dream_page_activity: str = field(default="android.service.dreams.DreamActivity")

    home_page_package: str = field(default="com.google.android.tvlauncher")
    home_page_activity: str = field(default=".MainActivity")
    


