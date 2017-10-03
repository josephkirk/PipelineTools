from PipelineTools import utilities as ul
from PipelineTools import riggingMisc as rm
reload(ul)
import string
"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
####misc
#@do_function_on('single')
def offcastshadow(wc='*eyeref*'):
    ob_list = pm.ls(wc,s=True)
    for ob in ob_list:
        eye.castsShadows.set(False)
###Rigging
class FacialGuide(object):
    def __init__(self, name, guide_mesh=None, suffix='loc', gp_suffix='Gp'):
        self._name = name
        self._suffix = suffix
        self._root_suffix = gp_suffix
        self.name = '_'.join([name, suffix])
        self.root_name = '_'.join([self.name, gp_suffix])
        self.constraint_name = '_'.join([self.name,'pointOnPolyConstraint'])
        self.guide_mesh = ul.get_shape(guide_mesh)
        self._get()

    def __call__(self,*args, **kwargs):
        self._create(*args, **kwargs)
        return self.node
    
    def set_guide_mesh(self, guide_mesh):
        if pm.objExists(guide_mesh):
            self.guide_mesh = ul.get_shape(guide_mesh)

    def _create(self, pos=[0, 0, 0], parent=None):
        self.node = pm.spaceLocator(name=self.name)
        if pm.objExists(self.root_name):
            self.root = pm.PyNode(self.root_name)
        else:
            self.root = pm.nt.Transform(name=self.root_name)
        self.node.setParent(self.root)
        self.root.setTranslation(pos, space='world')
        self.root.setParent(parent)

    def set_constraint(self, target = None):
        if all([self.guide_mesh, self.guide_mesh, self.root]):
            pm.delete(self.constraint)
            if target is None:
                target = self.root
            closest_uv = ul.get_closest_component(target, self.guide_mesh)
            self.constraint = pm.pointOnPolyConstraint(
                self.guide_mesh, self.node, mo=False,
                name=self.constraint_name)
            self.constraint.attr(self.guide_mesh.getParent().name()+'U0').set(closest_uv[0])
            self.constraint.attr(self.guide_mesh.getParent().name()+'V0').set(closest_uv[1])
            pm.select(closest_info['Closest Vertex'])
        else:
            pm.error('Please set guide mesh')

    def _get(self):
        self.node = ul.get_node(self.name)
        self.root = ul.get_node(self.root_name)
        self.constraint = ul.get_node(self.constraint_name)
        return self.node

class FacialControl(object):
    def __init__(self, name, suffix='ctl', offset_suffix='offset', root_suffix='Gp'):
        self._name = name
        self._suffix = suffix
        self._offset_suffix = offset_suffix
        self._root_suffix = root_suffix
        self.rename(name)
        self.attr_connect_list = ['translate', 'rotate', 'scale']
        self._get()
    
    def __repr__(self):
        return self.node.name()

    def __call__(self, *args, **kwargs):
        self.create(*args, **kwargs)
        return self.node

    def name(self):
        return self.name

    def rename(self,new_name):
        self.name = '_'.join([new_name, self._suffix])
        self.offset_name = '_'.join([self._name, self._offset_suffix])
        self.root_name = '_'.join([self._name, self._root_suffix])
        try:
            if self.node:
                pm.rename(self.node, self.name)
                print self.node
            if self.offset:
                pm.rename(self.offset, self.offset_name)
                print self.offset
            if self.root:
                pm.rename(self.root, self.root_name)
                print self.root
        except:
            pass

    def create(shape=None, pos=[0,0,0], parent=None, create_offset=True):
        if not self.node:
            self.node = pm.nt.Transform(name=self.name)
        if pm.objExists(shape):
            parent_shape(shape , self.node)
        if not self.offset and create_offset:
            self.offset = pm.nt.Transform(name='_'.join([self.name, 'offset', 'GP']))
            self.offset.setTranslation(self.node, space='world')
            self.node.setParent(self.offset)
        if not self.root:
            self.root = pm.nt.Transform(name='_'.join([self.name, 'GP']))
            self.root.setTranslation(self.node, space='world')
            if self.offset:
                self.offset.setParent(self.root)
            else:
                self.node.setParent(self.root)
            self.root.setParent(parent)

    def set(self, new_node, rename=True):
        if pm.objExists(new_node):
            self.node = pm.PyNode(new_node)
            if rename:
                pm.rename(new_node, self.name)
            self._get()
    def get_output(self):
        results = {}
        for atr in self.attr_connect_list:
            results[atr] = self.node.attr(atr).outputs()
        return results
    def _get(self):
        self.node = ul.get_node(self.name)
        self.offset = ul.get_node(self.offset_name)
        self.root = ul.get_node(self.root_name)
    
    @classmethod
    def Controls(cls, name='jaw',offset_suffix='offset', root_suffix='Gp', suffix='ctl', separator='_'):
        list_all = pm.ls('*%s*%s*'%(name,suffix), type='transform')
        jaw_controls = []
        for ob in list_all:
            if root_suffix not in ob.name():
                ob_name = ob.name().split(separator)
                control =  cls(ob_name[0], offset_suffix=offset_suffix, suffix=suffix, root_suffix=root_suffix)
                jaw_controls.append(control)
        return jaw_controls

