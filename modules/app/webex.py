from device import Device
from modules.module import App


class Webex(App):
    def run(self):
        defaults = self._config.defaults.get('webex', {})
        self._config.ui_main.prompt_user('input Webex email')
        Device.input_text(defaults['email'])
        Device.input_enter()
        self._config.ui_main.prompt_user('input Webex email again')
        Device.input_text(defaults['email'])
        Device.input_enter()
        self._config.ui_main.prompt_user('input Webex Password')
        Device.input_text(defaults['password'])
        Device.input_enter()
