#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import datetime
import os
import random
import signal
import socket
import subprocess
import sys
import tempfile
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
Spinbox = ttk.Spinbox if hasattr(ttk, "Spinbox") else tk.Spinbox
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
if sys.version_info[:2] > (3, 1):
    import warnings
    warnings.simplefilter("ignore", ResourceWarning) # For stdlib socket.py
import rpyc
import TkUtil
import TkUtil.Dialog
import MeterLogin
if sys.version_info[:2] < (3, 3):
    ConnectionError = socket.error


HOST = "localhost"
PORT = 11003
SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "meterserver-rpyc.py")
PAD = "0.75m"


def main():
    application = tk.Tk()
    application.withdraw() # hide until ready to show
    application.title("Meter")
    application.option_add("*tearOff", False) # Avoid ugly tear menu line
    application.option_add("*insertOffTime", 0, 100)
    set_icons(application)
    window = Window(application)
    application.protocol("WM_DELETE_WINDOW", window.close)
    application.deiconify() # show
    application.mainloop()


def set_icons(application):
    path = os.path.dirname(os.path.abspath(__file__))
    try:
        icon32 = tk.PhotoImage(file=os.path.join(path, "meter_32x32.gif"))
        icon16 = tk.PhotoImage(file=os.path.join(path, "meter_16x16.gif"))
        application.tk.call("wm", "iconphoto", application, "-default",
                icon32, icon16)
    except tk.TclError:
        pass # Let the application run without its icons


