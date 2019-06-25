#!/usr/bin/env python
#-*- coding:UTF-8 -*-
import time
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options
from handlers import *
from settings import conf

define("port", default=conf.BINDPORT, help="run on the given port", type=int)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/api/jjb/jobs/update", JJBEntryHandler),
        (r"/api/jjb/jobs/list", JJBEntryHandler),
        (r"/api/jjb/jobs/delete", JJBEntryHandler),
        (r"/api/jjb/jobs/action", JJBActionEntryHandler),
    ], autoreload=True)
    print("server is listen on %s"%(options.port))
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
