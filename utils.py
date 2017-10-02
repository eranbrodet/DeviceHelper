from platform import system

import requests #TODO Eran this is a dependency, can probably do just fine with builtin urllib
from re import search
from time import sleep

from requests.packages.urllib3 import disable_warnings


class AbortAction(Exception): pass


class Singleton(object):
    """
        Adapted from: http://stackoverflow.com/a/7346105/2134702
    """

    def __init__(self, decorated):
        self._decorated = decorated

    def getInstance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `getInstance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

    def __getattr__(self, name):
        return getattr(self._decorated, name)


class BlackBerryUtils(object):
    def __init__(self, defaults):
        self._defaults = defaults['good']

    def get_access_key_from_server(self, user_name):
        disable_warnings()
        user_id = self.get_user_id_by_username(user_name)
        for i in range(3):
            # Verify=False, is for SSL to not fail when cert is invalid.
            response = requests.post(self._defaults['service_url'], data=self._defaults['get_new_key_body'] % (user_id,), headers=self._defaults['header_data'], verify=False)
            if response.status_code == 200:
                return search("(?<=<ns4:pin>)(.*)(?=</ns4:pin>)", response._content).group(0)
            sleep(3)
        return ""

    def get_user_id_by_username(self, username):
        for i in range(3):
            response = requests.post(self._defaults['cap_url'], data=self._defaults['cap_body'], headers=self._defaults['cap_header_data'], verify=False)
            content = response._content.replace("><", ">\n<").split("\n")
            content = list(reversed(content))
            if response.status_code == 200:
                found_user = False
                #TODO eran content is everyone, can use it to generate ui list
                for line in content:
                    if found_user:
                        return search("(?<=<ns1:user_id>)(.*)(?=</ns1:user_id>)", line).group(0)
                    if username in line:
                        found_user = True
            else:
                print(response.status_code)
            sleep(3)
        return ""

def is_windows():
    return system == 'Windows'