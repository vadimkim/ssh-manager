import gtk


class EntryDialog(gtk.Dialog):
    def __init__(self, title, message, default_text='', modal=True, mask=False):
        gtk.Dialog.__init__(self)
        self.set_title(title)
        self.connect("destroy", self.quit)
        self.connect("delete_event", self.quit)
        if modal:
            self.set_modal(True)
        box = gtk.VBox(spacing=10)
        box.set_border_width(10)
        self.vbox.pack_start(box)
        box.show()
        if message:
            label = gtk.Label(message)
            box.pack_start(label)
            label.show()
        self.entry = gtk.Entry()
        self.entry.set_text(default_text)
        self.entry.set_visibility(not mask)
        box.pack_start(self.entry)
        self.entry.show()
        self.entry.grab_focus()
        button = gtk.Button(stock=gtk.STOCK_OK)
        button.connect("clicked", self.click)
        self.entry.connect("activate", self.click)
        button.set_flags(gtk.CAN_DEFAULT)
        self.action_area.pack_start(button)
        button.show()
        button.grab_default()
        button = gtk.Button(stock=gtk.STOCK_CANCEL)
        button.connect("clicked", self.quit)
        button.set_flags(gtk.CAN_DEFAULT)
        self.action_area.pack_start(button)
        button.show()
        self.ret = None

    def quit(self, w=None, event=None):
        self.hide()
        self.destroy()

    def click(self, button):
        self.value = self.entry.get_text()
        self.response(gtk.RESPONSE_OK)
