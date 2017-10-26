from distutils.version import StrictVersion
try:   # Python 2
    from urllib import urlopen
except ImportError:  # Python 3
    from urllib.request import urlopen

from utils import get_full_path

class VersionChecker(object):
    _URL = 'https://raw.githubusercontent.com/eranbrodet/DeviceHelper/master/version.txt'

    @classmethod
    def _getVersion(cls):
        #TODO Eran handle errors such as no connection
        r = urlopen(cls._URL).read()
        return StrictVersion(r.decode('utf-8'))

    @classmethod
    def check_upgrade_needed(cls):
        with open(get_full_path('version.txt')) as f:
            current_version = StrictVersion(f.read())
        latest_version = cls._getVersion()
        return current_version < latest_version

