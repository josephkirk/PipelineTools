# -*- coding: utf-8 -*-

import unittest
import PipelineTools.core.general_utils as ul
import pymel.core as pm
reload(ul)
class GeneralUltisTest(unittest.TestCase):
    """Basic test cases."""

    #test decorator
    def test_timeit( self ):
        self.assertTrue( True )

    def test_error_alert( self ):
        self.assertTrue( True )

    def test_do_function_on( self ):
        '''Test do_function_on decorator'''
        print '\nFunction Test:',ul.do_function_on.__name__
        print '-'*10
        def generate_object( count ):
            pm.newFile( f=True )
            new_obs = []
            for i in range(count):
                new_obs.append(pm.polySphere()[0])
            pm.select(new_obs)
            return new_obs
        @ul.do_function_on()
        def test_single_mode( ob ):
            ob.rename( 'testRename' )
            return ob

        @ul.do_function_on( 'hierachy' )
        def test_hierachy_mode( ob ):
            ob.rename(ob.name()+'_operated',ignoreShape=True)
            return ob

        # Testing single mode
        ob_count = 10
        gen_obs = generate_object(ob_count)
        print 'generate object:\n', gen_obs
        test_results = test_single_mode()
        print 'generate result:\n', test_results
        self.assertEqual(gen_obs, test_results)
        print '+testing single mode ... ok'

        # Testing hierachy mode
        gen_obs = generate_object(ob_count)

        for id, ob in enumerate(gen_obs[1:]):
            ob.setParent(gen_obs[id])
        gen_obs[6].setParent(gen_obs[0])
        gen_obs[-2].setParent(gen_obs[8])
        dup_obs = pm.duplicate(gen_obs[6],name='dup'+gen_obs[6].name(),rc=True)
        dup_obs[0].setParent(None)
        #gen_obs[-2].setParent(gen_obs[2])
        pm.select(gen_obs[0], r=True)
        pm.select(dup_obs[0], add=True)
        print 'generate object:\n', gen_obs
        test_results = test_hierachy_mode()
        print 'generate result:\n', test_results
        for ob in (gen_obs+dup_obs):
            print ob
            self.assertTrue(ob.name().endswith('_operated'))
            self.assertEqual(ob.name().count('_operated'),1)
        print '+testing hierachy mode ... ok'


    #test utility functions
    def test_get_closest_component(self):
        self.assertTrue(True)

    def test_get_closest_info(self):
        self.assertTrue(True)

    def test_get_node(self):
        self.assertTrue(True)

    def test_get_skin_cluster(self):
        self.assertTrue(True)

    def test_convert_component(self):
        self.assertTrue(True)

    def test_remove_number(self):
        self.assertTrue(True)

    def get_pos_center_from_edge(self):
        self.assertTrue(True)

    def test_get_shape(self):
        self.assertTrue(True)

    #test tool function
    def test_snap_nearest(self):
        self.assertTrue(True)

    def test_convert_edge_to_curve(self):
        self.assertTrue(True)

    def test_reset_tranform(self):
        self.assertTrue(True)

    def test_set_Vray_material(self):
        self.assertTrue(True)

    def test_timeit(self):
        self.assertTrue(True)

    def test_assign_curve_to_hair(self):
        self.assertTrue(True)

    def test_hair_from_curve(self):
        self.assertTrue(True)

    def test_parent_shape(self):
        self.assertTrue(True)

    def test_un_parent_shape(self):
        self.assertTrue(True)

    def test_detach_shape(self):
        self.assertTrue(True)

    def test_mirror_transform(self):
        self.assertTrue(True)

    def test_transfer_material(self):
        self.assertTrue(True)

    def test_set_material(self):
        self.assertTrue(True)

    def test_lock_transform(self):
        self.assertTrue(True)

    def test_add_vray_opensubdiv(self):
        self.assertTrue(True)

    def test_clean_attributes(self):
        self.assertTrue(True)

    def test_find_instances(self):
        self.assertTrue(True)

    def test_set_material(self):
        self.assertTrue(True)

    def test_send_current_file(self):
        self.assertTrue(True)

    def test_send_file(self):
        self.assertTrue(True)

    def test_get_asset_path(self):
        self.assertTrue(True)

    def test_check_dir(self):
        self.assertTrue(True)

    def test_sys_cop(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(GeneralUltisTest)
    # unittest.TextTestRunner(verbosity=2).run(suite)