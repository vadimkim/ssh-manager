#!/usr/bin/env python
#
# from __future__ import with_statement

import operator
import os
import sys
import time
import pango
import UiHelper
from UiHelper import Handler
from Configuration import Conf
from HostUtils import Host
from HostUtils import HostUtils
from NotebookTabLabel import NotebookTabLabel
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

try:
    import vte
except:
    error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                              'You must install libvte for python')
    error.run()
    sys.exit(1)

gtk.gdk.threads_init()
UiHelper.bindtextdomain(const.domain_name, const.locale_dir)


class MainWindow:
    def __init__(self):
        self.conf = Conf()
        self.real_transparency = False
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
        self.menuCustomCommands = builder.get_object("menuCustomCommands")
        self.popupMenu = gtk.Menu()
        self.popupMenuTab = gtk.Menu()
        self.builder = builder

    def init(self, group, host=None):
        self.cmbGroup.get_child().set_text(group)
        if host == None:
            self.isNew = True
            return

        self.isNew = False
        self.oldGroup = group
        self.txtName.set_text(host.name)
        self.oldName = host.name
        self.txtDescription.set_text(host.description)
        self.txtHost.set_text(host.host)
        i =  self.cmbType.get_model().get_iter_first()
        while i!=None:
            if (host.type == self.cmbType.get_model()[i][0]):
                self.cmbType.set_active_iter(i)
                break
            else:
                i = self.cmbType.get_model().iter_next(i)
        self.txtUser.set_text(host.user)
        self.txtPass.set_text(host.password)
        self.txtPrivateKey.set_text(host.private_key)
        self.txtPort.set_text(host.port)
        for t in host.tunnel:
            if t!="":
                tun = t.split(":")
                tun.append(t)
                self.treeModel.append(  tun )
        self.txtCommands.set_sensitive(False)
        self.chkCommands.set_active(False)
        if host.commands!='' and host.commands!=None:
            self.txtCommands.get_buffer().set_text(host.commands)
            self.txtCommands.set_sensitive(True)
            self.chkCommands.set_active(True)
        use_keep_alive = host.keep_alive!='' and host.keep_alive!='0' and host.keep_alive!=None
        self.txtKeepAlive.set_sensitive(use_keep_alive)
        self.chkKeepAlive.set_active(use_keep_alive)
        self.txtKeepAlive.set_text(host.keep_alive)
        if host.font_color!='' and host.font_color!=None and host.back_color!='' and host.back_color!=None:
            self.get_widget("chkDefaultColors").set_active(False)
            self.btnFColor.set_sensitive(True)
            self.btnBColor.set_sensitive(True)
            fcolor=host.font_color
            bcolor=host.back_color
        else:
            self.get_widget("chkDefaultColors").set_active(True)
            self.btnFColor.set_sensitive(False)
            self.btnBColor.set_sensitive(False)
            fcolor="#FFFFFF"
            bcolor="#000000"

        self.btnFColor.set_color(gtk.gdk.Color(fcolor))
        self.btnBColor.set_color(gtk.gdk.Color(bcolor))

        m = self.btnFColor.get_colormap()
        color = m.alloc_color("red")
        style = self.btnFColor.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = color
        self.btnFColor.set_style(style)
        self.btnFColor.queue_draw()

        self.btnFColor.selected_color=fcolor
        self.btnBColor.selected_color=bcolor
        self.chkX11.set_active(host.x11)
        self.chkAgent.set_active(host.agent)
        self.chkCompression.set_active(host.compression)
        self.txtCompressionLevel.set_text(host.compressionLevel)
        self.txtExtraParams.set_text(host.extra_params)
        self.chkLogging.set_active(host.log)
        self.cmbBackspace.set_active(host.backspace_key)
        self.cmbDelete.set_active(host.delete_key)
        self.update_texttags()

    def run(self):
        # before window construction
        if self.conf.WINDOW_WIDTH != -1 and self.conf.WINDOW_HEIGHT != -1:
            self.wMain.resize(self.conf.WINDOW_WIDTH, self.conf.WINDOW_HEIGHT)
        else:
            self.wMain.maximize()

        if self.conf.LEFT_PANEL_WIDTH != 0:
            self.hpMain.previous_position = self.conf.LEFT_PANEL_WIDTH
            self.set_panel_visible(self.conf.SHOW_PANEL)
        self.set_toolbar_visible(self.conf.SHOW_TOOLBAR)

        self.init_left_pane()
        self.create_menu()
        self.wMain.show_all()

        gtk.main()

        # after window construction
        if self.conf.TRANSPARENCY>0:
            # set top level window transparency
            screen = self.wMain.get_screen()
            colormap = screen.get_rgba_colormap()
            if colormap is not None and screen.is_composited():
                self.wMain.set_colormap(colormap)
                self.real_transparency = True

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

    def create_menu(self):
        self.popupMenu.mnuCopy = menuItem = gtk.ImageMenuItem(_("Copiar"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_COPY, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'C')
        menuItem.show()

        self.popupMenu.mnuPaste = menuItem = gtk.ImageMenuItem(_("Pegar"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_PASTE, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'V')
        menuItem.show()

        self.popupMenu.mnuCopyPaste = menuItem = gtk.ImageMenuItem(_("Copiar y Pegar"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'CV')
        menuItem.show()

        self.popupMenu.mnuSelect = menuItem = gtk.ImageMenuItem(_("Seleccionar todo"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_SELECT_ALL, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'A')
        menuItem.show()

        self.popupMenu.mnuCopyAll = menuItem = gtk.ImageMenuItem(_("Copiar todo"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_SELECT_ALL, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'CA')
        menuItem.show()

        self.popupMenu.mnuSelect = menuItem = gtk.ImageMenuItem(_("Guardar buffer en archivo"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_SAVE, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'S')
        menuItem.show()

        menuItem = gtk.MenuItem()
        self.popupMenu.append(menuItem)
        menuItem.show()

        self.popupMenu.mnuReset = menuItem = gtk.ImageMenuItem(_("Reiniciar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'RS2')
        menuItem.show()

        self.popupMenu.mnuClear = menuItem = gtk.ImageMenuItem(_("Reiniciar y Limpiar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'RC2')
        menuItem.show()

        self.popupMenu.mnuClone = menuItem = gtk.ImageMenuItem(_("Clonar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_COPY, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'CC2')
        menuItem.show()

        self.popupMenu.mnuLog = menuItem = gtk.CheckMenuItem(_("Habilitar log"))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'L2')
        menuItem.show()

        self.popupMenu.mnuClose = menuItem = gtk.ImageMenuItem(_("Cerrar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU))
        self.popupMenu.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'X')
        menuItem.show()

        menuItem = gtk.MenuItem()
        self.popupMenu.append(menuItem)
        menuItem.show()

        # Menu de comandos personalizados
        self.popupMenu.mnuCommands = gtk.Menu()

        self.popupMenu.mnuCmds = menuItem = gtk.ImageMenuItem(_("Comandos personalizados"))
        menuItem.set_submenu(self.popupMenu.mnuCommands)
        self.popupMenu.append(menuItem)
        menuItem.show()
        self.populateCommandsMenu()

        # Menu contextual para panel de servidores
        self.popupMenuFolder = gtk.Menu()

        self.popupMenuFolder.mnuConnect = menuItem = gtk.ImageMenuItem(_("Conectar"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU))
        self.popupMenuFolder.append(menuItem)
        menuItem.show()

        self.popupMenuFolder.mnuCopyAddress = menuItem = gtk.ImageMenuItem(_("Copiar Direccion"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_COPY, gtk.ICON_SIZE_MENU))
        self.popupMenuFolder.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'H')
        menuItem.show()

        self.popupMenuFolder.mnuAdd = menuItem = gtk.ImageMenuItem(_("Agregar Host"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU))
        self.popupMenuFolder.append(menuItem)
        menuItem.show()

        self.popupMenuFolder.mnuEdit = menuItem = gtk.ImageMenuItem(_("Editar"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU))
        self.popupMenuFolder.append(menuItem)
        menuItem.show()

        self.popupMenuFolder.mnuDel = menuItem = gtk.ImageMenuItem(_("Eliminar"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_MENU))
        self.popupMenuFolder.append(menuItem)
        menuItem.show()

        self.popupMenuFolder.mnuDup = menuItem = gtk.ImageMenuItem(_("Duplicar Host"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_DND_MULTIPLE, gtk.ICON_SIZE_MENU))
        self.popupMenuFolder.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'D')
        menuItem.show()

        menuItem = gtk.MenuItem()
        self.popupMenuFolder.append(menuItem)
        menuItem.show()

        self.popupMenuFolder.mnuExpand = menuItem = gtk.ImageMenuItem(_("Expandir todo"))
        self.popupMenuFolder.append(menuItem)
        menuItem.connect("activate", lambda *args: self.treeServers.expand_all())
        menuItem.show()

        self.popupMenuFolder.mnuCollapse = menuItem = gtk.ImageMenuItem(_("Contraer todo"))
        self.popupMenuFolder.append(menuItem)
        menuItem.connect("activate", lambda *args: self.treeServers.collapse_all())
        menuItem.show()

        # Menu contextual para tabs

        self.popupMenuTab.mnuRename = menuItem = gtk.ImageMenuItem(_("Renombrar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU))
        self.popupMenuTab.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'R')
        menuItem.show()

        self.popupMenuTab.mnuReset = menuItem = gtk.ImageMenuItem(_("Reiniciar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_MENU))
        self.popupMenuTab.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'RS')
        menuItem.show()

        self.popupMenuTab.mnuClear = menuItem = gtk.ImageMenuItem(_("Reiniciar y Limpiar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
        self.popupMenuTab.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'RC')
        menuItem.show()

        self.popupMenuTab.mnuReopen = menuItem = gtk.ImageMenuItem(_("Reconectar al host"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_CONNECT, gtk.ICON_SIZE_MENU))
        self.popupMenuTab.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'RO')
        # menuItem.show()

        self.popupMenuTab.mnuClone = menuItem = gtk.ImageMenuItem(_("Clonar consola"))
        menuItem.set_image(gtk.image_new_from_stock(gtk.STOCK_COPY, gtk.ICON_SIZE_MENU))
        self.popupMenuTab.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'CC')
        menuItem.show()

        self.popupMenuTab.mnuLog = menuItem = gtk.CheckMenuItem(_("Habilitar log"))
        self.popupMenuTab.append(menuItem)
        menuItem.connect("activate", self.on_popupmenu, 'L')
        menuItem.show()

    def on_popupmenu(self, widget, item, *args):
        if item == 'V':  # PASTE
            self.terminal_paste(self.popupMenu.terminal)
            return True
        elif item == 'C':  # COPY
            self.terminal_copy(self.popupMenu.terminal)
            return True
        elif item == 'CV':  # COPY and PASTE
            self.terminal_copy_paste(self.popupMenu.terminal)
            return True
        elif item == 'A':  # SELECT ALL
            self.terminal_select_all(self.popupMenu.terminal)
            return True
        elif item == 'CA':  # COPY ALL
            self.terminal_copy_all(self.popupMenu.terminal)
            return True
        elif item == 'X':  # CLOSE CONSOLE
            widget = self.popupMenu.terminal.get_parent()
            notebook = widget.get_parent()
            page = notebook.page_num(widget)
            notebook.remove_page(page)
            return True
        elif item == 'CP':  # CUSTOM COMMANDS
            self.popupMenu.terminal.feed_child(args[0])
        elif item == 'S':  # SAVE BUFFER
            self.show_save_buffer(self.popupMenu.terminal)
            return True
        elif item == 'H':  # COPY HOST ADDRESS TO CLIPBOARD
            if self.treeServers.get_selection().get_selected()[1] is not None and not self.treeModel.iter_has_child(
                    self.treeServers.get_selection().get_selected()[1]):
                host = self.treeModel.get_value(self.treeServers.get_selection().get_selected()[1], 1)
                cb = gtk.Clipboard()
                cb.set_text(host.host)
                cb.store()
            return True
        elif item == 'D':  # DUPLICATE HOST
            if self.treeServers.get_selection().get_selected()[1] is not None and not self.treeModel.iter_has_child(
                    self.treeServers.get_selection().get_selected()[1]):
                selected = self.treeServers.get_selection().get_selected()[1]
                group = self.get_group(selected)
                host = self.treeModel.get_value(selected, 1)
                newname = '%s (copy)' % (host.name)
                newhost = host.clone()
                for h in self.conf.groups[group]:
                    if h.name == newname:
                        newname = '%s (copy)' % (newname)
                newhost.name = newname
                self.conf.groups[group].append(newhost)
                self.updateTree()
                self.writeConfig()
            return True
        elif item == 'R':  # RENAME TAB
            text = HostUtils.inputbox(_('Renombrar consola'), _('Ingrese nuevo nombre'), const.ICON_PATH,
                            self.popupMenuTab.label.get_text().strip())
            if text != None and text != '':
                self.popupMenuTab.label.set_text("  %s  " % (text))
            return True
        elif item == 'RS' or item == 'RS2':  # RESET CONSOLE
            if (item == 'RS'):
                tab = self.popupMenuTab.label.get_parent().get_parent()
                term = tab.widget.get_child()
            else:
                term = self.popupMenu.terminal
            term.reset(True, False)
            return True
        elif item == 'RC' or item == 'RC2':  # RESET AND CLEAR CONSOLE
            if (item == 'RC'):
                tab = self.popupMenuTab.label.get_parent().get_parent()
                term = tab.widget.get_child()
            else:
                term = self.popupMenu.terminal
            term.reset(True, True)
            return True
        elif item == 'RO':  # REOPEN SESION
            tab = self.popupMenuTab.label.get_parent().get_parent()
            term = tab.widget.get_child()
            if not hasattr(term, "command"):
                term.fork_command(const.SHELL)
            else:
                term.fork_command(term.command[0], term.command[1])
                while gtk.events_pending():
                    gtk.main_iteration(False)

                # esperar 2 seg antes de enviar el pass para dar tiempo a que se levante expect y prevenir que se muestre el pass
                if term.command[2] != None and term.command[2] != '':
                    gobject.timeout_add(2000, self.send_data, term, term.command[2])
            tab.mark_tab_as_active()
            return True
        elif item == 'CC' or item == 'CC2':  # CLONE CONSOLE
            if item == 'CC':
                tab = self.popupMenuTab.label.get_parent().get_parent()
                term = tab.widget.get_child()
                ntbk = tab.get_parent()
            else:
                term = self.popupMenu.terminal
                ntbk = term.get_parent().get_parent()
                tab = ntbk.get_tab_label(term.get_parent())
            if not hasattr(term, "host"):
                self.addTab(ntbk, tab.get_text())
            else:
                host = term.host.clone()
                host.name = tab.get_text()
                host.log = hasattr(term, "log_handler_id") and term.log_handler_id != 0
                self.addTab(ntbk, host)
            return True
        elif item == 'L' or item == 'L2':  # ENABLE/DISABLE LOG
            if item == 'L':
                tab = self.popupMenuTab.label.get_parent().get_parent()
                term = tab.widget.get_child()
            else:
                term = self.popupMenu.terminal
            if not self.set_terminal_logger(term, widget.get_active()):
                widget.set_active(False)
            return True

    def populateCommandsMenu(self):
        self.popupMenu.mnuCommands.foreach(lambda x: self.popupMenu.mnuCommands.remove(x))
        self.menuCustomCommands.foreach(lambda x: self.menuCustomCommands.remove(x))
        for x in self.conf.shortcuts:
            if type(self.conf.shortcuts[x]) != list:
                menu_item = self.createMenuItem(x, self.conf.shortcuts[x][0:30])
                self.popupMenu.mnuCommands.append(menu_item)
                menu_item.connect("activate", self.on_popupmenu, 'CP', self.conf.shortcuts[x])

                menu_item = self.createMenuItem(x, self.conf.shortcuts[x][0:30])
                self.menuCustomCommands.append(menu_item)
                menu_item.connect("activate", self.on_menuCustomCommands_activate, self.conf.shortcuts[x])

    def createMenuItem(self, shortcut, label):
        menuItem = gtk.MenuItem('')
        menuItem.get_child().set_markup("<span color='blue'  size='x-small'>[%s]</span> %s" % (shortcut, label))
        menuItem.show()
        return menuItem

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
                menu_item.connect("activate", lambda arg, nb, h: self.addTab(nb, h), self.nbConsole, host)
                menu_node.append(menu_item)

        self.set_collapsed_nodes()

    def addTab(self, notebook, host):
        try:
            v = vte.Terminal()
            v.set_word_chars(self.conf.WORD_SEPARATORS)
            v.set_scrollback_lines(self.conf.BUFFER_LINES)
            if v.get_emulation() != os.getenv("TERM"):
                os.environ['TERM'] = v.get_emulation()

            if isinstance(host, basestring):
                host = Host('', host)

            fcolor = host.font_color
            bcolor = host.back_color
            if fcolor == '' or fcolor == None or bcolor == '' or bcolor == None:
                fcolor = self.conf.FONT_COLOR
                bcolor = self.conf.BACK_COLOR

            if len(fcolor) > 0 and len(bcolor) > 0:
                v.set_colors(gtk.gdk.Color(fcolor), gtk.gdk.Color(bcolor), [])

            if len(self.conf.FONT) == 0:
                self.conf.FONT = 'monospace'
            else:
                v.set_font(pango.FontDescription(self.conf.FONT))

            scrollPane = gtk.ScrolledWindow()
            scrollPane.connect('button_press_event', lambda *args: True)
            scrollPane.set_property('hscrollbar-policy', gtk.POLICY_NEVER)
            tab = NotebookTabLabel("  %s  " % (host.name), self.nbConsole, scrollPane, self.popupMenuTab, self.conf)

            v.connect("child-exited", lambda widget: tab.mark_tab_as_closed())
            v.connect('focus', self.on_tab_focus)
            v.connect('button_press_event', self.on_terminal_click)
            v.connect('key_press_event', self.on_terminal_keypress)
            v.connect('selection-changed', self.on_terminal_selection)

            if self.conf.TRANSPARENCY > 0:
                if not self.real_transparency:
                    v.set_background_transparent(True)
                    v.set_background_saturation(self.conf.TRANSPARENCY / 100.0)
                    if len(bcolor) > 0:
                        v.set_background_tint_color(gtk.gdk.Color(bcolor))
                else:
                    v.set_opacity(int((100 - self.conf.TRANSPARENCY) / 100.0 * 65535))

            v.set_backspace_binding(host.backspace_key)
            v.set_delete_binding(host.delete_key)

            scrollPane.show()
            scrollPane.add(v)
            v.show()

            notebook.append_page(scrollPane, tab_label=tab)
            notebook.set_current_page(self.nbConsole.page_num(scrollPane))
            notebook.set_tab_reorderable(scrollPane, True)
            notebook.set_tab_detachable(scrollPane, True)
            self.wMain.set_focus(v)
            self.on_tab_focus(v)
            self.set_terminal_logger(v, host.log)

            gobject.timeout_add(200, lambda: self.wMain.set_focus(v))

            # Dar tiempo a la interfaz para que muestre el terminal
            while gtk.events_pending():
                gtk.main_iteration(False)

            if host.host == '' or host.host == None:
                v.fork_command(const.SHELL)
            else:
                cmd = const.SSH_COMMAND
                password = host.password
                if host.type == 'ssh':
                    if len(host.user) == 0:
                        host.user = HostUtils.get_username()
                    if host.password == '':
                        cmd = const.SSH_BIN
                        args = [const.SSH_BIN, '-l', host.user, '-p', host.port]
                    else:
                        args = [const.SSH_COMMAND, host.type, '-l', host.user, '-p', host.port]
                    if host.keep_alive != '0' and host.keep_alive != '':
                        args.append('-o')
                        args.append('ServerAliveInterval=%s' % (host.keep_alive))
                    for t in host.tunnel:
                        if t != "":
                            if t.endswith(":*:*"):
                                args.append("-D")
                                args.append(t[:-4])
                            else:
                                args.append("-L")
                                args.append(t)
                    if host.x11:
                        args.append("-X")
                    if host.agent:
                        args.append("-A")
                    if host.compression:
                        args.append("-C")
                        if host.compressionLevel != '':
                            args.append('-o')
                            args.append('CompressionLevel=%s' % (host.compressionLevel))
                    if host.private_key != None and host.private_key != '':
                        args.append("-i")
                        args.append(host.private_key)
                    if host.extra_params != None and host.extra_params != '':
                        args += host.extra_params.split()
                    args.append(host.host)
                else:
                    if host.user == '' or host.password == '':
                        password = ''
                        cmd = const.TEL_BIN
                        args = [const.TEL_BIN]
                    else:
                        args = [const.SSH_COMMAND, host.type, '-l', host.user]
                    if host.extra_params != None and host.extra_params != '':
                        args += host.extra_params.split()
                    args += [host.host, host.port]
                v.command = (cmd, args, password)
                v.fork_command(cmd, args)
                while gtk.events_pending():
                    gtk.main_iteration(False)

                # esperar 2 seg antes de enviar el pass para dar tiempo a que se levante expect y prevenir que se muestre el pass
                if password != None and password != '':
                    gobject.timeout_add(2000, self.send_data, v, password)

            # esperar 3 seg antes de enviar comandos
            if host.commands != None and host.commands != '':
                basetime = 700 if len(host.host) == 0 else 3000
                lines = []
                for line in host.commands.splitlines():
                    if line.startswith("##D=") and line[4:].isdigit():
                        if len(lines):
                            gobject.timeout_add(basetime, self.send_data, v, "\r".join(lines))
                            lines = []
                        basetime += int(line[4:])
                    else:
                        lines.append(line)
                if len(lines):
                    gobject.timeout_add(basetime, self.send_data, v, "\r".join(lines))
            v.queue_draw()

            # guardar datos de consola para clonar consola
            v.host = host
        except:
            UiHelper.msgbox("%s [%s]" % (const.ERRMSG2, sys.exc_info()[1]), const.ICON_PATH)

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

    def get_group(self, i):
        if self.treeModel.iter_parent(i):
            p = self.get_group(self.treeModel.iter_parent(i))
            return (p+'/' if p!='' else '') + self.treeModel.get_value(self.treeModel.iter_parent(i),0)
        else:
            return ''

    def on_tab_focus(self, widget, *args):
        if isinstance(widget, vte.Terminal):
            self.current = widget

    def on_terminal_click(self, widget, event, *args):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            if self.conf.PASTE_ON_RIGHT_CLICK:
                widget.paste_clipboard()
            else:
                self.popupMenu.mnuCopy.set_sensitive(widget.get_has_selection())
                self.popupMenu.mnuLog.set_active( hasattr(widget, "log_handler_id") and widget.log_handler_id != 0 )
                self.popupMenu.terminal = widget
                self.popupMenu.popup( None, None, None, event.button, event.time)
            return True

    def on_terminal_keypress(self, widget, event, *args):
        if self.conf.shortcuts.has_key(self.get_key_name(event)):
            cmd = self.conf.shortcuts[self.get_key_name(event)]
            if type(cmd) == list:
                #comandos predefinidos
                if cmd == const.COPY:
                    self.terminal_copy(widget)
                elif cmd == const.PASTE:
                    self.terminal_paste(widget)
                elif cmd == const.COPY_ALL:
                    self.terminal_copy_all(widget)
                elif cmd == const.SAVE:
                    self.show_save_buffer(widget)
                elif cmd == const.FIND:
                    self.get_widget('txtSearch').select_region(0, -1)
                    self.get_widget('txtSearch').grab_focus()
                elif cmd == const.FIND_NEXT:
                    if hasattr(self, 'search'):
                        self.find_word()
                elif cmd == const.CLEAR:
                   widget.reset(True, True)
                elif cmd == const.FIND_BACK:
                    if hasattr(self, 'search'):
                        self.find_word(backwards=True)
                elif cmd == const.CONSOLE_PREV:
                    widget.get_parent().get_parent().prev_page()
                elif cmd == const.CONSOLE_NEXT:
                    widget.get_parent().get_parent().next_page()
                elif cmd == const.CONSOLE_CLOSE:
                    wid = widget.get_parent()
                    page = widget.get_parent().get_parent().page_num(wid)
                    if page != -1:
                        widget.get_parent().get_parent().remove_page(page)
                        wid.destroy()
                elif cmd == const.CONSOLE_RECONNECT:
                    if not hasattr(widget, "command"):
                        widget.fork_command(const.SHELL)
                    else:
                        widget.fork_command(widget.command[0], widget.command[1])
                        while gtk.events_pending():
                            gtk.main_iteration(False)

                        #esperar 2 seg antes de enviar el pass para dar tiempo a que se levante expect y prevenir que se muestre el pass
                        if widget.command[2]!=None and widget.command[2]!='':
                            gobject.timeout_add(2000, self.send_data, widget, widget.command[2])
                    widget.get_parent().get_parent().get_tab_label(widget.get_parent()).mark_tab_as_active()
                    return True
                elif cmd == const.CONNECT:
                    Handler.on_btnConnect_clicked(None)
                elif cmd[0][0:8] == "console_":
                    page = int(cmd[0][8:]) - 1
                    widget.get_parent().get_parent().set_current_page(page)
            else:
                #comandos del usuario
                widget.feed_child(cmd)
            return True
        return False

    def get_key_name(event):
        name = ""
        if event.state & 4:
            name = name + "CTRL+"
        if event.state & 1:
            name = name + "SHIFT+"
        if event.state & 8:
            name = name + "ALT+"
        if event.state & 67108864:
            name = name + "SUPER+"
        return name + gtk.gdk.keyval_name(event.keyval).upper()

    def on_terminal_selection(self, widget, *args):
        if self.conf.AUTO_COPY_SELECTION:
            self.terminal_copy(widget)
        return True

    def set_terminal_logger(self, terminal, enable_logging=True):
        if enable_logging:
            terminal.last_logged_col, terminal.last_logged_row = terminal.get_cursor_position()
            if hasattr(terminal, "log_handler_id"):
                if terminal.log_handler_id == 0:
                    terminal.log_handler_id = terminal.connect('contents-changed', self.on_contents_changed)
                return True
            terminal.log_handler_id = terminal.connect('contents-changed', self.on_contents_changed)
            p = terminal.get_parent()
            title = p.get_parent().get_tab_label(p).get_text().strip()
            prefix = "%s/%s-%s" % (os.path.expanduser(self.conf.LOG_PATH), title, time.strftime("%Y%m%d"))
            filename = ''
            for i in range(1,1000):
                if not os.path.exists("%s-%03i.log" % (prefix,i)):
                    filename = "%s-%03i.log" % (prefix,i)
                    break
            filename == "%s-%03i.log" % (prefix,1)
            try:
                terminal.log = open(filename, 'w', 0)
                terminal.log.write("Session '%s' opened at %s\n%s\n" % (title, time.strftime("%Y-%m-%d %H:%M:%S"), "-"*80))
            except:
                UiHelper.msgbox("%s\n%s" % (_("No se puede abrir el archivo de log para escritura"), filename))
                terminal.disconnect(terminal.log_handler_id)
                del terminal.log_handler_id
                return False
        else:
            if hasattr(terminal, "log_handler_id") and terminal.log_handler_id != 0:
                terminal.disconnect(terminal.log_handler_id)
                terminal.log_handler_id = 0
        return True


def main():
    w_main = MainWindow()
    w_main.run()


if __name__ == "__main__":
    main()
