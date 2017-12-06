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
    print '\n'*2,'='*20, 'Set up new Scene', '='*20
    pm.newFile(f=True)

def teardown():
    pm.newFile(f=True)
    print '\n','='*20, 'Cleanup Scene', '='*20,'\n'


# Test Class
class TestDecorator(unittest.TestCase):
    """test decorator"""
    def setUp(self):
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
        print '\n','='*50

    def tearDown(self):
        teardown()

    def general_test(self, orig, test_results):
        self.assertIsNotNone(
            test_results,
            'return result is empty')
        if test_results:
            self.assertEqual(
                len(orig), len(test_results),
                'return result do not match selected count\n%s objects to %s objects\nMissing:%s'%(
                    len(orig), len(test_results), str([o for o in orig if o not in test_results])
                ))

    def test_do_function_on_single_mode(self):
        def test_func(ob, newName):
            pm.rename(ob, newName)
            return ob
        try:
            pm.select(self.selected)
            test_results = self.test_func['single']()(
                test_func)('newTestSphere', sl=True)
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(self.selected, test_results)
        for ob in self.selected:
            self.assertTrue(
                ob.name().count('newTestSphere'),
                'result for %s do not match expected'%ob)

    def test_do_function_on_single_mode_direct(self):
        def test_func(ob, newName):
            pm.rename(ob, newName)
            return ob
        test_direct_results = []
        for ob in self.selected:
            try:
                result = self.test_func['single']()(
                    test_func)(ob,'newTestSphere')
                test_direct_results.append(result[0])
            except TypeError as why:
                print 'do_function_on did not feed argument to function'
                raise why
            except IndexError as why:
                print 'result return is None'
                raise why
        self.general_test(self.selected, test_direct_results)
        for ob in self.selected:
            self.assertTrue(
                ob.name().count('newTestSphere'),
                'result for %s do not match expected'%ob)

    def test_do_function_on_set_mode(self):
        def test_func(obs, newName):
            newobs = []
            for ob in obs:
                pm.rename(ob, newName)
                newobs.append(ob)
            return newobs
        try:
            pm.select(self.selected)
            test_results = self.test_func['set']()(
                test_func)('newTestSphere', sl=True)
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(self.selected, test_results)
        for ob in self.selected:
            self.assertTrue(
                ob.name().count('newTestSphere'),
                'result for %s do not match expected'%ob)

    def test_do_function_on_set_mode_direct(self):
        def test_func(obs, newName):
            newobs = []
            for ob in obs:
                pm.rename(ob, newName)
                newobs.append(ob)
            return newobs
        try:
            result = self.test_func['set']()(
                test_func)(self.selected, 'newTestSphere')
            test_direct_results = result
        except TypeError as why:
            print 'do_function_on did not feed argument to function'
            raise why
        self.general_test(self.selected, test_direct_results)
        for ob in self.selected:
            self.assertTrue(
                ob.name().count('newTestSphere'),
                'result for %s do not match expected'%ob)

    def test_do_function_on_hierachy_mode(self):
        def test_func(ob, newName):
            pm.rename(ob, newName)
            return ob
        try:
            pm.select(self.genObRoots)
            test_results = self.test_func['hierachy']()(
                test_func)('newTestSphere', sl=True)
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(self.selected, test_results)
        for ob in self.selected:
            self.assertTrue(
                ob.name().count('newTestSphere'),
                'result for %s do not match expected'%ob)

    def test_do_function_on_hierachy_mode_direct(self):
        def test_func(obs, newName):
            newobs = []
            for ob in obs:
                pm.rename(ob, newName)
                newobs.append(ob)
            return newobs
        try:
            test_results = self.test_func['hierachy']()(
                test_func)(self.selected, 'newTestSphere')
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(self.selected, test_results)
        for ob in self.selected:
            self.assertTrue(
                ob.name().count('newTestSphere'),
                'result for %s do not match expected'%ob)

    def test_do_function_on_oneToOne_mode(self):
        def test_func(ob, target):
            pc = pm.parentConstraint(target, ob)
            return ob
        try:
            pm.select(self.genObRoots)
            test_results = self.test_func['oneToOne']()(test_func)(sl=True)
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(pm.ls(type='parentConstraint'), test_results)

    def test_do_function_on_last_mode(self):
        def test_func(obs, target):
            newPC = []
            for ob in obs:
                pc = pm.parentConstraint(target, ob)
                newPC.append(pc)
            return newPC
        try:
            pm.select(self.selected)
            test_results = self.test_func['last']()(test_func)(sl=True)
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(self.selected[:-1], pm.ls(type='parentConstraint'))

    def test_do_function_on_singlelast_mode(self):
        def test_func(ob, target):
            pc = pm.parentConstraint(target, ob)
            return pc
        try:
            pm.select(self.selected)
            test_results = self.test_func['singleLast']()(test_func)(sl=True)
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(pm.ls(type='parentConstraint'), test_results)

    def test_do_function_on_lastType_mode(self):
        def test_func(obs, targets):
            for ob in obs:
                pm.select(ob, r=True)
                pm.select(targets, add=True)
                try:
                    pc = pm.skinCluster()
                    yield pc
                except RuntimeError:
                    pass
        try:
            pm.select(cl=True)
            joints = []
            for i in range(5):
                joints.append(pm.joint(p=[0, i, 0]))
            pm.select(self.selected, r=True)
            pm.select(joints, add=True)
            test_results = self.test_func['lastType'](
                type_filter=['mesh', 'joint'])(test_func)(sl=True)
        except (TypeError, RuntimeError) as why:
            print 'do_function_on did not feed selected object to function'
            raise why
        self.general_test(pm.ls(type='skinCluster'), test_results)
        for skinClter in pm.ls(type='skinCluster'):
            self.general_test(skinClter.getInfluence(), joints)

    def test_do_function_on_different_mode(self):
        '''Create Multiple Joint , Locator and OneSphere.
        Select Sphere Vertex accord to the amout of joint.
        After that also select joints and locs'''
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
        try:
            joints = []
            locs = []
            count = len(self.genObRoots)
            for i in range(count):
                pm.select(cl=True)
                joints.append(pm.joint(p=[0, i, 0]))
                loc = pm.spaceLocator()
                locs.append(loc)
            sph = pm.polySphere(radius=10)
            #print locs
            #pm.select(sph[0].getShape().vtx[1], r=True)
            pm.select(cl=True)
            for i in range(count):
                i+=1
                pm.select(sph[0].getShape().vtx[i], add=True)
            pm.select(locs, add=True)
            pm.select(joints, add=True)
            #print pm.selected()
            test_results = self.test_func['multiType'](
                type_filter=['joint', 'locator', 'vertex'])(test_func)(sl=True)
        except TypeError as why:
            print 'do_function_on did not feed selected object to function'
            raise why
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

class TestUtility(unittest.TestCase):
    def test_iter_hierachy(self):
        joints = []
        for i in range(5):
            joints.append(pm.joint(p=[0, i, 0]))
        results = ul.iter_hierachy(joints[0])
        self.assertEqual(
            pm.ls(type='joint'), list(results),
            'results does not match scene.\nScene:\n%s\nResult:\n%s'%(joints, results))
# Load Test
test_cases = ([TestUtility, TestDecorator,])

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