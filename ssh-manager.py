#!/usr/bin/env python
#
# from __future__ import with_statement

import ConfigParser
from ConfigParser import NoOptionError
import operator
import os
import sys
import UiHelper
import constants as const
from HostUtils import HostUtils

try:
    import gtk
    import gobject
    import pygtk
    import gtk.glade

    pygtk.require("2.0")

except:
    print >> sys.stderr, "pygtk 2.0 required"
    sys.exit(1)

# Ver si expect esta instalado
try:
    e = os.system("expect >/dev/null 2>&1 -v")
except:
    e = -1
if e != 0:
    error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, 'You must install expect', gtk.BUTTONS_OK)
    error.run()
    sys.exit(1)

gtk.gdk.threads_init()

UiHelper.bindtextdomain(const.domain_name, const.locale_dir)

groups = {}
shortcuts = {}


# Configuration variables
class conf():
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


def loadConfig():
    global groups
    cp = ConfigParser.RawConfigParser()
    cp.read(const.CONFIG_FILE)

    # Read general configuration
    try:
        conf.WORD_SEPARATORS = cp.get("options", "word-separators")
        conf.BUFFER_LINES = cp.getint("options", "buffer-lines")
        conf.CONFIRM_ON_EXIT = cp.getboolean("options", "confirm-exit")
        conf.FONT_COLOR = cp.get("options", "font-color")
        conf.BACK_COLOR = cp.get("options", "back-color")
        conf.TRANSPARENCY = cp.getint("options", "transparency")
        conf.PASTE_ON_RIGHT_CLICK = cp.getboolean("options", "paste-right-click")
        conf.CONFIRM_ON_CLOSE_TAB = cp.getboolean("options", "confirm-close-tab")
        conf.CHECK_UPDATES = cp.getboolean("options", "check-updates")
        conf.COLLAPSED_FOLDERS = cp.get("window", "collapsed-folders")
        conf.LEFT_PANEL_WIDTH = cp.getint("window", "left-panel-width")
        conf.WINDOW_WIDTH = cp.getint("window", "window-width")
        conf.WINDOW_HEIGHT = cp.getint("window", "window-height")
        conf.FONT = cp.get("options", "font")
        conf.HIDE_DONATE = cp.getboolean("options", "donate")
        conf.AUTO_COPY_SELECTION = cp.getboolean("options", "auto-copy-selection")
        conf.LOG_PATH = cp.get("options", "log-path")
        conf.VERSION = cp.get("options", "version")
        conf.AUTO_CLOSE_TAB = cp.getint("options", "auto-close-tab")
        conf.SHOW_PANEL = cp.getboolean("window", "show-panel")
        conf.SHOW_TOOLBAR = cp.getboolean("window", "show-toolbar")
        conf.STARTUP_LOCAL = cp.getboolean("options", "startup-local")
    except:
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

    global shortcuts
    shortcuts = scuts

    # Create hosts list
    hu = HostUtils()
    groups = hu.load_hosts(cp, version=conf.VERSION)


