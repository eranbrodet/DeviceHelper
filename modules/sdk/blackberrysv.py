from device import Device
from modules.module import Sdk
from utils import BlackBerryUtils


class BlackberrySV(Sdk):
    def run(self):
        server_user = self._config.defaults.get('blackberrysv', {}).get('good_user', 'Eran Brodet')
        if Device.MOCK_MODE:
            access_key = '123451234512345'
        else:
            access_key = BlackBerryUtils(self._config.defaults, 'blackberrysv').get_access_key_from_server(server_user)
        self._logger.info('Access key is ' + access_key)

        self._config.ui_main.prompt_user('input login')
        Device.input_text(self._config.user())
        Device.input_enter()
        Device.input_text(access_key)
        Device.input_enter()
        self._config.ui_main.prompt_user('input password')
        Device.input_text(self._config.local_password())
        Device.input_enter()
        Device.input_text(self._config.local_password())
        Device.input_enter()
        Device.input_enter()
