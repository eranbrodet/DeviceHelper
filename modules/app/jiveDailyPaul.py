from device import Device
from modules.module import App


class JiveDailyPaul(App):
    def run(self):
        # TODO relies on configuration being there and uses magic strings as dict keys
        defaults = self._config.defaults.get('jive_daily_paul', {})
        self._config.ui_main.prompt_user('input jive url')
        Device.input_text(defaults['url'])
        Device.input_tab()
        Device.input_enter()
        self._config.ui_main.prompt_user('input jive login')
        Device.input_text(defaults['user'])
        Device.input_tab()
        Device.input_text(defaults['password'])
        Device.input_tab()
        Device.input_enter()
