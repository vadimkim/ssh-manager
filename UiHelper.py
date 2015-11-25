import os
import gtk
import constants as const
from Whost import Whost
from EntryDialog import EntryDialog


def bindtextdomain(app_name, locale_dir=None):
    """
    Bind the domain represented by app_name to the locale directory locale_dir.
    It has the effect of loading translations, enabling applications for different
    languages.
        :param app_name: a domain to look for translations, typically the name of an application.
        :param locale_dir: a directory with locales like locale_dir/lang_isocode/LC_MESSAGES/app_name.mo
        If omitted or None, then the current binding for app_name is used.
    """
    try:
        import locale
        import gettext
        locale.setlocale(locale.LC_ALL, "")
        gtk.glade.bindtextdomain(app_name, locale_dir)
        gettext.install(app_name, locale_dir, unicode=1)
    except (IOError, locale.Error), e:
        # force english as default locale
        try:
            os.environ['LANGUAGE'] = "en_US.UTF-8"
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            gtk.glade.bindtextdomain(app_name, locale_dir)
            gettext.install(app_name, locale_dir, unicode=1)
            return
        except:
            # if english didn't work use spanish
            try:
                __builtins__.__dict__["_"] = lambda x: x
            except:
                __builtins__["_"] = lambda x: x


def message_box(text, icon=const.ICON_PATH, parent=None):
    msg_box = gtk.MessageDialog(parent, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, text)
    msg_box.set_icon_from_file(icon)
    msg_box.run()
    msg_box.destroy()


def msg_confirm(text, icon):
    msg_box = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, text)
    msg_box.set_icon_from_file(icon)
    response = msg_box.run()
    msg_box.destroy()
    return response


def input_box(title, text, icon, default='', password=False):
    msg_box = EntryDialog(title, text, default, mask=password)
    msg_box.set_icon_from_file(icon)
    if msg_box.run() == gtk.RESPONSE_OK:
        response = msg_box.value
    else:
        response = None
    msg_box.destroy()
    return response


def show_open_dialog(parent, title, action):
    dlg = gtk.FileChooserDialog(title=title, parent=parent, action=action)
    dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

    dlg.add_button(gtk.STOCK_SAVE if action==gtk.FILE_CHOOSER_ACTION_SAVE else gtk.STOCK_OPEN, gtk.RESPONSE_OK)
    dlg.set_do_overwrite_confirmation(True)
    if not hasattr(parent,'lastPath'):
        parent.lastPath = os.path.expanduser("~")
    dlg.set_current_folder( parent.lastPath )

    if dlg.run() == gtk.RESPONSE_OK:
        filename = dlg.get_filename()
        parent.lastPath = os.path.dirname(filename)
    else:
        filename = None
    dlg.destroy()
    return filename


