#! /usr/bin/python
from gevent import monkey
#monkey.patch_all()
monkey.patch_socket()
monkey.patch_ssl()
monkey.patch_thread()
monkey.patch_time()

from JumpScale import j
from JumpScale.baselib.alerter.alerts_service import AlertService


if __name__ == '__main__':
    j.application.start("alerts_server")
    AlertService().start()
    j.application.stop()
