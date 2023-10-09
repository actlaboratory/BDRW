class Byte:
	def __init__(self, data, index = 0, parent = None):
		if len(data) != 1:
			raise ValueError("The length of the specified bytes is invalid")
		self.data = data
		self.parent = parent
		self.index = index

	def getByte(self):
		return self.data

	def getStartIndex(self):
		return self.index

	def getHex(self):
		return self.data.hex()

	def getAscii(self):
		if 32 <= ord(self.data) <= 126:
			return chr(ord(self.data))
		else:
			return "."

	def __len__(self):
		return 3

	def __getitem__(self, item):
		if item == 0:
			return str(self.index)
		elif item == 1:
			return self.getHex()
		elif item == 2:
			return self.getAscii()
		return super().__getitem__(item)
