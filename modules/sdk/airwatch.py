from device import Device
from modules.module import Sdk


class Airwatch(Sdk):
    def run(self):
        self._config.ui_main.prompt_user('input Login')
        Device.input_text(self._config.user())
        Device.input_tab()
        Device.input_text(self._config.user_password())
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
        self._config.ui_main.prompt_user('input local password')
        Device.input_text(self._config.local_password())
        Device.input_tab()
        Device.input_text(self._config.local_password())
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()