class Window(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.serverPid = None
        self.create_variables()
        self.create_ui()
        self.statusText.set("Ready...")
        self.countsText.set("Read 0/0")
        self.master.after(100, self.login)


    def login(self):
        result = MeterLogin.Result()
        dialog = MeterLogin.Window(self, result)
        if result.ok and self.connect(result.username, result.password):
            self.get_job()
        else:
            self.close()


    def connect(self, username, password):
        try:
            self.service = rpyc.connect(HOST, PORT)
        except ConnectionError:
            filename = os.path.join(tempfile.gettempdir(),
                    "M{}.$$$".format(random.randint(1000, 9999)))
            self.serverPid = subprocess.Popen([sys.executable, SERVER,
                    filename]).pid
            self.wait_for_server(filename)
            try:
                self.service = rpyc.connect(HOST, PORT)
            except ConnectionError:
                self.handle_error("Failed to start the RPYC Meter server")
                return False
        self.manager = self.service.root
        return self.login_to_server(username, password)


    def wait_for_server(self, filename):
        tries = 100
        while tries:
            if os.path.exists(filename):
                os.remove(filename)
                break
            time.sleep(0.1) # Give the server a chance to start
            tries -= 1
        else:
            raise ConnectionError()


    def login_to_server(self, username, password):
        try:
            self.sessionId, name = self.manager.login(username, password)
            self.master.title("Meter \u2014 {}".format(name))
            return True
        except rpyc.core.vinegar.GenericException as err:
            self.handle_error(err)
            return False


    def create_variables(self):
        self.meter = tk.StringVar()
        self.reading = tk.StringVar()
        self.reading.set(-1)
        self.reason = tk.StringVar()
        self.statusText = tk.StringVar()
        self.countsText = tk.StringVar()


    def create_ui(self):
        self.create_widgets()
        self.layout_widgets()
        self.create_bindings()


    def create_widgets(self):
        self.meterLabel = ttk.Label(self, text="Meter")
        self.meterIdLabel = ttk.Label(self, textvariable=self.meter)
        self.readingLabel = ttk.Label(self, text="Reading:", underline=0)
        self.readingSpinbox = Spinbox(self, from_=-1, to=999999,
                textvariable=self.reading, validate="all")
        self.readingSpinbox.config(validatecommand=(
            self.readingSpinbox.register(self.validate), "%P"))
        self.reasonLabel = ttk.Label(self, text="Reason:", underline=1)
        self.reasonCombobox = ttk.Combobox(self,
                textvariable=self.reason, values=("Read",
                    "Refused entry", "No access", "Failed to find meter"))
        self.submitButton = TkUtil.Button(self, text="Submit",
                underline=0, command=self.submit, state=tk.DISABLED)
        self.quitButton = TkUtil.Button(self, text="Quit", underline=0,
                command=self.close)
        self.statusLabel = ttk.Label(self, textvariable=self.statusText,
                justify=tk.LEFT)
        self.countsLabel = ttk.Label(self, textvariable=self.countsText,
                anchor=tk.CENTER, relief=tk.SUNKEN)


    def validate(self, number=None):
        self.update_ui()
        return TkUtil.validate_spinbox_int(self.readingSpinbox, number)


    def layout_widgets(self):
        pad = dict(padx=PAD, pady=PAD)
        padWE = dict(sticky=(tk.W, tk.E), **pad)
        self.meterLabel.grid(row=0, column=0, sticky=tk.W, **pad)
        self.meterIdLabel.grid(row=0, column=1, columnspan=2, **padWE)
        self.readingLabel.grid(row=1, column=0, sticky=tk.W, **pad)
        self.readingSpinbox.grid(row=1, column=1, columnspan=2, **padWE)
        self.reasonLabel.grid(row=2, column=0, sticky=tk.W, **pad)
        self.reasonCombobox.grid(row=2, column=1, columnspan=2,
                **padWE)
        self.submitButton.grid(row=3, column=1, **pad)
        self.quitButton.grid(row=3, column=2, **pad)
        self.statusLabel.grid(row=4, column=0, columnspan=2, **padWE)
        self.countsLabel.grid(row=4, column=2, **padWE)
        self.grid_columnconfigure(1, weight=1)
        self.grid()
        self.master.resizable(False, False) # Get rid of size grip


    def create_bindings(self):
        self.master.bind("<Alt-e>",
                lambda *args: self.reasonCombobox.focus())
        self.master.bind("<Alt-r>",
                lambda *args: self.readingSpinbox.focus())
        self.master.bind("<Alt-s>", self.submit)
        self.master.bind("<Alt-q>", self.close)
        self.bind("<Return>", self.submit)
        self.bind("<Escape>", self.close)
        self.reading.trace("w", self.update_ui)
        self.reason.trace("w", self.update_ui)


    def update_ui(self, *args):
        reading = self.reading.get()
        reading = int(reading) if reading else -1
        reason = self.reason.get()
        state = ("!" + tk.DISABLED if reading > -1 or
                (reading == -1 and reason and reason != "Read")
                else tk.DISABLED)
        self.submitButton.state((state,))


    def get_job(self):
        try:
            meter = self.manager.get_job(self.sessionId)
            if not meter:
                messagebox.showinfo("Meter \u2014 Finished",
                    "All jobs done", parent=self)
                self.close()
            self.meter.set(meter)
            self.readingSpinbox.focus()
        except (xmlrpc.client.Fault, ConnectionError) as err:
            self.handle_error(err)



    def submit(self, event=None):
        if self.submitButton.instate((tk.DISABLED,)):
            return
        meter = self.meter.get()
        reading = self.reading.get()
        reading = int(reading) if reading else -1
        reason = self.reason.get()
        if reading > -1 or (reading == -1 and reason and reason != "Read"):
            try:
                self.manager.submit_reading(self.sessionId, meter,
                        datetime.datetime.now(), reading, reason)
                self.after_submit(meter, reading, reason)
            except (EOFError, rpyc.core.vinegar.GenericException) as err:
                self.handle_error(err)


    def after_submit(self, meter, reading, reason):
        count, total = self.manager.get_status(self.sessionId)
        self.statusText.set("Accepted {} for {}".format(
                reading if reading != -1 else reason, meter))
        self.countsText.set("Read {}/{}".format(count, total))
        self.reading.set(-1)
        self.reason.set("")
        self.get_job()


    def handle_error(self, err):
        err = str(err)
        i = err.find("\n")
        if i > -1:
            err = err[:i]
        messagebox.showinfo("Meter \u2014 Error",
                "{}\nIs the server still running?\n"
                "Try Quitting and restarting.".format(err), parent=self)


    def close(self, event=None):
        if self.serverPid is not None: # We stop it if we started it
            print("Stopping the server...")
            os.kill(self.serverPid, signal.SIGINT) # KeyboardInterrupt
            self.serverPid = None
        self.quit()


if __name__ == "__main__":
    if sys.stdout.isatty():
        main()
    else:
        print("Loaded OK")
