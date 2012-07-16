#!/usr/bin/env python
# coding:utf-8
import os
import sys
from optparse import OptionParser
from string import lowercase
import thread
from prettytable import PrettyTable


__author__ = 'xiongharry'

def log(msg):
    print msg
    thread.start_new(os.system, ('say %s' % msg.encode('utf-8'), ))

def num2string(num):
    numbers = []

    if num == 0:
        return 'a'

    while num:
        num, remain = divmod(num, 26)
        numbers.insert(0, lowercase[remain])

    return ''.join(numbers)

class Server(object):
    def __init__(self, name, host, version=2, user='root', desc=''):
        self.name = name
        self.host = host
        self.version = version
        self.user = user
        self.desc = desc

class HarryServer(object):
    def __init__(self):
        self.servers = self.get_servers()

    def check(self):
        hasServers = len(self.servers) > 0
        return hasServers

    def get_servers(self):
        def ip_key(server):
            ip = server.host
            x = [256*256*256, 256*256, 256, 1]
            return sum(a * int(b) for a, b in zip(x, ip.split('.')))

        config_file = os.path.expanduser('~/.harry_servers')
        if not os.path.exists(config_file):
            open(config_file, 'w').write(
            """# [user@]host name description
# example:
# 1.2.3.4 dev  the dev server
# harry@1.2.3.5 harry_dev harry's dev server

# tips:
#  Use ssh-copy-id to deploy your public key
""")
            return []

        servers = []
        for line in open(config_file):
            if line.startswith('#'):
                continue

            values = line.strip().split()
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

    def list(self, servers=None):
        if not servers:
            servers = self.servers
        t = PrettyTable(['Order', 'Name', 'User', 'HOST', 'Ver', 'Desc'])
        t.align = "l"

        for i, s  in enumerate(servers):
            t.add_row([num2string(i), s.name, s.user, s.host, str(s.version), s.desc])
        print t

    def search(self, key):
        key = key.lower()
        servers = []
        for server in self.servers:
            if key in server.name.lower() or key in server.host.lower() \
                or key in server.desc.lower():
                servers.append(server)

        self.list(servers)

    def ssh(self, host, user=None):
        server = self.get(host)

        if not server:
            return

        if user:
            server['user'] = user

        log(u'连接:%s' % host)
        print '{name}\t{user}@{host}\t{desc}'.format(
                name = server.name,
                user = server.user,
                host = server.host,
                desc = server.desc)

        if server.version == 1:
            os.system('ssh -1 %s@%s' % (server.user, server.host))
        elif server.version == 2:
            os.system('ssh %s@%s' % (server.user, server.host))
        else:
            sys.exit(-1)

    def get(self, name):
        for i, server in enumerate(self.servers):
            if server.host == name or server.name == name or num2string(i) == name:
                return server

    def add(self, server):
        servers = self.get_servers()
        for s in servers:
            if s.host == server.host:
                print 'Host:%s@%s has alredy been added!' % (server.user, server.host)
                return
        if server.version == 1:
            os.system("cat ~/.ssh/identity.pub | ssh -1 %s@%s 'mkdir ~/.ssh; cat >> ~/.ssh/authorized_keys'" % (server.user, server.host))
        elif server.version == 2:
            os.system('ssh-copy-id %s@%s' % (server.user, server.host))
        else:
            sys.exit(-1)
        self.append_server(server)

    def deploy(self, server, pub_key):
        if not pub_key.startswith('/'):
            pub_key = os.path.join(os.getcwd(), pub_key)

        if not os.path.exists(pub_key):
            print u'无效pub_key'
            return

        print 'Deploying to: %s@%s' % (server.user, server.host)
        os.system("cat %s | ssh  %s@%s 'mkdir ~/.ssh; cat >> ~/.ssh/authorized_keys'" %
                  (pub_key, server.user, server.host))

    def rewrite(self, config_file=None):
        for server in self.get_servers():
            self.append_server(server, config_file)

    def append_server(self, server, config_file=None):
        if not config_file:
            config_file = os.path.expanduser('~/.harry_servers')
        f = open(config_file, "a")
        if server.user == 'root':
            f.write("%s\t\t%d\t\t%s\t\t%s\n" % (server.host, server.version, server.name, server.desc))
        else:
            f.write("%s@%s\t\t%d\t\t%s\t\t%s\n" % (server.user, server.host, server.version, server.name, server.desc))
        f.close()

def get_options():
    usage = """
 1. log to server:
    %prog [order|host|name]
 2. add new server:
    %prog -a HOST -n NAME [-d DESC]
    """

    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--add", action="store", type="string", dest="host", 
            help=u"add new host")
    parser.add_option("-u", "--user", action="store", type="string", dest="user", 
            default="root", help=u"username default:root")
    parser.add_option("-n", "--name", action="store", type="string", dest="name",
            help=u"Server name")
    parser.add_option("-d", "--desc", action="store", type="string", dest="desc",
            default="", help=u"Server description")
    parser.add_option("-s", "--search", action="store", type="string", dest="search",
            default="", help=u"Search host")
    parser.add_option("-r", "--rewrite", action="store", type="string", dest="rewrite",
            default="", help=u"Search host")
    parser.add_option("-p", "--deploy", action="store", type="string", dest="deploy_file",
            default="", help=u"deploy ssh key")
    parser.add_option("-v", "--version", action="store", type="int", dest="version", 
            default="2", help=u"ssh version")
    (options, args) = parser.parse_args()
    return options, args

def main():
    h = HarryServer()
    options, args = get_options()

    if options.host:
        if not options.name:
            print "When adding host, name is required!"
            return
        s = Server(options.name, options.host, options.version, options.user, options.desc)
        h.add(s)
        return

    if options.search:
        h.search(options.search)
        return

    if options.rewrite:
        h.rewrite(options.rewrite)
        return

    if not len(args):
        h.list()
        return

    # 发布ssh-key文件
    if options.deploy_file:
        if args[0] == 'all':
            servers = h.get_servers()
        else:
            server = h.get(args[0])
            if not server:
                print u'无效host'
                return
            servers = [server]

        for server in servers:
            if options.user:
                server.user = options.user
            h.deploy(server, options.deploy_file)

        return

    h.ssh(args[0])

if __name__ == '__main__':
    main()
  
