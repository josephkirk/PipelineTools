import os
import pymel.core as pm
from functools import wraps
import math
import logging
# ------------------------
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
# ------------------------

class main(object):
    '''Class to create Control'''

    def __init__(
            self,
            name='ControlObject',
            suffix='ctl',
            radius=1.0,
            res=24,
            length=2.0,
            height=2.0,
            axis='XY',
            offset=[0.0, 0.0, 0.0],
            color='red'):
        self._suffix = suffix
        self.name = name
        self._radius = radius
        self._length = length
        self._height = height
        self._axis = axis
        self._offset = offset
        self._step = 24
        self._color = color
        self.controls = {}
        self.controls['all'] = []
        self.controlGps = []
        self._resolutions = {
            'low': 4,
            'mid': 8,
            'high': 24
        }
        self._axisList = ['XY', 'XZ', 'YZ']
        self._axisList.extend([a[::-1] for a in self._axisList])  ## add reverse asxis
        self._axisList.extend(['-%s' % a for a in self._axisList])  ## add minus axis
        self._colorData = {
            'white': pm.dt.Color.white,
            'red': pm.dt.Color.red,
            'green': pm.dt.Color.green,
            'blue': pm.dt.Color.blue,
            'yellow': [1, 1, 0, 0],
            'cyan': [0, 1, 1, 0],
            'violet': [1, 0, 1, 0],
            'orange': [1, 0.5, 0, 0],
            'pink': [1, 0, 0.5, 0],
            'jade': [0, 1, 0.5, 0]
        }
        self._controlType = {
            'Pin': self.Pin,
            'DoublePin': self.DoublePin,
            'SpherePin': self.SpherePin,
            'Circle': self.Circle,
            'Octa': self.Octa,
            'Cylinder': self.Cylinder,
            'Sphere': self.Sphere,
            'Hemisphere': self.HalfSphere,
            'NSphere': self.NSphere,
            'Rectangle': self.Rectangle,
            'Cube': self.Cube,
            'RoundSquare': self.RoundSquare,
            'Triangle': self.Triangle,
            'Cross': self.Cross,
            'ThinCross': self.ThinCross
        }

        self._currentType = self._controlType['Pin']
        self._uiOption = {
            'group':True,
            'pre':False
        }
        self._uiElement = {}
        self.groupControl = False
        self.forceSetAxis = False
        log.info('Control Object class name:{} initialize'.format(name))
        log.debug('\n'.join(['{}:{}'.format(key, value) for key, value in self.__dict__.items()]))

    ####Define Property
    @property
    def name(self):
        self._name = '{}_{}'.format(self._baseName, self._suffix)
        return self._name

    @name.setter
    def name(self, newName):
        self._baseName = newName

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, newradius):
        assert any([isinstance(newradius, typ) for typ in [float, int]]), "radius must be of type float"
        self._radius = newradius

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, newlength):
        assert any([isinstance(newlength, typ) for typ in [float, int]]), "length must be of type float"
        self._length = newlength

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, newheight):
        assert any([isinstance(newheight, typ) for typ in [float, int]]), "height must be of type float"
        self._height = newheight

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, newoffset):
        if any([isinstance(newoffset, typ) for typ in [list, set, tuple]]):
            assert (len(newoffset) == 3), 'offset must be a float3 of type list,set or tuple'
            self._offset = newoffset

    @property
    def color(self):
        return pm.dt.Color(self._color)

    @color.setter
    def color(self, newcolor):
        if isinstance(newcolor, str):
            assert (self._colorData.has_key(newcolor)), "color data don't have '%s' color.\nAvailable color:%s" % (
                newcolor, ','.join(self._colorData))
            self._color = self._colorData[newcolor]
        if any([isinstance(newcolor, typ) for typ in [list, set, tuple]]):
            assert (len(newcolor) >= 3), 'color must be a float4 or float3 of type list,set or tuple'
            self._color = pm.dt.Color(newcolor)
        print self._color

    @property
    def currentType(self):
        return self._currentType

    @currentType.setter
    def currentType(self, value):
        if value in self._controlType.keys():
            self._currentType = self._controlType[value]

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, newaxis):
        assert (newaxis in self._axisList), "axis data don't have '%s' axis.\nAvailable axis:%s" % (
            newaxis, ','.join(self._axisList))
        self._axis = newaxis

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, newres):
        assert (
            self._resolutions.has_key(newres)), "step resolution value not valid.\nValid Value:%s" % self._resolutions
        self._step = self._resolutions[newres]

    # @ul.error_alert
    def __setProperty__(func):
        '''Wraper that make keywords argument of control type function
        to tweak class Attribute'''
        @wraps(func)
        def wrapper(self, *args, **kws):
            control = func(self, *args, **kws)

            self.setColor(control)
            control.setTranslation(self.offset, 'world')
            pm.makeIdentity(control, apply=True)
            log.info('Control of type:{} name {} created along {}'.format(
                func.__name__, control.name(), self._axis))
            if self.groupControl:
                Gp = pm.nt.Transform(name=self.name+'Gp')
                control.setParent(Gp)
                self.controlGps.append(Gp)
            else:
                pm.xform(control, pivots=(0, 0, 0), ws=True, dph=True, ztp=True)
            if self.forceSetAxis:
                self.setAxis(control, self.axis)
            return control
        return wrapper

    #### Control Type
    @__setProperty__
    def Octa(self):
        crv = createPinCircle(
            self.name,
            step=4,
            sphere=True,
            radius=self.radius,
            length=0)
        print self
        return crv

    @__setProperty__
    def Pin(self):
        crv = createPinCircle(
            self.name,
            axis=self.axis,
            sphere=False,
            radius=self.radius,
            step=self.step,
            length=self.length)
        return crv

    @__setProperty__
    def DoublePin(self):
        axis = self.axis.replace('-','m') if self.axis.startswith('-') else ('m'+self.axis)
        crv = createPinCircle(
            self.name,
            axis=axis,
            sphere=False,
            radius=self.radius,
            step=self.step,
            length=self.length)
        return crv

    @__setProperty__
    def SpherePin(self):
        crv = createPinCircle(
            self.name,
            axis=self.axis,
            sphere=True,
            radius=self.radius,
            step=self.step,
            length=self.length)
        if self.axis == '-XY' or self.axis == '-XZ':
            crv.setRotation((180,0,0))
            pm.makeIdentity(crv, apply=True)
        elif self.axis == '-YX':
            crv.setRotation((0,0,180))
            pm.makeIdentity(crv, apply=True)
        return crv

    @__setProperty__
    def Circle(self):
        crv = pm.circle(
            name=self.name,
            radius=self.radius)
        crv[0].setRotation((-90,0,0))
        pm.makeIdentity(crv[0], apply=True)
        return crv[0]

    @__setProperty__
    def Cylinder(self):
        crv = createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            cylinder=True,
            height=self.length,
            length=0,
        )
        return crv

    @__setProperty__
    def NSphere(self):
        shaderName = self._baseName+'_mtl'
        crv = pm.sphere(r=self.radius, n=self.name)
        #### set invisible to render
        crvShape = crv[0].getShape()
        crvShape.castsShadows.set(False)
        crvShape.receiveShadows.set(False)
        crvShape.motionBlur.set(False)
        crvShape.primaryVisibility.set(False)
        crvShape.smoothShading.set(False)
        crvShape.visibleInReflections.set(False)
        crvShape.visibleInRefractions.set(False)
        crvShape.doubleSided.set(False)
        #### set Shader
        shdr_name = '{}_{}'.format(shaderName, self.name)
        sg_name = '{}{}'.format(shdr_name, 'SG')
        if pm.objExists(shdr_name) or pm.objExists(sg_name):
            try:
                pm.delete(shdr_name)
                pm.delete(sg_name)
            except:
                pass
        shdr, sg = pm.createSurfaceShader('surfaceShader')
        pm.rename(shdr, shdr_name)
        pm.rename(sg, sg_name)
        shdr.outColor.set(self.color.rgb)
        shdr.outTransparency.set([self.color.a for i in range(3)])
        pm.sets(sg, fe=crv[0])
        return crv[0]

    @__setProperty__
    def Sphere(self):
        crv = createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=True,
            length=0,
            height=self.height)
        return crv
