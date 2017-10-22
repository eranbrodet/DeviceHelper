from device import Device
from modules.module import App


class Tango(App):
    def run(self):
        defaults = self._config.defaults.get('tango', {})
        self._config.ui_main.prompt_user('input Tango Account ID')
        Device.input_text(defaults['user'])
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
        self._config.ui_main.prompt_user('input Tango Password')
        Device.input_text(defaults['password'])
        Device.input_tab()
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
        self._config.ui_main.prompt_user('input Tango URL')
        Device.input_text(defaults['url'])
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
