#!/usr/bin/env python
#
from __future__ import with_statement
import os
import operator
import sys
import base64
import time
import tempfile
import ConfigParser
import pango
import pyAES
from UiHelper import Handler
from UiHelper import bindtextdomain

try:
    import gtk
    import gobject
    import pygtk
    import gtk.glade
    pygtk.require("2.0")

except:
    print >> sys.stderr, "pygtk 2.0 required"
    sys.exit(1)

try:
    import vte
except:
    error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                              'You must install libvte for python')
    error.run()
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

pp_name = "SSH connection manager"
app_version = "1.0"
app_web = "http://www.kuthulu.com/gcm"
app_fileversion = "1"

BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

SSH_BIN = 'ssh'
TEL_BIN = 'telnet'
SHELL = os.environ["SHELL"]

SSH_COMMAND = BASE_PATH + "/ssh.expect"
CONFIG_FILE = os.getenv("HOME") + "/.gcm/gcm.conf"
KEY_FILE = os.getenv("HOME") + "/.gcm/.gcm.key"

if not os.path.exists(os.getenv("HOME") + "/.gcm"):
    os.makedirs(os.getenv("HOME") + "/.gcm")

HSPLIT = 0
VSPLIT = 1

_COPY = ["copy"]
_PASTE = ["paste"]
_COPY_ALL = ["copy_all"]
_SAVE = ["save"]
_FIND = ["find"]
_CLEAR = ["reset"]
_FIND_NEXT = ["find_next"]
_FIND_BACK = ["find_back"]
_CONSOLE_PREV = ["console_previous"]
_CONSOLE_NEXT = ["console_next"]
_CONSOLE_1 = ["console_1"]
_CONSOLE_2 = ["console_2"]
_CONSOLE_3 = ["console_3"]
_CONSOLE_4 = ["console_4"]
_CONSOLE_5 = ["console_5"]
_CONSOLE_6 = ["console_6"]
_CONSOLE_7 = ["console_7"]
_CONSOLE_8 = ["console_8"]
_CONSOLE_9 = ["console_9"]
_CONSOLE_CLOSE = ["console_close"]
_CONSOLE_RECONNECT = ["console_reconnect"]
_CONNECT = ["connect"]

ICON_PATH = BASE_PATH + "/icon.png"

domain_name = "sshm-lang"
locale_dir = BASE_PATH + "/lang"
bindtextdomain(domain_name, locale_dir)

groups = {}
shortcuts = {}

enc_passwd = ''


# Variables de configuracion
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


## funciones para encryptar passwords - no son muy seguras, pero impiden que los pass se guarden en texto plano
def xor(pw, str1):
    c = 0
    liste = []
    for k in xrange(len(str1)):
        if c > len(pw) - 1:
            c = 0
        fi = ord(pw[c])
        c += 1
        se = ord(str1[k])
        fin = operator.xor(fi, se)
        liste += [chr(fin)]
    return liste


def encrypt_old(passw, string):
    try:
        ret = xor(passw, string)
        s = base64.b64encode("".join(ret))
    except:
        s = ""
    return s


def decrypt_old(passw, string):
    try:
        ret = xor(passw, base64.b64decode(string))
        s = "".join(ret)
    except:
        s = ""
    return s


def encrypt(passw, string):
    try:
        s = pyAES.encrypt(string, passw)
    except:
        s = ""
    return s


def decrypt(passw, string):
    try:
        s = decrypt_old(passw, string) if conf.VERSION == 0 else pyAES.decrypt(string, passw)
    except:
        s = ""
    return s


class Wmain():
    def run(self):
        builder = gtk.Builder()
        builder.set_translation_domain(domain_name)
        builder.add_from_file("gnome-connection-manager.ui")
        builder.connect_signals(Handler())
        wMain = builder.get_object("wMain")
        wMain.show_all()
        gtk.main()


def main():
    w_main = Wmain()
    w_main.run()


if __name__ == "__main__":
    main()
