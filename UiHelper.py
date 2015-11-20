import os
import gtk
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
            os.environ["LANGUAGE"] = "en_US.UTF-8"
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
            gtk.glade.bindtextdomain(app_name, locale_dir)
            gettext.install(app_name, locale_dir, unicode=1)
            return
        except:
            # english didnt work, just use spanish
            try:
                __builtins__.__dict__["_"] = lambda x: x
            except:
                __builtins__["_"] = lambda x: x


def msgbox(text, icon, parent=None):
    msgBox = gtk.MessageDialog(parent, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, text)
    msgBox.set_icon_from_file(icon)
    msgBox.run()
    msgBox.destroy()


def msgconfirm(text, icon):
    msgBox = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, text)
    msgBox.set_icon_from_file(icon)
    response = msgBox.run()
    msgBox.destroy()
    return response


def inputbox(title, text, icon, default='', password=False):
    msgBox = EntryDialog(title, text, default, mask=password)
    msgBox.set_icon_from_file(icon)
    if msgBox.run() == gtk.RESPONSE_OK:
        response = msgBox.value
    else:
        response = None
    msgBox.destroy()
    return response


class Handler:
    def __init__(self, window):
        self.main = window

    def on_wMain_destroy(self, *args):
        gtk.main_quit(*args)

    def on_wMain_delete_event(self, *args):
        gtk.main_quit(*args)

    def on_hpMain_button_press_event(self, *args):
        pass

    def on_double_click(self, *args):
        pass

    def on_tvServers_button_press_event(self, *args):
        pass

    def on_tvServers_row_activated(self, widget, *args):
        if not self.main.treeModel.iter_has_child(widget.get_selection().get_selected()[1]):
            selected = widget.get_selection().get_selected()[1]
            host = self.main.treeModel.get_value(selected, 1)
            self.main.addTab(self.main.nbConsole, host)

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

    def on_btnDel_clicked(self, widget, *args):
        if self.main.treeServers.get_selection().get_selected()[1] is not None:
            if not self.main.treeModel.iter_has_child(self.main.treeServers.get_selection().get_selected()[1]):
                #Eliminar solo el nodo
                name = self.main.treeModel.get_value(self.main.treeServers.get_selection().get_selected()[1],0)
                if msgconfirm("%s [%s]?" % (_("Confirma que desea eliminar el host"), name) ) == gtk.RESPONSE_OK:
                    host = self.main.treeModel.get_value(self.main.treeServers.get_selection().get_selected()[1],1)
                    self.conf.groups[host.group].remove(host)
                    self.main.updateTree()
            else:
                #Eliminar todo el grupo
                group = self.get_group(self.treeModel.iter_children(self.treeServers.get_selection().get_selected()[1]))
                if msgconfirm("%s [%s]?" % (_("Confirma que desea eliminar todos los hosts del grupo"), group) ) == gtk.RESPONSE_OK:
                    try:
                        del self.main.groups[group]
                    except:
                        pass
                    for h in dict(self.main.groups):
                        if h.startswith(group+'/'):
                            del self.main.groups[h]
                    self.main.updateTree()
        self.main.conf.writeConfig()

    def on_btnEdit_clicked(self, widget, *args):
        if self.main.treeServers.get_selection().get_selected()[1]is not None and not self.main.treeModel.iter_has_child(self.main.treeServers.get_selection().get_selected()[1]):
            selected = self.main.treeServers.get_selection().get_selected()[1]
            host = self.main.treeModel.get_value(selected,1)
            self.main.init(host.group, host)

    def on_btnAdd_clicked(self, widget, *args):
        group=""
        if self.main.treeServers.get_selection().get_selected()[1] is None:
            selected = self.main.treeServers.get_selection().get_selected()[1]
            group = self.main.get_group(selected)
            if self.main.treeModel.iter_has_child(self.main.treeServers.get_selection().get_selected()[1]):
                selected = self.main.treeServers.get_selection().get_selected()[1]
                group = self.main.treeModel.get_value(selected,0)
                parent_group = self.main.get_group(selected)
                if parent_group != '':
                    group = parent_group + '/' + group
        self.main.init(group)
        self.main.updateTree()

    def on_btnConnect_clicked(self, widget, *args):
        if self.main.treeServers.get_selection().get_selected()[1] is not None:
            if not self.main.treeModel.iter_has_child(self.main.treeServers.get_selection().get_selected()[1]):
                self.on_tvServers_row_activated(self.main.treeServers)
            else:
                selected = self.main.treeServers.get_selection().get_selected()[1]
                group = self.main.treeModel.get_value(selected, 0)
                parent_group = self.main.get_group(selected)
                if parent_group != '':
                    group = parent_group + '/' + group

                for g in self.conf.groups:
                    if g == group or g.startswith(group + '/'):
                        for host in self.conf.groups[g]:
                            self.main.addTab(self.main.nbConsole, host)

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

    def on_cancelbutton1_clicked(self, *args):
        pass

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

    def on_menuFileQuit_activate(self, *args):
        gtk.main_quit(*args)

    def on_showToolbar_toggled(self, widget, *args):
        self.main.set_toolbar_visible(widget.get_active())

    def on_showPanel_toggled(self, widget, *args):
        self.main.set_panel_visible(widget.get_active())
