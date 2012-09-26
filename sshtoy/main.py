# coding: utf-8
from optparse import OptionParser
from sshtoy.ssh import Server


def get_options():
    usage = """
 1. login to server:
    %prog [host|name]

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
    parser.add_option("-v", "--version", action="store", type="int", dest="version",
            default="2", help=u"ssh version")

    parser.add_option("-s", "--search", action="store", type="string", dest="search_key",
            default="", help=u"Search host")

    parser.add_option("-p", "--publish", action="store", type="string", dest="pub_key_file",
            default="", help=u"deploy ssh key")
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
        Server.add(options.name, options.host, options.version, options.user, options.desc)
        return

    # search by pattern
    if options.search_key:
        servers = Server.search(options.search_key)
        Server.show_list(servers)
        return

    # publish ssh-key file to servers
    if options.pub_key_file:
        Server.publish_by_keys(options.pub_key_file, options.server_list)

    # show list
    if not len(args):
        Server.show_list()
        return

    # login to server
    server = Server.get(args[0])
    if not server:
        print 'no server founded'
        return
    server.ssh()

if __name__ == '__main__':
    main()