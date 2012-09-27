# coding: utf-8
from optparse import OptionParser
from sshtoy.ssh import Server, USAGE


def get_options():
    parser = OptionParser(usage=USAGE)
    parser.add_option("-a", "--add", action="store", type="string", dest="host",
            help=u"add new host")
    parser.add_option("-u", "--user", action="store", type="string", dest="user",
            default="root", help=u"username default:root")
    parser.add_option("-n", "--name", action="store", type="string", dest="name",
            help=u"host alias name")
    parser.add_option("-d", "--desc", action="store", type="string", dest="desc",
            default="", help=u"host description")
    parser.add_option("-p", "--port", action="store", type="int", dest="port",
                default=22, help=u"remote port")
    parser.add_option("-v", "--version", action="store", type="int", dest="version",
            default=2, help=u"ssh version")

    parser.add_option("-x", "--remove", action="store", type="string", dest="remove_name",
                help=u"add new host")

    parser.add_option("-s", "--search", action="store", type="string", dest="pattern",
            default="", help=u"search host")

    parser.add_option("--push", action="store", type="string", dest="pub_key_file",
            default="", help=u"push ssh key to remote hosts")
    parser.add_option("-r", "--server_list", action="store", type="string", dest="server_list",
                default="", help=u"servers to deploy the ssh key. (only used when -p is supplied.)")

    (options, args) = parser.parse_args()

    return options, args

def main():
    options, args = get_options()

    # add host
    if options.host:
        if not options.name:
            print "When adding host, name is required!"
            return
        Server.add(options.name, options.host, options.port, options.version, options.user, options.desc)
        return

    # search by pattern
    if options.pattern:
        servers = Server.search(options.pattern)
        Server.show_list(servers)
        return

    # remove by key
    if options.remove_name:
        server = Server.get(options.remove_name)
        if not server:
            print 'no server founded'
            return
        Server.remove(server)
        return

    # publish ssh-key file to servers
    if options.pub_key_file:
        Server.publish_by_keys(options.pub_key_file, options.server_list.split(','))
        return

    # show list
    if not len(args):
        servers = Server.load()
        if not servers:
            print 'h -h to get help.'
        else:
            Server.show_list(servers)
        return

    # login to server
    server = Server.get(args[0])
    if not server:
        print 'no server founded'
        return
    server.ssh()

if __name__ == '__main__':
    main()