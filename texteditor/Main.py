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

import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter.font as tkfont
import tkinter.messagebox as messagebox
Spinbox = ttk.Spinbox if hasattr(ttk, "Spinbox") else tk.Spinbox
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import About
import Editor
import Find
import Options
import Preferences
import TkUtil
import TkUtil.Settings
import TkUtil.Tooltip
from Globals import *


class Window(ttk.Frame):

    def __init__(self, master, filename=None):
        super().__init__(master, padding=PAD)
        settings = TkUtil.Settings.Data
        if settings.get_bool(GENERAL, RESTORE):
            geometry = settings.get_str(GENERAL, GEOMETRY)
            if geometry is not None:
                self.master.geometry(geometry)
        self.create_variables()
        self.update_variables()
        self.create_ui()
        self.update_ui()
        self.maybe_load_file(filename)


    def maybe_load_file(self, filename):
        settings = TkUtil.Settings.Data
        self.restoreLastFile = settings.get_bool(GENERAL,
                RESTORE_LAST_FILE, True)
        lastFile = settings.get_str(GENERAL, LAST_FILE)
        if filename is None and self.restoreLastFile:
            filename = lastFile
        elif lastFile is not None and os.path.isfile(lastFile):
            self.update_recent_files(lastFile)
        if filename is not None and os.path.isfile(filename):
            self.master.after(100,
                    lambda: self.load(os.path.abspath(filename)))


    def create_variables(self):
        settings = TkUtil.Settings.Data
        self.restore = settings.get_bool(GENERAL, RESTORE, True)
        self.menuImages = {}
        self.toolbarImages = {}
        self.toolbars = []
        self.toolbarMenu = None
        self.statusText = tk.StringVar()
        self.fontFamily = tk.StringVar()
        self.fontPointSize = tk.StringVar()
        self.bold = tk.BooleanVar()
        self.italic = tk.BooleanVar()
        self.alignment = tk.StringVar()
        self.recentFiles = []
        self.findDialog = None


    def update_variables(self):
        settings = TkUtil.Settings.Data
        family, pointSize, bold, italic = ("Helvetica", 11, False, False)
        self.restoreFont = settings.get_bool(FONT, RESTORE, True)
        if self.restoreFont:
            family = settings.get_str(FONT, FAMILY, family)
            pointSize = settings.get_int(FONT, FONT_SIZE, pointSize)
            bold = settings.get_bool(FONT, BOLD, bold)
            italic = settings.get_bool(FONT, ITALIC, italic)
        self.fontFamily.set(family)
        self.fontPointSize.set(pointSize)
        self.fontPointSize.trace("w", self.update_font)
        self.bold.set(bold)
        self.italic.set(italic)
        self.recentFiles = []
        for i in range(MAX_RECENT_FILES):
            filename = settings.get_str(RECENT_FILES, "file{}".format(i))
            if filename is not None and os.path.exists(filename):
                self.update_recent_files(filename, False)
        self.recentFiles.reverse()


    def create_ui(self):
        self.create_images()
        self.create_central_area()
        self.create_menubar()
        self.create_toolbars()
        self.create_statusbar()
        self.create_bindings()
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.master.minsize(300, 300)


    def create_images(self):
        imagePath = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), "images")
        for name in (NEW, OPEN, SAVE, SAVEAS, PREFERENCES,
                QUIT, UNDO, REDO, COPY, CUT, PASTE, FIND,
                BOLD, ITALIC, ALIGNLEFT, ALIGNCENTER, ALIGNRIGHT,
                HELP, ABOUT):
            filename = os.path.join(imagePath, name + "_16x16.gif")
            if os.path.exists(filename):
                self.menuImages[name] = tk.PhotoImage(file=filename)
            filename = os.path.join(imagePath, name + "_24x24.gif")
            if os.path.exists(filename):
                self.toolbarImages[name] = tk.PhotoImage(file=filename)
        filename = os.path.join(imagePath, "ToolbarMenu_3x24.gif")
        self.toolbarImages[TOOLBARMENU] = tk.PhotoImage(file=filename)


    def create_menubar(self):
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_window_menu()
        self.create_help_menu()


    def create_file_menu(self):
        modifier = TkUtil.menu_modifier()
        self.fileMenu = tk.Menu(self.menubar, name="apple")
        self.fileMenu.add_command(label=NEW, underline=0,
                command=self.new, image=self.menuImages[NEW],
                compound=tk.LEFT, accelerator=modifier + "+N")
        self.fileMenu.add_command(label=OPEN + ELLIPSIS, underline=0,
                command=self.open, image=self.menuImages[OPEN],
                compound=tk.LEFT, accelerator=modifier + "+O")
        self.fileMenu.add_cascade(label=OPEN_RECENT,
                underline=5, image=self.menuImages[OPEN],
                compound=tk.LEFT)
        self.fileMenu.add_command(label=SAVE, underline=0,
                command=self.save, image=self.menuImages[SAVE],
                compound=tk.LEFT, accelerator=modifier + "+S")
        self.fileMenu.add_command(label=SAVE_AS + ELLIPSIS, underline=5,
                command=self.save_as, image=self.menuImages[SAVEAS],
                compound=tk.LEFT)
        if TkUtil.mac():
            self.master.createcommand("::tk::mac::ShowPreferences",
                    self.preferences)
            self.master.createcommand("exit", self.close)
        else:
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label=PREFERENCES + ELLIPSIS,
                    underline=0, image=self.menuImages[PREFERENCES],
                    compound=tk.LEFT, command=self.preferences)
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label=QUIT, underline=0,
                    command=self.close, compound=tk.LEFT,
                    image=self.menuImages[QUIT],
                    accelerator=modifier + "+Q")
        self.menubar.add_cascade(label="File", underline=0,
                menu=self.fileMenu)


    # NOTE: the Tkinter API doesn't seem to let us check whether redo is
    # possible (so here we always leave Redo enabled).
    def create_edit_menu(self):
        modifier = TkUtil.menu_modifier()
        self.editMenu = tk.Menu(self.menubar)
        self.editMenu.add_command(label=UNDO, underline=0,
                command=self.editor.edit_undo,
                image=self.menuImages[UNDO], compound=tk.LEFT,
                accelerator=modifier + "+Z")
        redo = "+Shift+Z"
        if TkUtil.windows():
            redo = "+Y"
        self.editMenu.add_command(label=REDO, underline=0,
                command=self.editor.edit_redo,
                image=self.menuImages[REDO], compound=tk.LEFT,
                accelerator=modifier + redo)
        self.editMenu.add_separator()
        self.editMenu.add_command(label=COPY, underline=0,
                command=lambda: self.editor.text.event_generate(
                    "<<Copy>>"), image=self.menuImages[COPY],
                compound=tk.LEFT, accelerator=modifier + "+C")
        self.editMenu.add_command(label=CUT, underline=2,
                command=lambda: self.editor.text.event_generate("<<Cut>>"),
                image=self.menuImages[CUT], compound=tk.LEFT,
                accelerator=modifier + "+X")
        self.editMenu.add_command(label=PASTE, underline=0,
                command=lambda: self.editor.text.event_generate(
                    "<<Paste>>"), image=self.menuImages[PASTE],
                compound=tk.LEFT, accelerator=modifier + "+V")
        self.editMenu.add_separator()
        self.editMenu.add_command(label=FIND + ELLIPSIS, underline=0,
                command=self.find, image=self.menuImages[FIND],
                compound=tk.LEFT, accelerator=modifier + "+F")
        self.menubar.add_cascade(label="Edit", underline=0,
                menu=self.editMenu)


    # Tcl/Tk 8.6 provides access to the native font chooser dialog
    def create_view_menu(self):
        modifier = TkUtil.menu_modifier()
        viewMenu = tk.Menu(self.menubar)
        viewMenu.add_checkbutton(label=BOLD, underline=0,
                image=self.menuImages[BOLD], compound=tk.LEFT,
                variable=self.bold,
                command=lambda: self.toggle_button(self.boldButton))
        viewMenu.add_checkbutton(label=ITALIC, underline=0,
                image=self.menuImages[ITALIC], compound=tk.LEFT,
                variable=self.italic,
                command=lambda: self.toggle_button(self.italicButton))
        viewMenu.add_separator()
        viewMenu.add_radiobutton(label=ALIGN_LEFT, underline=6,
                image=self.menuImages[ALIGNLEFT], compound=tk.LEFT,
                variable=self.alignment, value=tk.LEFT,
                command=self.toggle_alignment)
        viewMenu.add_radiobutton(label=ALIGN_CENTER, underline=6,
                image=self.menuImages[ALIGNCENTER],
                compound=tk.LEFT, variable=self.alignment, value=tk.CENTER,
                command=self.toggle_alignment)
        viewMenu.add_radiobutton(label=ALIGN_RIGHT, underline=6,
                image=self.menuImages[ALIGNRIGHT],
                compound=tk.LEFT, variable=self.alignment, value=tk.RIGHT,
                command=self.toggle_alignment)
        self.menubar.add_cascade(label="View", underline=0,
                menu=viewMenu)


    def create_window_menu(self):
        modifier = TkUtil.menu_modifier()
        self.windowMenu = tk.Menu(self.menubar, name="window")
        self.windowToolbarMenu = tk.Menu(self.windowMenu)
        self.windowMenu.add_cascade(label="Toolbars", underline=0,
                menu=self.windowToolbarMenu)
        self.menubar.add_cascade(label="Window", underline=0,
                menu=self.windowMenu)


    def create_help_menu(self):
        helpMenu = tk.Menu(self.menubar, name="help")
        if TkUtil.mac():
            self.master.createcommand("tkAboutDialog", self.about)
            self.master.createcommand("::tk::mac::ShowHelp",
                    self.help)
        else:
            helpMenu.add_command(label=HELP, underline=0,
                    command=self.help, image=self.menuImages[HELP],
                    compound=tk.LEFT, accelerator="F1")
            helpMenu.add_command(label=ABOUT, underline=0,
                    command=self.about, image=self.menuImages[ABOUT],
                    compound=tk.LEFT)
        self.menubar.add_cascade(label=HELP, underline=0,
                menu=helpMenu)


    def create_toolbars(self):
        self.toolbarFrame = ttk.Frame(self.master)
        self.create_file_toolbar()
        self.create_edit_toolbar()
        self.create_view_toolbar()
        self.create_alignment_toolbar()
        self.toolbarFrame.grid(row=0, column=0, columnspan=3,
                sticky=(tk.W, tk.E))
        self.master.after(50, self.initialize_toolbars)


    def initialize_toolbars(self):
        settings = TkUtil.Settings.Data
        for toolbar in self.toolbars: # Show them all first to size them
            toolbar.visible = tk.BooleanVar()
            toolbar.visible.set(True)
        self.force_update_toolbars()
        for toolbar in self.toolbars: # Hide those that should be hidden
            toolbar.visible.set(settings.get_bool(toolbar.text, VISIBLE,
                    True))
            self.windowToolbarMenu.add_checkbutton(label=toolbar.text,
                    underline=toolbar.underline, variable=toolbar.visible,
                    onvalue=True, offvalue=False)
            toolbar.visible.trace("w", self.force_update_toolbars)
        self.force_update_toolbars()
        self.master.bind("<Configure>", self.update_toolbars, "+")


    def update_toolbars(self, event=None):
        TkUtil.layout_in_rows(self.toolbarFrame, self.master.winfo_width(),
                DEFAULT_TOOLBAR_HEIGHT, self.toolbars)


    def force_update_toolbars(self, *args):
        TkUtil.layout_in_rows(self.toolbarFrame, self.master.winfo_width(),
                DEFAULT_TOOLBAR_HEIGHT, self.toolbars, True)


    def create_file_toolbar(self):
        settings = TkUtil.Settings.Data
        self.fileToolbar = ttk.Frame(self.toolbarFrame, relief=tk.RAISED)
        self.fileToolbar.text = FILE_TOOLBAR
        self.fileToolbar.underline = 0
        menuButton = ttk.Button(self.fileToolbar,
                text="File Toolbar Menu", 
                image=self.toolbarImages[TOOLBARMENU],
                command=self.toolbar_menu)
        TkUtil.bind_context_menu(menuButton, self.toolbar_menu)
        TkUtil.Tooltip.Tooltip(menuButton, text="File Toolbar Menu")
        newButton = ttk.Button(self.fileToolbar, text=NEW,
                image=self.toolbarImages[NEW], command=self.new)
        TkUtil.Tooltip.Tooltip(newButton, text="New Document")
        openButton = ttk.Button(self.fileToolbar, text=OPEN,
                image=self.toolbarImages[OPEN], command=self.open)
        TkUtil.Tooltip.Tooltip(openButton, text="Open Document")
        self.saveButton = ttk.Button(self.fileToolbar, text=SAVE,
                image=self.toolbarImages[SAVE], command=self.save)
        TkUtil.Tooltip.Tooltip(self.saveButton, text="Save Document")
        preferencesButton = ttk.Button(self.fileToolbar,
                text=PREFERENCES, image=self.toolbarImages[PREFERENCES],
                command=self.preferences)
        TkUtil.Tooltip.Tooltip(preferencesButton, text=PREFERENCES)
        TkUtil.add_toolbar_buttons(self.fileToolbar, (menuButton,
                newButton, openButton, self.saveButton, None,
                preferencesButton))
        self.toolbars.append(self.fileToolbar)


    def create_edit_toolbar(self):
        settings = TkUtil.Settings.Data
        self.editToolbar = ttk.Frame(self.toolbarFrame, relief=tk.RAISED)
        self.editToolbar.text = EDIT_TOOLBAR
        self.editToolbar.underline = 0
        menuButton = ttk.Button(self.editToolbar,
                text="Edit Toolbar Menu", 
                image=self.toolbarImages[TOOLBARMENU],
                command=self.toolbar_menu)
        TkUtil.bind_context_menu(menuButton, self.toolbar_menu)
        TkUtil.Tooltip.Tooltip(menuButton, text="Edit Toolbar Menu")
        self.undoButton = ttk.Button(self.editToolbar,
                text=UNDO, image=self.toolbarImages[UNDO],
                command=self.editor.edit_undo)
        TkUtil.Tooltip.Tooltip(self.undoButton, text=UNDO)
        self.redoButton = ttk.Button(self.editToolbar,
                text=REDO, image=self.toolbarImages[REDO],
                command=self.editor.edit_redo)
        TkUtil.Tooltip.Tooltip(self.redoButton, text=REDO)
        self.copyButton = ttk.Button(self.editToolbar,
                text=COPY, image=self.toolbarImages[COPY],
                command=self.editor.text.event_generate("<<Copy>>"))
        TkUtil.Tooltip.Tooltip(self.copyButton, text=COPY)
        self.cutButton = ttk.Button(self.editToolbar, text=CUT,
                image=self.toolbarImages[CUT],
                command=self.editor.text.event_generate("<<Cut>>"))
        TkUtil.Tooltip.Tooltip(self.cutButton, text=CUT)
        self.pasteButton = ttk.Button(self.editToolbar, text=PASTE,
                image=self.toolbarImages[PASTE],
                command=self.editor.text.event_generate("<<Paste>>"))
        TkUtil.Tooltip.Tooltip(self.pasteButton, text=PASTE)
        self.findButton = ttk.Button(self.editToolbar,
                text=FIND, image=self.toolbarImages[FIND],
                command=self.find)
        TkUtil.Tooltip.Tooltip(self.findButton, text=FIND)
        TkUtil.add_toolbar_buttons(self.editToolbar, (menuButton,
                self.undoButton, self.redoButton, None, self.copyButton,
                self.cutButton, self.pasteButton, None, self.findButton))
        self.toolbars.append(self.editToolbar)


    def create_view_toolbar(self):
        settings = TkUtil.Settings.Data
        self.viewToolbar = ttk.Frame(self.toolbarFrame, relief=tk.RAISED)
        self.viewToolbar.text = FORMAT_TOOLBAR
        self.viewToolbar.underline = 1
        menuButton = ttk.Button(self.viewToolbar,
                text="Format Toolbar Menu", 
                image=self.toolbarImages[TOOLBARMENU],
                command=self.toolbar_menu)
        TkUtil.bind_context_menu(menuButton, self.toolbar_menu)
        TkUtil.Tooltip.Tooltip(menuButton, text="Format Toolbar Menu")
        self.fontFamilyCombobox = ttk.Combobox(self.viewToolbar,
                width=15, textvariable=self.fontFamily,
                state="readonly", values=TkUtil.font_families())
        self.fontFamilyCombobox.bind("<<ComboboxSelected>>",
                self.update_font)
        TkUtil.set_combobox_item(self.fontFamilyCombobox,
                self.fontFamily.get())
        TkUtil.Tooltip.Tooltip(self.fontFamilyCombobox, text="Font Family")
        self.fontSizeSpinbox = Spinbox(self.viewToolbar, width=2,
                textvariable=self.fontPointSize, from_=6, to=72,
                justify=tk.RIGHT, validate="all")
        self.fontSizeSpinbox.config(validatecommand=(
                self.fontSizeSpinbox.register(self.validate_int),
                    "fontSizeSpinbox", "%P"))
        TkUtil.Tooltip.Tooltip(self.fontSizeSpinbox,
                text="Font Point Size")
        self.boldButton = ttk.Button(self.viewToolbar,
                text=BOLD, image=self.toolbarImages[BOLD])
        self.boldButton.config(
                command=lambda: self.toggle_button(self.boldButton,
                    self.bold))
        TkUtil.Tooltip.Tooltip(self.boldButton, text=BOLD)
        self.italicButton = ttk.Button(self.viewToolbar,
                text=ITALIC,
                image=self.toolbarImages[ITALIC])
        self.italicButton.config(
                command=lambda: self.toggle_button(self.italicButton,
                    self.italic))
        TkUtil.Tooltip.Tooltip(self.italicButton, text=ITALIC)
        TkUtil.add_toolbar_buttons(self.viewToolbar, (menuButton,
                self.fontFamilyCombobox, self.fontSizeSpinbox,
                self.boldButton, self.italicButton))
        self.toolbars.append(self.viewToolbar)


    def validate_int(self, spinbox, number):
        spinbox = getattr(self, spinbox)
        return TkUtil.validate_spinbox_int(spinbox, number)


    def toggle_button(self, button, variable=None):
        if button.instate((TkUtil.SELECTED,)):
            button.state((TkUtil.NOT_SELECTED,))
        else:
            button.state((TkUtil.SELECTED,))
        if variable is not None:
            variable.set(not variable.get())
        self.update_font()


    def create_alignment_toolbar(self):
        settings = TkUtil.Settings.Data
        self.alignmentToolbar = ttk.Frame(self.toolbarFrame,
                relief=tk.RAISED)
        self.alignmentToolbar.text = ALIGNMENT_TOOLBAR
        self.alignmentToolbar.underline = 0
        menuButton = ttk.Button(self.alignmentToolbar,
                text="Alignment Toolbar Menu", 
                image=self.toolbarImages[TOOLBARMENU],
                command=self.toolbar_menu)
        TkUtil.bind_context_menu(menuButton, self.toolbar_menu)
        TkUtil.Tooltip.Tooltip(menuButton, text="Alignment Toolbar Menu")
        self.leftButton = ttk.Button(self.alignmentToolbar,
                text=ALIGN_LEFT, image=self.toolbarImages[ALIGNLEFT])
        self.leftButton.config(
                command=lambda: self.toggle_alignment(tk.LEFT))
        TkUtil.Tooltip.Tooltip(self.leftButton, text=ALIGN_LEFT)
        self.centerButton = ttk.Button(self.alignmentToolbar,
                text=ALIGN_CENTER, 
                image=self.toolbarImages[ALIGNCENTER])
        self.centerButton.config(
                command=lambda: self.toggle_alignment(tk.CENTER))
        TkUtil.Tooltip.Tooltip(self.centerButton, text=ALIGN_CENTER)
        self.rightButton = ttk.Button(self.alignmentToolbar,
                text=ALIGN_RIGHT, image=self.toolbarImages[ALIGNRIGHT])
        self.rightButton.config(
                command=lambda: self.toggle_alignment(tk.RIGHT))
        TkUtil.Tooltip.Tooltip(self.rightButton, text=ALIGN_RIGHT)
        TkUtil.add_toolbar_buttons(self.alignmentToolbar, (menuButton,
                self.leftButton, self.centerButton, self.rightButton))
        self.toolbars.append(self.alignmentToolbar)
        self.leftButton.state((TkUtil.SELECTED,))
        self.alignment.set(tk.LEFT)


    def toggle_alignment(self, alignment=None):
        if alignment is None:
            alignment = self.alignment.get()
        else:
            self.alignment.set(alignment)
        for button, value in ((self.leftButton, tk.LEFT),
                (self.centerButton, tk.CENTER),
                (self.rightButton, tk.RIGHT)):
            if value == alignment:
                button.state((TkUtil.SELECTED,))
                self.editor.align(alignment)
            else:
                button.state((TkUtil.NOT_SELECTED,))


    def toolbar_menu(self, event=None):
        if self.toolbarMenu is None:
            self.toolbarMenu = tk.Menu(self.toolbarMenu)
            for toolbar in self.toolbars:
                self.toolbarMenu.add_checkbutton(label=toolbar.text,
                        underline=toolbar.underline,
                        variable=toolbar.visible, onvalue=True,
                        offvalue=False)
        self.toolbarMenu.tk_popup(self.winfo_pointerx(),
                self.winfo_pointery())


    def create_central_area(self):
        self.editor = Editor.Editor(self.master,
                set_status_text=self.set_status_text,
                font=self.create_font(), maxundo=0, undo=True,
                wrap=tk.WORD)
        self.editor.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.W, tk.E),
                padx=PAD, pady=PAD)
        self.editor.text.bind("<<Selection>>", self.on_selection)
        self.editor.text.bind("<<Modified>>", self.on_modified)
        self.editor.text.bind("<KeyRelease>", self.on_moved, "+")
        self.editor.text.bind("<ButtonRelease>", self.on_moved, "+")
        self.editor.text.focus()


    def create_statusbar(self):
        statusBar = ttk.Frame(self.master)
        statusLabel = ttk.Label(statusBar, textvariable=self.statusText)
        statusLabel.grid(column=0, row=0, sticky=(tk.W, tk.E))
        self.modifiedLabel = ttk.Label(statusBar, relief=tk.SUNKEN,
                anchor=tk.CENTER)
        self.modifiedLabel.grid(column=1, row=0, pady=2, padx=1)
        TkUtil.Tooltip.Tooltip(self.modifiedLabel,
                text="MOD if the text has unsaved changes")
        self.positionLabel = ttk.Label(statusBar, relief=tk.SUNKEN,
                anchor=tk.CENTER)
        self.positionLabel.grid(column=2, row=0, sticky=(tk.W, tk.E),
                pady=2, padx=1)
        TkUtil.Tooltip.Tooltip(self.positionLabel,
                text="Current line and column position")
        ttk.Sizegrip(statusBar).grid(row=0, column=4, sticky=(tk.S, tk.E))
        statusBar.columnconfigure(0, weight=1)
        statusBar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        self.set_status_text("Start typing to create a new document or "
                "click File→Open")


    def create_bindings(self):
        modifier = TkUtil.key_modifier()
        self.master.bind("<{}-f>".format(modifier), self.find)
        self.master.bind("<{}-n>".format(modifier), self.new)
        self.master.bind("<{}-o>".format(modifier), self.open)
        self.master.bind("<{}-q>".format(modifier), self.close)
        self.master.bind("<{}-s>".format(modifier), self.save)
        self.master.bind("<F1>", self.help)
        for key in "fnoqs": # Avoid conflicts
            self.unbind_class("Text", "<{}-{}>".format(modifier, key))
        # Ctrl+C etc. from the edit menu are already supported by the
        # Text (Editor) widget.
        TkUtil.bind_context_menu(self.editor.text, self.context_menu)


    def update_ui(self):
        self.on_modified()
        self.on_selection()
        self.on_moved()
        self.update_recent_files_menu()
        self.boldButton.state((TkUtil.SELECTED if bool(self.bold.get())
                else TkUtil.NOT_SELECTED,))
        self.italicButton.state((TkUtil.SELECTED if bool(self.italic.get())
                else TkUtil.NOT_SELECTED,))
        self.update_font()


    def on_modified(self, event=None):
        if not hasattr(self, "modifiedLabel"):
            self.editor.edit_modified(False)
            return
        if self.editor.edit_modified():
            text, mac, state = "MOD", True, tk.NORMAL
        else:
            text, mac, state = "", False, tk.DISABLED
        self.modifiedLabel.config(text=text)
        if TkUtil.mac():
            self.master.attributes("-modified", mac)
        self.fileMenu.entryconfigure(SAVE, state=state)
        self.fileMenu.entryconfigure(SAVE_AS + ELLIPSIS, state=state)
        self.saveButton.config(state=state)
        self.editMenu.entryconfigure(UNDO, state=state)
        self.undoButton.config(state=state)


    def on_selection(self, event=None):
        state = (tk.NORMAL if self.editor.text.tag_ranges(tk.SEL)
                 else tk.DISABLED)
        self.editMenu.entryconfigure(COPY, state=state)
        self.copyButton.config(state=state)
        self.editMenu.entryconfigure(CUT, state=state)
        self.cutButton.config(state=state)


    def on_moved(self, event=None):
        state = tk.NORMAL if not self.editor.is_empty() else tk.DISABLED
        self.editMenu.entryconfigure(FIND + ELLIPSIS, state=state)
        self.findButton.config(state=state)
        lineCol = self.editor.index(tk.INSERT).split(".")
        self.positionLabel.config(text="↓{}→{}".format(lineCol[0],
                lineCol[1]))


    def context_menu(self, event):
        modifier = TkUtil.menu_modifier()
        menu = tk.Menu(self.master)
        if self.editor.text.tag_ranges(tk.SEL):
            menu.add_command(label=COPY, underline=0,
                    command=lambda: self.editor.text.event_generate(
                        "<<Copy>>"), image=self.menuImages[COPY],
                    compound=tk.LEFT, accelerator=modifier + "+C")
            menu.add_command(label=CUT, underline=2,
                    command=lambda: self.editor.text.event_generate(
                        "<<Cut>>"), image=self.menuImages[CUT],
                    compound=tk.LEFT, accelerator=modifier + "+X")
        menu.add_command(label=PASTE, underline=0,
                command=lambda: self.editor.text.event_generate(
                    "<<Paste>>"), image=self.menuImages[PASTE],
                compound=tk.LEFT, accelerator=modifier + "+V")
        menu.add_separator()
        menu.add_checkbutton(label=BOLD, underline=0,
                image=self.menuImages[BOLD], compound=tk.LEFT,
                variable=self.bold,
                command=lambda: self.toggle_button(self.boldButton))
        menu.add_checkbutton(label=ITALIC, underline=0,
                image=self.menuImages[ITALIC], compound=tk.LEFT,
                variable=self.italic,
                command=lambda: self.toggle_button(self.italicButton))
        menu.add_separator()
        menu.add_radiobutton(label=ALIGN_LEFT, underline=6,
                image=self.menuImages[ALIGNLEFT], compound=tk.LEFT,
                variable=self.alignment, value=tk.LEFT,
                command=self.toggle_alignment)
        menu.add_radiobutton(label=ALIGN_CENTER, underline=6,
                image=self.menuImages[ALIGNCENTER],
                compound=tk.LEFT, variable=self.alignment, value=tk.CENTER,
                command=self.toggle_alignment)
        menu.add_radiobutton(label=ALIGN_RIGHT, underline=6,
                image=self.menuImages[ALIGNRIGHT],
                compound=tk.LEFT, variable=self.alignment, value=tk.RIGHT,
                command=self.toggle_alignment)
        menu.tk_popup(event.x_root, event.y_root)


    def update_font(self, *args):
        self.editor.text.config(font=self.create_font())


    def set_status_text(self, text):
        self.statusText.set(text)
        self.master.after(STATUS_SHOW_TIME,
                lambda: self.statusText.set(""))


    def create_font(self):
        weight = tkfont.BOLD if int(self.bold.get()) else tkfont.NORMAL
        slant = tkfont.ITALIC if int(self.italic.get()) else tkfont.ROMAN
        return tkfont.Font(family=self.fontFamily.get(),
                size=self.fontPointSize.get(), weight=weight, slant=slant)


    def new(self, event=None):
        if self.ok_to_clear():
            self.editor.new()
            self.update_ui()


    def load(self, filename):
        if self.ok_to_clear():
            if self.editor.load(filename):
                self.update_recent_files(filename)
                self.update_ui()


    def open(self, event=None,):
        if self.ok_to_clear():
            path = "."
            if self.editor.filename is not None:
                path = os.path.dirname(self.editor.filename)
            filename = filedialog.askopenfilename(parent=self,
                    title="{} — {}".format(OPEN, APPNAME),
                    initialdir=path, filetypes=FILE_TYPES)
            if filename:
                if self.editor.load(filename):
                    self.update_recent_files(filename)
                    self.update_ui()


    def save(self, event=None):
        if self.editor.filename is None:
            return self.save_as()
        return self.editor.save()


    def save_as(self):
        path = "."
        if self.editor.filename is not None:
            path = os.path.dirname(self.editor.filename)
        filename = filedialog.asksaveasfilename(parent=self,
                    title="{} — {}".format(SAVE_AS, APPNAME),
                    initialdir=path, defaultextension=".txt",
                    filetypes=FILE_TYPES)
        if filename:
            self.editor.filename = filename
            result = self.save()
            if result:
                self.update_recent_files(filename)
            return result
        return False


    def ok_to_clear(self):
        if not self.editor.edit_modified():
            return True
        if messagebox.askyesno(
                "Unsaved Changes — {}".format(APPNAME),
                "Save unsaved changes?", parent=self):
            return self.save()
        return True


    def update_recent_files(self, filename, populateMenu=True):
        if filename not in self.recentFiles:
            self.recentFiles.insert(0, filename)
            self.recentFiles = self.recentFiles[:MAX_RECENT_FILES]
        if populateMenu:
            self.update_recent_files_menu()


    def update_recent_files_menu(self):
        if self.recentFiles:
            menu = tk.Menu(self.fileMenu)
            i = 1
            for filename in self.recentFiles:
                if filename != self.editor.filename:
                    menu.add_command(label="{}. {}".format(i, filename),
                            underline=0, command=lambda filename=filename:
                                    self.load(filename))
                    i += 1
            self.fileMenu.entryconfigure(OPEN_RECENT,
                    menu=menu)
            self.fileMenu.entryconfigure(OPEN_RECENT,
                    state=tk.NORMAL if i > 1 else tk.DISABLED)
        else:
            self.fileMenu.entryconfigure(OPEN_RECENT,
                    state=tk.DISABLED)


    def close(self, event=None):
        if not self.ok_to_clear():
            return
        settings = TkUtil.Settings.Data
        settings.put(GENERAL, RESTORE, self.restore)
        if self.restore:
            settings.put(GENERAL, GEOMETRY, self.master.geometry())
        self.save_toolbars()
        self.save_font()
        self.save_recent_files()
        TkUtil.Settings.save()
        self.quit()


    def save_toolbars(self):
        settings = TkUtil.Settings.Data
        settings.put(FILE_TOOLBAR, VISIBLE, self.fileToolbar.visible.get())
        settings.put(EDIT_TOOLBAR, VISIBLE, self.editToolbar.visible.get())
        settings.put(FORMAT_TOOLBAR, VISIBLE,
                self.viewToolbar.visible.get())
        settings.put(ALIGNMENT_TOOLBAR, VISIBLE,
                self.alignmentToolbar.visible.get())


    def save_font(self):
        settings = TkUtil.Settings.Data
        settings.put(FONT, RESTORE, self.restoreFont)
        if self.restoreFont:
            settings.put(FONT, BOLD, self.bold.get())
            settings.put(FONT, ITALIC, self.italic.get())
            settings.put(FONT, FAMILY, self.fontFamily.get())
            settings.put(FONT, FONT_SIZE, self.fontPointSize.get())


    def save_recent_files(self):
        """Make sure the current file is the first in the list if not
        restoring last file"""
        settings = TkUtil.Settings.Data
        settings.put(GENERAL, RESTORE_LAST_FILE, self.restoreLastFile)
        filename = self.editor.filename
        if filename is not None and os.path.isfile(filename):
            try:
                self.recentFiles.remove(filename)
            except ValueError:
                pass
            if self.restoreLastFile:
                settings.put(GENERAL, LAST_FILE, filename)
            else:
                self.recentFiles.insert(0, filename)
        else:
            settings.put(GENERAL, LAST_FILE, "")
        for i, filename in enumerate(self.recentFiles):
            settings.put(RECENT_FILES, "file{}".format(i), filename)


    def preferences(self):
        settings = TkUtil.Settings.Data
        blink = settings.get_bool(GENERAL, BLINK, True)
        options = Options.Options(self.restore, self.restoreFont,
                self.restoreLastFile, blink)
        preferences = Preferences.Window(self, options)
        if preferences.ok:
            self.restore = options.restoreWindow
            self.restoreFont = options.restoreFont
            self.restoreLastFile = options.restoreSession
            if options.blink != blink:
                settings.put(GENERAL, BLINK, options.blink)
                self.editor.text.config(insertofftime=300
                        if options.blink else 0)
        self.focus()


    def find(self, event=None):
        if self.findDialog is None:
            self.findDialog = Find.Window(self, self.editor.text)
        else:
            self.findDialog.deiconify() # TODO make sure that it repositions correctly


    def help(self, event=None):
        paras = [
"""{} is a basic plain text editor (using the UTF-8 encoding).""".format(
    APPNAME),
"""The purpose is really to show how to create a standard
main-window-style application with menus, toolbars, etc.,
as well as showing basic use of the Text widget.""",
]
        messagebox.showinfo("{} — {}".format(HELP, APPNAME),
                "\n\n".join([para.replace("\n", " ") for para in paras]),
                parent=self)


    def about(self):
        About.Window(self)


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("Window")
        TkUtil.Settings.DOMAIN = "Qtrac"
        TkUtil.Settings.APPNAME = APPNAME
        TkUtil.Settings.load()
        window = Window(application)
        application.protocol("WM_DELETE_WINDOW", window.close)
        application.mainloop()
    else:
        print("Loaded OK")
