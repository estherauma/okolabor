import unittest
from common.push_id import PushID

class PushIDTestCase(unittest.TestCase):
    def setUp(self):
        self.push_id = PushID()

    def test_next_id(self):
        # Generate two IDs and check if they are different
        id1 = self.push_id.next_id()
        id2 = self.push_id.next_id()
        self.assertNotEqual(id1, id2)

    def test_id_length(self):
        # Generate an ID and check if its length is 20
        unique_id = self.push_id.next_id()
        self.assertEqual(len(unique_id), 20)

if __name__ == '__main__':
    unittest.main()
