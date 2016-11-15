import asyncio
import sys
import time

fileName =  sys.argv[1]
buffer_size=10000

@asyncio.coroutine
def handle_echo(reader, writer):
    with open(fileName, "ab") as f:
        data = yield from reader.read(buffer_size)
        f.write(data)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))
#        print("Send: %r" % message)
        writer.write(data)
        yield from writer.drain()
        print("Close the client socket")
        writer.close()


loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 5000 , loop=loop)
server = loop.run_until_complete(coro)

print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass


# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
