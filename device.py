from contextlib import contextmanager
from os import system, getenv
try:
    from os import mkfifo
except ImportError:
    pass  # mkfifo doesn't exist on Windows
from os.path import exists, join
from re import compile
from shutil import move
from subprocess import Popen, PIPE
from time import time

from config import Config
from logger import logger
from utils import is_windows, get_full_path



class DeviceMeta(type):
    def __getattr__(cls, item):
        if cls.is_android and hasattr(_AndroidDevice, item):
            return getattr(_AndroidDevice, item)
        elif not cls.is_android and hasattr(_IosDevice, item):
            return getattr(_IosDevice, item)
        else:
            message = 'Unsupported opetaion: ' + item + ' for platform ' + ('Android' if cls.is_android else 'iOS')
            try:
                logger().error(message)
            finally:
                raise AttributeError(message)


class Device(object):
    """
        Accessing this class statically will redirect to the device class of the current choosen platform
    """
    #TODO it might be cleaner to have the current device class on the config and everyone to access it from there
    #TODO   and have a parent class with unsupported thrown from there (would also be better to have the interface as abstract)
    __metaclass__ = DeviceMeta
    is_android = True  # Changed from UI when needed


class _IosDevice(object):
    MOCK_MODE = False #TODO move to config? or dedup with android, also find use for it
    _PIPE_PATH = get_full_path('typethree_pipe')
    _typethree_process = None

    @classmethod
    def connect(cls):
        if is_windows():
            logger().error('iOS not yet supported on Windows')
            return False
        device_name = Config.getInstance().ui_main.ios_device_var.get()
        if not device_name:
            logger().warning('No device to connect to')
            return False
        if not exists(cls._PIPE_PATH):
            try:
                mkfifo(cls._PIPE_PATH)
            except OSError:
                logger().error("Pipe operation isn't supported here")
                return False
        typethree_path = join(getenv('DEV_ENV_PATH'), 'AutoFill', 'TypeThree', 'TypeThree')
        if not typethree_path:
            logger().error("Can't locate typethree")
            return False
        cls._typethree_process = Popen([typethree_path, device_name, '-p', cls._PIPE_PATH], stderr=PIPE)
        ready = False
        while not ready:
            ready = 'Trying to read input from' in cls._typethree_process.stderr.readline()
        logger().debug('iOS connected')
        return True

    @classmethod
    def disconnect(cls):
        #TODO needs to be called before shutting down otherwise typethree process will remain in the background
        if cls._typethree_process:
            cls._typethree_process.terminate()
            cls._typethree_process = None
            logger().debug('iOS disconnected')

    @classmethod
    def input_text(cls, text):
        if not text:
            return
        with open(cls._PIPE_PATH, 'w') as pipe:
            pipe.write(text)
            pipe.flush()
        logger().debug('iOS text: ' + text)

    @classmethod
    def input_enter(cls):
        cls.input_text('\n')

    @classmethod
    def input_tab(cls):
        cls.input_text('\t')

    @classmethod
    @contextmanager
    def get_logs(cls):
        #TODO implement
        yield

    @classmethod
    def install(cls):
        pass #TODO implement

    @classmethod
    def uninstall(cls):
        pass #TODO implement

    @classmethod
    def run(cls):
        pass  # TODO implement


