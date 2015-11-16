import os
import sys

pp_name = "SSH connection manager"
app_version = "1.0"
app_web = "https://github.com/vadimkim/ssh-manager"
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
ERRMSG1 = "Entrada invalida en archivo de configuracion"

ICON_PATH = BASE_PATH + "/icon.png"

domain_name = "sshm-lang"
locale_dir = BASE_PATH + "/lang"
enc_passwd = ""