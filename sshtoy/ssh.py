#!/usr/bin/env python
# coding:utf-8

import os
import sys
from prettytable import PrettyTable

DEFAULT_CONF_FILE = '~/.sshtoy.conf'

DEFAULT_CONF_TEMPLATE = """
# [user@]host:port version name description
# example:
# root@192.168.1.2:22 2 t1 the test server

# tips:
#  Use "h -a" to  deploy your public key
"""

USAGE = """
1. add a host
    h -a <host> -n <name> -d <description>

    h -a 192.168.1.2 -n t1 -d some test machine

2. login to a remote host
    h <name>|<host>

    h t1
    h 192.168.1.2

3. search hosts
    h -s <name|host|description>

    h -s t
    h -s 168

4. remove a host
    h -x t1
"""

def ip_key(ip):
    x = [256*256*256, 256*256, 256, 1]
    return sum(a * int(b) for a, b in zip(x, ip.split('.')))

def log(msg):
    print msg

class Server(object):
    counter = 0
    def __init__(self, name, host, port=22, version=2, user='root', desc=''):
        self.name = name
        self.host = host
        self.port = port
        self.version = version
        self.user = user
        self.desc = desc
        self.ip_key = ip_key(self.host)

    def ssh(self):
        log(u'connecting: %s@%s' % (self.user, self.host))

        if self.version == 1:
            os.system('ssh -1 %s@%s -p %s' % (self.user, self.host, self.port))
        elif self.version == 2:
            os.system('ssh %s@%s -p %s' % (self.user, self.host, self.port))
        else:
            log(u'Server协议错误 server:[%s]')
            sys.exit(-1)

    @classmethod
    def add(cls, name, host, port, version=2, user='root', desc=''):
        server = cls(name, host, port, version, user, desc)
        servers = cls.load()
        for s in servers:
            if s.name == server.name:
                log('Host: %s with the same name!' % s.simple_str)
                return
            if s == server:
                log('Host: %s has already been added!' % s.simple_str)
                return

        error = int(server.publish())
        if error:
            return

        servers.append(server)
        cls.dump(servers)

    def publish(self, pub_key_file=None):
        log('Deploying to: %s@%s:%s' % (self.user, self.host, self.port))

        if not pub_key_file:
            if self.version == 1:
                pub_key_file = '~/.ssh/identity.pub'
            else:
                pub_key_file = '~/.ssh/id_rsa.pub'

        if not os.path.exists(os.path.expanduser(pub_key_file)):
            log('public key not found.')
            return -1

        cmd = "cat %s | ssh -%s %s@%s -p %s 'if [ ! -d ~/.ssh ]; then echo 'mkdir ~/.ssh'; fi; cat >> ~/.ssh/authorized_keys'" % \
                (pub_key_file, self.version, self.user, self.host, self.port)
        return os.system(cmd)

    def __eq__(self, other):
        return self.host == other.host and self.user == other.user and self.port == other.port

    def __ne__(self, other):
        return not self.__eq__(other)

    def like(self, key):
        return key.lower() in [self.name.lower(), self.host]

    def match(self, pattern):
        for item in [self.name.lower(), self.host, self.desc.lower()]:
            if pattern in item:
                return True

        return False

    @property
    def simple_str(self):
        return u'[{name}] {user}@{host}:{port}'.format(
                                name = self.name,
                                user = self.user,
                                host = self.host,
                                port = self.port).encode('utf-8')

    def __unicode__(self):
        return u'{user}@{host}:{port}\t{version}\t{name}\t{desc}'.format(
                        name = self.name,
                        user = self.user,
                        host = self.host,
                        port = self.port,
                        version = self.version,
                        desc = self.desc)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @classmethod
    def publish_by_keys(cls, pub_key_file, server_keys):
        if not server_keys:
            log('--server_list is required.')

        if not pub_key_file.startswith('/'):
            pub_key_file = os.path.join(os.getcwd(), pub_key_file)

        if not os.path.exists(pub_key_file):
            log('pub key file is not found!')
            return

        if server_keys == '__all__':
            servers = Server.load()
        else:
            servers = []
            for key in server_keys:
                for server in Server.load():
                    if server.like(key):
                        servers.append(server)

        for server in servers:
            server.publish(pub_key_file)

    @classmethod
    def show_list(cls, servers=None):
        if servers is None:
            servers = cls.load()

        t = PrettyTable(['Order', 'Name', 'User', 'HOST', 'PORT', 'Ver', 'Desc'])
        t.align = "l"

        for i, s  in enumerate(servers):
            t.add_row([i, s.name, s.user, s.host, str(s.port), str(s.version), s.desc])

        log(t)


    @classmethod
    def remove(cls, server):
        servers = [s for s in cls.load() if s != server]
        cls.dump(servers)

    @classmethod
    def get(cls, key):
        servers = []
        for server in cls.load():
            if server.like(key):
                servers.append(server)

        if not servers:
            return None

        if len(servers) == 1:
            return servers[0]

        log('multiple servers found, please specify by name!')
        cls.show_list(servers)

    @classmethod
    def search(cls, pattern):
        return [server for server in cls.load() if server.match(pattern)]

    @classmethod
    def write_default_config(cls, config_file=DEFAULT_CONF_FILE):
        config_file = os.path.expanduser(config_file)

        if os.path.exists(config_file):
            log(u'config file exists:%s !' % config_file)
            return

        with open(config_file, 'w') as f:
            f.write(DEFAULT_CONF_TEMPLATE.strip())

    @classmethod
    def load(cls, config_file=DEFAULT_CONF_FILE):
        config_file = os.path.expanduser(config_file)

        if not os.path.exists(config_file):
            cls.write_default_config()

        servers = []
        for line in open(config_file):
            if line.startswith('#'):
                continue

            values = line.decode('utf-8').strip().split()
            if len(values) < 3:
                continue

            if '@' in values[0]:
                user, host= values[0].split('@')
            else:
                user = 'root'
                host = values[0]

            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            else:
                port = 22

            version = int(values[1])
            name = values[2]
            desc = len(values) > 3 and ' '.join(values[3:]) or ''

            servers.append(Server(name, host, port, version, user, desc))
            servers.sort(key=lambda server:server.ip_key)

        return servers

    @classmethod
    def dump(cls, servers):
        config_file = os.path.expanduser(DEFAULT_CONF_FILE)

        with open(config_file, "w") as f:
            f.write(DEFAULT_CONF_TEMPLATE.strip() + '\n')
            for server in servers:
                f.write(str(server) + '\n')