class FacialBone(object):
    def __init__(self, name, suffix='bon', offset_suffix='offset', ctl_suffix='ctl', gp_suffix='Gp'):
        self._name = name
        self._suffix = suffix
        self._offset_suffix = offset_suffix
        self._ctl_suffix = ctl_suffix
        self.name = '_'.join([self._name, suffix])
        self.offset_name = '_'.join([self._name, self._offset_suffix, self._suffix])
        self.connect_attrs = [
            'translate',
            'rotate',
            'scale']
        self.control_name = self.name.replace(suffix, ctl_suffix)
        self._get()

    def __str__(self):
        return self.name

    def __call__(self,new_bone=None, pos=[0,0,0], parent=None, create_control=False):
        if pm.objExists(newBone):
            newBone = pm.PyNode(new_bone)
            pm.rename(newBone, self.name)
            self._set(newBone, pos=pos, parent=parent)
        else:
            if self._get():
                self._set(self.bone)
            else:
                newBone = pm.nt.Joint()
                newBone.setTranslation(pos, space='world')
                newBone.setParent(parent)
                self.__call__(newBone=newBone)
        if create_control:
            self.create_control()
        return self.bone

    def create_offset(self, pos=[0,0,0], space='world', reset_pos=False, parent=None):
        boneParent = self.bone.getParent()
        if boneParent and self._offset_suffix in boneParent.name():
            self.offset_bone = boneParent
        elif pm.objExists(self.offset_name):
            self.offset_bone = pm.PyNode(self.offset_name)
            self.offset_bone.setParent(boneParent)
            self.bone.setParent(self.offset_bone)
            reset_transform(self.bone)
        else:
            self.offset_bone = pm.nt.Joint(name=self.offset_name)
            self.bone.setParent(self.offset_bone)
            if reset_pos:
                reset_transform(self.bone)
            self.offset_bone.setTranslation(pos, space=space)
            if parent:
                self.offset_bone.setParent(parent)
            else:
                self.offset_bone.setParent(parent)
        return self.offset_bone

    def create_control(self, shape=None, parent=None):
        pass

    def is_connected(self):
        if self.control:
            connect_state = []
            for atr in self.connect_attrs:
                input = self.bone.attr(atr).inputs()
                if input:
                    if input[0] == self.control:
                        connect = True
                    else:
                        connect = False
                    print '%s connection to %s is %s'%(atr, self.control_name, connect)
                    connect_state.append((atr, connect))
        return connect_state

    def connect(self):
        if self.bone and self.control:
            for atr in self.connect_attrs:
                self.control.attr(atr) >> self.bone.attr(atr)

    def set_control(self, control_ob, rename=True):
        if pm.objExists(control_ob):
            self.control = pm.PyNode(control_ob)
            if rename:
                pm.rename(self.control, self.control_name)
        else:
            self.create_control()
        self.connect()
        self.is_connected()
        return self.control

    def get_control(self):
        self.control = FacialControl(self.control_name)
        return self.control

    def _get(self):
        self.bone = pm.PyNode(self.name) if pm.objExists(self.name) else None
        if self.bone:
            self._set(self.bone)
        self.get_control()
        return self.bone

    def _set(self, bone):
        self.bone = bone
        self.create_offset(
            pos=self.bone.getTranslation(space='world'),
            reset_pos=True)

class FacialEyeRig(object):
    pass

