import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Start an appserver6")
    parser.add_argument("-p", "--port", default=8000, type=int,
                        help="The port the server should listen on")
    parser.add_argument("-s", "--secret", help="The secret", required=True)
    parser.add_argument("-w", "--workers", default=3, type=int,
                        help="The number of workers")
    parser.add_argument("-d", "--dbtype", choices=["memory", "arakoon",
                                                   "file_system"], default="arakoon",
                        help="The type of key value store that should be used")
    parser.add_argument("--no-messagehandler", dest="messagehandler",
                        action="store_false")

    args = parser.parse_args()
    if args.messagehandler is None:
        messageHandler = False
    else:
        messageHandler = args.messagehandler

    # Importing q before the arg parsing seems to mess up its error handling
    from JumpScale import j
    import JumpScale.portal
    from Appserver6 import Appserver6

    j.application.start("appserver6")

    # Make sure the enumerator is loaded
    j.db.keyvaluestore

    dbtype = j.enumerators.KeyValueStoreType.getByName(args.dbtype)

    server = Appserver6(
        args.port,
        args.secret,
        args.workers,
        messageHandler,
        dbtype=dbtype)
    j.core.portal.runningPortal = server
    j.console.echo("Started application server on port %s" % (args.port))
    server.addActors(applicationName="core", path="actorscore",
                     inPylabsExtensionsDir=True)
    server.start()

    j.application.stop()