# pm.select(pm.PyNode('controlObject_ctl').cv[38:48], pm.PyNode('controlObject_ctl').cv[70:80])

    @__setProperty__
    def HalfSphere(self):
        crv = createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=True,
            length=0,
            height=self.height)
        pm.delete(crv.cv[38:48], crv.cv[70:80])
        crv.setRotation((-90,0,0))
        pm.makeIdentity(crv, apply=True)
        return crv

    @__setProperty__
    def Rectangle(self):
        crv = create_square(
            self.name,
            length=self.length,
            width=self.radius,
            offset=self.offset)
        return crv

    @__setProperty__
    def Cube(self):
        crv = create_shape(
            self.name,
            'cube',
            length=self.length,
            width=self.radius,
            height=self.height,
            offset=self.offset)
        return crv

    @__setProperty__
    def RoundSquare(self):
        crv = create_shape(
            self.name,
            'square_rounded',
            length=self.length,
            height=self.height,
            width=self.radius,
            offset=self.offset)
        crv = pm.closeCurve(crv, replaceOriginal=True)[0]
        crv.setRotation((0,-90,0))
        # pm.makeIdentity(crv, apply=True)
        return crv

    @__setProperty__
    def Triangle(self):
        crv = create_shape(
            self.name,
            'triangle',
            length=self.length,
            height=self.height,
            width=self.radius,
            offset=self.offset)
        crv.setRotation((0,-90,0))
        pm.makeIdentity(crv, apply=True)
        return crv

    @__setProperty__
    def Cross(self):
        crv = create_shape(
            self.name,
            'cross',
            length=self.length,
            height=self.height,
            width=self.radius,
            offset=self.offset)
        crv.setRotation((0,-90,0))
        pm.makeIdentity(crv, apply=True)
        return crv

    @__setProperty__
    def ThinCross(self):
        crv = create_shape(
            self.name,
            'thin_cross',
            length=self.length,
            height=self.height,
            width=self.radius,
            offset=self.offset)
        crv.setRotation((0,-90,0))
        pm.makeIdentity(crv, apply=True)
        return crv
    #### control method

    def setAxis(self, control, axis='XY'):
        axisData = {}
        axisData['XY'] = (0, 0, 0)
        axisData['XZ'] = (90, 0, 0)
        axisData['YZ'] = (0, 0, 90)
        axisData['YX'] = (180, 0, 0)
        axisData['ZX'] = (-90, 0, 0)
        axisData['ZY'] = (0, 0, -90)
        assert (axis in axisData), "set axis data don't have '%s' axis.\nAvailable axis:%s" % (axis, ','.join(axisData))
        control.setRotation(axisData[axis])
        print axisData[axis]
        # print control.getRotation()
        pm.makeIdentity(control, apply=True)

    def setColor(self, control):
        try:
            controlShape = control.getShape()
            if controlShape:
                controlShape.overrideEnabled.set(True)
                controlShape.overrideRGBColors.set(True)
                controlShape.overrideColorRGB.set(self.color)
            sg = control.shadingGroups()[0] if control.shadingGroups() else None
            if sg:
                shdr = sg.inputs()[0]
                shdr.outColor.set(self.color.rgb)
                shdr.outTransparency.set([self.color.a for i in range(3)])
        except AttributeError as why:
            log.error(why)
        print self.color

