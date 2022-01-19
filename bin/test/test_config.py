import unittest
from data.config import Config
import os

class EmptyConfigTestCase(unittest.TestCase):
    
    def setUp(self) -> None:
        with open('.\\data.ini', 'x') as configFile:
            configFile.write('[TRACKLIST]\n\n[TRACKED]\nsources = \nextensions = \ndestinations = ')
        self.configObject = Config('data.ini')

    def tearDown(self) -> None:
        os.remove('data.ini')

    def test_load(self):
        self.assertEqual(self.configObject.load(), ([], [], [], {}))

    def test_add(self) -> None:
        self.configObject.add("TRACKED", "sources", "C:\\Users\\mallo\\Desktop")
        self.configObject.add("TRACKED", "extensions", ".txt")
        self.configObject.add("TRACKED", "destinations", "C:\\Users\\mallo\\Download")
        
        self.assertEqual(self.configObject.load()[0], ["C:\\Users\\mallo\\Desktop"])
        self.assertEqual(self.configObject.load()[1], [".txt"])
        self.assertEqual(self.configObject.load()[2], ["C:\\Users\\mallo\\Download"])
        self.assertEqual(self.configObject.load()[3], {"C:\\Users\\mallo\\Download": []})

    def test_edit(self) -> None:
        pass

    def test_delete(self) -> None:
        pass

    def test_addKey(self) -> None:
        pass

    def test_editKey(self) -> None:
        pass

    def test_deleteKey(self) -> None:
        pass

    def test_hasChanged(self) -> None:
        pass

    def test_update(self) -> None:
        pass

    def test_saveChanges(self) -> None:
        pass

class UserDefinedConfigTestCase(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()