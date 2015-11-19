#!/usr/bin/env python
#
# from __future__ import with_statement

import operator
import os
import sys
import UiHelper
from Configuration import Conf
import constants as const

try:
    import gtk
    import gobject
    import pygtk
    import gtk.glade

    pygtk.require("2.0")

except:
    print >> sys.stderr, "pygtk 2.0 required"
    sys.exit(1)

# check if @expect is installed
try:
    e = os.system("expect >/dev/null 2>&1 -v")
except OSError:
    print >> sys.stderr, 'You must install expect'
    sys.exit(1)

gtk.gdk.threads_init()
UiHelper.bindtextdomain(const.domain_name, const.locale_dir)


class MainWindow():
    def __init__(self):
        self.conf = Conf()
        builder = gtk.Builder()
        builder.set_translation_domain(const.domain_name)
        builder.add_from_file("ssh-manager.ui")
        builder.connect_signals(UiHelper.Handler(self))
        self.menuServers = builder.get_object("menuServers")
        self.nbConsole = builder.get_object("nbConsole")
        self.treeModel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT, gtk.gdk.Pixbuf)
        self.treeServers = builder.get_object("treeServers")
        self.wMain = builder.get_object("wMain")
        self.hpMain = builder.get_object("hpMain")
        self.builder = builder

    def run(self):
        if self.conf.WINDOW_WIDTH != -1 and self.conf.WINDOW_HEIGHT != -1:
            self.wMain.resize(self.conf.WINDOW_WIDTH, self.conf.WINDOW_HEIGHT)
        else:
            self.wMain.maximize()

        if self.conf.LEFT_PANEL_WIDTH != 0:
            self.hpMain.previous_position = self.conf.LEFT_PANEL_WIDTH
            self.set_panel_visible(self.conf.SHOW_PANEL)

        self.set_toolbar_visible(self.conf.SHOW_TOOLBAR)

        self.init_left_pane()
        self.wMain.show_all()
        gtk.main()

    def init_left_pane(self):

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
        self.treeServers.connect('query-tooltip', self.on_tree_servers_tooltip)
        self.update_tree()

    @staticmethod
    def on_tree_servers_tooltip(widget, x, y, keyboard, tooltip):
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

    def update_tree(self):
        for group in dict(self.conf.groups):
            if len(self.conf.groups[group]) == 0:
                del self.conf.groups[group]

        self.menuServers.foreach(self.menuServers.remove)
        self.treeModel.clear()

        icon_host = self.treeServers.render_icon("gtk-network", size=gtk.ICON_SIZE_BUTTON, detail=None)
        icon_dir = self.treeServers.render_icon("gtk-directory", size=gtk.ICON_SIZE_BUTTON, detail=None)

        group_keys = self.conf.groups.keys()
        group_keys.sort(lambda x, y: cmp(y, x))

        for key in group_keys:
            group = None
            path = ""
            menu_node = self.menuServers

            for folder in key.split("/"):
                path = path + '/' + folder
                row = self.get_folder(self.treeModel, '', path)
                if row is None:
                    group = self.treeModel.prepend(group, [folder, None, icon_dir])
                else:
                    group = row.iter

                menu = self.get_folder_menu(self.menuServers, '', path)
                if menu is None:
                    menu = gtk.ImageMenuItem(folder)
                    # menu.set_image(gtk.image_new_from_stock(gtk.STOCK_DIRECTORY, gtk.ICON_SIZE_MENU))
                    menu_node.prepend(menu)
                    menu_node = gtk.Menu()
                    menu.set_submenu(menu_node)
                    menu.show()
                else:
                    menu_node = menu

            self.conf.groups[key].sort(key=operator.attrgetter('name'))
            for host in self.conf.groups[key]:
                self.treeModel.append(group, [host.name, host, icon_host])
                menu_item = gtk.ImageMenuItem(host.name)
                menu_item.set_image(gtk.image_new_from_stock(gtk.STOCK_NETWORK, gtk.ICON_SIZE_MENU))
                menu_item.show()
                # mnuItem.connect("activate", lambda arg, nb, h: self.addTab(nb, h), self.nbConsole, host) TODO
                menu_node.append(menu_item)

        self.set_collapsed_nodes()

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
            for node in self.conf.COLLAPSED_FOLDERS.split(","):
                if node != '':
                    self.treeServers.collapse_row(node)

    def set_panel_visible(self, visibility):
        if visibility:
            gobject.timeout_add(200, lambda: self.hpMain.set_position(
                self.hpMain.previous_position if self.hpMain.previous_position > 10 else 150))
        else:
            self.hpMain.previous_position = self.hpMain.get_position()
            gobject.timeout_add(200, lambda: self.hpMain.set_position(0))
        self.builder.get_object("showPanel").set_active(visibility)
        self.conf.SHOW_PANEL = visibility

    def set_toolbar_visible(self, visibility):
        if visibility:
            self.builder.get_object("toolbar1").show()
            self.builder.get_object("showToolbar").set_active(visibility)
        else:
            self.builder.get_object("toolbar1").hide()
            self.builder.get_object("showToolbar").set_active(visibility)
            self.conf.SHOW_TOOLBAR = visibility


def main():
    w_main = MainWindow()
    w_main.run()


if __name__ == "__main__":
    main()
