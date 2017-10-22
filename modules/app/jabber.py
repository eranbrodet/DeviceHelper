from device import Device
from modules.module import App


class Jabber(App):
    def run(self):
        defaults = self._config.defaults.get('jabber', {})
        self._config.ui_main.prompt_user('input Jabber user')
        Device.input_text(defaults['user'])
        Device.input_enter()
        self._config.ui_main.prompt_user('input Jabber Password')
        Device.input_text(defaults['password'])
        Device.input_enter()