import os
import sys
import constants as const
import ConfigParser
from ConfigParser import NoOptionError
from HostUtils import HostUtils


# Configuration variables
class Conf:
    WORD_SEPARATORS = "-A-Za-z0-9,./?%&#:_=+@~"
    BUFFER_LINES = 2000
    STARTUP_LOCAL = True
    CONFIRM_ON_EXIT = True
    FONT_COLOR = ""
    BACK_COLOR = ""
    TRANSPARENCY = 0
    PASTE_ON_RIGHT_CLICK = 1
    CONFIRM_ON_CLOSE_TAB = 0
    AUTO_CLOSE_TAB = 0
    COLLAPSED_FOLDERS = ""
    LEFT_PANEL_WIDTH = 100
    CHECK_UPDATES = True
    WINDOW_WIDTH = -1
    WINDOW_HEIGHT = -1
    FONT = ""
    HIDE_DONATE = False
    AUTO_COPY_SELECTION = 0
    LOG_PATH = os.path.expanduser("~")
    SHOW_TOOLBAR = True
    SHOW_PANEL = True
    VERSION = 0
    shortcuts = {}
    groups = {}

    def __init__(self):
        self.load_config()

    def load_config(self):
        global groups
        cp = ConfigParser.RawConfigParser()
        cp.read(const.CONFIG_FILE)

        # Read general configuration
        try:
            self.WORD_SEPARATORS = cp.get("options", "word-separators")
            self.BUFFER_LINES = cp.getint("options", "buffer-lines")
            self.CONFIRM_ON_EXIT = cp.getboolean("options", "confirm-exit")
            self.FONT_COLOR = cp.get("options", "font-color")
            self.BACK_COLOR = cp.get("options", "back-color")
            self.TRANSPARENCY = cp.getint("options", "transparency")
            self.PASTE_ON_RIGHT_CLICK = cp.getboolean("options", "paste-right-click")
            self.CONFIRM_ON_CLOSE_TAB = cp.getboolean("options", "confirm-close-tab")
            self.CHECK_UPDATES = cp.getboolean("options", "check-updates")
            self.COLLAPSED_FOLDERS = cp.get("window", "collapsed-folders")
            self.LEFT_PANEL_WIDTH = cp.getint("window", "left-panel-width")
            self.WINDOW_WIDTH = cp.getint("window", "window-width")
            self.WINDOW_HEIGHT = cp.getint("window", "window-height")
            self.FONT = cp.get("options", "font")
            self.HIDE_DONATE = cp.getboolean("options", "donate")
            self.AUTO_COPY_SELECTION = cp.getboolean("options", "auto-copy-selection")
            self.LOG_PATH = cp.get("options", "log-path")
            self.VERSION = cp.get("options", "version")
            self.AUTO_CLOSE_TAB = cp.getint("options", "auto-close-tab")
            self.SHOW_PANEL = cp.getboolean("window", "show-panel")
            self.SHOW_TOOLBAR = cp.getboolean("window", "show-toolbar")
            self.STARTUP_LOCAL = cp.getboolean("options", "startup-local")
        except NoOptionError:
            print "%s: %s" % (const.ERRMSG1, sys.exc_info()[1])

        # Read shortcuts
        scuts = {}
        try:
            scuts[cp.get("shortcuts", "copy")] = const.COPY
        except NoOptionError:
            scuts["CTRL+SHIFT+C"] = const.COPY
        try:
            scuts[cp.get("shortcuts", "paste")] = const.PASTE
        except NoOptionError:
            scuts["CTRL+SHIFT+V"] = const.PASTE
        try:
            scuts[cp.get("shortcuts", "copy_all")] = const.COPY_ALL
        except NoOptionError:
            scuts["CTRL+SHIFT+A"] = const.COPY_ALL
        try:
            scuts[cp.get("shortcuts", "save")] = const.SAVE
        except NoOptionError:
            scuts["CTRL+S"] = const.SAVE
        try:
            scuts[cp.get("shortcuts", "find")] = const.FIND
        except NoOptionError:
            scuts["CTRL+F"] = const.FIND
        try:
            scuts[cp.get("shortcuts", "find_next")] = const.FIND_NEXT
        except NoOptionError:
            scuts["F3"] = const.FIND_NEXT
        try:
            scuts[cp.get("shortcuts", "find_back")] = const.FIND_BACK
        except NoOptionError:
            scuts["SHIFT+F3"] = const.FIND_BACK

        try:
            scuts[cp.get("shortcuts", "console_previous")] = const.CONSOLE_PREV
        except NoOptionError:
            scuts["CTRL+SHIFT+LEFT"] = const.CONSOLE_PREV

        try:
            scuts[cp.get("shortcuts", "console_next")] = const.CONSOLE_NEXT
        except NoOptionError:
            scuts["CTRL+SHIFT+RIGHT"] = const.CONSOLE_NEXT

        try:
            scuts[cp.get("shortcuts", "console_close")] = const.CONSOLE_CLOSE
        except NoOptionError:
            scuts["CTRL+W"] = const.CONSOLE_CLOSE

        try:
            scuts[cp.get("shortcuts", "console_reconnect")] = const.CONSOLE_RECONNECT
        except NoOptionError:
            scuts["CTRL+N"] = const.CONSOLE_RECONNECT

        try:
            scuts[cp.get("shortcuts", "connect")] = const.CONNECT
        except NoOptionError:
            scuts["CTRL+RETURN"] = const.CONNECT

        try:
            scuts[cp.get("shortcuts", "reset")] = const.CLEAR
        except NoOptionError:
            scuts["CTRL+K"] = const.CLEAR

        # shortcuts for console1-console9
        for x in range(1, 10):
            try:
                scuts[cp.get("shortcuts", "console_%d" % x)] = eval("const.CONSOLE_%d" % x)
            except NoOptionError:
                scuts["F%d" % x] = eval("CONSOLE_%d" % x)

        # shortcuts for custom commands
        try:
            i = 1
            while True:
                scuts[cp.get("shortcuts", "shortcut%d" % i)] = cp.get("shortcuts", "command%d" % i).replace('\\n', '\n')
                i += 1
        except NoOptionError:
            pass

        self.shortcuts = scuts

        # create hosts list
        hu = HostUtils()
        self.groups = hu.load_hosts(cp, version=self.VERSION)

    def write_config(self):
        cp = ConfigParser.RawConfigParser()
        cp.read(const.CONFIG_FILE + ".tmp")

        cp.add_section("options")
        cp.set("options", "word-separators", self.WORD_SEPARATORS)
        cp.set("options", "buffer-lines", self.BUFFER_LINES)
        cp.set("options", "startup-local", self.STARTUP_LOCAL)
        cp.set("options", "confirm-exit", self.CONFIRM_ON_EXIT)
        cp.set("options", "font-color", self.FONT_COLOR)
        cp.set("options", "back-color", self.BACK_COLOR)
        cp.set("options", "transparency", self.TRANSPARENCY)
        cp.set("options", "paste-right-click", self.PASTE_ON_RIGHT_CLICK)
        cp.set("options", "confirm-close-tab", self.CONFIRM_ON_CLOSE_TAB)
        cp.set("options", "check-updates", self.CHECK_UPDATES)
        cp.set("options", "font", self.FONT)
        cp.set("options", "donate", self.HIDE_DONATE)
        cp.set("options", "auto-copy-selection", self.AUTO_COPY_SELECTION)
        cp.set("options", "log-path", self.LOG_PATH)
        cp.set("options", "version", const.app_file_version)
        cp.set("options", "auto-close-tab", self.AUTO_CLOSE_TAB)

        cp.add_section("window")
        cp.set("window", "collapsed-folders", self.COLLAPSED_FOLDERS)
        cp.set("window", "left-panel-width", self.LEFT_PANEL_WIDTH)
        cp.set("window", "window-width", self.WINDOW_WIDTH)
        cp.set("window", "window-height", self.WINDOW_HEIGHT)
        cp.set("window", "show-panel", self.SHOW_PANEL)
        cp.set("window", "show-toolbar", self.SHOW_TOOLBAR)

        i = 1
        for group in self.groups:
            for host in groups[group]:
                section = "host " + str(i)
                cp.add_section(section)
                HostUtils.save_host_to_ini(cp, section, host)
                i += 1

        cp.add_section("shortcuts")
        i = 1
        for s in self.shortcuts:
            if type(self.shortcuts[s]) == list:
                cp.set("shortcuts", self.shortcuts[s][0], s)
            else:
                cp.set("shortcuts", "shortcut%d" % i, s)
                cp.set("shortcuts", "command%d" % i, self.shortcuts[s].replace('\n', '\\n'))
                i += 1

        f = open(const.CONFIG_FILE + ".tmp", "w")
        cp.write(f)
        f.close()
        os.rename(const.CONFIG_FILE + ".tmp", const.CONFIG_FILE)
