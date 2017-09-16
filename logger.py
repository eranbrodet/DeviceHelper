from logging import Handler, getLogger, Formatter, StreamHandler, DEBUG, INFO, WARNING, ERROR
from sys import stdout
try:
    from Tkinter import END, NORMAL, DISABLED  # Python 2
except ImportError:
    from tkinter import END, NORMAL, DISABLED  # Python 3
from config import Config


class UiHandler(Handler):
    _COLOURS = {DEBUG: '#0077ff', INFO: '#007700', WARNING: '#FF4500', ERROR:'#990000'}
    _BUFFER = 1000  # TODO Worry about performance of too many tags?
    _lines = 0


    def emit(self, record):
        ui_log_box = Config.getInstance().ui_main.log
        ui_log_box.config(state=NORMAL)

        if self._lines >= self._BUFFER:
            ui_log_box.delete(1.0, END)
            self._lines = 0

        message = self.format(record)+"\n"
        tag_name = str(self._lines)
        ui_log_box.tag_config(tag_name, foreground=self._COLOURS[record.levelno])
        ui_log_box.insert(END, message, tag_name)
        ui_log_box.see(END)
        ui_log_box.config(state=DISABLED)
        self._lines += 1


def logger():
    """
        @name Logger's name.
        @returns A logger object which will log to the screen (only).
    """
    if hasattr(logger, '_logger'):
        return logger._logger
    logger._logger = getLogger('mylogger')
    formatter = Formatter(fmt="[%(levelname)s] %(message)s")
    for handler in [StreamHandler(stdout), UiHandler()]:
        handler.setFormatter(formatter)
        logger._logger.addHandler(handler)
        logger._logger.setLevel(DEBUG)
    return logger._logger
