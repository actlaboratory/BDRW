from byte import Byte

class segment:
	def __init__(self, parent = None):
		self.data_list = []
		self.parent = parent

	def addData(self, data: bytes):
		# Python標準のbytesオブジェクトを渡すと、Byteオブジェクトに展開して追加します。
		for d in data:
			b = Byte(d, self)
			self.data_list.append(b)

