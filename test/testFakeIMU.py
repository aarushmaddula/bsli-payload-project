import unittest

from src import FakeIMU
from src import IMU

class TestFakeIMU(unittest.TestCase):

    def test(self):
      e = "Hi"
      j = "Hi"
      self.assertEqual(e, j)

if __name__ == '__main__':
    unittest.main()
