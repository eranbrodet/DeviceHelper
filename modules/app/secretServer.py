from device import Device
from modules.module import App


class SecretServer(App):
    def run(self):
        defaults = self._config.defaults.get('secret_server', {})
        self._config.ui_main.prompt_user('input Secret Server credentials')
        Device.input_text(defaults['user'])
        Device.input_tab()
        Device.input_text(defaults['org'])
        Device.input_tab()
        Device.input_text(defaults['password'])
        Device.input_tab()
        Device.input_enter()