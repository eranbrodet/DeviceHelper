from device import Device
from modules.module import App


class Appian(App):
    def run(self):
        defaults = self._config.defaults.get('appian', {})
        self._config.ui_main.prompt_user('input Appian url')
        Device.input_text(defaults['url'])
        Device.input_enter()
        Device.input_enter()
        self._config.ui_main.prompt_user('input Appian credentials')
        Device.input_text(defaults['user'])
        Device.input_tab()
        Device.input_text(defaults['password'])
        Device.input_enter()