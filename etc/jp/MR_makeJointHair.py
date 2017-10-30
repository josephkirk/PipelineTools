## -*- coding: Shift_JIS -*-

##
## Name   : Make Joint Hair ver.1.4
##
## Update : Feb 02, 2016 (ver 1.4)
##			Dec 02, 2015 (ver 1.3)
##			Feb 20, 2014 (ver 1.2)
##			Feb 17, 2014 (ver 1.1)
##
## Date   : May 30, 2013 (ver 1.0)
##
## Description :
## 		This assigns hair system to a joint chain.
##
## Input Args   : (None)
## Return Value : (None)
##

import pymel.core as pm
import math

class main:

	def getJointChainList(self, top):
		
		selList = pm.selected()
		pm.select(top, hi=True)
		chainList = pm.selected(type='joint')
		pm.select(selList, r=True)

		for chain in chainList:
			if len(chain.getChildren()) > 1:
				pm.displayError('%s has more than one child.' % current)
				return False
		
		return chainList

	def lockXformAttrs(self, node, isShown):
		
		attrList = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
		
		for attr in attrList:
			node.attr(attr).lock()
			node.attr(attr).setKeyable(isShown)
			node.attr(attr).showInChannelBox(isShown)
		
	def makeOctaController(self, name):
		
		pntMatrix = [
			[ 0, 1, 0], [ 1, 0, 0], [ 0, 0,-1],
			[ 0, 1, 0],	[-1, 0, 0], [ 0, 0,-1],
			[ 0,-1, 0],	[ 1, 0, 0],	[ 0, 0, 1],
			[-1, 0, 0],	[ 0,-1, 0],	[ 0, 0, 1], [ 0, 1, 0]]
		
		crv = pm.curve(d=1, p=pntMatrix, n=name)
		
		return crv

	def makePinController(self, name):
	
		rd = 0.5
		lt = 2.0
		hw = math.sqrt(2.0) / 4.0
	
		pntMatrix = [
			[0,  0,  0],
			[0,   lt-rd,0],[-hw, lt-hw,0],
			[-rd,    lt,0],[-hw, lt+hw,0],
			[0,   lt+rd,0], [hw, lt+hw,0],
			[rd,     lt,0], [hw, lt-hw,0],
			[0,   lt-rd,0]]
		
		crv = pm.curve(d=1, p=pntMatrix, n=name)
		
		return crv
	
	def makeCircleController(self, name):
		
		return pm.circle(nr=[1,0,0], r=1.0, n=name, ch=False)[0]

	def makeXformController(self, name, axisName, joint):
		
		circle = pm.circle(n=name,ch=1,o=1,nr=[1,0,0],d=1,s=8,r=2.0)[0]
		axis = pm.group(circle,n=axisName)
		
		circle.attr('overrideEnabled').set(1)
		circle.attr('overrideColor').set((self.colrPLTval))

		const = pm.parentConstraint(joint, axis)
		pm.delete(const)

		return (axis, circle)
	
	def assignHair(self, crv, hairSystem):
		
		pm.select(crv, r=1)
		pm.mel.source('DynCreateHairMenu.mel') # C:/Program Files/Autodesk/Maya(ver)/scripts/startup/

		if hairSystem is None:

			oldAllList = pm.ls(type='hairSystem')
			pm.mel.assignNewHairSystem()
			newAllList = pm.ls(type='hairSystem')

			hairSystem = (list(set(newAllList) - set(oldAllList))[0]).getParent()

		else:
			pm.mel.assignHairSystem(hairSystem)
			
		follicle = list(set(hairSystem.getShapes()[0].inputs()).intersection(set(crv[0].getShapes()[0].outputs())))[0]
		#follicle = hairSystem.getShapes()[0].attr('inputHair[%s]'%id).inputs()[0]
		hcrv = follicle.attr('outCurve').outputs()[0]
		
		pm.rename(hcrv, 'outputCurve#')
		
		return (follicle, hcrv, hairSystem)
		
	def makeGroupIfNotExist(self, grpName, isHidden):
		
		if not pm.objExists(grpName):
			grp = pm.group(n=grpName, em=1)
			if isHidden:
				pm.hide(grp)
		else:
			grp = pm.PyNode(grpName)
		
		return grp

	def makeJointHair(self, sel, hairSystem):

		simDuped = pm.duplicate(sel, n='sim_%s'%sel.nodeName())[0]
		mixDuped = pm.duplicate(sel, n='mix_%s'%sel.nodeName())[0]
		wgtDuped = pm.duplicate(sel, n='weight_%s'%sel.nodeName())[0]
		
		selJointList = self.getJointChainList(sel)
		simJointList = self.getJointChainList(simDuped)
		mixJointList = self.getJointChainList(mixDuped)
		wgtJointList = self.getJointChainList(wgtDuped)
		
		if not (selJointList and simJointList and mixJointList):
			return False
		
		num = len(selJointList)
		pos = sel.getTranslation(space='world')
		ctrlGrp = pm.group(n='ctrls#', em=1)

		axis, circle = self.makeXformController('top_ctrl#','top_ctrl_axis#',selJointList[0])
		circle.addAttr('space',at='enum',en='World:Local', k=1, dv=self.dnspRBGval-1)
		circle.addAttr('ctrl_size',at='double',k=1, dv=1.0)
		circle.attr('ctrl_size') >> circle.attr('scaleX')
		circle.attr('ctrl_size') >> circle.attr('scaleY')
		circle.attr('ctrl_size') >> circle.attr('scaleZ')
		
		pntMatrix = []

		skclList = list(set(sel.outputs(type='skinCluster')))
		
		for i in xrange(num):
			
			if i != 0:
				pm.rename(simJointList[i], 'sim_%s'%simJointList[i].nodeName())
				pm.rename(mixJointList[i], 'mix_%s'%mixJointList[i].nodeName())
			
			pos = selJointList[i].getTranslation(space='world')
			ofstJoint = pm.rename(pm.insertJoint(mixJointList[i]), mixJointList[i].nodeName().replace('mix','offset'))

			pntMatrix.append(pos)
			
			attrList = ['tx','ty','tz','rx','ry','rz']
			for attr in attrList:
				simJointList[i].attr(attr) >> mixJointList[i].attr(attr)
			
			pm.parentConstraint(ofstJoint, selJointList[i], mo=True)
			
			mixJointList[i].attr('radius').set(0.0)
			ofstJoint.attr('radius').set(0.0)
			
			if not (i == num - 1 and not self.pctlCBXval):
				
				''' # If on, no controllers will be created to the joints which does't have any skinCluster
				for skcl in skclList:
					if selJointList[i] in skcl.getInfluence():
						break
				else:
					continue
				'''
								
				if self.ctshRBGval==1:
					ctrl = self.makeCircleController('%s_ctrl' % selJointList[i].nodeName())
				elif self.ctshRBGval==2:
					ctrl = self.makePinController('%s_ctrl' % selJointList[i].nodeName())
				elif self.ctshRBGval==3:
					ctrl = self.makeOctaController('%s_ctrl' % selJointList[i].nodeName())
	
				ctrl.attr('overrideEnabled').set(1)
				ctrl.attr('overrideColor').set((self.colrPLTval))
	
				ctrlAxis = pm.group(ctrl, n='%s_ctrl_axis' % selJointList[i].nodeName())
				ctrlAxis.attr('rotatePivot').set([0,0,0])
				ctrlAxis.attr('scalePivot').set([0,0,0])
				
				circle.attr('ctrl_size') >> ctrl.attr('scaleX')
				circle.attr('ctrl_size') >> ctrl.attr('scaleY')
				circle.attr('ctrl_size') >> ctrl.attr('scaleZ')
				
				pm.parentConstraint(mixJointList[i], ctrlAxis)
				pm.parentConstraint(ctrl, ofstJoint)
				pm.parent(ctrlAxis, ctrlGrp)
			
			# Pour weights to simJointList temporarily
			
			for skcl in skclList:
				
				if selJointList[i] in skcl.getInfluence():
				
					skcl.addInfluence(wgtJointList[i], wt=0)
					inflList = skcl.getInfluence()

					isMaintainMax = skcl.attr('maintainMaxInfluences').get()
					maxInfl = skcl.attr('maxInfluences').get()
			
					isFullInfl = False
					if isMaintainMax and maxInfl == len(inflList):
						isFullInfl=True
						skcl.attr('maintainMaxInfluences').set(False)
									
					for infl in inflList:
						if infl == selJointList[i] or infl == wgtJointList[i]:
							infl.attr('lockInfluenceWeights').set(False)
						else:
							infl.attr('lockInfluenceWeights').set(True)
					
					for geo in skcl.getGeometry():
						pm.skinPercent(skcl,geo.verts,nrm=True,tv=[selJointList[i],0])
						
					skcl.removeInfluence(selJointList[i])
					
					if isFullInfl:
						skcl.attr('maintainMaxInfluences').set(True)

		crv1d = pm.curve(d=1, p=pntMatrix)
		crv = pm.fitBspline(crv1d, ch=1, tol=0.001)
				
		follicle, hcrv, hairSystem = self.assignHair(crv, hairSystem)

		follicleGrp = follicle.getParent()
		curveGrp = hcrv.getParent()
		
		ikhandle = pm.ikHandle(sj=simJointList[0],ee=simJointList[num-1],c=hcrv,createCurve=0,solver='ikSplineSolver')[0]

		# Pour back

		for i in xrange(num):
	
			for skcl in skclList:
				
				if wgtJointList[i] in skcl.getInfluence():

					skcl.addInfluence(selJointList[i], wt=0)				
					inflList = skcl.getInfluence()

					isMaintainMax = skcl.attr('maintainMaxInfluences').get()
					maxInfl = skcl.attr('maxInfluences').get()
					
					isFullInfl = False
					if isMaintainMax and maxInfl == len(inflList):
						isFullInfl=True
						skcl.attr('maintainMaxInfluences').set(False)
	
					for infl in inflList:
						if infl == selJointList[i] or infl == wgtJointList[i]:
							infl.attr('lockInfluenceWeights').set(False)
						else:
							infl.attr('lockInfluenceWeights').set(True)
							
					for geo in skcl.getGeometry():
						pm.skinPercent(skcl,geo.verts,nrm=True,tv=[wgtJointList[i],0])	
									
					for infl in inflList:
						infl.attr('lockInfluenceWeights').set(False)		
					
					attrList = [wgtJointList[i].attr('message'), wgtJointList[i].attr('bindPose')]
					for attr in attrList:
						for dst in pm.connectionInfo(attr, dfs=True):
							dst = pm.Attribute(dst)
							if dst.node().type()=='dagPose':
								attr // dst

					if isFullInfl:
						skcl.attr('maintainMaxInfluences').set(True)
		
		pm.delete(wgtJointList)
		
		simGrp = pm.group(simJointList[0], follicle, n='sim_joints#')
		xformer = pm.group(simGrp, mixJointList[0], selJointList[0], n='transformer#')

		hcrv.attr('scalePivot').set(selJointList[0].getTranslation(space='world'))
		hcrv.attr('rotatePivot').set(selJointList[0].getTranslation(space='world'))
		ctrlGrp.attr('scalePivot').set(selJointList[0].getTranslation(space='world'))
		ctrlGrp.attr('rotatePivot').set(selJointList[0].getTranslation(space='world'))
		simGrp.attr('scalePivot').set(selJointList[0].getTranslation(space='world'))
		simGrp.attr('rotatePivot').set(selJointList[0].getTranslation(space='world'))
	
		mixJointList[0].attr('template').set(1)
		hcrv.attr('template').set(1)
		hairSystem.attr('iterations').set(20)
		xformer.attr('scalePivot').set(axis.getTranslation())
		xformer.attr('rotatePivot').set(axis.getTranslation())

		wcnst = pm.parentConstraint(circle, hcrv, mo=True)
		lcnst = pm.parentConstraint(circle, xformer, mo=True)
		
		rev = pm.shadingNode('reverse', asUtility=True)
		circle.attr('space') >> wcnst.attr('%sW0'%wcnst.getTargetList()[0])
		circle.attr('space') >> rev.attr('inputX')
		rev.attr('outputX') >> lcnst.attr('%sW0'%lcnst.getTargetList()[0])

		pm.delete(follicleGrp, curveGrp, crv1d)
		pm.hide(simGrp)
		
		crvGrp = self.makeGroupIfNotExist('hairSystemOutputCurves',0)
		ikGrp = self.makeGroupIfNotExist('hairSystemIKHandles',1)
		nodesGrp = self.makeGroupIfNotExist('hairSystemNodes',1)

		pm.parent(hcrv, crvGrp)
		pm.parent(ikhandle, ikGrp)
	
		if hairSystem.getParent() != nodesGrp:
			pm.parent(hairSystem, nodesGrp)

		if not pm.objExists(self.topName):
			topGrp = pm.group(n=self.topName,em=1)
			pm.parent(nodesGrp, ikGrp, crvGrp, xformer, axis, ctrlGrp, topGrp)
		else:
			pm.parent(xformer, axis, ctrlGrp, self.topName)
			
		topNode = pm.PyNode(self.topName)
		
		self.lockXformAttrs(topNode,False)
		self.lockXformAttrs(ctrlGrp,False)
		self.lockXformAttrs(crvGrp,False)
		self.lockXformAttrs(ikGrp,False)
		self.lockXformAttrs(nodesGrp,False)
	
		pm.select(topNode, r=1)

		self.selList.pop(0)

		windowName = 'hairSystem_Window'
	
		if pm.window(windowName,ex=1):
			pm.deleteUI(windowName)
					
		if self.selList:
			self.dialog(self.selList[0])

		pm.displayInfo('"Make Joint Hair" has been successfully done.')

		return True

	def getTopGroupFromHair(self, hs):

		prnt = hs.getParent()
		if prnt:
			grnp = prnt.getParent()
			if grnp:
				top = grnp.getParent()
				if top:
					return top

		return False

	def getTopJointFromHair(self, hs, isBake):
		
		jntList = []
		
		for flc in hs.outputs(type='follicle', sh=True):
			crv = flc.outputs(type='nurbsCurve', sh=True)
			if crv:
				ikh = crv[0].outputs(type='ikHandle', sh=True)
				if ikh:
					simjnt = ikh[0].inputs(type='joint')
					if simjnt:
						if isBake:
							jnt = simjnt[0].attr('translateX').outputs(type='joint')
						else:
							jnt = simjnt[0].attr('radius').outputs(type='joint')
						if jnt:
							jntList.append(jnt[0])
		
		return jntList		

	def bake(self):
		
		opmTxt = self.hsysOPM.getValue()
		isAll = self.alhsCBX.getValue()
		
		if isAll:
			hsList = pm.ls(type='hairSystem')

		else:
			hsList = pm.ls(opmTxt, r=True)[0].getShapes()

		for hs in hsList:
			
			if isAll:
				topList = [self.getTopGroupFromHair(hs)]
				
			else:
				topList = self.getTopJointFromHair(hs, True)

			if not topList:
				pm.displayError('The top node not found.')
				return False

			else:
				dagList = pm.ls(topList, dag=True)
				allMixJntList = pm.ls('*mix*', type='joint', r=True)
				mixJntList = list(set(dagList) & set(allMixJntList))

				if not mixJntList:
					continue

				ncls = hs.inputs(type='nucleus')[0]

				for mixJnt in mixJntList:
					simJnt = mixJnt.attr('tx').inputs()
					if simJnt:
						simJnt = simJnt[0]
						if simJnt.nodeType() == 'joint':
							simJnt.attr('radius') >> mixJnt.attr('radius') # This is for the unbaking
	
				if self.tmrgRBG.getSelect() == 1:
					min = pm.env.getMinTime()
					max = pm.env.getMaxTime()
				else:
					min = self.stedIFG.getValue1()
					max = self.stedIFG.getValue2()
	
				ncls.attr('enable').set(True)

				pm.bakeResults(mixJntList, sm=True, t=[min,max], ral=False, mr=True, at=['tx','ty','tz','rx','ry','rz'])

				ncls.attr('enable').set(False)

				pm.displayInfo('Successfully baked.')

		
	def unbake(self):

		opmTxt = self.hsysOPM.getValue()
		isAll = self.alhsCBX.getValue()
		
		if isAll:
			hsList = pm.ls(type='hairSystem')

		else:
			hsList = pm.ls(opmTxt, r=True)[0].getShapes()

		for hs in hsList:
			
			if isAll:
				topList = [self.getTopGroupFromHair(hs)]
				
			else:
				topList = self.getTopJointFromHair(hs, False)

			if not topList:
				pm.displayError('The top node not found.')
				return False

			else:
				dagList = pm.ls(topList , dag=True)
				allMixJntList = pm.ls('*mix*', type='joint', r=True)
				mixJntList = list(set(dagList) & set(allMixJntList))

				if not mixJntList:
					continue

				ncls = hs.inputs(type='nucleus')[0]

				for mixJnt in mixJntList:
					
					ancvList = mixJnt.inputs(type='animCurve')
					pm.delete(ancvList)
					simJnt = mixJnt.attr('radius').inputs()
					
					if simJnt:
						simJnt = simJnt[0]
						simJnt.attr('radius') // mixJnt.attr('radius')
						simJnt.attr('tx') >> mixJnt.attr('tx')
						simJnt.attr('ty') >> mixJnt.attr('ty')
						simJnt.attr('tz') >> mixJnt.attr('tz')
						simJnt.attr('rx') >> mixJnt.attr('rx')
						simJnt.attr('ry') >> mixJnt.attr('ry')
						simJnt.attr('rz') >> mixJnt.attr('rz')

				ncls.attr('enable').set(True)

				pm.displayInfo('Successfully unbaked.')

	def clickedDialogButton(self, window, sel, isNew):

		if isNew:
			self.makeJointHair(sel, None)
		else:
			self.currentHsysVal = self.exhsOPM.getValue()
			
			print self.currentHsysVal
			
			self.makeJointHair(sel, pm.PyNode(self.exhsOPM.getValue()))

		self.ui()
				
	def dialog(self, sel):
		
		hsysList = pm.ls(type='hairSystem')
	
		windowName = 'hairSystem_Window'
	
		if pm.window(windowName,ex=1):
			pm.deleteUI(windowName)
	
		window = pm.window(windowName,title=sel.nodeName(),mb=1)
	
		with window:
		
			formLOT = pm.formLayout()
			with formLOT:
				self.exhsOPM = pm.optionMenu(label='')
				
				for hsys in hsysList:
					pm.menuItem(l=hsys.getParent().shortName())
				
				if 'currentHsysVal' in dir(self):
					self.exhsOPM.setValue(self.currentHsysVal)
				
				self.wrngTXT = pm.text(l='HairSystem can be shared.\nShould the selected HairSystem be used?', align='left')
				self.usesBTN = pm.button(l='Use selected', w=90, c=pm.Callback(self.clickedDialogButton,window, sel, 0))
				self.crtnBTN = pm.button(l='Create new', w=90, c=pm.Callback(self.clickedDialogButton,window, sel, 1))
			
			formLOT.attachForm(self.exhsOPM, 'top',   5)
			formLOT.attachForm(self.exhsOPM, 'left', 20)
			formLOT.attachForm(self.wrngTXT, 'top',  30)
			formLOT.attachForm(self.wrngTXT, 'left', 20)
			formLOT.attachForm(self.usesBTN, 'top',  70)
			formLOT.attachForm(self.usesBTN, 'left', 20)
			formLOT.attachForm(self.crtnBTN, 'top',  70)
			formLOT.attachForm(self.crtnBTN, 'left',130)
		
	def conditionBranch(self):
		
		self.selList = pm.selected(type='joint')
		self.topName = 'hairSystem'

		if not self.selList:
			pm.displayError('Select joints.')
			return False
		
		if pm.ls(type='hairSystem'):
			self.dialog(self.selList[0])
		else:
			self.makeJointHair(self.selList[0], None)

	def doCreate(self):
		
		self.pctlCBXval = self.pctlCBX.getValue()
		self.colrPLTval = self.colrPLT.getSetCurCell()
		self.dnspRBGval = self.dnspRBG.getSelect()
		self.ctshRBGval = self.ctshRBG.getSelect()
		self.conditionBranch()
		self.ui()

	def toggleUi(self):

		self.stedIFG.setEnable(self.tmrgRBG.getSelect()==2)
		self.hsysOPM.setEnable(not self.alhsCBX.getValue())

	def ui(self):

		windowName = 'makeJointHair_Window'
	
		if pm.window(windowName,ex=1):
			pm.deleteUI(windowName)
	
		window = pm.window(windowName,title='Make Joint Hair',mb=1)
	
		with window:
			pm.menu(l='Edit')
			pm.menuItem(l='Exit',c=pm.Callback(pm.deleteUI, window))
			pm.menu(l='Help')
			pm.menuItem(l='Open document...',c=pm.Callback(pm.showHelp,'',a=True))

			tabLOT = pm.tabLayout(imh=10, imw=2)
			with tabLOT:
				frameLOT = pm.frameLayout('Make', mh=10,mw=2,w=440,h=160, lv=False,bs='etchedIn')
				with frameLOT:
					formLOT = pm.formLayout()
					with formLOT:
						with pm.columnLayout():
							with pm.rowLayout(nc=2, cw=[1,120], cal=[2,'right'], rat=[1,'top',2]):
								pm.text(l='')
								self.pctlCBX = pm.checkBox(l='Put Controller to leaf', ann=u'末端のジョイントにもコントローラを付け加えます')
							self.dnspRBG = pm.radioButtonGrp(nrb = 2, l='Dynamics Space: ', la2=['World','Local'], cw3=[120,80,80], sl=1, ann=u'ダイナミクス空間。\n\nWorld:ルートジョイントの動きの影響を受けます。 \nLocal:ルートジョイントの動きの影響を受けません。')
							self.ctshRBG = pm.radioButtonGrp(nrb = 3, l='Controller Shape: ', la3=['Circle', 'Pin', 'Octahedron'], cw4=[120,80,80,80], sl=1, ann=u'コントローラの形状。 \n\nCircle:円形 Pin:ピン Octahedron: 八面体')
							with pm.rowLayout(nc=2, cw=[1,100], cal=[2,'right'], rat=[1,'top',2]):
								self.colrTXT = pm.text(label='Controller Color: ', w=120, al='right', ann=u'コントローラの色')
								self.colrPLT = pm.palettePort('ColorPalette', dimensions=[16,2], width=16*17, height=2*17, transparent=0, topDown=True, colorEditable=False, ann=u'コントローラの色')
								for i in range(1,32):
									rgb = pm.colorIndex(i,q=True)
									self.colrPLT.setRgbValue([i,rgb[0],rgb[1],rgb[2]])

						makeBTN = pm.button(l='Make', c=pm.Callback(self.doCreate), ann=u'ジョイントを選択してクリックしてください。\nジョイントをヘアシミュレーションによって制御されるようにし、\nその上からコントローラでオフセットをかけられるようにします。')

					formLOT.attachForm(makeBTN, 'left',  5)
					formLOT.attachForm(makeBTN, 'right', 5)
					formLOT.attachForm(makeBTN, 'bottom',5)


				frameLOT = pm.frameLayout('Bake', mh=10,mw=2,w=440,lv=False,bs='etchedIn')
				with frameLOT:
					formLOT = pm.formLayout()
					with formLOT:
						cw3List = [100,80,180]
						with pm.columnLayout(adj=True):
							with pm.rowLayout(nc=2, cw=[1,cw3List[0]], cal=[2,'right'], rat=[1,'top',2]):
								pm.text('Hair System: ', w=cw3List[0], al='right', ann=u'ベイクまたはベイク解除をするヘアシステムを選択してください。')
								with pm.columnLayout():
									self.alhsCBX = pm.checkBox(v=True, l='All Hair Systems', ann=u'シーン内にある全てのヘアシステムを一括でベイクします。', cc=pm.Callback(self.toggleUi))
									self.hsysOPM = pm.optionMenu(w=300, en=False, ann=u'ベイクまたはベイク解除をするヘアシステムを選択してください。')

									hsList = pm.ls(type='hairSystem')

									if not hsList:
										pm.menuItem('( No Found )')
									else:
										for hs in hsList:
											pm.menuItem(hs.getParent().nodeName())
							
							pm.separator(w=440, h=20, st='in')
							
							self.tmrgRBG = pm.radioButtonGrp(nrb = 2, l='Time range: ', la2=['Time Slider','Start / End'], cw3=cw3List, sl=1, cc=pm.Callback(self.toggleUi), ann=u'ベイクするタイムレンジ。\nTime Slider: タイムスライダの設定に則ります。\nStart/End: 開始/終了フレームを自分で設定します。')
							self.stedIFG = pm.intFieldGrp(nf = 2, l='Start / End: ', v1=pm.env.getMinTime(), v2=pm.env.getMaxTime(), cw3=[100,80,80], en=False, ann=u'ベイクする開始/終了フレーム')

						bakeBTN = pm.button(l='Bake', c=pm.Callback(self.bake), ann=u'アニメーションをベイクし、Nucleus の Enable アトリビュートをオフに設定します。\n\n[NOTE]\nmix_ で始まる名前のジョイントにベイクされます。')
						unbkBTN = pm.button(l='Unbake', c=pm.Callback(self.unbake), ann=u'ベイクを解除し、Nucleus の Enable アトリビュートをオンに設定します。')

						formLOT.attachForm    (bakeBTN, 'left',  5)
						formLOT.attachPosition(bakeBTN, 'right', 2,50)
						formLOT.attachForm    (bakeBTN, 'bottom',5)
						formLOT.attachPosition(unbkBTN, 'left',  2,50)
						formLOT.attachForm    (unbkBTN, 'right', 5)
						formLOT.attachForm    (unbkBTN, 'bottom',5)
	
			formLOT = pm.formLayout()
			with formLOT:
				clsBTN = pm.button('Close', c=pm.Callback(pm.deleteUI,window))
			formLOT.attachForm(clsBTN, 'left', 5)
			formLOT.attachForm(clsBTN, 'right', 5)
			formLOT.attachForm(clsBTN, 'bottom', 5)
	
	def __init__(self):
		
		self.ui()
		
if __name__=='__main__':
	
	main()