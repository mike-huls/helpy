import unittest
# from dotenv import load_dotenv
# from config.definitions import ROOT_DIR

class TestCreateConnection(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # load_dotenv(dotenv_path=os.path.join(ROOT_DIR, 'config', 'conf', '.env'))

    def test_isEqual(self):
        """ Create valid SQL SERVER db engine """

        # 1. Arrange
        def function_from_project(a:float, b:float):
            return a * b

        # 2. Act
        result = function_from_project(5, 5)

        # 3. Assert
        self.assertEqual(result, 25)