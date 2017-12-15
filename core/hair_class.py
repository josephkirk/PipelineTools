import pymel.core as pm
from function import wraps
################ Error Handling class
class ColorInputError(Exception):
    """raise error if input for color not tuple3"""
    def __init__(self, expr):
        self.expr = expr
        self.msg = "Color Input must be tuple3"
        print self.expr
        print self.msg
################ Decorator

################ Main Class

class HairObj(object):
    """hair Mesh object"""
    def __init__(self, name, length_divisions=7, width_divisions=4, control_count=5):
        self.name = name
        self.lengthDivs = length_divisions
        self.widthDivs = width_divisions
        self.ctrlsCount = control_count 
        self.transform = None
        self.shape = None
        self.gen_node = None
        self.tesselate = None
        self.control = None

    def getConnection(self, type=''):
        if self.shape:
            connection = self.shape.listConnections(type=type)
            if connection:
                return connection[0]

    def get(self):
        if pm.objExists(self.name):
            self.transform = pm.ls(self.name)[0]
            self.shape = self.transform.getShape()
            self.gen_node = self.getConnection(type=pm.nt.Loft)
            self.tesselate = self.getConnection(type=pm.nt.NurbsSurface.tesselate)
        else:
            del self

    def create(self,control_count):
        """Generate hairMesh"""
        self.control = HairCtrlGrp(num_ctrl=control_count)
        pm.select(self.control.ctrls)
        pm.nurbsToPolygonsPref(pt=1, un=4, vn=7, f=2, ut=2, vt=2)
        hairMesh = pm.loft(n=self.name, po=1, ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, rsn=True)
        self.transform = hairMesh[0]
        self.transform.addAttr('lengthDivisions', min=1, at='long', dv=self.lengthDivs)
        self.transform.addAttr('widthDivisions', min=4, at='long', dv=self.widthDivs)
        self.transform.setAttr('lengthDivisions', e=1, k=1)
        self.transform.setAttr('widthDivisions', e=1, k=1)
        self.tesselate = pm.listConnections(hairMesh)[-1]
        self.transform.connectAttr('widthDivisions', self.tesselate+".uNumber")
        self.transform.connectAttr('lengthDivisions', self.tesselate+".vNumber")
        self.shape = self.transform.getShape()
        self.gen_node = hairMesh[1]


class HairCtrlObj(object):
    """control for hair Mesh"""
    common_color = (0.2, 0.5, 0.2)
    ###############################################
    def __init__(self, name, shapeType, radius_value, color_value):
        self.shapetype = shapeType
        self.create(name, radius_value, color_value)

    ##### Set property
    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

    @property
    def radius(self):
        return self._radius

    @name.setter
    def name(self, value):
        self._name = value
        pm.rename(self.transform, value)

    @radius.setter
    def radius(self, value):
        if any([type(value)==float, type(value)==int]) and value>=0.0:
            self._radius = value
            pm.setAttr(self.gen_node.radius,value)
        else:
            raise

    @color.setter
    def color(self, value):
        if type(value)==tuple and len(value)==3:
            self._color = value
            for attr in [('overrideEnabled', 1),
                         ('overrideRGBColors', 1),
                         ('overrideColorRGB', value)]:
                self.shape_node.attr(attr[0]).set(attr[1])
        else:
            raise ColorInputError(self.color)
    ###########
    def get_shape_info(self, pos):
        """return appropriate data for ctrl generation"""
        shape_type = {
            'circle':(3, 8),
            'triangle':(1, 3),
            'diamond':(1, 4)
        }
        return shape_type[self.shapetype][pos]

    def create(self,name, radius_value, color_value):
        """"generate Control Shape"""
        temp_ob = pm.circle(c=(0, 0, 0),
                            nr=(0, 1, 0),
                            sw=360, r=radius_value,
                            name=name,
                            d=self.get_shape_info(0),
                            s=self.get_shape_info(1),
                            ut=0, tol=5.77201e-008, ch=1)
        self.transform = temp_ob[0]
        self.shape_node = self.transform.getShape()
        self.gen_node = temp_ob[1]
        self.name = name
        self.color = color_value
        self.radius = radius_value

    @classmethod
    def circle(cls, name='CircleControl#', radius=1.0, color=common_color):
        """Create circle controls"""
        return HairCtrlObj(name, 'circle', radius, color)

    @classmethod
    def triangle(cls, name='TriangleControl#', radius=1.0, color=common_color):
        """Create triangle controls"""
        return HairCtrlObj(name, 'triangle', radius, color)

    @classmethod
    def diamond(cls, name='DiamondControl#', radius=1.0, color=common_color):
        """Create diamond controls"""
        return HairCtrlObj(name, 'diamond', radius, color)


class HairCtrlGrp(object):
    """Hair Control Groups
       Contain Control for hairMesh"""
    def __init__(self, grp_name="HairControlGroup#", num_ctrl=5, gen_node = None):
        self.count = num_ctrl
        self.gen_node = gen_node
        self.ctrls = []
        self.transform = pm.nt.Transform(name=grp_name)
        self.name = self.transform.name()
        self.create()

    def create(self):
        if pm.objExists("HairControlsAllGrp"):
            pm.parent(self.transform, pm.ls("HairControlsAllGrp")[0])
        else:
            pm.group(name="HairControlsAllGrp")
        if not self.gen_node:
            for i in range(self.count):
                new_hairctrl = HairCtrlObj.triangle()
                new_hairctrl.transform.setTranslation((0,i*5,0))
                pm.parent(new_hairctrl.transform, self.transform)
                new_hairctrl.name = "_".join([self.name, new_hairctrl.name])
                self.ctrls.append(new_hairctrl.transform)

    def rename(self, new_name):
        pm.rename(self.transform, new_name)
    #def __get__(self, instance, owner):
    #    return self.transform