class FacialBonRig(object):
    offset_name = 'offset'
    bone_name = 'bon'
    alphabet = list(string.ascii_uppercase)
    def __init__(self):
        self._joints = {
            'eye':{'Left':alphabet[:4],
                   'SubLeft':alphabet[:4]},
            'eyebrow':{'Left':alphabet[:3]},
            'nose':{'Top':"", 'Left':alphabet[0]},
            'cheek':{'Left':alphabet[:3]},
            'jaw':{'Root':"", 'Top':""},
            'lip':{'Center':alphabet[:2], 'Left':alphabet[:3]},
            'teeth':{'Lower':"", 'Upper':""},
            'tongue':{
                'Root':"",
                'Center':([i+'Root' for i in alphabet[:4]]+alphabet[:4]),
                'Left':alphabet[:4]}}
        self._get()
    def _get(self):
        self.joints = {}
        for name,variations in self._joints.items():
            self.joints[name] = {}
            for variation in variations:
                offset_bon = '_'.join([name+variation, self.offset_name, self.bone_name])
                bon_name = '_'.join([name+variation, self.bone_name])
                try:
                    self.joints[name]['offset'] = pm.PyNode(offset_bon)
                    self.joints[name]['joint'] = pm.PyNode(bon_name)
                except:
                    print offset_bon,' or', bon_name, ' is not exist'
                    raise

class FacialBsRig(object):
    def __init__(self):
        self.facebs_name = 'FaceBaseBS'
        self.control_name = "ctl"
        self.joint_name = 'bon'
        self.bs_names = ['eyebrow', 'eye', 'mouth']
        self.ctl_names = ['brow', 'eye', 'mouth']
        self.direction_name = ['Left', 'Right']
    
    def facectl(self,value=None):
        if value is not None:
            if isinstance(value,list):
                self.ctl_names = value
        self.ctl_fullname = ['_'.joint([ctl_name,'ctl']) for ctl_name in ctl_names]
        self.ctl = []
        def create_bs_ctl():
            pass
        try:
            for ctl_name in self.ctl_fullname:
                ctl = PyNode(ctl)
                self.ctl.append(ctl)
        except:
            create_bs_ctl(ctl)
    def facebs(self,value=None):
        if value is not None:
            self.facebs_name = value
        self.facebs = get_blendshape_target(self.facebs_name)
        if self.facebs:
            self.facebs_def ={}
            self.facebs_def[misc] = []
            for bs in self.facebs[0]:
                for bs_name in bs_def:
                    for direction in direction_name:
                        if bs.startswith(bs_name):
                            if not self.facebs_def.has_key(bs_name):
                                self.facebs_def[bs_name] ={}
                            if bs.endswith(direction[0]):
                                if not self.facebs_def[bs_name].has_key(direction): 
                                    self.facebs_def[bs_name][direction] = []
                                self.facebs_def[bs_name][direction].append(bs)
                            else:
                                self.facebs_def[bs_name] = []
                                self.facebs_def[bs_name].append(bs)
            else:
                self.facebs_def[misc].append(bs)
        else:
            print "no blendShape with name" % self.facebs_name
        return self.facebs_def

    def connect_bs_controller(self):
        facepart = self.facepart_name
        bs_control_name = ["_".join([n, self.control_name])
                           for n in facepart[:3]]
        def create_bs_list(part, bs_name_list, add_dir=False):
            bs_list = [
                '_'.join([part, bs])
                for bs in bs_name_list]
            if add_dir is True:
                bs_list = self.add_direction(bs_list)
            return bs_list
        bs_controller = {}
        eyebrow = facepart[0].replace(facepart[1],'')
        bs_controller[
            '_'.join([eyebrow,self.control_name])
            ] = create_bs_list(
            facepart[0],
            self.eyebs_name[:3],
            True)
        bs_controller[
            '_'.join([facepart[1],self.control_name])
            ] = create_bs_list(
            facepart[1],
            self.eyebs_name[1:],
            True)
        bs_controller[
            '_'.join([facepart[2],self.control_name])
            ] = create_bs_list(
            facepart[2],
            self.mouthbs_name,
        )
        for ctl_name,bs_targets in bs_controller.items():
            for bs_target in bs_targets:
                print '%s.%s >> %s.%s' %(ctl_name,bs_target,self.facebs(),bs_target)
        #print bs_controller

