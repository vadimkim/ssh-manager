import os
import operator
import pyAES
import base64
import gtk
import sys
import constants as const

try:
    import vte
except:
    error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                              'You must install libvte for python')
    error.run()
    sys.exit(1)


def encrypt_old(passw, string):
    try:
        ret = HostUtils.xor(passw, string)
        s = base64.b64encode("".join(ret))
    except:
        s = ""
    return s


def encrypt(passw, string):
    try:
        s = pyAES.encrypt(string, passw)
    except:
        s = ""
    return s


def load_encryption_key():
    try:
        if os.path.exists(const.KEY_FILE):
            with open(const.KEY_FILE) as f:
                password = f.read()
        else:
            password = ''
        return password
    except IOError:
        print >> sys.stderr, "Error trying to open key_file"


class HostUtils:
    enc_passwd = ''

    def __init__(self):
        self.enc_passwd = load_encryption_key()

    def load_hosts(self, cp, pwd='', version=''):
        groups = {}
        if version == 0:
            self.initialise_encyption_key()
        for section in cp.sections():
            if not section.startswith("host "):
                continue
            try:
                host = self.load_host_from_ini(cp, section, version=version)
                if not groups.has_key(host.group):
                    groups[host.group] = []
                groups[host.group].append(host)
            except:
                print "%s: %s" % (const.ERRMSG1, sys.exc_info()[1])
        return groups

    def initialise_encyption_key(self):
        import random
        x = int(str(random.random())[2:])
        y = int(str(random.random())[2:])
        self.enc_passwd = "%x" % (x * y)
        try:
            with os.fdopen(os.open(const.KEY_FILE, os.O_WRONLY | os.O_CREAT, 0600), 'w') as f:
                f.write(self.enc_passwd)
        except IOError:
            print >> sys.stderr, "Error initialising key_file"

    @staticmethod
    def get_username():
        return os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')

    @staticmethod
    def get_val(cp, section, name, default):
        try:
            return cp.get(section, name) if type(default) != type(True) else cp.getboolean(section, name)
        except:
            return default

    def load_host_from_ini(self, cp, section, pwd='', version=''):
        if pwd == '':
            pwd = self.get_password()
        group = cp.get(section, "group")
        name = cp.get(section, "name")
        host = cp.get(section, "host")
        user = cp.get(section, "user")
        password = self.decrypt(pwd, cp.get(section, "pass"), version)
        description = self.get_val(cp, section, "description", "")
        private_key = self.get_val(cp, section, "private_key", "")
        port = self.get_val(cp, section, "port", "22")
        tunnel = self.get_val(cp, section, "tunnel", "")
        ctype = self.get_val(cp, section, "type", "ssh")
        commands = self.get_val(cp, section, "commands", "").replace('\x00', '\n')
        keepalive = self.get_val(cp, section, "keepalive", "")
        fcolor = self.get_val(cp, section, "font-color", "")
        bcolor = self.get_val(cp, section, "back-color", "")
        x11 = self.get_val(cp, section, "x11", False)
        agent = self.get_val(cp, section, "agent", False)
        compression = self.get_val(cp, section, "compression", False)
        compressionLevel = self.get_val(cp, section, "compression-level", "")
        extra_params = self.get_val(cp, section, "extra_params", "")
        log = self.get_val(cp, section, "log", False)
        backspace_key = int(self.get_val(cp, section, "backspace-key", int(vte.ERASE_AUTO)))
        delete_key = int(self.get_val(cp, section, "delete-key", int(vte.ERASE_AUTO)))
        h = Host(group, name, description, host, user, password, private_key, port, tunnel, ctype, commands, keepalive,
                 fcolor, bcolor, x11, agent, compression, compressionLevel, extra_params, log, backspace_key,
                 delete_key)
        return h

    @staticmethod
    def save_host_to_ini(cp, section, host):
        cp.set(section, "group", host.group)
        cp.set(section, "name", host.name)
        cp.set(section, "description", host.description)
        cp.set(section, "host", host.host)
        cp.set(section, "user", host.user)
        cp.set(section, "pass", encrypt(host.password))
        cp.set(section, "private_key", host.private_key)
        cp.set(section, "port", host.port)
        cp.set(section, "tunnel", host.tunnel_as_string())
        cp.set(section, "type", host.type)
        cp.set(section, "commands", host.commands.replace('\n', '\x00'))
        cp.set(section, "keepalive", host.keep_alive)
        cp.set(section, "font-color", host.font_color)
        cp.set(section, "back-color", host.back_color)
        cp.set(section, "x11", host.x11)
        cp.set(section, "agent", host.agent)
        cp.set(section, "compression", host.compression)
        cp.set(section, "compression-level", host.compressionLevel)
        cp.set(section, "extra_params", host.extra_params)
        cp.set(section, "log", host.log)
        cp.set(section, "backspace-key", host.backspace_key)
        cp.set(section, "delete-key", host.delete_key)

    def get_password(self):
        return self.get_username() + self.enc_passwd

    ## funciones para encryptar passwords - no son muy seguras, pero impiden que los pass se guarden en texto plano
    def xor(self, pw, str1):
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

    def decrypt_old(self, passw, string):
        try:
            ret = self.xor(passw, base64.b64decode(string))
            s = "".join(ret)
        except:
            s = ""
        return s

    def decrypt(self, passw, string, version):
        try:
            s = self.decrypt_old(passw, string) if version == 0 else pyAES.decrypt(string, passw)
        except:
            s = ""
        return s


class Host:
    def __init__(self, *args):
        try:
            self.i = 0
            self.group = self.get_arg(args, None)
            self.name = self.get_arg(args, None)
            self.description = self.get_arg(args, None)
            self.host = self.get_arg(args, None)
            self.user = self.get_arg(args, None)
            self.password = self.get_arg(args, None)
            self.private_key = self.get_arg(args, None)
            self.port = self.get_arg(args, 22)
            self.tunnel = self.get_arg(args, '').split(",")
            self.type = self.get_arg(args, 'ssh')
            self.commands = self.get_arg(args, None)
            self.keep_alive = self.get_arg(args, 0)
            self.font_color = self.get_arg(args, '')
            self.back_color = self.get_arg(args, '')
            self.x11 = self.get_arg(args, False)
            self.agent = self.get_arg(args, False)
            self.compression = self.get_arg(args, False)
            self.compressionLevel = self.get_arg(args, '')
            self.extra_params = self.get_arg(args, '')
            self.log = self.get_arg(args, False)
            self.backspace_key = self.get_arg(args, int(vte.ERASE_AUTO))
            self.delete_key = self.get_arg(args, int(vte.ERASE_AUTO))
        except:
            pass

    def get_arg(self, args, default):
        arg = args[self.i] if len(args) > self.i else default
        self.i += 1
        return arg

    def __repr__(self):
        return "group=[%s],\t name=[%s],\t host=[%s],\t type=[%s]" % (self.group, self.name, self.host, self.type)

    def tunnel_as_string(self):
        return ",".join(self.tunnel)

    def clone(self):
        return Host(self.group, self.name, self.description, self.host, self.user, self.password, self.private_key,
                    self.port, self.tunnel_as_string(), self.type, self.commands, self.keep_alive, self.font_color,
                    self.back_color, self.x11, self.agent, self.compression, self.compressionLevel, self.extra_params,
                    self.log, self.backspace_key, self.delete_key)
