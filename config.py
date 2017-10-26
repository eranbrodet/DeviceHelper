try:
    from Tkinter import BooleanVar, Tk, StringVar  # Python 2
except ImportError:
    from tkinter import BooleanVar, Tk, StringVar  # Python 3
from json import load as json_load

from utils import Singleton, get_full_path


class Types(object):
    Checkbox, String, File, Combo = range(4)


class Item(object):
    def __init__(self, var, type, defaults_name=None, position=0):
        self.type = type
        self.var = var
        self._defaults_name = defaults_name
        self.pos = position

    def __call__(self, *args, **kwargs):
        ret = self.var.get()
        if self.type == Types.String and not ret:
            config = Config.getInstance()
            ret = config.defaults.get(config.current_sdk, {}).get(self._defaults_name)
        return ret


@Singleton
class Config(object):
    def __init__(self):
        # UI stuff
        self.ui_root = Tk()
        self.ui_main = None
        # Checkboxes
        self.input_only = Item(BooleanVar(), Types.Checkbox, position=0)
        self.logs = Item(BooleanVar(), Types.Checkbox, position=1)

        # Text fields
        self.user = Item(StringVar(), Types.String, 'user', 0)
        self.user_password = Item(StringVar(), Types.String, 'user_password', 1)
        self.local_password = Item(StringVar(), Types.String, 'local_password', 2)
        self.log_name = Item(StringVar(), Types.String, position=3)

        # Combo boxes
        self.text_entry = Item(StringVar(), Types.Combo, 'text', 0)
        self._text_history = []

        self.app = Item(StringVar(), Types.File)
        self.defaults = self._load_defaults()
        self.current_sdk = None

    def get_checkboxes(self):
        return {k:v for k, v in vars(self).items() if type(v) == Item and v.type == Types.Checkbox}

    def get_textboxes(self):
        return {k:v for k, v in vars(self).items() if type(v) == Item and v.type == Types.String}

    def set_sdk_for_defaults(self, sdk):
        self.current_sdk = sdk

    def _load_defaults(self):
        with open(get_full_path('defaults.json')) as f:
            return json_load(f)
