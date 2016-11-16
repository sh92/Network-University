import asyncio
import sys
import time

fileName =  sys.argv[1]
buffer_size=10000

def verifyChecksum(data, checksum):
    sum = 0
    for i in range(0, len(data), 2):
        if i+1 < len(data):
            data16= ord(data[i]) + (ord(data[i+1]) << 8)      
            tempSum= sum +data16
            sum = (tempSum & 0xffff) + (tempSum >> 16)      
    currChk = sum & 0xffff 
    result = currChk & checksum
    if result == 0:
        return True
    else:
        return False

@asyncio.coroutine
def handle_echo(reader, writer):
    with open(fileName, "ab") as f:
        #recv_data = yield from reader.read(buffer_size)
        data = yield from reader.read(buffer_size)
        decoded_data = data.decode('utf-8')
        #checksumSeq= decoded_data[buffer_size:buffer_size+4]
        #if checksumSeq!='':
        #    checksum = int(checksumSeq,16)
        #data = decoded_data[:buf]
        #    if verifyChecksum(data,checksum) ==True:
        f.write(data)
        addr = writer.get_extra_info('peername')
        #print("Received %r from %r" % (data, addr))
        #print("Send: %r" % data)
        writer.write("ok".encode('utf-8'))
        yield from writer.drain()
        print("data received")
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
