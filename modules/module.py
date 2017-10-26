from config import Config
from device import Device
from logger import logger
from utils import AbortAction


class Module(object):
    def run(self):
        pass

    @classmethod
    def iter(cls):
        for x in cls.__subclasses__():
            yield x

    def __init__(self):
        self._logger = logger()
        self._config = Config.getInstance()

    @classmethod
    def get(cls, name):
        for item in cls.iter():
            if item.__name__ == name:
                return item

    _config = Config.getInstance()

    @classmethod
    def run_all(cls):
        try:
            if not Device.MOCK_MODE and Device.is_android and cls._config.ui_main.devices.size() == 0:
                raise AbortAction('no devices found')
            sdk = None
            sdk_indices = cls._config.ui_main.sdks.curselection()
            if sdk_indices:
                sdk = Sdk.get(cls._config.ui_main.sdks.get(sdk_indices[0]))

            app = None
            app_indices = cls._config.ui_main.apps.curselection()
            if app_indices:
                app = App.get(cls._config.ui_main.apps.get(app_indices[0]))

            with Device.get_logs():
                if not cls._config.input_only():
                    cls._common_pre()
                if sdk:
                    cls._config.set_sdk_for_defaults(sdk.__name__.lower())
                    sdk().run()
                if app:
                    app().run()
                if not cls._config.input_only():
                    cls._common_post()
                if cls._config.logs():
                    cls._config.ui_main.prompt_user('stop logs')
        except AbortAction as e:
            logger().info('Abort: ' + str(e))
        else:
            logger().info('Done')

    @classmethod
    def _common_pre(cls):
        Device.uninstall()
        Device.install()
        Device.run()

    @classmethod
    def _common_post(cls):
        pass


class Sdk(Module):
    pass


class App(Module):
    pass
