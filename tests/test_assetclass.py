import pymel.core as pm
from PipelineTools import customclass as cc
import unittest

projectRoot = 'D:/Drive/Work/NS57'
class Character_Test(unittest.TestCase):
    """Basic test cases."""

    def get_character(self):
        self.assertTrue(cc.Character('KG',project_root=projectRoot)),'no Character create'
        return cc.Character('KG',project_root=projectRoot)

if __name__ == '__main__':
    unittest.main()