def get_skin_cluster(ob):
    '''return skin cluster from ob, if cannot find raise error'''
    ob_shape = get_shape(ob)
    try:
        shape_connections = ob_shape.listConnections(type=['skinCluster', 'objectSet'])
        for connection in shape_connections:
            if 'skinCluster' in connection.name():
                if type(connection) == pm.nt.SkinCluster:
                    return connection
                try_get_skinCluster = connection.listConnections(type='skinCluster')
                if try_get_skinCluster:
                    return try_get_skinCluster[0]
                else:
                    pm.error('Object have no skin bind')
    except:
        pm.error('Cannot get skinCluster from object')

def get_blendshape_target(
    bsname,
    reset_value=False,
    rebuild=False,
    delete_old=True,
    parent=None,
    offset=0,
    exclude=[], exclude_last=False):
    """get blendShape in scene match bsname 
        misc function:
            bsname : blendShape name or id to search for 
            reset_value : reset all blendShape weight Value 
            rebuild: rebuild all Target
            parent: group all rebuild target under parent
            offset: offset rebuild target in X axis
            exclude: list of exclude blendShape target to rebuild and reset
            exclude_last: exclude the last blendShape target from rebuild and reset"""
    bs_list = pm.ls(type='blendShape')
    if not bs_list:
        return
    if isinstance(bsname,int):
        blendshape = bs_list[bsname]
    else:
        blendshape = pm.PyNode(bsname)
    if blendshape is None:
        return
    target_list = []
    for id,target in enumerate(blendshape.weight):
        target_name = pm.aliasAttr(target,q=True)
        if reset_value is True or rebuild is True:
            if target_name not in exclude:
                target.set(0)
        target_weight = target.get()
        target_list.append((target, target_name, target_weight))
    #print target_list
    if rebuild is True:
        base_ob_node = blendshape.getBaseObjects()[0].getParent().getParent()
        print base_ob_node
        base_ob_name = base_ob_node.name()
        blendshape_name = blendshape.name()
        iter = 1
        target_rebuild_list =[]
        if parent != None and type(parent) is str:
            if pm.objExists(parent):
                pm.delete(pm.PyNode(parent))
            parent = pm.group(name=parent)
        if exclude_last is True:
            target_list[-1][0].set(1)
            target_list = target_list[:-1]
        base_dup = pm.duplicate(base_ob_node,name=base_ob_name+"_rebuild")
        for target in target_list: 
            if target[1] not in exclude:
                target[0].set(1)
                new_target = pm.duplicate(base_ob_node)
                target_rebuild_list.append(new_target)
                pm.parent(new_target, parent)
                pm.rename(new_target, target[1])
                target[0].set(0)
                pm.move(offset*iter ,new_target, moveX=True)
                iter += 1
        pm.select(target_rebuild_list, r=True)
        pm.select(base_dup, add=True)
        pm.blendShape()
        blend_reget = get_blendshape_target(blendshape_name)
        blendshape = blend_reget[0]
        target_list = blend_reget[1]
    return (blendshape,target_list)
#get_blendshape_target(-1, True, True, "MorphTarget", 20, exclude_last=True)
@do_function_on(mode='singlelast')
def skin_weight_filter(ob, joint,min=0.0, max=0.1, select=False):
    '''return vertex with weight less than theshold'''
    skin_cluster = get_skin_cluster(ob)
    ob_shape = get_shape(ob)
    filter_weight = []
    for vtx in ob_shape.vtx:
        weight = pm.skinPercent(skin_cluster, vtx, query=True, transform=joint, transformValue=True)
        #print weight
        if min < weight <= max:
            filter_weight.append(vtx)
    if select:
        pm.select(filter_weight)
    return filter_weight

@do_function_on(mode='single')
def switch_skin_type(ob,type='classis'):
    type_dict = {
        'Classis':0,
        'Dual':1,
        'Blend':2}
    if not get_skin_cluster(ob) and type not in type_dict.keys():
        return
    skin_cluster = get_skin_cluster(ob)
    skin_cluster.setSkinMethod(type_dict[type])
    deform_normal_state = 0 if type_dict[type] is 2 else 1
    skin_cluster.attr('deformUserNormals').set(deform_normal_state)

