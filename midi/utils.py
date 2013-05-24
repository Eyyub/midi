# utils.py

import struct

class BooleanizeError(Exception):
  pass

def booleanize(b):
	if b == "True":
		return True
	elif b == "False":
		return False
	else:
		raise BooleanizeError('b is not a boolean : ' + b)

def read_VLV(file):
	value = 0

	value, = struct.unpack('>B', file.read(1))

	if value >> 7 == 0b1:
		value = value & 0x7F
		buffer, = struct.unpack('>B', file.read(1))
		value = value << 7 | (buffer & 0x7F)
		while buffer >> 7 == 0b1:
			buffer, = struct.unpack('>B', file.read(1))
			value = value << 7 | (buffer & 0x7F)
	return value

def write_VLV(value, file):
	if (value >> 7) == 0b0:
		file.write(struct.pack('>B', value))
	else:
		nbOctet = 1 # specifie le nombre d'octet de la vlv
		buffer = value & 0x7F
		value = value >> 7
		while value != 0:
			buffer <<= 8
			buffer = buffer | ((value & 0x7F) | 0x80)
			value = (value >> 7)
			nbOctet += 1
		VLV_array = []
		while nbOctet != 0: 
			VLV_array.append(buffer & 0xFF)
			buffer >>= 8
			nbOctet -= 1
		for b in VLV_array:
			file.write(struct.pack('>B', b))