class MainWindow():
    def __init__(self):
        builder = gtk.Builder()
        builder.set_translation_domain(const.domain_name)
        builder.add_from_file("ssh-manager.ui")
        builder.connect_signals(UiHelper.Handler())
        self.menuServers = builder.get_object("menuServers")
        self.nbConsole = builder.get_object("nbConsole")
        self.treeModel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT, gtk.gdk.Pixbuf)
        self.treeServers = builder.get_object("treeServers")
        self.wMain = builder.get_object("wMain")

        self.initLeftPane()

    def run(self):
        self.wMain.show_all()
        gtk.main()

    def initLeftPane(self):
        global groups

        self.treeServers.set_model(self.treeModel)

        self.treeServers.set_level_indentation(5)
        # Force the alternating row colors, by default it's off with one column
        self.treeServers.set_property('rules-hint', True)
        gtk.rc_parse_string("""
                style "custom-treestyle"{
                    GtkTreeView::allow-rules = 1
                }
                widget "*treeServers*" style "custom-treestyle"
            """)
        column = gtk.TreeViewColumn()
        column.set_title('Servers')
        self.treeServers.append_column(column)

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, expand=False)
        column.add_attribute(renderer, 'pixbuf', 2)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, expand=True)
        column.add_attribute(renderer, 'text', 0)

        self.treeServers.set_has_tooltip(True)
        self.treeServers.connect('query-tooltip', self.on_treeServers_tooltip)
        self.updateTree()

    def on_treeServers_tooltip(self, widget, x, y, keyboard, tooltip):
        x, y = widget.convert_widget_to_bin_window_coords(x, y)
        pos = widget.get_path_at_pos(x, y)
        if pos:
            host = list(widget.get_model()[pos[0]])[1]
            if host:
                text = "<span><b>%s</b>\n%s:%s@%s\n</span><span size='smaller'>%s</span>" % (
                    host.name, host.type, host.user, host.host, host.description)
                tooltip.set_markup(text)
                return True
        return False

    def updateTree(self):
        for group in dict(groups):
            if len(groups[group]) == 0:
                del groups[group]

        if conf.COLLAPSED_FOLDERS is None:
            conf.COLLAPSED_FOLDERS = ','.join(self.get_collapsed_nodes())

        self.menuServers.foreach(self.menuServers.remove)
        self.treeModel.clear()

        iconHost = self.treeServers.render_icon("gtk-network", size=gtk.ICON_SIZE_BUTTON, detail=None)
        iconDir = self.treeServers.render_icon("gtk-directory", size=gtk.ICON_SIZE_BUTTON, detail=None)

        groupKeys = groups.keys()
        groupKeys.sort(lambda x, y: cmp(y, x))

        for key in groupKeys:
            group = None
            path = ""
            menuNode = self.menuServers

            for folder in key.split("/"):
                path = path + '/' + folder
                row = self.get_folder(self.treeModel, '', path)
                if row == None:
                    group = self.treeModel.prepend(group, [folder, None, iconDir])
                else:
                    group = row.iter

                menu = self.get_folder_menu(self.menuServers, '', path)
                if menu is None:
                    menu = gtk.ImageMenuItem(folder)
                    # menu.set_image(gtk.image_new_from_stock(gtk.STOCK_DIRECTORY, gtk.ICON_SIZE_MENU))
                    menuNode.prepend(menu)
                    menuNode = gtk.Menu()
                    menu.set_submenu(menuNode)
                    menu.show()
                else:
                    menuNode = menu

            groups[key].sort(key=operator.attrgetter('name'))
            for host in groups[key]:
                self.treeModel.append(group, [host.name, host, iconHost])
                mnuItem = gtk.ImageMenuItem(host.name)
                mnuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_NETWORK, gtk.ICON_SIZE_MENU))
                mnuItem.show()
                # mnuItem.connect("activate", lambda arg, nb, h: self.addTab(nb, h), self.nbConsole, host) TODO
                menuNode.append(mnuItem)

        self.set_collapsed_nodes()
        conf.COLLAPSED_FOLDERS = None

    def get_folder(self, obj, folder, path):
        if not obj:
            return None
        for row in obj:
            if path == folder + '/' + row[0]:
                return row
            i = self.get_folder(row.iterchildren(), folder + '/' + row[0], path)
            if i:
                return i

    def get_folder_menu(self, obj, folder, path):
        if not obj or not (isinstance(obj, gtk.Menu) or isinstance(obj, gtk.MenuItem)):
            return None
        for item in obj.get_children():
            if path == folder + '/' + item.get_label():
                return item.get_submenu()
            i = self.get_folder_menu(item.get_submenu(), folder + '/' + item.get_label(), path)
            if i:
                return i

    def set_collapsed_nodes(self):
        self.treeServers.expand_all()
        if self.treeModel.get_iter_root():
            for node in conf.COLLAPSED_FOLDERS.split(","):
                if node != '':
                    self.treeServers.collapse_row(node)


def main():
    loadConfig()
    w_main = MainWindow()
    w_main.run()


if __name__ == "__main__":
    main()
