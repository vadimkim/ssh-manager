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

COPY = ["copy"]
PASTE = ["paste"]
COPY_ALL = ["copy_all"]
SAVE = ["save"]
FIND = ["find"]
CLEAR = ["reset"]
FIND_NEXT = ["find_next"]
FIND_BACK = ["find_back"]
CONSOLE_PREV = ["console_previous"]
CONSOLE_NEXT = ["console_next"]
CONSOLE_1 = ["console_1"]
CONSOLE_2 = ["console_2"]
CONSOLE_3 = ["console_3"]
CONSOLE_4 = ["console_4"]
CONSOLE_5 = ["console_5"]
CONSOLE_6 = ["console_6"]
CONSOLE_7 = ["console_7"]
CONSOLE_8 = ["console_8"]
CONSOLE_9 = ["console_9"]
CONSOLE_CLOSE = ["console_close"]
CONSOLE_RECONNECT = ["console_reconnect"]
CONNECT = ["connect"]
ERRMSG1 = "Entrada invalida en archivo de configuracion"
ERRMSG2 = "Error al conectar con servidor"

ICON_PATH = BASE_PATH + "/icon.png"

domain_name = "sshm-lang"
locale_dir = BASE_PATH + "/lang"