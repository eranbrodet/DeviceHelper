#!/usr/bin/python
from functools import partial
try:   # Python 2
    from Tkinter import *
    from ttk import *
    from tkFileDialog import askopenfilename
except ImportError as e:  # Python 3
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.filedialog import askopenfilename
from config import Config
from device import Device
from sdks import Sdks
from utils import AbortAction, is_windows


class MyDialog(object):
    def __init__(self, main_ui, next_action):
        self.top = Toplevel(main_ui._parent)
        size = (300, 100)
        # Center position on screen
        w = main_ui._parent.winfo_screenwidth()
        h = main_ui._parent.winfo_screenheight()
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        self.top.geometry("%dx%d+%d+%d" % (size + (x, y)))

        self.success = False

        Label(self.top, text='Will ' + next_action + '\nEsc to abort, any other key to continue').pack()
        b = Button(self.top, text="OK", command=partial(self.ok, True))
        b.pack(pady=5)
        b.focus_set()
        b.bind('<Escape>', partial(self.ok, False))
        b.bind('<Key>', partial(self.ok, True))

    def ok(self, code, event=None):
        self.success = code
        self.top.destroy()


class AndroidHelperUI(Frame, object):
    _SDKS = ['Airwatch', 'Good', 'Lagoon']
    BUTTON_WIDTH = 15 if is_windows() else 9

    def __init__(self, **kw):
        super(AndroidHelperUI, self).__init__(**kw)
        self._config = Config.getInstance()
        self._parent = self._config.ui_root
        Frame.__init__(self, self._parent)
        self._config.ui_main = self
        self._init_window()
        self._init_ui_elements()
        self.refresh_devices()
        self._parent.mainloop()

    def prompt_user(self, next_action):
        d = MyDialog(self, next_action)
        self.wait_window(d.top)
        self._parent.focus_set() #TODO does this solve the take focus after popup issue?
        if not d.success:
            raise AbortAction("Action aborted by user")

    def _init_window(self):
        size = 700, 400
        # Center position on screen
        w = self._parent.winfo_screenwidth()
        h = self._parent.winfo_screenheight()
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        self._parent.geometry("%dx%d+%d+%d" % (size + (x, y)))
        self._parent.minsize(*size)

        # Set the root icon, for some reason Linux acts a bit special here. See http://stackoverflow.com/a/11180300/2134702
        # TODO eran set icon for linux?
        # if platform == "linux" or platform == "linux2":
        #     daffy_image = PhotoImage(file=join("images", 'daffy.png'))
        #     root.tk.call('wm', 'iconphoto', root._w, daffy_image)
        # else:
        self._parent.iconbitmap('icon.ico')
        self._parent.title("Android Helper")

    def _init_ui_elements(self):
        self._buttons = []
        for i, sdk_name in enumerate(self._SDKS):
            b = Button(self._parent, text=sdk_name, width=self.BUTTON_WIDTH, command=partial(Sdks.run, getattr(Sdks, sdk_name.lower())))
            b.grid(row=i, column=0, sticky=W + N)
            self._buttons.append(b)

        for checkbox in self._config.get_checkboxes().items():
            name, item = checkbox
            c = Checkbutton(self._parent, text=name.replace('_',' ').title(), variable=item.var)
            c.grid(row=item.pos, column=1, sticky=W + N)

        #TODO Eran clarify 'leave empty for defaults'
        for textbox in self._config.get_textboxes().items():
            name, item = textbox
            Label(self._parent, text=name.replace('_',' ').title()).grid(row=item.pos, column=2, sticky=E + N)
            e = Entry(self._parent, width=self.BUTTON_WIDTH, textvariable=item.var)
            e.grid(row=item.pos, column=3, sticky=W + N)

        file_frame = Frame(self._parent)
        file_frame.grid(row=10, column=0, columnspan=4, sticky=W + S)
        Label(file_frame, textvariable=self._config.app.var).grid(row=0, column=1, sticky=W + N)
        open_file = Button(file_frame, width=self.BUTTON_WIDTH, command=self._handle_file, text="OPEN FILE")
        open_file.grid(row=0, column=0, sticky=W + N)

        Button(self._parent, text='Uninstall', width=self.BUTTON_WIDTH, command=Device.uninstall).grid(row=11, column=0, sticky=W + N)
        Button(self._parent, text='Install', width=self.BUTTON_WIDTH, command=Device.install).grid(row=11, column=1, sticky=W + N)
        Button(self._parent, text='apktoold d', width=self.BUTTON_WIDTH, command=Device.apktool_d).grid(row=14, column=0, sticky=W + N)
        Button(self._parent, text='apktoold b', width=self.BUTTON_WIDTH, command=Device.apktool_b).grid(row=14, column=1, sticky=W + N)
        Button(self._parent, text='Screenshot', width=self.BUTTON_WIDTH, command=Device.take_screenshot).grid(row=14, column=2, sticky=W + N)

        self.log = Text(self._parent, height=10, width=self.BUTTON_WIDTH*4, background='#ddd', state=DISABLED, font=('Consolas', 10))
        self.log.grid(row=16, column=0, columnspan=5, sticky=W + E)
        ys = Scrollbar(self._parent, command=self.log.yview)
        ys.grid(row=16, column=6, sticky=E+N+S)
        self.log['yscrollcommand'] = ys.set
        xs = Scrollbar(self._parent, command=self.log.xview, orient=HORIZONTAL)
        xs.grid(row=17, column=0, columnspan=5, sticky=E+W+S)
        self.log['xscrollcommand'] = xs.set

        Button(self._parent, text='Refresh', width=self.BUTTON_WIDTH, command=self.refresh_devices).grid(row=0, column=10, sticky=W + N)
        self.devices = Listbox(self._parent, width=self.BUTTON_WIDTH*2, selectmode='single', exportselection=0, activestyle='none')
        self.devices.grid(row=1, column=10, rowspan=17, sticky=W+N)

        self._text_entry = Combobox(self._parent, textvariable=self._config.text_entry.var, width=(self.BUTTON_WIDTH*2)-3)
        self._text_entry.grid(row=17, column=10)
        Button(self._parent, text='>', width=2, command=self._enter_text).grid(row=17, column=11, sticky=W + N)

    def _handle_file(self):
        if is_windows():
            f = askopenfilename(filetypes=[('App','*.apk;*.ipa'), ('All files', '*')], initialdir=self._config.defaults.get('folder'))
        else:
            #TODO Eran for mac the filetypes didn't work correctly
            f = askopenfilename(initialdir=self._config.defaults.get('folder'))
        if f:
            self._config.app.var.set(f)

    def _enter_text(self):
        text = self._config.text_entry()
        # Send command
        Device.input_text(self._config.text_entry())
        # Update history
        if text in self._config._text_history:
            self._config._text_history.remove(text)
        self._config._text_history.insert(0, text)
        self._text_entry.config(values=self._config._text_history)
        #TODO Eran consider limiting the history

    def refresh_devices(self):
        previous_selection = None
        new_selection_index = 0
        if self.devices.size() != 0:
            previous_selection = self.devices.get(self.devices.curselection()[0])

        self.devices.delete(0, END)
        for i, device in enumerate(Device.get_device_list()):
            self.devices.insert(END, device)
            if device == previous_selection:
                new_selection_index = i
        self.devices.selection_set(new_selection_index)


#######################################################################################
######################################### Main ########################################
#######################################################################################
if __name__ == '__main__':
    AndroidHelperUI()
