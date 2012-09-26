#!/usr/bin/env python
# coding:utf-8

import os
import sys
from prettytable import PrettyTable

DEFAULT_CONF_FILE = '~/.sshtoy.conf'

DEFAULT_CONF_TEMPLATE = """
# [user@]host name description
# example:
# 1.2.3.4 dev  the dev server
# harry@1.2.3.5 harry_dev harry's dev server

# tips:
#  Use ssh-copy-id to deploy your public key
"""

def log(msg):
    print msg

class Server(object):
    counter = 0
    def __init__(self, name, host, version=2, user='root', desc=''):
        self.name = name
        self.host = host
        self.version = version
        self.user = user
        self.desc = desc

    def ssh(self):
        log(u'connecting: %s@%s' % (self.user, self.host))

        if self.version == 1:
            os.system('ssh -1 %s@%s' % (self.user, self.host))
        elif self.version == 2:
            os.system('ssh %s@%s' % (self.user, self.host))
        else:
            log(u'Server协议错误 server:[%s]')
            sys.exit(-1)

    @classmethod
    def add(cls, name, host, version=2, user='root', desc=''):
        server = cls(name, host, version, user, desc)
        servers = cls.load()
        for s in servers:
            if s == server:
                log('Host:%s@%s has alredy been added!' % (s.user, s.host))
                return

        if server.version == 1:
            print("cat ~/.ssh/identity.pub | ssh -1 %s@%s 'mkdir ~/.ssh; cat >> ~/.ssh/authorized_keys'" % (server.user, server.host))
        else:
            print('ssh-copy-id %s@%s' % (server.user, server.host))

        servers.append(server)
        cls.dump(servers)

    def publish(self, pub_key_file):
        log('Deploying to: %s@%s' % (self.user, self.host))
        os.system("cat %s | ssh  %s@%s 'mkdir ~/.ssh; cat >> ~/.ssh/authorized_keys'" %
                  (pub_key_file, self.user, self.host))

    def __eq__(self, other):
        return self.host == other.host and self.user == other.user

    def like(self, key):
        return key.lower() in [self.name.lower(), self.host]

    def match(self, pattern):
        for item in [self.name.lower(), self.host, self.desc.lower()]:
            if pattern in item:
                return True

        return False

    def __unicode__(self):
        return u'{user}@{host}\t{version}\t{name}\t{desc}'.format(
                        name = self.name,
                        user = self.user,
                        host = self.host,
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

        t = PrettyTable(['Order', 'Name', 'User', 'HOST', 'Ver', 'Desc'])
        t.align = "l"

        for i, s  in enumerate(servers):
            t.add_row([i, s.name, s.user, s.host, str(s.version), s.desc])

        log(t)

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
            f.write(settings.DEFAULT_CONF_TEMPLATE.strip())

    @classmethod
    def load(cls, config_file=DEFAULT_CONF_FILE):
        def ip_key(server):
            ip = server.host
            x = [256*256*256, 256*256, 256, 1]
            return sum(a * int(b) for a, b in zip(x, ip.split('.')))

        config_file = os.path.expanduser(config_file)

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

            version = int(values[1])
            name = values[2]
            user = user
            host = host
            desc = len(values) > 3 and ' '.join(values[3:]) or ''

            servers.append(Server(name, host,  version, user, desc))
            servers.sort(key=ip_key)

        return servers

    @classmethod
    def dump(cls, servers):
        config_file = os.path.expanduser(settings.DEFAULT_CONF_FILE)

        with open(config_file, "w") as f:
            for server in servers:
                f.write(str(server) + '\n')