class _AndroidDevice(object):
    _adb_input_cmd = ['shell', 'input']
    MOCK_MODE = False #TODO move to config?

    @classmethod
    def input_enter(cls):
        cls._action(cls._get_adb_command_prefix() + cls._adb_input_cmd + ['keyevent', '66'])

    @classmethod
    def input_tab(cls):
        cls._action(cls._get_adb_command_prefix() + cls._adb_input_cmd + ['keyevent', '61'])

    @classmethod
    def input_text(cls, text):
        if not text:
            return
        cls._action(cls._get_adb_command_prefix() + cls._adb_input_cmd + ['text', '"' + text + '"'])

    @classmethod
    def install(cls):
        file_path = Config.getInstance().app()
        if not file_path:
            logger().error('No app to install')
            return
        cls._action(cls._get_adb_command_prefix() + ['install', file_path])

    @classmethod
    def uninstall(cls):
        if not Config.getInstance().app():
            logger().error('No app to uninstall')
            return
        package_id = cls._get_package_id()
        cls._action(cls._get_adb_command_prefix() + ['uninstall', package_id])

    @classmethod
    def run(cls):
        if not Config.getInstance().app():
            logger().error('No app to run')
            return
        package_id = cls._get_package_id()
        cls._action(cls._get_adb_command_prefix() + ['shell', 'monkey', '-p', package_id, '-c', 'android.intent.category.LAUNCHER', '1'])

    @classmethod
    def _action(cls, cmd):
        logger().debug(" ".join(cmd))
        if not cls.MOCK_MODE:
            try:
                if is_windows():
                    CREATE_NO_WINDOW = 0x08000000 # Doesn't really work, shows a window and hides it
                    # TODO synchronicity should be according to param, sometimes it might be could to cancel it
                    Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW).communicate()
                else:
                    system(" ".join(cmd))
            except Exception as e:
                logger().error("Command failed " + str(e)) #TODO eran also check ret code

    @classmethod
    def _get_package_id(cls):
        if cls.MOCK_MODE:
            return 'abc'
        cmd = ['aapt', 'dump', 'badging', Config.getInstance().app()]
        out = Popen(cmd, stdout=PIPE).communicate()[0]
        return out.split("package: name='")[1].split("'", 1)[0]

    @staticmethod
    def get_device_list():
        ret = []
        p = compile(r'(.*?)\s+.*?model:(.*?)\s+.*')
        try:
            out = Popen(['adb', 'devices', '-l'], stdout=PIPE).communicate()[0]
            for line in out.splitlines():
                m = p.match(line)
                if m:
                    ret.append((m.group(1), m.group(2)))
        except:
            logger().error("Can't get device list, no adb?")
        return ret

    @staticmethod
    def _get_selected_device():
        Config.getInstance().ui_main.refresh_devices()
        device_list = Config.getInstance().ui_main.devices
        indices = device_list.curselection()
        if not indices:
            return
        return device_list.get(indices[0])

    @classmethod
    def _get_adb_command_prefix(cls):
        device = cls._get_selected_device()
        if device:
            return ['adb', '-s', device[0]]
        return ['adb']

    @classmethod
    @contextmanager
    def get_logs(cls):
        config = Config.getInstance()
        if not config.logs() or cls.MOCK_MODE:
            yield
            return

        filename = config.log_name()
        if not filename:
            filename = str(time()).replace('.', '')
        filename += '.log'
        filename = join(config.defaults.get('folder'), filename)
        logger().info('Starting logs capture to ' + filename)
        with open(filename, 'w') as f:
            cls._action(cls._get_adb_command_prefix() + ['logcat', '-c'])
            cmd = cls._get_adb_command_prefix() + ['logcat', '-v', 'time']
            if is_windows():
                CREATE_NO_WINDOW = 0x08000000  # Doesn't really work, shows a window and hides it
                p = Popen(cmd, stdout=f, creationflags=CREATE_NO_WINDOW)
            else:
                p = Popen(cmd, stdout=f)
            try:
                yield
            finally:
                p.kill()
                logger().info('finished logs capture to ' + filename)

    @classmethod
    def take_screenshot(cls):
        device = cls._get_selected_device()
        if not device:
            logger().error("Can't take screenshot, no device connected")
            return
        filename = device[1] + str(time()).replace('.', '') + '.png'
        cls._action(cls._get_adb_command_prefix() + ['shell', 'screencap', '-p', '/sdcard/', filename])
        cls._action(cls._get_adb_command_prefix() + ['pull', '/sdcard/', filename])
        cls._action(cls._get_adb_command_prefix() + ['shell', 'rm', '/sdcard/', filename])
        dest = Config.getInstance().defaults.get('folder')
        move(filename, dest)
        logger().info("Saved image to " + join(dest, filename))

    @classmethod
    def apktool_d(cls):
        app = Config.getInstance().app()
        if not app:
            logger().error('No app selected')
            return
        # TODO eran if exists delete it or error, otherwise apktool fails anyway
        folder = app[:-4]
        cls._action(['apktool', 'd', app, '-o', folder])

        logger().info("Done")

    @classmethod
    def apktool_b(cls):
        app = Config.getInstance().app()
        if not app:
            logger().error('No app selected')
            return
        folder = app[:-4]
        if not exists(folder):
            logger().error("app wasn't disassembled")
            return
        cls._action(['apktool', 'b', folder, '-o', folder + '_rebuilt' + app[-4:]])
        logger().info("Done")
