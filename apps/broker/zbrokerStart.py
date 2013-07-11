from pylabs.InitBase import q
q.application.appname = "zbroker"
q.application.start()

q.core.grid.startBroker()

q.application.stop()
