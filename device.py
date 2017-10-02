from contextlib import contextmanager
from os import system
from os.path import exists, join
from re import compile
from shutil import move
from subprocess import Popen, PIPE
from time import time

from config import Config
from logger import logger
from utils import is_windows


class Device(object):
    MOCK_MODE = False #TODO move to config?
    _adb_input_cmd = ' shell input'

    @classmethod
    def input_enter(cls):
        cls.action(cls.get_adb_command_prefix() + cls._adb_input_cmd + ' keyevent 66')

    @classmethod
    def input_tab(cls):
        cls.action(cls.get_adb_command_prefix() + cls._adb_input_cmd + ' keyevent 61')

    @classmethod
    def input_text(cls, text):
        cls.action(cls.get_adb_command_prefix() + cls._adb_input_cmd + ' text "' + text + '"')

    @classmethod
    def install(cls):
        file_path = Config.getInstance().app()
        if not file_path:
            logger().error('No app to install')
            return
        cls.action(cls.get_adb_command_prefix() + ' install ' + file_path)

    @classmethod
    def uninstall(cls):
        if not Config.getInstance().app():
            logger().error('No app to uninstall')
            return
        package_id = cls.get_package_id()
        cls.action(cls.get_adb_command_prefix() + ' uninstall ' + package_id)

    @classmethod
    def run(cls):
        if not Config.getInstance().app():
            logger().error('No app to run')
            return
        package_id = cls.get_package_id()
        cls.action(cls.get_adb_command_prefix() + ' shell monkey -p ' + package_id + ' -c android.intent.category.LAUNCHER 1')

    @classmethod
    def action(cls, cmd):
        logger().debug(cmd)
        if not cls.MOCK_MODE:
            try:
                if is_windows():
                    CREATE_NO_WINDOW = 0x08000000 # Doesn't really work, shows a window and hides it
                    # TODO synchronicity should be according to param, sometimes it might be could to cancel it
                    Popen(cmd.split(' '), shell=True, stdout=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW).communicate()
                else:
                    system(cmd)
            except Exception as e:
                logger().error("Command failed " + str(e)) #TODO eran also check ret code

    @classmethod
    def get_package_id(cls):
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
    def get_selected_device():
        Config.getInstance().ui_main.refresh_devices()
        device_list = Config.getInstance().ui_main.devices
        indices = device_list.curselection()
        if not indices:
            return
        return device_list.get(indices[0])

    @classmethod
    def get_adb_command_prefix(cls):
        device = cls.get_selected_device()
        if device:
            return 'adb -s ' + device[0]
        return 'adb'

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
            cls.action(cls.get_adb_command_prefix() + ' logcat -c')
            cmd = cls.get_adb_command_prefix().split() + ['logcat', '-v', 'time']

            CREATE_NO_WINDOW = 0x08000000  # Doesn't really work, shows a window and hides it
            p = Popen(cmd, stdout=f, creationflags=CREATE_NO_WINDOW)
            try:
                yield
            finally:
                p.kill()
                logger().info('finished logs capture to ' + filename)

    @classmethod
    def take_screenshot(cls):
        device = cls.get_selected_device()
        if not device:
            logger().error("Can't take screenshot, no device connected")
            return
        filename = device[1] + str(time()).replace('.', '') + '.png'
        cls.action(cls.get_adb_command_prefix() + ' shell screencap -p /sdcard/' + filename)
        cls.action(cls.get_adb_command_prefix() + ' pull /sdcard/' + filename)
        cls.action(cls.get_adb_command_prefix() + ' shell rm /sdcard/' + filename)
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
        cls.action('apktool d ' + app + ' -o ' + folder)

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
        cls.action('apktool b ' + folder + ' -o ' + folder + '_rebuilt' + app[-4:])
        logger().info("Done")
