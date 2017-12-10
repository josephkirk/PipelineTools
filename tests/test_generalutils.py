# -*- coding: utf-8 -*-
import unittest
from functools import partial
# Initilize Maya
print '='*20, 'Initialize Maya Test Environment','='*20 
from context import pt
from context import pm
ul = pt.core.ul
print '='*20, 'Initialize Finished ', '='*20, '\n'

# Set up & tear down

def setup():
    '''Set up new Scene'''
    pm.newFile(f=True)

def teardown():
    '''Clean up new Scene'''
    pm.newFile(f=True)

# Test Class
class TestDecorator(unittest.TestCase):
    """test decorator"""
    def setUp(self):
        '''Create New Scene with group of hierachy spheres'''
        setup()
        new_obs = []
        collumn = 5
        row = 7
        for i in range(collumn):
            new_ob = pm.polySphere(name='testSphere_%s'%i)[0]
            if len(new_obs):
                #last_ob = new_obs.pop(-1)
                new_ob.setParent(new_obs[-1])
            new_obs.append(new_ob)
        new_obs = [new_obs[0]]
        for i in range(row):
            dup_ob = pm.duplicate(
                new_obs[0],
                name = new_obs[0].name()+'_%s'%(i+1),
                rc=True)[0]
            new_obs.append(dup_ob)
        self.genObRoots = new_obs
        self.selected = pm.ls('testSphere_*', type='transform')
        self.suffix = '_suffix'
        self.test_func = {}
        for m in [
                'single',
                'set',
                'hierachy',
                'oneToOne',
                'last',
                'singleLast',
                'lastType',
                'multiType']:
            self.test_func[m] = partial(ul.do_function_on,mode=m)
        # print '\n','='*50

    def tearDown(self):
        '''Clean up scene'''
        teardown()

    def general_test(self, orig, test_results):
        '''Test for results if results and created nodes are equal'''
        self.assertIsNotNone(
            test_results,
            'return result is empty')
        if test_results:
            self.assertEqual(
                len(orig), len(test_results),
                'return result do not match selected count\n%s objects to %s objects\nMissing:%s\n%s'%(
                    len(orig), len(test_results), str([o for o in orig if o not in test_results]), test_results))

    def test_do_function_on_single_mode(self):
        ''' test Wraper to feed each of selected object'''

        @ul.do_function_on()
        def test_func(ob, newName='newTestSphere'):
            '''function made for testing'''
            pm.rename(ob, newName)
            return ob

        @ul.error_alert
        def run_test(use_wrapper=False):
            '''test function with wrapper'''
            pm.select(self.selected)
            test_wrapper = partial(
                test_func, sl=use_wrapper)
            if use_wrapper:
                test_results = test_wrapper()
            else:
                test_results = map(test_wrapper, pm.selected())
            self.general_test(self.selected, test_results)
            for ob in self.selected:
                self.assertTrue(
                    ob.name().count('newTestSphere'),
                    'result for %s do not match expected'%ob)
            return test_results

        # test with argument feed from wrapper
        wrap_result = run_test(use_wrapper=True)

        self.setUp()

        # test with argument feed through wrapper
        direct_result = run_test()
        self.assertEqual(len(wrap_result), len(direct_result))


    def test_do_function_on_set_mode(self):
        '''test Wraper to feet a set of selected objects'''

        @ul.do_function_on('set')
        def test_func(obs, newName='newTestSphere'):
            '''function made for testing'''
            op_obs = []
            for ob in obs:
                pm.rename(ob, newName)
                op_obs.append(ob)
            return op_obs

        @ul.error_alert
        def run_test(use_wrapper=False):
            '''test function with wrapper'''
            pm.select(self.selected)
            test_wrapper = partial(
                test_func, sl=use_wrapper)
            if use_wrapper:
                test_results = test_wrapper()
            else:
                test_results = test_wrapper(pm.selected())
            self.general_test(self.selected, test_results)
            for ob in self.selected:
                self.assertTrue(
                    ob.name().count('newTestSphere'),
                    'result for %s do not match expected'%ob)

            return test_results

        # test with argument feed from wrapper
        wrap_result = run_test(use_wrapper=True)

        self.setUp()

        # test with argument feed through wrapper
        direct_result = run_test()
        self.assertEqual(len(wrap_result), len(direct_result))

    def test_do_function_on_hierachy_mode(self):
        '''test Wraper to feet a set of selected objects with their childs'''

        @ul.do_function_on('hierachy')
        def test_func(ob, newName='newTestSphere'):
            '''function made for testing'''
            pm.rename(ob, newName)
            return ob

        @ul.error_alert
        def run_test(use_wrapper=False):
            '''test function with wrapper'''
            pm.select(self.genObRoots)
            test_wrapper = partial(
                test_func, sl=use_wrapper)
            if use_wrapper:
                test_results = test_wrapper()
            else:
                test_results = map(
                    test_wrapper,
                    pm.selected() + [oc for o in pm.selected()
                                     for oc in o.getChildren(
                                         type='transform', ad=True)])
            self.general_test(self.selected, test_results)
            for ob in self.selected:
                self.assertTrue(
                    ob.name().count('newTestSphere'),
                    'result for %s do not match expected'%ob)
            return test_results

        # test with argument feed from wrapper
        wrap_result = run_test(use_wrapper=True)

        self.setUp()

        # test with argument feed through wrapper
        direct_result = run_test()
        self.assertEqual(len(wrap_result), len(direct_result))

    def test_do_function_on_oneToOne_mode(self):
        '''test Wraper to feet a set of 2 selected objects'''

        @ul.do_function_on('oneToOne')
        def test_func(ob, target):
            pc = pm.parentConstraint(target, ob)
            return pc
 
        @ul.error_alert
        def run_test(use_wrapper=False):
            '''test function with wrapper'''
            pm.select(self.genObRoots)
            test_wrapper = partial(
                test_func, sl=use_wrapper)
            if use_wrapper:
                test_results = test_wrapper()
            else:
                test_results = [
                    test_wrapper(o, pm.selected()[id+1])
                    for id, o in enumerate(pm.selected())
                    if not id%2]
            self.general_test(pm.ls(type='parentConstraint'), test_results)
            return test_results

        # test with argument feed from wrapper
        wrap_result = run_test(use_wrapper=True)

        self.setUp()

        # test with argument feed through wrapper
        direct_result = run_test()
        self.assertEqual(len(wrap_result), len(direct_result))


    def test_do_function_on_last_mode(self):
        '''test Wraper to feet a set of objects to the last selected '''

        @ul.do_function_on('last')
        def test_func(obs, target):
            result = [pm.parentConstraint(target, ob) for ob in obs]
            return result
 
        @ul.error_alert
        def run_test(use_wrapper=False):
            '''test function with wrapper'''
            pm.select(self.genObRoots)
            test_wrapper = partial(
                test_func, sl=use_wrapper)
            if use_wrapper:
                test_results = test_wrapper()
            else:
                test_results = test_wrapper(self.genObRoots[:-1], self.genObRoots[-1])
            self.general_test(pm.ls(type='parentConstraint'), test_results)
            return test_results

        # test with argument feed from wrapper
        wrap_result = run_test(use_wrapper=True)

        self.setUp()
        # test with argument feed through wrapper
        direct_result = run_test()
        #self.assertEqual(len(wrap_result), len(direct_result))

    def test_do_function_on_lastType_mode(self):
        '''test Wraper to feet multi type set of objects to the last selected type '''

        @ul.do_function_on('lastType', type_filter=['mesh', 'joint'])
        def test_func(meshes, joints):
            results = []
            for geo in meshes:
                pm.select(geo, r=True)
                pm.select(joints, add=True)
                try:
                    pc = pm.skinCluster()
                    results.append(pc)
                except RuntimeError:
                    pass
            return results

        @ul.error_alert
        def run_test(use_wrapper=False):
            '''test function with wrapper'''
            pm.select(cl=True)
            joints = []
            for i in range(5):
                joints.append(pm.joint(p=[0, i, 0]))
            pm.select(self.selected, r=True)
            pm.select(joints, add=True)
            test_wrapper = partial(
                test_func, sl=use_wrapper)
            if use_wrapper:
                test_results = test_wrapper()
            else:
                test_results = [
                    test_wrapper(m,js) for m, js in zip(
                        [o for o in pm.selected() if ul.get_type(o) == 'mesh'],
                        [o for o in pm.selected() if ul.get_type(o) == 'joint'])]
            self.general_test(pm.ls(type='skinCluster'), test_results)
            for skinClter in pm.ls(type='skinCluster'):
                self.general_test(skinClter.getInfluence(), joints)

            return test_results

        # test with argument feed from wrapper
        wrap_result = run_test(use_wrapper=True)

        self.setUp()

        # test with argument feed through wrapper
        #direct_result = run_test()
        #self.assertEqual(len(wrap_result), len(direct_result))

    def test_do_function_on_different_mode(self):
        '''Create Multiple Joint , Locator and OneSphere.
        Select Sphere Vertex accord to the amout of joint.
        After that also select joints and locs'''

        @ul.do_function_on('multiType', type_filter=['joint', 'locator', 'vertex'])
        def test_func(joint, loc, vert):
            print joint, loc ,vert
            paconstraint = pm.parentConstraint(loc, joint)
            uv = vert.getUV()
            mesh = vert.node()
            ppconstraint = pm.pointOnPolyConstraint(
                mesh, loc, mo=False)
            stripname = ul.get_name(mesh.getParent())
            ppconstraint.attr(stripname + 'U0').set(uv[0])
            ppconstraint.attr(stripname + 'V0').set(uv[1])
            return (paconstraint, ppconstraint)

        @ul.error_alert
        def run_test(use_wrapper=False):
            joints = []
            locs = []
            count = len(self.genObRoots)
            for i in range(count):
                pm.select(cl=True)
                joints.append(pm.joint(p=[0, i, 0]))
                loc = pm.spaceLocator()
                locs.append(loc)
            sph = pm.polySphere(radius=10)
            pm.select(cl=True)
            for i in range(count):
                i += 1
                pm.select(sph[0].getShape().vtx[i], add=True)
            pm.select(locs, add=True)
            pm.select(joints, add=True)
            test_wrapper = partial(
                test_func, sl=use_wrapper)
            if use_wrapper:
                test_results = test_wrapper()
            else:
                test_results = test_wrapper(pm.selected())
            self.assertTrue(
                pm.ls(type='parentConstraint'),
                'Joint and Loc did not connect, No Parent Constraint in Scene')
            self.assertTrue(
                pm.ls(type='pointOnPolyConstraint'),
                'Loc did not connect to mesh, no PointOnPoly Constraint in Scene')
            for j, l in zip(joints, locs):
                self.assertTrue(
                    j.inputs(type='parentConstraint'),
                    '%s do not have any Parent Constraint Connection'%j)
                self.assertTrue(
                    l.outputs(type='parentConstraint'),
                    '%s do not have any Parent Constraint Connection'%l)
                self.assertTrue(
                    l.inputs(type='pointOnPolyConstraint'),
                    '%s do not have any Point On Poly Constraint Connection'%l)

            return test_results

        # test with argument feed from wrapper
        wrap_result = run_test(use_wrapper=True)

        self.setUp()
        # test with argument feed through wrapper
        #direct_result = run_test()
        #self.assertEqual(len(wrap_result), len(direct_result))

