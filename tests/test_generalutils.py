# -*- coding: utf-8 -*-

import unittest
from context import pt
import pymel.core as pm
ul = pt.core.ul
class TestDoFunctionOn(unittest.TestCase):
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
                rc=True)[0]
            new_obs.append(dup_ob)
        self.selected = pm.selected()
        self.suffix = '_suffix'
        self.test_func = lambda ob:pm.rename( ob, ob.name()+self.suffix )

    def tearDown(self):
        pm.newFile(f=True)

    def test_single_mode(self):
        test_func = ul.do_function_on()(self.test_func)
        def run_test():
            self.assertEqual(
                len(self.selected), len(test_results),
                'return result do not match selected count\n%s to %s'%(
                    len(self.selected), len(test_results)
                ))
            for ob in self.selected:
                self.assertTrue(
                    ob.name().endswith(self.suffix),
                    'result for %s do not match expected'%ob)
        print '\nrun test with select objects'
        test_results = test_func()
        run_test()
        print 'run test with direct feed'
        test_results = []
        for ob in self.selected:
            test_results.append(test_func(ob, cl=True))
        run_test()

    def test_hierachy_mode(self):
        pass


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(GeneralUltisTest)
    # unittest.TextTestRunner(verbosity=2).run(suite)