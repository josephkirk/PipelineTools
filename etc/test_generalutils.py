# -*- coding: utf-8 -*-

import unittest
import PipelineTools.core.general_utils as ul
import pymel.core as pm
try:
    from importlib import reload
except:
    pass
reload(ul)
class DoFunctionOnTest(unittest.TestCase):
    """Basic test cases."""
    def setUp(self):
        new_obs = []
        collumn = 5
        row = 6
        for i in range(collumn):
            new_ob = pm.polySphere()[0]
            if new_obs:
                new_ob.setParent(new_obs[-1])
            new_obs.append(new_ob)
        new_obs = [new_obs[0]]
        for i in range(row):
            dup_ob = pm.duplicate(
                new_obs[-1],
                name = new_obs[-1].name()+'_i',
                rc=True)
            new_obs.append(dup_ob)
        self.selected = pm.selected()

    def tearDown(self):
        pm.newFile(f=True)

    def test_single_mode(self):
        suffix = '_suffix'
        test_func = lambda ob:pm.rename( ob, ob.name+suffix )
        test_results = ul.do_function_on()( test_func )
        self.assertEqual(
            self.selected, test_results,
            'return result do not match selected count')
        for ob in self.selected:
            self.assertTrue(
                ob.name().endswith(suffix),
                'result for %s do not match expected'%ob)


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(GeneralUltisTest)
    # unittest.TextTestRunner(verbosity=2).run(suite)