class Handler:
    def __init__(self, window):
        self.main = window

    def on_wMain_destroy(self, *args):
        gtk.mainquit()

    def on_wMain_delete_event(self, *args):
        gtk.mainquit()

    def on_hpMain_button_press_event(self, *args):
        pass

    def on_double_click(self, *args):
        pass

    def on_tvServers_button_press_event(self, widget, event, *args):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            path_info = self.main.treeServers.get_path_at_pos(x, y)
            if path_info is None:
                self.main.popupMenuFolder.mnuDel.hide()
                self.main.popupMenuFolder.mnuEdit.hide()
                self.main.popupMenuFolder.mnuCopyAddress.hide()
                self.main.popupMenuFolder.mnuDup.hide()
            else:
                path, col, cell_x, cell_y = path_info
                if self.main.treeModel.iter_children(self.main.treeModel.get_iter(path)):
                    self.main.popupMenuFolder.mnuEdit.hide()
                    self.main.popupMenuFolder.mnuCopyAddress.hide()
                    self.main.popupMenuFolder.mnuDup.hide()
                else:
                    self.main.popupMenuFolder.mnuEdit.show()
                    self.main.popupMenuFolder.mnuCopyAddress.show()
                    self.main.popupMenuFolder.mnuDup.show()
                self.main.popupMenuFolder.mnuDel.show()
                self.main.treeServers.grab_focus()
                self.main.treeServers.set_cursor(path, col, 0)
            self.main.popupMenuFolder.popup(None, None, None, event.button, event.time)
            return True

    def on_tvServers_row_activated(self, widget, *args):
        if not self.main.treeModel.iter_has_child(widget.get_selection().get_selected()[1]):
            selected = widget.get_selection().get_selected()[1]
            host = self.main.treeModel.get_value(selected, 1)
            self.main.add_tab(self.main.nbConsole, host)

    def on_btnDonate_clicked(self, *args):
        pass

    def on_btnCluster_clicked(self, *args):
        pass

    def on_btnSearch_clicked(self, *args):
        pass

    def on_btnSearchBack_clicked(self, *args):
        pass

    def on_txtSearch_focus(self, *args):
        pass

    def on_txtSearch_focus_out_event(self, *args):
        pass

    def on_btnConfig_clicked(self, *args):
        pass

    def on_btnUnsplit_clicked(self, *args):
        pass

    def on_btnVSplit_clicked(self, *args):
        pass

    def on_btnHSplit_clicked(self, *args):
        pass

    def on_btn_del_clicked(self, widget, *args):
        if self.main.treeServers.get_selection().get_selected()[1] is not None:
            if not self.main.treeModel.iter_has_child(self.main.treeServers.get_selection().get_selected()[1]):
                # Eliminar solo el nodo
                name = self.main.treeModel.get_value(self.main.treeServers.get_selection().get_selected()[1], 0)
                if msg_confirm("%s [%s]?" % (const.LABEL_TXT1, name)) == gtk.RESPONSE_OK:
                    host = self.main.treeModel.get_value(self.main.treeServers.get_selection().get_selected()[1], 1)
                    self.main.conf.groups[host.group].remove(host)
                    self.main.update_tree()
            else:
                # Eliminar todo el grupo
                group = self.get_group(self.treeModel.iter_children(self.main.treeServers.get_selection().get_selected()[1]))
                if msg_confirm("%s [%s]?" % (const.LABEL_TXT2, group)) == gtk.RESPONSE_OK:
                    try:
                        del self.main.groups[group]
                    except:
                        pass
                    for h in dict(self.main.groups):
                        if h.startswith(group + '/'):
                            del self.main.groups[h]
                    self.main.update_tree()
        self.main.conf.write_config()

    def on_btn_edit_clicked(self, widget, *args):
        if self.main.treeServers.get_selection().get_selected()[
            1] is not None and not self.main.treeModel.iter_has_child(
                self.main.treeServers.get_selection().get_selected()[1]):
            selected = self.main.treeServers.get_selection().get_selected()[1]
            host = self.main.treeModel.get_value(selected, 1)
            self.main.init(host.group, host)

    def on_btn_add_clicked(self, widget, *args):
        group = ""
        if self.main.treeServers.get_selection().get_selected()[1] is not None:
            selected = self.main.treeServers.get_selection().get_selected()[1]
            group = self.main.get_group(selected)
            if self.main.treeModel.iter_has_child(self.main.treeServers.get_selection().get_selected()[1]):
                selected = self.main.treeServers.get_selection().get_selected()[1]
                group = self.main.treeModel.get_value(selected, 0)
                parent_group = self.main.get_group(selected)
                if parent_group != '':
                    group = parent_group + '/' + group
        window_host = Whost(self.main)
        window_host.init(group)
        # self.main.update_tree()       TODO not relevant ?

    def on_btn_connect_clicked(self, widget):
        if self.main.treeServers.get_selection().get_selected()[1] is not None:
            if not self.main.treeModel.iter_has_child(self.main.treeServers.get_selection().get_selected()[1]):
                self.on_tvServers_row_activated(self.main.treeServers)
            else:
                selected = self.main.treeServers.get_selection().get_selected()[1]
                group = self.main.treeModel.get_value(selected, 0)
                parent_group = self.main.get_group(selected)
                if parent_group != '':
                    group = parent_group + '/' + group

                for g in self.main.conf.groups:
                    if g == group or g.startswith(group + '/'):
                        for host in self.main.conf.groups[g]:
                            self.main.add_tab(self.main.nbConsole, host)

    def on_btnLocal_clicked(self, *args):
        pass

    def on_btnFColor_clicked(self, *args):
        pass

    def on_chkDefaultColors_toggled(self, *args):
        pass

    def on_btnBColor_clicked(self, *args):
        pass

    def on_chkCommands_toggled(self, *args):
        pass

    def on_chkDynamic_toggled(self, *args):
        pass

    def on_chkCompression_toggled(self, *args):
        pass

    def on_chkKeepAlive_toggled(self, *args):
        pass

    def on_cmbType_changed(self, *args):
        pass

    def on_btnBrowse_clicked(self, *args):
        pass

    def on_okbutton1_clicked(self, *args):
        pass

    def on_cancelbutton1_clicked(self, widget, *args):
        top_level = widget.get_toplevel()
        top_level.destroy()

    # TODO remove this event after correct dialog init to see if close signal call destroy() automatically
    def on_wHost_response (self, widget, event):
        if event == -4:
            widget.destroy()

    def on_treeCommands_key_press_event(self, *args):
        pass

    def on_btnFont_clicked(self, *args):
        pass

    def on_chkDefaultFont_toggled(self, *args):
        pass

    def on_wCluster_destroy(self, *args):
        pass

    def on_txtCommands_key_press_event(self, *args):
        pass

    def on_btnInvert_clicked(self, *args):
        pass

    def on_btnNone_clicked(self, *args):
        pass

    def on_btnAll_clicked(self, *args):
        pass

    def on_cancelbutton2_clicked(self, *args):
        pass

    def on_wAbout_close(self, *args):
        pass

    def on_menu_file_quit_activate(self, menu_item):
        gtk.mainquit()

    def on_show_toolbar_toggled(self, widget, *args):
        self.main.set_toolbar_visible(widget.get_active())

    def on_show_panel_toggled(self, widget, *args):
        self.main.set_panel_visible(widget.get_active())