@do_function_on(mode='doubleType', type_filter=['float3', 'transform', 'joint'])
def skin_weight_setter(component_list, joints_list, skin_value=1.0, normalized=True, hierachy=False):
    '''set skin weight to skin_value for vert in verts_list to first joint,
       other joint will receive average from normalized weight,
       can be use to set Dual Quarternion Weight'''
    def get_skin_weight():
        skin_weight = []
        if normalized:
            skin_weight.append((joints_list[0], skin_value))
            if len(joints_list) > 1:
                skin_normalized = (1.0-skin_value)/(len(joints_list)-1)
                for joint in joints_list[1:]:
                    skin_weight.append((joint, skin_normalized))
            return skin_weight
        for joint in joints_list:
            skin_weight.append((joint,skin_value))
        return skin_weight
    if hierachy:
        child_joint = joints_list[0].listRelatives(allDescendents=True)
        joints_list.extend(child_joint)
        print joints_list

    if any([type(component) is pm.nt.Transform for component in component_list]):
        for component in component_list:
            skin_cluster = get_skin_cluster(component)
            pm.select(component, r=True)
            pm.skinPercent(skin_cluster, transformValue=get_skin_weight())
            print component_list
        pm.select(component_list,joints_list)
    else:
        verts_list = convert_component(component_list)
        skin_cluster = get_skin_cluster(verts_list[0])
        if all([skin_cluster, verts_list, joints_list]):
            pm.select(verts_list)
            pm.skinPercent(skin_cluster, transformValue=get_skin_weight())
            pm.select(joints_list, add=True)
        #print verts_list
        #print skin_weight
        #skin_cluster.setWeights(joints_list,[skin])


@do_function_on(mode='sets', type_filter=['float3'])
def dual_weight_setter(component_list, weight_value=0.0, query=False):
    verts_list = convert_component(component_list)
    shape = verts_list[0].node()
    skin_cluster = get_skin_cluster(verts_list[0])
    if query:
        weight_list = []
        for vert in verts_list:
            for vert in vert.indices():
                weight = skin_cluster.getBlendWeights(shape, shape.vtx[vert])
                weight_list.append((shape.vtx[vert], weight))
        return weight_list
    else:
        for vert in verts_list:
            for vert in vert.indices():
                skin_cluster.setBlendWeights(shape, shape.vtx[vert], [weight_value,weight_value])
        #     print skin_cluster.getBlendWeights(shape, vert)
        #pm.select(verts_list)
        #skin_cluster.setBlendWeights(shape, verts_list, [weight_value,])

@do_function_on(mode='single', type_filter=['float3', 'transform'])
def create_joint(ob_list):
    new_joints = []
    for ob in ob_list:
        if type(ob) == pm.nt.Transform:
            get_pos = ob.translate.get()
        elif type(ob) == pm.general.MeshVertex:
            get_pos = ob.getPosition(space='world')
        elif type(ob) == pm.general.MeshEdge:
            get_pos = get_pos_center_from_edges(ob)
        new_joint = pm.joint(p=get_pos)
        new_joints.append(new_joint)
    for new_joint in new_joints:
        pm.joint(new_joint, edit=True, oj='xyz', sao='yup', ch=True, zso=True)
        if new_joint == new_joints[-1]:
            pm.joint(new_joint, edit=True, oj='none', ch=True, zso=True)

@error_alert
@do_function_on(mode='single')
def insert_joint(joint, num_joint=2):
    og_joint = joint
    joint_child = joint.getChildren()[0] if joint.getChildren() else None
    joint_child.orientJoint('none')
    joint_name = remove_number(joint.name())
    if joint_child:
        distance = joint_child.tx.get()/(num_joint+1)
        while num_joint:
            insert_joint = pm.insertJoint(joint)
            pm.joint(insert_joint, edit=True, co=True, ch=False, p=[distance, 0, 0], r=True)
            joint = insert_joint
            num_joint -= 1
        joint_list = og_joint.listRelatives(type='joint', ad=1)
        joint_list.reverse()
        joint_list.insert(0, og_joint)
        for index, bone in enumerate(joint_list):
            try:
                pm.rename(bone, "%s%02d"%(joint_name[0], index+1))
            except:
                pm.rename(bone, "%s#"%joint_name[0])

@do_function_on(mode='double')
def parent_shape(src, target, delete_src=True):
    '''parent shape from source to target'''
    pm.parent(src.getShape(), target, r=True, s=True)
    if delete_src:
        pm.delete(src)