def create_square(
        name,
        width=1,
        length=1,
        offset=[0, 0, 0]):
    xMax = width/2
    yMax = length/2
    pointMatrix = [
        [ xMax,0, yMax ],
        [ xMax,0, -yMax ],
        [ -xMax,0, -yMax ],
        [ -xMax,0, yMax ],
        [  xMax,0, yMax ]
    ]
    key = range(len(pointMatrix))
    crv = pm.curve(name=name, d=1, p=pointMatrix, k=key)
    log.debug(crv)
    return crv

def create_shape(
        name,
        shapename,
        width=1.0,
        length=1.0,
        height=1.0,
        offset=[0, 0, 0]):
    data = {
    'circle': ([(0.0, 0.7, -0.7), (0.0, 0.0, -1.0), (0.0, -0.7, -0.7), (0.0, -1.0, 0.0), (0.0, -0.7, 0.7), (0.0, 0.0, 1.0), (0.0, 0.7, 0.7), (0.0, 1.0, 0.0)], 3, 1),
    'cross': ([(0.0, 0.5, -0.5), (0.0, 1.0, -0.5), (0.0, 1.0, 0.5), (0.0, 0.5, 0.5), (0.0, 0.5, 1.0), (0.0, -0.5, 1.0), (0.0, -0.5, 0.5), (0.0, -1.0, 0.5), (0.0, -1.0, -0.5), (0.0, -0.5, -0.5), (0.0, -0.5, -1.0), (0.0, 0.5, -1.0), (0.0, 0.5, -0.5)], 1, 1),
    'cube': ([(-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (-1.0, -1.0, -1.0), (-1.0, -1.0, 1.0), (1.0, -1.0, 1.0), (1.0, -1.0, -1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0), (1.0, -1.0, 1.0), (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (-1.0, -1.0, -1.0)], 1, 1),
    'locator': ([(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)], 1, 0),
    'square': ([(0.0, -1.0, 1.0), (0.0, 1.0, 1.0), (0.0, 1.0, -1.0), (0.0, -1.0, -1.0), (0.0, -1.0, 1.0)], 1, 1),
    'square_rounded': ([(0.0, 0.0, -1.0), (0.0, 0.5, -1.0), (0.0, 0.75, -1.0), (0.0, 1.0, -1.0), (0.0, 1.0, -0.75), (0.0, 1.0, -0.5), (0.0, 1.0, 0.5), (0.0, 1.0, 0.75), (0.0, 1.0, 1.0), (0.0, 0.75, 1.0), (0.0, 0.5, 1.0), (0.0, -0.5, 1.0), (0.0, -0.75, 1.0), (0.0, -1.0, 1.0), (0.0, -1.0, 0.75), (0.0, -1.0, 0.5), (0.0, -1.0, -0.5), (0.0, -1.0, -0.75), (0.0, -1.0, -1.0), (0.0, -0.75, -1.0), (0.0, -0.5, -1.0), (0.0, 0.0, -1.0)], 3, 1),
    'thin_cross': ([(0.0, 0.2, -0.2), (0.0, 0.2, -1.0), (0.0, -0.2, -1.0), (0.0, -0.2, -0.2), (0.0, -1.0, -0.2), (0.0, -1.0, 0.2), (0.0, -0.2, 0.2), (0.0, -0.2, 1.0), (0.0, 0.2, 1.0), (0.0, 0.2, 0.2), (0.0, 1.0, 0.2), (0.0, 1.0, -0.2), (0.0, 0.2, -0.2)], 1, 1),
    'triangle': ([(0.0, 1.0, 0.0), (0.0, -0.5, -0.86), (0.0, -0.5, 0.86), (0.0, 1.0, 0.0)], 1, 1)}
    pointMatrix = [pm.dt.Vector(d)*(width, length, height) for d in data[shapename][0]]
    key = range(len(pointMatrix)+data[shapename][1]-1)
    crv = pm.curve(name=name, d=data[shapename][1], p=pointMatrix, k=key)
    log.debug(crv)
    return crv

def createPinCircle(
        name,
        createCurve=True,
        axis='XY',
        sphere=False,
        cylinder=False,
        offset=[0, 0, 0],
        radius=1.0,
        length=3.0,
        height=2,
        step=20.0,
        maxAngle=360.0):
    '''Master function to create all curve control'''
    log.debug('''create Control with value:\n
        name: {}\n
        create Curve: {}\n
        axis: {}\n
        sphere: {}\n
        offset: {}\n
        radius: {}\n
        length: {}\n
        step: {}\n
        max Angle: {}'''.format(name, createCurve, axis, sphere, offset, radius, length, step, maxAngle))
    maxAngle = maxAngle / 180.0 * math.pi
    inc = maxAngle / step
    pointMatrix = []
    theta = 0
    if length > 0:
        pointMatrix.append([0, 0])
        pointMatrix.append([0, length])
        offset = [offset[0], -radius - length - offset[1], offset[2]]
    # print offset
    while theta <= maxAngle:
        if length > 0:
            x = (-offset[0] + radius * math.sin(theta))
            y = (offset[1] + radius * math.cos(theta)) * -1.0
        else:
            x = (offset[0] + radius * math.cos(theta))
            y = (offset[1] + radius * math.sin(theta))
        pointMatrix.append([x, y])
        # print "theta angle {} produce [{},{}]".format(round(theta,2),round(x,4),round(y,4))
        theta += inc
    if not createCurve:
        return pointMatrix
    axisData = {}
    axisData['XY'] = [[x, y, offset[2]] for x, y in pointMatrix]
    axisData['YX'] = [[y, x, offset[2]] for x, y in pointMatrix]
    axisData['-XY'] = [[-x, -y, offset[2]] for x, y in pointMatrix]
    axisData['-YX'] = [[-y, -x, offset[2]] for x, y in pointMatrix]
    axisData['XZ'] = [[x, offset[2], y] for x, y in pointMatrix]
    axisData['ZX'] = [[y, offset[2], x] for x, y in pointMatrix]
    axisData['-XZ'] = [[-x, offset[2], -y] for x, y in pointMatrix]
    axisData['-ZX'] = [[-y, offset[2], -x] for x, y in pointMatrix]
    axisData['YZ'] = [[offset[2], x, y] for x, y in pointMatrix]
    axisData['ZY'] = [[offset[2], y, x] for x, y in pointMatrix]
    axisData['-YZ'] = [[offset[2], -x, -y] for x, y in pointMatrix]
    axisData['-ZY'] = [[offset[2], -y, -x] for x, y in pointMatrix]
    axisData['mXY'] = axisData['XY'] + axisData['-XY']
    axisData['mYX'] = axisData['YX'] + axisData['-YX']
    axisData['mXZ'] = axisData['XZ'] + axisData['-XZ']
    axisData['mZX'] = axisData['ZX'] + axisData['-ZX']
    axisData['mYZ'] = axisData['YZ'] + axisData['-YZ']
    axisData['mZY'] = axisData['ZY'] + axisData['-ZY']
    axisData['all'] = axisData['XY'] + axisData['XZ'] + \
                      axisData['ZX'] + axisData['-XY'] + \
                      axisData['-XZ'] + axisData['-ZX']
    newname = name
    try:
        assert (axisData.has_key(axis)), \
            "Wrong Axis '%s'.\nAvailable axis: %s" % (axis, ','.join(axisData))
        finalPointMatrix = axisData[axis]
    except AssertionError as why:
        finalPointMatrix = axisData['XY']
        log.error(str(why) + '\nDefault to XY')
    if sphere and not cylinder and not length > 0:
        quarCircle = len(pointMatrix) / 4 + 1
        finalPointMatrix = axisData['XY'] + axisData['XZ'] + \
                           axisData['XY'][:quarCircle] + axisData['YZ']
    elif sphere and not cylinder and length > 0:
        if axis[-1] == 'X':
            finalPointMatrix = axisData['YX'] + axisData['ZX']
        elif axis[-1] == 'Y':
            finalPointMatrix = axisData['XY'] + axisData['ZY']
        elif axis[-1] == 'Z':
            finalPointMatrix = axisData['XZ'] + axisData['YZ']
    elif cylinder and not sphere and not length > 0:
        newpMatrix = []
        pMatrix = pointMatrix
        newpMatrix.extend(
            [[x, 0, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1][::-1]])
        newpMatrix.extend(
            [[x, 0, y] for x, y in pMatrix[::-1][:len(pMatrix) / 2 + 1]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[::-1][len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
        newpMatrix.extend(
            [[x, 0, y] for x, y in pMatrix[len(pMatrix) / 4:len(pMatrix) / 2 + 1]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
        newpMatrix.append(
            [newpMatrix[-1][0], 0, newpMatrix[-1][2]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[-len(pMatrix) / 4:]])
        finalPointMatrix = newpMatrix
    key = range(len(finalPointMatrix))
    crv = pm.curve(name=newname, d=1, p=finalPointMatrix, k=key)
    log.debug(crv)
    return crv
