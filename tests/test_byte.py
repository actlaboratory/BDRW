import unittest
from byte import Byte

class testByte(unittest.TestCase):
	def test_getData(self):
		d = Byte(b'\x01')
		self.assertEqual(d.getByte(), b'\x01')

	def test_invalid_length(self):
		with self.assertRaises(ValueError):
			b = Byte(b'\xff12')
		with self.assertRaises(ValueError):
			b = Byte(b'')

	def test_getIndex(self):
		b = Byte(b'\xff')
		self.assertEqual(b.getStartIndex(), 0)

	def test_getHex(self):
		b = Byte(b'\xfb', 0)
		self.assertEqual(b.getHex(), "fb")

	def test_getAscii(self):
		b = Byte(b'\x30', 0)
		self.assertEqual(b.getAscii(), "0")
		b = Byte(B'\x19', 0)
		self.assertEqual(b.getAscii(), ".")
		b = Byte(b'\x7f', 0)
		self.assertEqual(b.getAscii(), ".")

	def test_getLen(self):
		b = Byte(b'\x00')
		self.assertEqual(len(b), 1)

	def test_getitem(self):
		b = Byte(b'\x41', 0)
		self.assertEqual(b[0], "0")
		self.assertEqual(b[1], "41")
		self.assertEqual(b[2], "A")
