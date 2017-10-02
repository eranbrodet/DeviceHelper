from distutils.version import StrictVersion
from urllib import urlopen


class VersionChecker(object):
    _URL = 'https://raw.githubusercontent.com/eranbrodet/DeviceHelper/master/version.txt'

    @classmethod
    def _getVersion(cls):
        #TODO Eran handle errors such as no connection
        r = urlopen(cls._URL).read()
        return StrictVersion(r)

    @classmethod
    def check_upgrade_needed(cls):
        with open('version.txt') as f:
            current_version = StrictVersion(f.read())
        latest_version = cls._getVersion()
        return current_version < latest_version