class TestUtility(unittest.TestCase):
    def test_iter_hierachy(self):
        joints = []
        for i in range(5):
            joints.append(pm.joint(p=[0, i, 0]))
        results = ul.iter_hierachy(joints[0])
        self.assertEqual(
            pm.ls(type='joint'), list(results),
            'results does not match scene.\nScene:\n%s\nResult:\n%s'%(joints, results))

    def test_recurse_functions(self):
        try:
            import os
            import sys
            import shutil
            test_path = os.path.dirname(__file__)
            new_dir_list = []
            dir_root = os.path.abspath(
                os.path.join(test_path, 'dir_root'))
            sub_dirs = [os.path.abspath(
                            os.path.join(dir_root, 'testdir_{:02d}'.format(i+1)))
                        for i in range(6)]
            sub_subdirs = [os.path.abspath(
                            os.path.join(subdir, 'testdir_{:02d}'.format(i+1)))
                        for subdir in sub_dirs]
            new_dir_list = ul.recurse_collect(dir_root,sub_dirs,sub_subdirs)
            for dtr in new_dir_list:
                os.mkdir(dtr)
            new_file_list = []
            for sub_subdir in new_dir_list:
                for i in range(6):
                    file_name = '{}_file_{:02d}.txt'.format(os.path.basename(sub_subdir),i+1)
                    file_path = os.path.abspath(os.path.join(
                        sub_subdir, file_name))
                    newFile = open(file_path,'w+')
                    newFile.close()
                    new_file_list.append(file_name)
            def test_list_branch(_path):
                if os.path.isdir(_path):
                    subpaths = [
                        os.path.join(_path, subpath)
                        for subpath in os.listdir(_path)]
                    return subpaths
            def test_func(_file):
                if os.path.isfile(_file):
                    if _file.endswith('.txt'):
                        return os.path.basename(_file)
            run_test_result = ul.recurse_collect(
                ul.recurse_trees(dir_root, test_list_branch, test_func))
            run_test_result.sort()
            self.assertTrue(run_test_result, 'Result is empty')
            self.assertEqual(
                len(new_file_list), len(run_test_result),
                'Result is not right\nTotalFiles: {} files \nResut: {} files'.format(
                    len(new_file_list),
                    len(run_test_result)))
            self.assertTrue(
                all([i in new_file_list for i in run_test_result]))
            #project_path = pm.workspace.path()
        finally:
            shutil.rmtree(dir_root)


# Load Test
test_cases = [TestUtility, TestDecorator]

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

# Run Test
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(GeneralUltisTest)
    # unittest.TextTestRunner(verbosity=2).run(suite)