@do_function_on(mode='single')
def un_parent_shape(ob):
    '''unParent all shape and create new trasnform for each shape'''
    shapeList = ob.listRelatives(type=pm.nt.Shape)
    if shapeList:
        for shape in shapeList:
            newTr = pm.nt.Transform(name=(shape.name()[:shape.name().find('Shape')]))
            newTr.setMatrix(ob.getMatrix(ws=True), ws=True)
            pm.parent(shape, newTr, r=True, s=True)
    if type(ob) != pm.nt.Joint:
        pm.delete(ob)

@do_function_on(mode='double')
def snap_simple(ob1, ob2, worldspace=False, hierachy=False, preserve_child=False):
    '''snap Transform for 2 object'''
    ob1_childs = ob1.listRelatives(type=['joint', 'transform'], ad=1)
    if hierachy:
        ob1_childs.append(ob1)
        ob2_childs = ob2.listRelatives(type=['joint', 'transform'], ad=1)
        ob2_childs.append(ob2)
        for ob1_child, ob2_child in zip(ob1_childs, ob2_childs):
            ob1_child.setMatrix(ob2_child.getMatrix(ws=worldspace), ws=worldspace)
    else:
        ob1_child_old_matrixes = [ob_child.getMatrix(ws=True)
                                  for ob_child in ob1_childs]
        ob1.setMatrix(ob2.getMatrix(ws=worldspace), ws=worldspace)
        if preserve_child:
            for ob1_child, ob1_child_old_matrix in zip(ob1_childs, ob1_child_old_matrixes):
                ob1_child.setMatrix(ob1_child_old_matrix, ws=True)

@do_function_on(mode='double')
def copy_skin_multi(source_skin_grp, dest_skin_grp):
    '''copy skin for 2 identical group hierachy'''
    source_skins = source_skin_grp.listRelatives(type='transform', ad=1)
    dest_skins = dest_skin_grp.listRelatives(type='transform', ad=1)
    if len(dest_skins) == len(source_skins):
        print '---Copying skin from %s to %s---'%(source_skin_grp, dest_skin_grp)
        for skinTR, dest_skinTR in zip(source_skins, dest_skins):
            if skinTR.name().split(':')[-1] != dest_skinTR.name().split(':')[-1]:
                print skinTR.name().split(':')[-1], dest_skinTR.name().split(':')[-1]
            else:
                try:
                    skin = skinTR.getShape().listConnections(type='skinCluster')[0]
                    dest_skin = dest_skinTR.getShape().listConnections(type='skinCluster')[0]
                    pm.copySkinWeights(ss=skin.name(), ds=dest_skin.name(),
                                       noMirror=True, normalize=True,
                                       surfaceAssociation='closestPoint',
                                       influenceAssociation='closestJoint')
                    dest_skin.setSkinMethod(skin.getSkinMethod())
                    print skinTR, 'copied to', dest_skinTR, '\n'
                except:
                    print '%s cannot copy skin to %s'%(skinTR.name(), dest_skinTR.name()), '\n'
        print '---Copy Skin Finish---'
    else:
        print 'source and target are not the same'
@error_alert
@do_function_on(mode='double')
def copy_skin_single(source_skin,dest_skin):
    '''copy skin for 2 object, target object do not need to have skin Cluster'''
    skin = source_skin.getShape().listConnections(type='skinCluster')[0]
    dest_skin = dest_skin.getShape().listConnections(type='skinCluster')[0]
    print skin,dest_skin
    pm.copySkinWeights(ss=skin.name(),ds=dest_skin.name(),
                       nm=True,nr=True,sm=True,sa='closestPoint',ia=['closestJoint','name'])
    dest_skin.setSkinMethod(skin.getSkinMethod())

@do_function_on(mode='double')
def parent_shape(src,target):
    if src.getShape():
        pm.parent(src.getShape(), target, r=True, s=True)
        pm.delete(src)

@do_function_on(mode='single')
def un_parent_shape(ob):
    shapeList = ob.listRelatives(type=pm.nt.Shape)
    if shapeList:
        for shape in shapeList:
            newTr = pm.nt.Transform(name=(shape.name()[:shape.name().find('Shape')]))
            newTr.setMatrix(ob.getMatrix(ws=True),ws=True)
            pm.parent(shape,newTr,r=True,s=True)
    if type(ob) != pm.nt.Joint:
        pm.delete(ob)

