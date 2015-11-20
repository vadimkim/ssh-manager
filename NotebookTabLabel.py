import gtk
import UiHelper


class NotebookTabLabel(gtk.HBox):
    """Notebook tab label with close button.
    """

    def __init__(self, title, owner_, widget_, popup_, conf):
        gtk.HBox.__init__(self, False, 0)

        self.conf = conf
        self.title = title
        self.owner = owner_
        self.eb = gtk.EventBox()
        label = self.label = gtk.Label()
        self.eb.connect('button-press-event', self.popup_menu, label)
        label.set_alignment(0.0, 0.5)
        label.set_text(title)
        self.eb.add(label)
        self.pack_start(self.eb)
        label.show()
        self.eb.show()
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        self.widget = widget_
        self.popup = popup_
        close_btn = gtk.Button()
        close_btn.set_relief(gtk.RELIEF_NONE)
        close_btn.connect('clicked', self.on_close_tab, owner_)
        close_btn.set_size_request(image_w + 7, image_h + 6)
        close_btn.add(close_image)
        self.eb2 = gtk.EventBox()
        self.eb2.add(close_btn)
        self.pack_start(self.eb2, False, False)
        self.eb2.show()
        close_btn.show_all()
        self.is_active = True
        self.show()

    def change_color(self, color):
        self.eb.modify_bg(gtk.STATE_ACTIVE, color)
        self.eb2.modify_bg(gtk.STATE_ACTIVE, color)
        self.eb.modify_bg(gtk.STATE_NORMAL, color)
        self.eb2.modify_bg(gtk.STATE_NORMAL, color)

    def restore_color(self):
        bg = self.label.style.bg
        self.eb.modify_bg(gtk.STATE_ACTIVE, bg[gtk.STATE_ACTIVE])
        self.eb2.modify_bg(gtk.STATE_ACTIVE, bg[gtk.STATE_ACTIVE])
        self.eb.modify_bg(gtk.STATE_NORMAL, bg[gtk.STATE_NORMAL])
        self.eb2.modify_bg(gtk.STATE_NORMAL, bg[gtk.STATE_NORMAL])

    def on_close_tab(self, widget, notebook, *args):
        if self.conf.CONFIRM_ON_CLOSE_TAB and UiHelper.msgconfirm(
                        "%s [%s]?" % (_("Cerrar consola"), self.label.get_text().strip())) != gtk.RESPONSE_OK:
            return True

        self.close_tab(widget)

    def close_tab(self, widget):
        notebook = self.widget.get_parent()
        page = notebook.page_num(self.widget)
        if page >= 0:
            notebook.is_closed = True
            notebook.remove_page(page)
            notebook.is_closed = False
            self.widget.destroy()

    def mark_tab_as_closed(self):
        self.label.set_markup("<span color='darkgray' strikethrough='true'>%s</span>" % (self.label.get_text()))
        self.is_active = False
        if self.conf.AUTO_CLOSE_TAB != 0:
            if self.conf.AUTO_CLOSE_TAB == 2:
                terminal = self.widget.get_parent().get_nth_page(
                    self.widget.get_parent().page_num(self.widget)).get_child()
                if terminal.get_child_exit_status() != 0:
                    return
            self.close_tab(self.widget)

    def mark_tab_as_active(self):
        self.label.set_markup("%s" % (self.label.get_text()))
        self.is_active = True

    def get_text(self):
        return self.label.get_text()

    def popup_menu(self, widget, event, label):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.popup.label = self.label
            if self.is_active:
                self.popup.mnuReopen.hide()
            else:
                self.popup.mnuReopen.show()

            # enable or disable log checkbox according to terminal
            self.popup.mnuLog.set_active(
                hasattr(self.widget.get_child(), "log_handler_id") and self.widget.get_child().log_handler_id != 0)
            self.popup.popup(None, None, None, event.button, event.time)
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 2:
            self.close_tab(self.widget)
