from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from myflask.app import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000)#对应flask的端口
IOLoop.instance().start()