@do_function_on(mode='last')
def connect_joint(bones,boneRoot,**kwargs):
    for bone in bones:
        pm.connectJoint(bone, boneRoot, **kwargs)

@do_function_on(mode='single')
def create_roll_joint(oldJoint):
    newJoint = pm.duplicate(oldJoint,rr=1,po=1)[0]
    pm.rename(newJoint,('%sRoll1'%oldJoint.name()).replace('Left','LeafLeft'))
    newJoint.attr('radius').set(2)
    pm.parent(newJoint, oldJoint)
    return newJoint

@do_function_on(mode='single')
def create_sub_joint(ob):
    subJoint = pm.duplicate(ob,name='%sSub'%ob.name(),rr=1,po=1,)[0]
    new_pairBlend = pm.createNode('pairBlend')
    subJoint.radius.set(2.0)
    pm.rename(new_pairBlend,'%sPairBlend'%ob.name())
    new_pairBlend.attr('weight').set(0.5)
    ob.rotate >> new_pairBlend.inRotate2
    new_pairBlend.outRotate >> subJoint.rotate
    return (ob,new_pairBlend,subJoint)

@do_function_on(mode='single')
def reset_attr_value(ob):
    attr_exclude_list = [
        "translateX", "translateY", "translateZ",
        "rotateX", "rotateY", "rotateZ",
        "scaleX", "scaleY", "scaleZ",
        "visibility"
    ]
    attr_list = ob.listattr()
    for at in attrList[:-1]:
        bone.attr(at).set(0)

@do_function_on(mode='single')
def create_skinDeform(ob):
    dupOb = pm.duplicate(ob,name="_".join([ob.name(),"skinDeform"]))
    for child in dupOb[0].listRelatives(ad=True):
        add_suffix(child)

@do_function_on(mode='single')
def mirror_joint_tranform(bone, translate=False, rotate=True, **kwargs):
    #print bone
    opbone = get_opposite_joint(bone, customPrefix=(kwargs['customPrefix']if kwargs.has_key('customPrefix') else None))
    offset = 1
    if not opbone:
        opbone = bone
        offset = -1
        translate = False
    if all([type(b) == pm.nt.Joint for b in [bone, opbone]]):
        if rotate:
            pm.joint(opbone, edit=True, ax=pm.joint(bone, q=True, ax=True),
                     ay=pm.joint(bone, q=True, ay=True)*offset,
                     az=pm.joint(bone, q=True, az=True)*offset)
        if translate:
            bPos = pm.joint(bone, q=True, p=True)
            pm.joint(opbone, edit=True, p=(bPos[0]*-1, bPos[1], bPos[2]),
                     ch=kwargs['ch'] if kwargs.has_key('ch') else False,
                     co=not kwargs['ch'] if kwargs.has_key('ch') else True)

#@do_function_on
def get_opposite_joint(bone, select=False, opBoneOnly=True, customPrefix=None):
    "get opposite Bone"
    mirrorPrefixes_list = [
        ('Left', 'Right'),
        ('_L_', '_R_')
    ]
    try:
        if all(customPrefix, type(customPrefix) == tuple, len(customPrefix) == 2):
            mirrorPrefixes_list.append(customPrefix)
    except:
        pass
    for mirrorprefix in mirrorPrefixes_list:
        for index,mp in enumerate(mirrorprefix):
            if mp in bone.name():
                opBoneName = bone.name().replace(mirrorprefix[index], mirrorprefix[index-1])
                opBone = pm.ls(opBoneName)[0] if pm.ls(opBoneName) else None
                if select:
                    if opBoneOnly:
                        pm.select(opBone)
                    else:
                        pm.select(bone, opBone)
                print opBoneName
                return opBone
@do_function_on('single')
def reset_bindPose(joint_root):
    joint_childs = joint_root.listRelatives(type=pm.nt.Joint,ad=True)
    for joint in joint_childs:
        if joint.rotate.get() != pm.dt.Vector(0,0,0):
            #print type(joint.rotate.get())
            joint.jointOrient.set(joint.rotate.get())
            joint.rotate.set(pm.dt.Vector(0,0,0))
    newbp = pm.dagPose(bp=True, save=True)
    bindPoses = pm.ls(type=pm.nt.DagPose)
    for bp in bindPoses:
        if bp != newbp:
            pm.delete(bp)
    print "All bindPose has been reseted to %s" % newbp
    return newbp