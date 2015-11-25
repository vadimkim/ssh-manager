import sys
import gtk
import pango
import gobject
import UiHelper
from HostUtils import Host


class Whost:
    def __init__(self, window):
        self.main = window
        self.wHost = self.main.builder.get_object("wHost")
        self.groups = self.main.conf.groups
        self.treeModel = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING,
                                       gobject.TYPE_STRING)
        self.treeTunel = self.main.builder.get_object("treeTunel")
        self.cmbGroup = self.main.builder.get_object("cmbGroup")
        self.txtName = self.main.builder.get_object("txtName")
        self.txtDescription = self.main.builder.get_object("txtDescription")
        self.txtHost = self.main.builder.get_object("txtHost")
        self.cmbType = self.main.builder.get_object("cmbType")
        self.txtUser = self.main.builder.get_object("txtUser")
        self.txtPass = self.main.builder.get_object("txtPassword")
        self.txtPrivateKey = self.main.builder.get_object("txtPrivateKey")
        self.btnBrowse = self.main.builder.get_object("btnBrowse")
        self.txtPort = self.main.builder.get_object("txtPort")
        self.chkDynamic = self.main.builder.get_object("chkDynamic")
        self.txtLocalPort = self.main.builder.get_object("txtLocalPort")
        self.txtRemoteHost = self.main.builder.get_object("txtRemoteHost")
        self.txtRemotePort = self.main.builder.get_object("txtRemotePort")
        self.txtComamnds = self.main.builder.get_object("txtCommands")
        self.chkComamnds = self.main.builder.get_object("chkCommands")
        self.chkKeepAlive = self.main.builder.get_object("chkKeepAlive")
        self.txtKeepAlive = self.main.builder.get_object("txtKeepAlive")
        self.btnFColor = self.main.builder.get_object("btnFColor")
        self.btnBColor = self.main.builder.get_object("btnBColor")
        self.chkX11 = self.main.builder.get_object("chkX11")
        self.chkAgent = self.main.builder.get_object("chkAgent")
        self.chkCompression = self.main.builder.get_object("chkCompression")
        self.txtCompressionLevel = self.main.builder.get_object("txtCompressionLevel")
        self.txtExtraParams = self.main.builder.get_object("txtExtraParams")
        self.chkLogging = self.main.builder.get_object("chkLogging")
        self.cmbBackspace = self.main.builder.get_object("cmbBackspace")
        self.cmbDelete = self.main.builder.get_object("cmbDelete")
        self.cmbType.set_active(0)
        self.cmbBackspace.set_active(0)
        self.cmbDelete.set_active(0)

        # initialization
        # self.cmbGroup.get_model().clear()  TODO check how to clear model
        model = self.cmbGroup.get_model
        for group in self.groups:
            self.cmbGroup.append_text(group)
        self.isNew = True

        # buf = self.txtComamnds.get_buffer()
        # buf.create_tag('DELAY1', style=pango.STYLE_ITALIC, foreground='darkgray')
        # buf.create_tag('DELAY2', style=pango.STYLE_ITALIC, foreground='cadetblue')
        # buf.connect("changed", self.update_texttags)

        self.treeTunel.set_model(self.treeModel)
        column = gtk.TreeViewColumn(_("Local"), gtk.CellRendererText(), text=0)
        self.treeTunel.append_column(column)
        column = gtk.TreeViewColumn(_("Host"), gtk.CellRendererText(), text=1)
        self.treeTunel.append_column(column)
        column = gtk.TreeViewColumn(_("Remoto"), gtk.CellRendererText(), text=2)
        self.treeTunel.append_column(column)

    # -- Whost custom methods {
    def init(self, group, host=None):
        self.wHost.show_all()
        # self.cmbGroup.get_child().set_text(group) TODO replace
        if host is None:
            self.isNew = True
            self.wHost.set_title("Add host")
            return

        self.isNew = False
        self.oldGroup = group
        self.txtName.set_text(host.name)
        self.oldName = host.name
        self.txtDescription.set_text(host.description)
        self.txtHost.set_text(host.host)
        i = self.cmbType.get_model().get_iter_first()
        while i != None:
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
            if t != "":
                tun = t.split(":")
                tun.append(t)
                self.treeModel.append(tun)
        self.txtCommands.set_sensitive(False)
        self.chkCommands.set_active(False)
        if host.commands != '' and host.commands != None:
            self.txtCommands.get_buffer().set_text(host.commands)
            self.txtCommands.set_sensitive(True)
            self.chkCommands.set_active(True)
        use_keep_alive = host.keep_alive != '' and host.keep_alive != '0' and host.keep_alive != None
        self.txtKeepAlive.set_sensitive(use_keep_alive)
        self.chkKeepAlive.set_active(use_keep_alive)
        self.txtKeepAlive.set_text(host.keep_alive)
        if host.font_color != '' and host.font_color != None and host.back_color != '' and host.back_color != None:
            self.get_widget("chkDefaultColors").set_active(False)
            self.btnFColor.set_sensitive(True)
            self.btnBColor.set_sensitive(True)
            fcolor = host.font_color
            bcolor = host.back_color
        else:
            self.get_widget("chkDefaultColors").set_active(True)
            self.btnFColor.set_sensitive(False)
            self.btnBColor.set_sensitive(False)
            fcolor = "#FFFFFF"
            bcolor = "#000000"

        self.btnFColor.set_color(gtk.gdk.Color(fcolor))
        self.btnBColor.set_color(gtk.gdk.Color(bcolor))

        m = self.btnFColor.get_colormap()
        color = m.alloc_color("red")
        style = self.btnFColor.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = color
        self.btnFColor.set_style(style)
        self.btnFColor.queue_draw()

        self.btnFColor.selected_color = fcolor
        self.btnBColor.selected_color = bcolor
        self.chkX11.set_active(host.x11)
        self.chkAgent.set_active(host.agent)
        self.chkCompression.set_active(host.compression)
        self.txtCompressionLevel.set_text(host.compressionLevel)
        self.txtExtraParams.set_text(host.extra_params)
        self.chkLogging.set_active(host.log)
        self.cmbBackspace.set_active(host.backspace_key)
        self.cmbDelete.set_active(host.delete_key)
        self.update_texttags()

    def update_texttags(self, *args):
        buf = self.txtCommands.get_buffer()
        text_iter = buf.get_start_iter()
        buf.remove_all_tags(text_iter, buf.get_end_iter())
        while True:
            found = text_iter.forward_search("##D=", 0, None)
            if not found:
                break
            start, end = found
            n = end.copy()
            end.forward_line()
            if buf.get_text(n, end).rstrip().isdigit():
                buf.apply_tag_by_name("DELAY1", start, n)
                buf.apply_tag_by_name("DELAY2", n, end)
            text_iter = end

    # -- Whost custom methods }

    # -- Whost.on_okbutton1_clicked {
    def on_okbutton1_clicked(self, widget, *args):
        group = self.cmbGroup.get_active_text().strip()
        name = self.txtName.get_text().strip()
        description = self.txtDescription.get_text().strip()
        host = self.txtHost.get_text().strip()
        ctype = self.cmbType.get_active_text().strip()
        user = self.txtUser.get_text().strip()
        password = self.txtPass.get_text().strip()
        private_key = self.txtPrivateKey.get_text().strip()
        port = self.txtPort.get_text().strip()
        buf = self.txtCommands.get_buffer()
        commands = buf.get_text(buf.get_start_iter(),
                                buf.get_end_iter()).strip() if self.chkCommands.get_active() else ""
        keepalive = self.txtKeepAlive.get_text().strip()
        if self.get_widget("chkDefaultColors").get_active():
            fcolor = ""
            bcolor = ""
        else:
            fcolor = self.btnFColor.selected_color
            bcolor = self.btnBColor.selected_color

        x11 = self.chkX11.get_active()
        agent = self.chkAgent.get_active()
        compression = self.chkCompression.get_active()
        compressionLevel = self.txtCompressionLevel.get_text().strip()
        extra_params = self.txtExtraParams.get_text()
        log = self.chkLogging.get_active()
        backspace_key = self.cmbBackspace.get_active()
        delete_key = self.cmbDelete.get_active()

        if ctype == "":
            ctype = "ssh"
        tunnel = ""

        if ctype == "ssh":
            for x in self.treeModel:
                tunnel = '%s,%s' % (x[3], tunnel)
            tunnel = tunnel[:-1]

        # Validar datos
        if group == "" or name == "" or (host == "" and ctype != 'local'):
            UiHelper.message_box(_("Los campos grupo, nombre y host son obligatorios"))
            return

        if not (port and port.isdigit() and 1 <= int(port) <= 65535):
            UiHelper.message_box(_("Puerto invalido"))
            return

        host = Host(group, name, description, host, user, password, private_key, port, tunnel, ctype, commands,
                    keepalive, fcolor, bcolor, x11, agent, compression, compressionLevel, extra_params, log,
                    backspace_key, delete_key)

        try:
            # Guardar
            if not self.groups.has_key(group):
                self.groups[group] = []

            if self.isNew:
                for h in self.groups[group]:
                    if h.name == name:
                        UiHelper.message_box("%s [%s] %s [%s]" % (_("El nombre"), name, _("ya existe para el grupo"), group))
                        return
                # agregar host a grupo
                self.groups[group].append(host)
            else:
                if self.oldGroup != group:
                    # revisar que no este el nombre en el nuevo grupo
                    if not self.groups.has_key(group):
                        self.groups[group] = [host]
                    else:
                        for h in self.groups[group]:
                            if h.name == name:
                                UiHelper.message_box("%s [%s] %s [%s]" % (_("El nombre"), name, _("ya existe para el grupo"), group))
                                return
                        self.groups[group].append(host)
                        for h in self.groups[self.oldGroup]:
                            if h.name == self.oldName:
                                self.groups[self.oldGroup].remove(h)
                                break
                else:
                    if self.oldName != name:
                        for h in self.groups[self.oldGroup]:
                            if h.name == name:
                                UiHelper.message_box("%s [%s] %s [%s]" % (_("El nombre"), name, _("ya existe para el grupo"), group))
                                return
                        for h in self.groups[self.oldGroup]:
                            if h.name == self.oldName:
                                index = self.groups[self.oldGroup].index(h)
                                self.groups[self.oldGroup][index] = host
                                break
                    else:
                        for h in self.groups[self.oldGroup]:
                            if h.name == self.oldName:
                                index = self.groups[self.oldGroup].index(h)
                                self.groups[self.oldGroup][index] = host
                                break
        except:
            UiHelper.message_box("%s [%s]" % (_("Error al guardar el host. Descripcion"), sys.exc_info()[1]))

        global wMain
        wMain.updateTree()
        wMain.write_config()

        self.get_widget("wHost").destroy()

    # -- Whost.on_okbutton1_clicked }

    # -- Whost.on_cmbType_changed {
    def on_cmbType_changed(self, widget, *args):
        is_local = widget.get_active_text() == "local"
        self.txtUser.set_sensitive(not is_local)
        self.txtPassword.set_sensitive(not is_local)
        self.txtPort.set_sensitive(not is_local)
        self.txtHost.set_sensitive(not is_local)
        self.txtExtraParams.set_sensitive(not is_local)

        if widget.get_active_text() == "ssh":
            self.get_widget("table2").show_all()
            self.txtKeepAlive.set_sensitive(True)
            self.chkKeepAlive.set_sensitive(True)
            self.chkX11.set_sensitive(True)
            self.chkAgent.set_sensitive(True)
            self.chkCompression.set_sensitive(True)
            self.txtCompressionLevel.set_sensitive(self.chkCompression.get_active())
            self.txtPrivateKey.set_sensitive(True)
            self.btnBrowse.set_sensitive(True)
            port = "22"
        else:
            self.get_widget("table2").hide_all()
            self.txtKeepAlive.set_text('0')
            self.txtKeepAlive.set_sensitive(False)
            self.chkKeepAlive.set_sensitive(False)
            self.chkX11.set_sensitive(False)
            self.chkAgent.set_sensitive(False)
            self.chkCompression.set_sensitive(False)
            self.txtCompressionLevel.set_sensitive(False)
            self.txtPrivateKey.set_sensitive(False)
            self.btnBrowse.set_sensitive(False)
            port = "23"
            if is_local:
                self.txtUser.set_text('')
                self.txtPassword.set_text('')
                self.txtPort.set_text('')
                self.txtHost.set_text('')
        self.txtPort.set_text(port)

    # -- Whost.on_cmbType_changed }

    # -- Whost.on_chkKeepAlive_toggled {
    def on_chkKeepAlive_toggled(self, widget, *args):
        if (widget.get_active()):
            self.txtKeepAlive.set_text('120')
        else:
            self.txtKeepAlive.set_text('0')
        self.txtKeepAlive.set_sensitive(widget.get_active())

    # -- Whost.on_chkKeepAlive_toggled }

    # -- Whost.on_chkCompression_toggled {
    def on_chkCompression_toggled(self, widget, *args):
        self.txtCompressionLevel.set_text('')
        self.txtCompressionLevel.set_sensitive(widget.get_active())

    # -- Whost.on_chkCompression_toggled }


    # -- Whost.on_chkDynamic_toggled {
    def on_chkDynamic_toggled(self, widget, *args):
        self.txtRemoteHost.set_sensitive(not widget.get_active())
        self.txtRemotePort.set_sensitive(not widget.get_active())

    # -- Whost.on_chkDynamic_toggled }

    # -- Whost.on_btnAdd_clicked {
    def on_btnAdd_clicked(self, widget, *args):
        local = self.txtLocalPort.get_text().strip()
        host = self.txtRemoteHost.get_text().strip()
        remote = self.txtRemotePort.get_text().strip()

        if self.chkDynamic.get_active():
            host = '*'
            remote = '*'

        # Validar datos del tunel
        if host == "":
            UiHelper.message_box(_("Debe ingresar host remoto"))
            return

        for x in self.treeModel:
            if x[0] == local:
                UiHelper.message_box(_("Puerto local ya fue asignado"))
                return

        tunel = self.treeModel.append([local, host, remote, '%s:%s:%s' % (local, host, remote)])

    # -- Whost.on_btnAdd_clicked }

    # -- Whost.on_btnDel_clicked {
    def on_btnDel_clicked(self, widget, *args):
        if self.treeTunel.get_selection().get_selected()[1] != None:
            self.treeModel.remove(self.treeTunel.get_selection().get_selected()[1])

    # -- Whost.on_btnDel_clicked }

    # -- Whost.on_chkCommands_toggled {
    def on_chkCommands_toggled(self, widget, *args):
        self.txtCommands.set_sensitive(widget.get_active())

    # -- Whost.on_chkCommands_toggled }

    # -- Whost.on_btnBColor_clicked {
    def on_btnBColor_clicked(self, widget, *args):
        widget.selected_color = widget.get_color().to_string()

    # -- Whost.on_btnBColor_clicked }

    # -- Whost.on_chkDefaultColors_toggled {
    def on_chkDefaultColors_toggled(self, widget, *args):
        self.btnFColor.set_sensitive(not widget.get_active())
        self.btnBColor.set_sensitive(not widget.get_active())

    # -- Whost.on_chkDefaultColors_toggled }

    # -- Whost.on_btnFColor_clicked {
    def on_btnFColor_clicked(self, widget, *args):
        widget.selected_color = widget.get_color().to_string()

    # -- Whost.on_btnFColor_clicked }

    # -- Whost.on_btnBrowse_clicked {
    def on_btnBrowse_clicked(self, widget, *args):
        global wMain
        filename = UiHelper.show_open_dialog(parent=wMain.wMain, title=_("Abrir"), action=gtk.FILE_CHOOSER_ACTION_OPEN)
        if filename is not None:
            self.txtPrivateKey.set_text(filename)
            # -- Whost.on_btnBrowse_clicked }
