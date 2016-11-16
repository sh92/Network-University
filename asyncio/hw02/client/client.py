import asyncio
import sys
import time
import os
from concurrent.futures import ProcessPoolExecutor

filePath = sys.argv[1]
fileSize = os.path.getsize(filePath) 
buffer_size=10000

server_ip ='127.0.0.1'
server_port = 5000

def getChecksum(data):
    sum=0
    for i in range(0, len(data), 2):
        if i+1 < len(data):
            data16= ord(data[i]) + (ord(data[i+1]) << 8) 
            tempSum = sum + data16 
            sum = (tempSum & 0xffff) + (tempSum >> 16)    
    return ~sum & 0xffff

@asyncio.coroutine
def tcp_echo_client(data,loop):
    reader, writer = yield from asyncio.open_connection(server_ip, server_port,loop=loop)
    while True:
        #checksumSeq = "{0:04x}".format(checksum)
        #writer.write(data+checksumSeq.encode('utf-8'))
        writer.write(data)
        d= yield from reader.read(100) 
        decoded_data = d.decode('utf-8')
        print('Received: %r' % decoded_data)
        if(decoded_data == 'ok'):
             break
    writer.close()
    

remain=fileSize
datas = []
with open(filePath, 'rb') as f:
     while True:
          if remain >= buffer_size:
             remain -=buffer_size
             data = f.read(buffer_size)
             datas.append(data)
          else:
             data = f.read(remain)
             datas.append(data)
             break

@asyncio.coroutine
def fetch_all(datas,loop):
    fetches = [asyncio.ensure_future(tcp_echo_client(data,loop)) for data in datas]
    yield from asyncio.gather(*fetches)


start_time = time.time()
loop = asyncio.get_event_loop()
data_len = len(datas)
thread_size = 1000

remain = data_len % thread_size

for i in range(len(datas)):
    loop.run_until_complete(tcp_echo_client(datas[i],loop))
'''
for i in range(0,data_len-thread_size,thread_size):
    print(i, i+thread_size)
    loop.run_until_complete(fetch_all(datas[i:i+thread_size],loop))
    max_i = i+thread_size
print(max_i, data_len)
loop.run_until_complete(fetch_all(datas[max_i:data_len+1],loop))
'''

print('Close the socket')
loop.close()

end_time = time.time()
print("Time elapsed : ", end_time - start_time)
