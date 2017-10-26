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
from modules.module import App, Sdk, Module
from utils import AbortAction, is_windows, BUTTON_WIDTH
from versionChecker import VersionChecker


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


class AndroidTab(Frame, object):
    def __init__(self, main_ui):
        Frame.__init__(self, main_ui._notebook)
        main_ui.devices = Listbox(self, width=BUTTON_WIDTH * 2, selectmode='single', exportselection=0, activestyle='none')
        main_ui.devices.grid(row=0, column=0, sticky=W+N)
        Button(self, text='Refresh', width=BUTTON_WIDTH, command=main_ui.refresh_devices).grid(row=1, column=0, sticky=W + N)


class IosTab(Frame, object):
    class ButtonStates(object):
        CONNECT, DISCONNECT, WAIT = 'Connect', 'Disconnect', 'Wait'

    def __init__(self, main_ui):
        Frame.__init__(self, main_ui._notebook)
        Label(self, text='Device').grid(row=0, column=0, sticky=W + N)
        main_ui.ios_device_var = StringVar()
        self._device_field = Entry(self, width=BUTTON_WIDTH, textvariable=main_ui.ios_device_var)
        self._device_field.grid(row=0, column=1, sticky=E + N)
        self._button = Button(self, width=BUTTON_WIDTH, command=self._button_pressed, text=self.ButtonStates.CONNECT)
        self._button.grid(row=1, column=0)

    def _button_pressed(self):
        disconnect = self._button['text'] == self.ButtonStates.DISCONNECT
        if self._button['text'] == self.ButtonStates.CONNECT:
            self._button.config(text=self.ButtonStates.WAIT)
            self._device_field.config(state='disabled')
            self.update_idletasks()
            disconnect = not Device.connect()
            self._button.config(text=self.ButtonStates.DISCONNECT)
        if disconnect:
            Device.disconnect()
            self._device_field.config(state='enabled')
            self._button.config(text=self.ButtonStates.CONNECT)


class AndroidHelperUI(Frame, object):
    def __init__(self, **kw):
        super(AndroidHelperUI, self).__init__(**kw)
        self._config = Config.getInstance()
        self._parent = self._config.ui_root
        self.devices = None
        self.ios_device_var = None
        Frame.__init__(self, self._parent)
        self._config.ui_main = self
        self._init_window()
        self._init_ui_elements()
        self.after(1000, self.refresh_devices)  # 1sec
        self._parent.mainloop()

    def prompt_user(self, next_action):
        d = MyDialog(self, next_action)
        self.wait_window(d.top)
        self._parent.focus_set() #TODO does this solve the take focus after popup issue?
        if not d.success:
            raise AbortAction("Action aborted by user")

    def _init_window(self):
        size = 710, 460
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
        #TODO dedup?
        self.sdks = Listbox(self._parent, width=BUTTON_WIDTH, selectmode='single', exportselection=0, activestyle='none')
        self.sdks.grid(row=0, column=0, rowspan=10, sticky=W + N)
        for sdk in Sdk.iter():
            self.sdks.insert(END, sdk.__name__)
        self.sdks.bind('<Double-Button-1>', self._clear_list)

        self.apps = Listbox(self._parent, width=BUTTON_WIDTH, selectmode='single', exportselection=0, activestyle='none')
        self.apps.grid(row=0, column=1, rowspan=10, sticky=W + N)
        for app in App.iter():
            self.apps.insert(END, app.__name__)
        self.apps.bind('<Double-Button-1>', self._clear_list)

        for checkbox in self._config.get_checkboxes().items():
            name, item = checkbox
            c = Checkbutton(self._parent, text=name.replace('_', ' ').title(), variable=item.var)
            c.grid(row=5 + item.pos, column=2, sticky=W + N) #TODO magic number 5
        #TODO Eran clarify 'leave empty for defaults'
        for textbox in self._config.get_textboxes().items():
            name, item = textbox
            Label(self._parent, text=name.replace('_',' ').title()).grid(row=item.pos, column=2, sticky=E + N)
            e = Entry(self._parent, width=BUTTON_WIDTH, textvariable=item.var)
            e.grid(row=item.pos, column=3, sticky=W + N)

        file_frame = Frame(self._parent)
        file_frame.grid(row=10, column=0, columnspan=4, sticky=W + S)
        Label(file_frame, textvariable=self._config.app.var, width=BUTTON_WIDTH*4).grid(row=0, column=1, sticky=W + N)
        open_file = Button(file_frame, width=BUTTON_WIDTH, command=self._handle_file, text="OPEN FILE")
        open_file.grid(row=0, column=0, sticky=W + N)

        Button(self._parent, text='Run', width=BUTTON_WIDTH, command=Module.run_all).grid(row=11, column=0, sticky=W + N)
        Button(self._parent, text='Uninstall', width=BUTTON_WIDTH, command=Device.uninstall).grid(row=11, column=1, sticky=W + N)
        Button(self._parent, text='Install', width=BUTTON_WIDTH, command=Device.install).grid(row=11, column=2, sticky=W + N)
        Button(self._parent, text='apktoold d', width=BUTTON_WIDTH, command=Device.apktool_d).grid(row=14, column=0, sticky=W + N)
        Button(self._parent, text='apktoold b', width=BUTTON_WIDTH, command=Device.apktool_b).grid(row=14, column=1, sticky=W + N)
        Button(self._parent, text='Screenshot', width=BUTTON_WIDTH, command=Device.take_screenshot).grid(row=14, column=2, sticky=W + N)

        self.log = Text(self._parent, height=10, width=BUTTON_WIDTH*4, background='#ddd', state=DISABLED, font=('Consolas', 10))
        self.log.grid(row=16, column=0, columnspan=5, sticky=W + E)
        ys = Scrollbar(self._parent, command=self.log.yview)
        ys.grid(row=16, column=6, sticky=E+N+S)
        self.log['yscrollcommand'] = ys.set
        xs = Scrollbar(self._parent, command=self.log.xview, orient=HORIZONTAL)
        xs.grid(row=17, column=0, columnspan=5, sticky=E+W+S)
        self.log['xscrollcommand'] = xs.set

        self._notebook = Notebook(self._parent)
        self._notebook.add(AndroidTab(self), text='Android')
        self._notebook.add(IosTab(self), text='iOS')
        self._notebook.bind("<<NotebookTabChanged>>", self._tab_change)
        self._notebook.grid(row=0, column=10, rowspan=19, sticky=W + N)

        self._text_entry = Combobox(self._parent, textvariable=self._config.text_entry.var, width=(BUTTON_WIDTH*2)-3)
        self._text_entry.grid(row=17, column=10)
        Button(self._parent, text='>', width=2, command=self._enter_text).grid(row=17, column=11, sticky=W + N)

        self.new_version = Label(self._parent, foreground="#ff0000")
        self.new_version.grid(row=18, column=0, columnspan=10, sticky=W + S)
        self.after(1000, self._check_version)  # run in one second

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
        if not Device.is_android:
            return
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

    def _check_version(self):
        if VersionChecker.check_upgrade_needed():
            self.new_version.config(text="Newer version detected, please update")
        else:
            self.after(86400000, self._check_version)  # 1 day in milliseconds

    def _clear_list(self, event):
        w = event.widget
        w.selection_clear(0, END)

    def _tab_change(self, event):
        Device.is_android = event.widget.tab(event.widget.select(), "text") == 'Android'


#######################################################################################
######################################### Main ########################################
#######################################################################################
if __name__ == '__main__':
    AndroidHelperUI()
