#!/usr/bin/env python
# coding:utf-8
import os
import sys
import shelve
import operator
from pprint import pprint
from pty import spawn
from optparse import OptionParser
from string import Template
from string import lowercase

__author__ = 'harry'

class Table:
    def __init__(self,title,headers,rows):
        self.title=title
        self.headers=headers
        self.rows=rows
        self.nrows=len(self.rows)
        self.fieldlen=[]

        ncols=len(headers)

        for i in range(ncols):
            max=0
            for j in rows:
                if len(str(j[i]))>max: max=len(str(j[i]))
            self.fieldlen.append(max)

        for i in range(len(headers)):
            if len(str(headers[i]))>self.fieldlen[i]: self.fieldlen[i]=len(str(headers[i]))


        self.width=sum(self.fieldlen)+(ncols-1)*3+4

    def __str__(self):
        bar="-"*self.width
        title="| "+self.title+" "*(self.width-3-(len(self.title)))+"|"
        out=[bar,title,bar]
        header=""
        for i in range(len(self.headers)):
            header+="| %s" %(str(self.headers[i])) +" "*(self.fieldlen[i]-len(str(self.headers[i])))+" "
        header+="|"
        out.append(header)
        out.append(bar)
        for i in self.rows:
            line=""
            for j in range(len(i)):
                line+="| %s" %(str(i[j])) +" "*(self.fieldlen[j]-len(str(i[j])))+" "
            out.append(line+"|")

        out.append(bar)
        return "\r\n".join(out)

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
        if not hasServers:
            print 'EDIT your configure file to add servers: ~/.harry_servers'

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
        title = 'Servers'
        headers = ['Order', 'Name', 'User', u'HOST', 'Version', u'Description']
        servers = [[num2string(i), s.name, s.user, s.host, s.version, s.desc] for i, s in enumerate(servers)]
        print Table(title, headers, servers)

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

        print 'Conecting to server:'
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
    usage = """usage: %prog [order|host|name]

Tips:
  use ssh-copy-id to deploy your public key"""

    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--add", action="store", type="string", dest="host", 
            help=u"增加服务器")
    parser.add_option("-u", "--user", action="store", type="string", dest="user", 
            default="root", help=u"用户名")
    parser.add_option("-n", "--name", action="store", type="string", dest="name",
            help=u"Server name")
    parser.add_option("-d", "--desc", action="store", type="string", dest="desc",
            default="", help=u"Server description")
    parser.add_option("-s", "--search", action="store", type="string", dest="search",
            default="", help=u"Search host")
    parser.add_option("-r", "--rewrite", action="store", type="string", dest="rewrite",
            default="", help=u"Search host")
    parser.add_option("-v", "--version", action="store", type="int", dest="version", 
            default="2", help=u"ssh version")
    (options, args) = parser.parse_args()
    return options, args

def main():
    h = HarryServer()
    options, args = get_options()

    if not h.check():
        return

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

    h.ssh(args[0])

if __name__ == '__main__':
    main()
  
