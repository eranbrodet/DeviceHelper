from config import Config
from device import Device
from logger import logger
from utils import BlackBerryUtils, AbortAction


class Sdks(object):
    _config = Config.getInstance()
    _black_berry_utils = BlackBerryUtils(_config.defaults)

    @classmethod
    def run(cls, sdk_action):
        try:
            if cls._config.ui_main.devices.size() == 0:
                raise AbortAction('no devices found')
            with Device.get_logs():
                cls._config.set_sdk_for_defaults(sdk_action.__name__)
                if not cls._config.input_only():
                    cls._common_pre()
                sdk_action()
                if not cls._config.input_only():
                    cls._common_post()
                if cls._config.logs():
                    cls._config.ui_main.prompt_user('stop logs')
        except AbortAction as e:
            logger().info('Abort: ' + str(e))
        else:
            logger().info('Done')

    @classmethod
    def good(cls):
        server_user = cls._config.defaults.get('good', {}).get('good_user', 'Eran Brodet')
        if Device.MOCK_MODE:
            access_key = '123451234512345'
        else:
            access_key = cls._black_berry_utils.get_access_key_from_server(server_user)
        logger().info('Access key is ' + access_key)

        cls._config.ui_main.prompt_user('input login')
        Device.input_text(cls._config.user())
        Device.input_enter()
        Device.input_text(access_key)
        Device.input_enter()
        cls._config.ui_main.prompt_user('input password')
        Device.input_text(cls._config.local_password())
        Device.input_enter()
        Device.input_text(cls._config.local_password())
        Device.input_enter()
        Device.input_enter()

    @classmethod
    def airwatch(cls):
        cls._config.ui_main.prompt_user('input Login')
        Device.input_text(cls._config.user())
        Device.input_tab()
        Device.input_text(cls._config.user_password())
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
        cls._config.ui_main.prompt_user('input local password')
        Device.input_text(cls._config.local_password())
        Device.input_tab()
        Device.input_text(cls._config.local_password())
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()

    @classmethod
    def lagoon(cls):
        cls._config.ui_main.prompt_user('input user')
        Device.input_text(cls._config.user())
        Device.input_tab()
        Device.input_enter()
        cls._config.ui_main.prompt_user('input password')
        Device.input_text(cls._config.user_password())
        Device.input_tab()
        Device.input_enter()
        cls._config.ui_main.prompt_user('input local password')
        Device.input_text(cls._config.local_password())
        Device.input_tab()
        Device.input_text(cls._config.local_password())
        Device.input_tab()
        Device.input_enter()

    @classmethod
    def _common_pre(cls):
        Device.uninstall()
        Device.install()
        Device.run()

    @classmethod
    def _common_post(cls):
        if cls._config.jive_daily():
            cls._jive_daily()
        elif cls._config.secret_server():
            cls._secret_server()
        elif cls._config.tango():
            cls._tango()
        elif cls._config.jabber():
            cls._jabber()

    @classmethod
    def _jive_daily(cls):
        #TODO relies on configuration being there and uses magic strings as dict keys
        defaults = cls._config.defaults.get('jive_daily', {})
        cls._config.ui_main.prompt_user('input jive url')
        Device.input_text(defaults['url'])
        Device.input_tab()
        Device.input_enter()
        cls._config.ui_main.prompt_user('input jive login')
        Device.input_text(defaults['user'])
        Device.input_tab()
        Device.input_text(defaults['password'])
        Device.input_tab()
        Device.input_enter()

    @classmethod
    def _secret_server(cls):
        defaults = cls._config.defaults.get('secret_server', {})
        cls._config.ui_main.prompt_user('input Secret Server credentials')
        Device.input_text(defaults['user'])
        Device.input_tab()
        Device.input_text(defaults['org'])
        Device.input_tab()
        Device.input_text(defaults['password'])
        Device.input_tab()
        Device.input_enter()

    @classmethod
    def _tango(cls):
        defaults = cls._config.defaults.get('tango', {})
        cls._config.ui_main.prompt_user('input Tango Account ID')
        Device.input_text(defaults['user'])
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
        cls._config.ui_main.prompt_user('input Tango Password')
        Device.input_text(defaults['password'])
        Device.input_tab()
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
        cls._config.ui_main.prompt_user('input Tango URL')
        Device.input_text(defaults['url'])
        Device.input_tab()
        Device.input_tab()
        Device.input_enter()
        
    @classmethod
    def _jabber(cls):
        defaults = cls._config.defaults.get('jabber', {})
        cls._config.ui_main.prompt_user('input Jabber user')
        Device.input_text(defaults['user'])
        Device.input_enter()
        cls._config.ui_main.prompt_user('input Jabber Password')
        Device.input_text(defaults['password'])
        Device.input_enter()
