import hashlib
import sys
fileName = sys.argv[1]

def check_md5(file_path, block_size=8192):
	md5 = hashlib.md5()
	try:
		f=open(file_path ,'rb')
	except IOError as e:
		print(e)
		return
	while True:
		buf = f.read(block_size)
		if not buf:
			break
		md5.update(buf)
	print(md5.hexdigest())

check_md5(fileName)
