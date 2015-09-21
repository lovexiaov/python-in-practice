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

import sys
import webbrowser
import tkinter as tk
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil.Dialog
import TkUtil.TextEdit


class Window(TkUtil.Dialog.Dialog):

    def __init__(self, master, appname, width=60, height=20):
        self.appname = appname
        self.width = width
        self.height = height
        super().__init__(master, "About — {}".format(appname))
            

    def body(self, master):
        self.editor = TkUtil.TextEdit.TextEdit(master, takefocus=False,
                exportselection=False, width=self.width,
                height=self.height, undo=False, wrap=tk.WORD, relief=None,
                borderwidth=0, setgrid=True)
        self.text = self.editor.text
        self.create_tags()
        self.populate_text()
        self.text.config(state=tk.DISABLED)
        self.editor.pack(fill=tk.BOTH, expand=True)
        return self.editor


    def create_tags(self):
        self.text.tag_config("center", justify=tk.CENTER)
        self.text.tag_config("url", underline=True)
        self.text.tag_bind("url", "<Double-Button-1>", self.handle_url)


    def add_lines(self, lines):
        self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, lines.replace("\n", " ").strip())
        self.text.insert(tk.END, "\n")


    def populate_text(self):
        "Override"
        self.text.insert(tk.END, "[Override populate_text()]")


    def handle_url(self, event):
        index = self.text.index("@{0.x},{0.y}".format(event))
        indexes = self.text.tag_prevrange("url", index)
        url = self.text.get(*indexes).strip()
        if url:
            HTTP = "http://"
            if not url.startswith(HTTP):
                url = HTTP + url
            webbrowser.open_new_tab(url)


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        Window(application, "About")
        application.bind("<Escape>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
