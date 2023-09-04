"""
Quick Rig Tool

This module contains the UI code for the QuickRig tool.

It also holds several utility methods that are used by the tool.  These are
used to automatically perform tasks such as guides creation, guides mirroring,
skeleton creation, joint orientation, rig creation, etc.
"""
import maya
maya.utils.loadStringResourcesForModule(__name__)


import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from maya.common.ui import LayoutManager
from maya.common.ui import showMessageBox
from maya.common.ui import showConfirmationDialog
from maya.common.utils import getSourceNodes
from maya.common.utils import getSourceNodeFromPlug
from maya.common.utils import getSourceNode
from maya.common.utils import getIndexAfterLastValidElement
import json
from math import degrees , fabs , sqrt
from functools import partial , wraps

# For now, we only expose the entry point to QuickRig UI.
__all__ = [ 'OpenQuickRigUI' ]




###############################################################################
#                                                                             #
#  Constants                                                                  #
#                                                                             #
###############################################################################

# These are used in the tweaking of the joint placement.
kTweakSpine = True
kTweakSpineFirstRatio = 0.20
kTweakSpineLastRatio  = 0.60
kTweakNeck = True
kTweakNeckFirstRatioNoTweak = 0.4
kTweakNeckFirstRatio        = 0.25
kTweakNeckLastRatio         = 0.45
kTweakShoulder = True
kTweakShoulderRatio = 0.6
kTweakFoot = True
kTweakFootToeRatio                = 0.4
kTweakFootAnkleRatio              = 0.2
kTweakFootUseCorrectedAnkleForToe = False
kTweakHand = True
kTweakHandRatio = 0.4

# Available resolutions.
kResolutions = [ 1024  , 512 , 256 , 128 , 64  ]

# Hard-coded options window layout information.
kFrameMarginWidth = 25
kFrameMarginHeight = 4
kFrameParam = dict( marginWidth=kFrameMarginWidth , marginHeight=kFrameMarginHeight , collapse=False , collapsable=True )
kRowLayoutHeight = 21
kSkeletonFieldWidth = 60
kOptionsTextWidth = 90
kOptionsButtonWidth = 40
kColorSwatchWidth = 30
kColorSwatchHeight = 30
kColorSwatchColorWidth = 15
kColorSwatchColorHeight = 15

# List of options for symmetry.
kSymmetryOptions = [
    ( maya.stringTable['y_quickRigUI.kSymmetryBoundingBox' ] , True  , None   ) ,
    ( maya.stringTable['y_quickRigUI.kSymmetryHips' ]                , True  , 'Hips' ) ,
    ( maya.stringTable['y_quickRigUI.kSymmetryNoSymmetry' ]   , False , None   ) ,
    ]

# List of options for joint orientation.
kOrientJointsOptions = [
    # Left is towards child, right is not.
    ( maya.stringTable['y_quickRigUI.kMirroredBehavior' ]     , True  , ( True , False ) ) ,
    # Left is towards child, right is too.
    ( maya.stringTable['y_quickRigUI.kXTowardsNextJoint' ] , True  , ( True , True  ) ) ,
    # No alignment.
    ( maya.stringTable['y_quickRigUI.kWorldNoAlignment' ]  , False , None             ) ,
    ]

# List of options for skin binding.
kSkinBindingOptions = [
    maya.stringTable['y_quickRigUI.kGVBBindingMethod' ] ,
    maya.stringTable['y_quickRigUI.kCurrentSettingsBindingMethod' ] ,
    ]
# Index of the option that uses current settings.
kSkinBindingCurrentSettingsIndex = 1

# Name of the attribute on the character node used to store the connection to the Quick Rig info.
kQuickRigInfoAttributeName = 'quickRigInfo'
# Name of the child attribute on the Quick Rig info attribute to store the meshes.
kMeshesAttributeName = 'meshes'
# Name of the child attribute on the Quick Rig info attribute to store the guides.
kGuidesAttributeName = 'guides'
# Name of the child attribute on the Quick Rig info attribute to store the skeleton.
kSkeletonAttributeName = 'skeleton'
# Color of the created guides joints.
kGuidesColor = [ 160 / 255.0 , 60 / 255.0 , 0 / 255.0 ]
# Color of the guides color swatch when it is disabled.
kDisabledGuidesColor = [ 93 / 255.0 , 93 / 255.0 , 93 / 255.0 ]

# Space definition: Up is positive Y, mirror plane is along X axis.
kCharacterSymmetryAxis  = 0
kCharacterDownDirection = 0 # Min corner of bounding box.
kCharacterUpDirection   = 1 # Max corner of bounding box.
kCharacterUpAxis        = 1 # Y direction.




###############################################################################
#                                                                             #
#  UI class                                                                   #
#                                                                             #
###############################################################################
class QuickRigTool:
    """
    This is the main UI class for the QuickRig tool.
    
    It handles creation of the UI and provides various callbacks to handle
    user interactions.
    """
    
    def __init__( self , windowName="quickRigWindowId" ):
        """
        Simple constructor.
        
        It does not create the UI.  UI creation is deferred until create() is
        called
        """
        
        self.windowTitle = maya.stringTable['y_quickRigUI.kQuickRigWindowName' ]
        self.windowName  = windowName
        
        # This is the default error handler.  It can be overwritten if, for instance
        # some scripting tool wants to be notified in a different way.
        self.handleError = QuickRigTool.__handleError
        # Same idea for confirmation requests.
        self.requestConfirmation = QuickRigTool.__requestConfirmation
    
    
    def create( self ):
        """
        This method completely builds the UI.  It shows the resulting window
        when it is fully created.
        """
        
        # Initialize needed scripts.
        qrInitialize( )
        
        
        # Destroy current window if it already exists.
        if cmds.window( self.windowName , exists=True ):
            cmds.deleteUI( self.windowName )
        
        # Create the window.
        cmds.window( self.windowName , title=self.windowTitle )
        
        # Create the main layout.
        with LayoutManager( cmds.scrollLayout( childResizable=True ) ):
            with LayoutManager( cmds.columnLayout( adjustableColumn=True ) ):
                # Character options
                with LayoutManager( cmds.rowLayout( numberOfColumns=5 , adjustableColumn=1 ) ):
                    self.characterMenu = cmds.optionMenuGrp(
                        label=maya.stringTable['y_quickRigUI.kCharacter' ] ,
                        cw=( 1 , 60 ) ,
                        w=1 , # This makes the textbox not stretch the scrollLayout when the name gets long
                        adjustableColumn=2 ,
                        changeCommand=self._callbackTool( callback_step0_UpdateCharacterButtons )
                        ) + '|OptionMenu'
                    # Adding a default value so there is always at least something in the menu list.
                    cmds.menuItem( parent=self.characterMenu , label=hikNoneString( ) )
                    
                    cmds.iconTextButton(
                        image='QR_refresh.png' ,
                        command=self._callbackTool( callback_step0_RefreshCharacterList ) ,
                        annotation=maya.stringTable['y_quickRigUI.kRefreshCharacterList'  ]
                        )
                    cmds.iconTextButton(
                        image='QR_add.png' ,
                        command=self._callbackTool( callback_step0_CreateCharacter ) ,
                        annotation=maya.stringTable['y_quickRigUI.kCreateCharacter'  ]
                        )
                    self.buttonRename = cmds.iconTextButton(
                        image='QR_rename.png' ,
                        command=self._callbackTool( callback_step0_RenameCharacter ) ,
                        annotation=maya.stringTable['y_quickRigUI.kRenameCharacter'  ]
                        )
                    self.buttonDelete = cmds.iconTextButton(
                        image='QR_delete.png' ,
                        command=self._callbackTool( callback_step0_DeleteCharacter ) ,
                        annotation=maya.stringTable['y_quickRigUI.kDeleteCharacter'  ]
                        )
                
                # Radio button to switch mode.
                self.layoutModes = cmds.formLayout( )
                with LayoutManager( self.layoutModes ):
                    self.buttonMode = cmds.radioCollection( )
                    self.radioButtonOneClick   = cmds.radioButton( onCommand=self._callbackTool( callback_step0_ChangeMode ) , label=maya.stringTable['y_quickRigUI.kOneClick' ] )
                    self.radioButtonStepByStep = cmds.radioButton( onCommand=self._callbackTool( callback_step0_ChangeMode ) , label=maya.stringTable['y_quickRigUI.kStepByStep' ] )
                    
                    cmds.formLayout(
                        self.layoutModes ,
                        edit=True ,
                        attachPosition=[ ( self.radioButtonOneClick , 'right' , 20 , 50 ) , ( self.radioButtonStepByStep , 'left' , 5 , 50 ) ]
                        )
                
                # First tab: one-click rig.
                self.layoutOneClick = cmds.columnLayout( adjustableColumn=True )
                with LayoutManager( self.layoutOneClick ):
                    with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kOneClickTitle' ] , **kFrameParam ) ):
                        cmds.separator( style='none', height=5 , width=kOptionsButtonWidth )
                        textOneClick = cmds.text( align='center' , label=maya.stringTable['y_quickRigUI.kSelectedCharacterMeshes' ] )
                        cmds.separator( style='none', height=5 , width=kOptionsButtonWidth )
                        with LayoutManager( cmds.formLayout() ) as buttonLayout:
                            buttonOneClick = cmds.button( label=maya.stringTable['y_quickRigUI.kAutoRig' ] , command=self._callbackTool( callback_AutoRig ) )
                            
                            cmds.formLayout(
                                buttonLayout ,
                                edit=True ,
                                attachPosition=[ ( buttonOneClick , 'left' , -100 , 50 ) , ( buttonOneClick , 'right' , -100 , 50 ) ]
                                )
                
                # Second tab: step-by-step rigging.
                self.layoutStepByStep = cmds.columnLayout( adjustableColumn=True )
                with LayoutManager( self.layoutStepByStep ):
                    # Geometry selection.
                    with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kGeometry' ] , **kFrameParam ) ):
                        with LayoutManager( cmds.rowLayout( numberOfColumns=3 ) ) as geometryLayout:
                            cmds.iconTextButton(
                                image='QR_add.png' ,
                                command=self._callbackTool( callback_step1_AddSelectedMeshes ) ,
                                annotation=maya.stringTable['y_quickRigUI.kAddSelectedMeshes'  ]
                                )
                            cmds.iconTextButton(
                                image='QR_selectAll.png' ,
                                command=self._callbackTool( callback_step1_SelectAllMeshes ) ,
                                annotation=maya.stringTable['y_quickRigUI.kSelectAllMeshes'  ]
                                )
                            cmds.iconTextButton(
                                image='QR_delete.png' ,
                                command=self._callbackTool( callback_step1_ClearMeshes ) ,
                                annotation=maya.stringTable['y_quickRigUI.kCleanMeshes'  ]
                                )
                        self.meshesList = cmds.textScrollList( height=80 )
                    
                    # Guides.
                    with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kGuides' ] , **kFrameParam ) ):
                        with LayoutManager( cmds.rowLayout( numberOfColumns=3 , adjustableColumn=2 , columnAlign3=( 'left', 'left', 'right' ) , height=kRowLayoutHeight ) ):
                            # First line, embedding method.
                            cmds.text( width=kOptionsTextWidth , label=maya.stringTable['y_quickRigUI.kEmbedMethod' ] )
                            self.segmentationMethodList = cmds.optionMenuGrp( w=1 , adjustableColumn=1 ) + '|OptionMenu'
                            cmds.menuItem( parent=self.segmentationMethodList , label=maya.stringTable['y_quickRigUI.kPerfectMeshNoVoxelization' ] )
                            cmds.menuItem( parent=self.segmentationMethodList , label=maya.stringTable['y_quickRigUI.kWatertightMeshFloodFill' ] )
                            cmds.menuItem( parent=self.segmentationMethodList , label=maya.stringTable['y_quickRigUI.kImperfectMeshFloodFillGrowing' ] )
                            cmds.menuItem( parent=self.segmentationMethodList , label=maya.stringTable['y_quickRigUI.kPolygonSoupRepair' ] )
                            cmds.menuItem( parent=self.segmentationMethodList , label=maya.stringTable['y_quickRigUI.kNoEmbedding' ] )
                            cmds.optionMenu( self.segmentationMethodList , edit=True , select=3 )
                            cmds.iconTextButton( image1=mel.eval( 'languageResourcePath QR_help.png' ) , command=self._callbackTool( callback_step2_ShowSegmentationHelp ) , width=kOptionsButtonWidth )
                            
                        with LayoutManager( cmds.rowLayout( numberOfColumns=3 , adjustableColumn=2 , columnAlign3=( 'left', 'left', 'right' ) , height=kRowLayoutHeight ) ):
                            # Second line, 
                            cmds.text( width=kOptionsTextWidth , label=maya.stringTable['y_quickRigUI.kResolution' ] )
                            self.resolutionList = cmds.optionMenuGrp( w=1 , adjustableColumn=1 ) + '|OptionMenu'
                            for resolution in kResolutions:
                                cmds.menuItem( parent=self.resolutionList , label=str(resolution) )
                            cmds.optionMenu( self.resolutionList , edit=True , select=3 )
                            cmds.separator( style='none', height=5 , width=kOptionsButtonWidth )
                        
                        with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kGuideSettings' ] , marginWidth=kFrameMarginWidth , collapse=True , collapsable=True ) ):
                            cmds.text( label=maya.stringTable['y_quickRigUI.kCharacterOrientation' ] )
                            with LayoutManager( cmds.rowLayout( numberOfColumns=2 , adjustableColumn=2 , columnAlign2=( 'left', 'left' ) , height=kRowLayoutHeight ) ):
                                cmds.text( label=maya.stringTable['y_quickRigUI.kSymmetry' ] )
                                self.symmetryList = cmds.optionMenuGrp( w=1 , adjustableColumn=1 ) + '|OptionMenu'
                                for option in kSymmetryOptions:
                                    cmds.menuItem( parent=self.symmetryList , label=option[ 0 ] )
                                cmds.optionMenu( self.symmetryList , edit=True , select=1 )
                            
                            with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kCenter' ] , marginWidth=kFrameMarginWidth , collapse=False , collapsable=True ) ):
                                with LayoutManager( cmds.formLayout( ) ) as centerForm:
                                    # These values are copied from hikSkeletonUI.mel.
                                    textSpine = cmds.text( label=maya.stringTable['y_quickRigUI.kSpineCount' ] )
                                    fieldSpine = cmds.intField( width=kSkeletonFieldWidth , minValue=1 , maxValue=10 , value=3 , step=1 )
                                    
                                    textNeck = cmds.text( label=maya.stringTable['y_quickRigUI.kNeckCount' ] )
                                    fieldNeck = cmds.intField( width=kSkeletonFieldWidth , minValue=0 , maxValue=10 , value=1 , step=1 )
                                    
                                    textShoulder = cmds.text( label=maya.stringTable['y_quickRigUI.kShoulderCount' ] )
                                    fieldShoulder = cmds.intField( width=kSkeletonFieldWidth , minValue=0 , maxValue=2 , value=1 , step=1 )
                                    
                                    cmds.formLayout(
                                        centerForm ,
                                        edit=True ,
                                        attachForm=[(textSpine, 'top' , 8), (textSpine, 'left' , 10) , (fieldSpine, 'top' , 5), (fieldSpine, 'left' , 110)]
                                        )
                                    cmds.formLayout(
                                        centerForm ,
                                        edit=True ,
                                        attachControl=[(textNeck, 'top' , 7, textSpine), (fieldNeck, 'top' , 4, textSpine)] ,
                                        attachForm=[(textNeck, 'left' , 10), (fieldNeck, 'left' , 110)]
                                        )
                                    cmds.formLayout(
                                        centerForm ,
                                        edit=True ,
                                        attachControl=[(textShoulder, 'top' , 7, textNeck), (fieldShoulder, 'top' , 4, textNeck)] ,
                                        attachForm=[(textShoulder, 'left' , 10), (fieldShoulder, 'left' , 110), (fieldShoulder, 'bottom' , 5)]
                                        )
                                    
                                    self.fieldSpine    = fieldSpine
                                    self.fieldNeck     = fieldNeck
                                    self.fieldShoulder = fieldShoulder
                        
                            with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kExtra' ] , marginWidth=kFrameMarginWidth , collapse=False , collapsable=True ) ):
                                self.checkboxHipsTranslation = cmds.checkBox( label=maya.stringTable['y_quickRigUI.kHipsTranslation' ] , value=False )
                        
                        with LayoutManager( cmds.rowLayout( numberOfColumns=2 , adjustableColumn=1 ) ):
                            cmds.button( label=maya.stringTable['y_quickRigUI.kGuidesCreateUpdate' ] , command=self._callbackTool( callback_step2_CreateGuides ) )
                            cmds.iconTextButton(
                                image='QR_delete.png' ,
                                command=self._callbackTool( callback_step2_DeleteGuides ) ,
                                annotation=maya.stringTable['y_quickRigUI.kGuidesDelete'  ]
                                )
                    
                    # User adjustments.
                    with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kUserAdjustmentOfGuides' ] , **kFrameParam ) ):
                        with LayoutManager( cmds.rowLayout( numberOfColumns=7 ) ):
                            cmds.iconTextButton(
                                image='QR_mirrorGuidesLeftToRight_150.png' ,
                                command=self._callbackTool( callback_step3_MirrorGuidesLeftToRight ) ,
                                annotation=maya.stringTable['y_quickRigUI.kMirrorSelectedGuidesLeftToRight'  ]
                                )
                            cmds.iconTextButton(
                                image='QR_mirrorGuidesRightToLeft_150.png' ,
                                command=self._callbackTool( callback_step3_MirrorGuidesRightToLeft ) ,
                                annotation=maya.stringTable['y_quickRigUI.kMirrorSelectedGuidesRightToLeft'  ]
                                )
                            cmds.iconTextButton(
                                image='QR_selectAll_150.png' ,
                                command=self._callbackTool( callback_step3_SelectAllGuides ) ,
                                annotation=maya.stringTable['y_quickRigUI.kSelectAllGuides'  ]
                                )
                            cmds.iconTextButton(
                                image='QR_show_150.png' ,
                                command=self._callbackTool( callback_step3_ShowAllGuides ) ,
                                annotation=maya.stringTable['y_quickRigUI.kShowAllGuides'  ]
                                )
                            cmds.iconTextButton(
                                image='QR_hide_150.png' ,
                                command=self._callbackTool( callback_step3_HideAllGuides ) ,
                                annotation=maya.stringTable['y_quickRigUI.kHideAllGuides'  ]
                                )
                            cmds.iconTextButton(
                                image='QR_xRay_150.png' ,
                                command=self._callbackTool( callback_step3_EnableXRayJoints ) ,
                                annotation=maya.stringTable['y_quickRigUI.kEnableXRayJoints'  ]
                                )
                            with LayoutManager( cmds.formLayout( width=kColorSwatchWidth , height=kColorSwatchHeight ) ) as colorLayout:
                                self.guidesColorButton = cmds.button(
                                    enableBackground=True ,
                                    label='' ,
                                    width=kColorSwatchColorWidth ,
                                    height=kColorSwatchColorHeight ,
                                    command=self._callbackTool( callback_step3_ChooseGuidesColor ) ,
                                    annotation=maya.stringTable['y_quickRigUI.kChooseGuidesColor'  ]
                                    )
                                qruiSetGuidesColor( self , kGuidesColor )
                                
                                cmds.formLayout(
                                    colorLayout ,
                                    edit=True ,
                                    attachPosition=[
                                        ( self.guidesColorButton , 'left' , ( kColorSwatchWidth - kColorSwatchColorWidth ) / 2 , 0 ) ,
                                        ( self.guidesColorButton , 'top' , ( kColorSwatchHeight - kColorSwatchColorHeight ) / 2 , 0 )
                                        ]
                                    )
                        
                        with LayoutManager( cmds.formLayout( ) ) as adjustmentLayout:
                            textAdjustment = cmds.text( align='center' , label=maya.stringTable['y_quickRigUI.kManuallyMoveGuides' ] )
                            
                            cmds.formLayout(
                                adjustmentLayout ,
                                edit=True ,
                                attachPosition=[ ( textAdjustment , 'left' , 0 , 0 ) , ( textAdjustment , 'right' , 0 , 100 ) ]
                                )
                    
                    # Skeleton and rig generation.
                    with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kSkeletonGeneration' ] , **kFrameParam ) ):
                        with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.kSkeletonSettings' ] , marginWidth=kFrameMarginWidth , collapse=True , collapsable=True ) ):
                            self.checkboxTStanceCorrection = cmds.checkBox( label=maya.stringTable['y_quickRigUI.kTStanceCorrection' ] , value=True )
                            with LayoutManager( cmds.rowLayout( numberOfColumns=2 , adjustableColumn=2 , columnAlign2=( 'left', 'left' ) , height=kRowLayoutHeight ) ):
                                cmds.text( label=maya.stringTable['y_quickRigUI.kJointXAxisAlignment' ] )
                                self.orientJointsList = cmds.optionMenuGrp( w=1 , adjustableColumn=1 ) + '|OptionMenu'
                                for option in kOrientJointsOptions:
                                    cmds.menuItem( parent=self.orientJointsList , label=option[ 0 ] )
                                cmds.optionMenu( self.orientJointsList , edit=True , select=1 )
                        
                        self.skeletonControlRigList = cmds.optionMenuGrp( w=1 , adjustableColumn=1 ) + '|OptionMenu'
                        cmds.menuItem( parent=self.skeletonControlRigList , label=maya.stringTable['y_quickRigUI.kGenerationSkeletonOnly' ] )
                        cmds.menuItem( parent=self.skeletonControlRigList , label=maya.stringTable['y_quickRigUI.kGenerationSkeletonAndControlRig' ] )
                        cmds.optionMenu( self.skeletonControlRigList , edit=True , select=2 )
                        with LayoutManager( cmds.rowLayout( numberOfColumns=2 , adjustableColumn=1 ) ):
                            cmds.button( label=maya.stringTable['y_quickRigUI.kSkeletonCreateUpdate' ] , command=self._callbackTool( callback_step4_CreateSkeleton ) )
                            cmds.iconTextButton(
                                image='QR_delete.png' ,
                                command=self._callbackTool( callback_step4_DeleteSkeleton ) ,
                                annotation=maya.stringTable['y_quickRigUI.kSkeletonDelete'  ]
                                )
                    
                    # Skinning.
                    with LayoutManager( cmds.frameLayout( label=maya.stringTable['y_quickRigUI.Skinning' ] , **kFrameParam ) ):
                        with LayoutManager( cmds.rowLayout( numberOfColumns=3 , adjustableColumn=2 , columnAlign3=( 'left', 'left', 'right' ) , height=kRowLayoutHeight ) ):
                            cmds.text( width=kOptionsTextWidth , label=maya.stringTable['y_quickRigUI.kBindingMethod' ] )
                            self.bindingMethodList = cmds.optionMenuGrp( w=1 , adjustableColumn=1 ) + '|OptionMenu'
                            for option in kSkinBindingOptions:
                                cmds.menuItem( parent=self.bindingMethodList , label=option )
                            cmds.optionMenu( self.bindingMethodList , edit=True , select=1 )
                            cmds.iconTextButton( image1=mel.eval( 'languageResourcePath QR_settings.png' ) , command=self._callbackTool( callback_step5_BindOptions ) , width=kOptionsButtonWidth )
                        
                        with LayoutManager( cmds.rowLayout( numberOfColumns=2 , adjustableColumn=1 ) ):
                            cmds.button( label=maya.stringTable['y_quickRigUI.kSkinCreateUpdate' ] , command=self._callbackTool( callback_step5_BindSkin ) )
                            cmds.iconTextButton(
                                image='QR_delete.png' ,
                                command=self._callbackTool( callback_step5_DeleteSkin ) ,
                                annotation=maya.stringTable['y_quickRigUI.kSkinDelete'  ]
                                )
        
        # Update the UI.
        cmds.radioCollection( self.buttonMode , edit=True , select=self.radioButtonOneClick )
        self.updateUI( )
        
        # Add callbacks as Maya scriptJob.
        self.scriptJobFileNew = cmds.scriptJob( event=( 'deleteAll' , self._callbackTool( callback_scriptJob_deleteAll ) ) )
        cmds.scriptJob( uiDeleted=( self.windowName , self._callbackTool( callback_scriptJob_uiDeleted ) ) )
        
        # Show the window.
        cmds.showWindow( self.windowName )
        cmds.window( self.windowName , edit=True , widthHeight=(350, 610) )
    
    
    def _updateCharacterList( self ):
        """
        This method refreshes the character list at the top of the tool.
        
        It also enables or disables the rename / delete buttons based the
        currently selected character.
        """
        
        # OPTME: We could check if the list needs to be updated, but this requires
        #        looping over all the menu items as well.
        oldItems = cmds.optionMenu( self.characterMenu , query=True , itemListLong=True ) or []
        newItems = [ hikNoneString( ) ] + qrGetSceneCharacters( )
        
        # Clean up old list.
        for item in oldItems:
            cmds.deleteUI( item )
        
        # Add characters.
        for character in newItems:
            cmds.menuItem( parent=self.characterMenu , label=character )
        
        # Select the current character.
        try:
            indexToSet = newItems.index( hikGetCurrentCharacter( ) )
        except ValueError:
            hikSetCurrentCharacter( '' )
            indexToSet = 0
        cmds.optionMenu( self.characterMenu , edit=True , select=indexToSet+1 )
    
    
    def _updateCharacterButtons( self ):
        """
        This method enables or disables the rename / delete buttons based the
        currently selected character.
        """
        
        characterIndex = cmds.optionMenu( self.characterMenu , query=True , select=True )
        
        enabled = ( characterIndex != 1 )
        cmds.iconTextButton( self.buttonRename , edit=True , enable=enabled )
        cmds.iconTextButton( self.buttonDelete , edit=True , enable=enabled )
    
    
    def _updateModes( self ):
        """
        This method shows the proper UI (one-click VS step-by-step) depending
        on the selected mode.
        """
        
        character = qruiGetCharacter( self )
        visibleOneClick = cmds.radioButton( self.radioButtonOneClick , query=True , select=True )
        visibleStepByStep = cmds.radioButton( self.radioButtonStepByStep , query=True , select=True )
        
        cmds.layout( self.layoutOneClick   , edit=True , visible=visibleOneClick )
        cmds.layout( self.layoutStepByStep , edit=True , visible=visibleStepByStep )
        
        # We would like the widget to handle this, but apparently it does not
        # gray the background color properly.
        enabled = True if character else False
        cmds.layout( self.layoutStepByStep , edit=True , enable=enabled )
        qruiEnableGuidesColor( self , enabled )
    
    
    def updateUI( self ):
        """
        This method performs a full UI refresh.
        
        It refreshes the character list and its associated buttons.  It also
        refreshes the HumanIK tool.
        """
        
        # Apparently, updating the modes first reduces flickering when switching
        # from None character to an actual character and vice-versa.
        self._updateCharacterList( )
        self._updateCharacterButtons( )
        self._updateModes( )
        qruiRefreshMeshes( self )
        qruiRefreshGuidesColor( self )
        
        hikUpdateTool( )
    
    
    @staticmethod
    def __handleError( message ):
        """
        This method is the default error handler for user errors.
        
        It simply shows a dialog box with the error message.
        """
        
        showMessageBox(
            title=maya.stringTable['y_quickRigUI.kErrorTitle' ] ,
            message=message ,
            icon='critical'
            )
    
    
    @staticmethod
    def __requestConfirmation( title , message ):
        """
        This method is the default handler to request confirmation.
        
        It simply shows a ok / cancel dialog box with the message.
        """
        
        return showConfirmationDialog( title , message )
    
    
    @staticmethod
    def __callbackWrapper( *args , **kwargs ):
        """
        This method is a wrapper in the form expected by UI elements.
        
        Its signature allows it to be flexible with regards to what UI elements
        expects.  Then it simply calls the given functor.
        """
        
        kwargs[ 'functor' ]( )
    
    
    def _callbackTool( self , function ):
        """
        This method returns a callback method that can be used by the UI
        elements.
        
        It wraps the "easier to define" callbacks that only takes the tool as
        an element into the callbacks that UI element expects.
        """
        
        functor = partial( function , tool=self )
        return partial( QuickRigTool.__callbackWrapper , functor=functor )




###############################################################################
#                                                                             #
#  Helpers for UI callbacks                                                   #
#                                                                             #
#  These allows the definition, for each step, of:                            #
#  - The input needed by this step.                                           #
#  - The output it produces (and therefore that might need to be deleted).    #
#  - The actual deletion of its output.                                       #
#                                                                             #
#                                                                             #
###############################################################################
class UserException( Exception ):
    """
    This class is the exception class for errors caused by improper user
    interaction.
    """
    
    def __init__( self , message ):
        self.message = message


def getInput_step0( input ):
    # The tool should have been set.
    assert( hasattr( input , 'tool' ) )
    
    # This step needs the character.
    input.character = qruiGetCharacter( input.tool )
    if not input.character:
        message = maya.stringTable['y_quickRigUI.kNoCharacterErrorMessage' ]
        raise UserException( message )
    
    hikSetCurrentCharacter( input.character )


def getOutput_step0( input ):
    objects = [ ]
    
    if input.character:
        objects.append( 'Character' )
    
    return objects


def removeOutput_step0( input ):
    hikDeleteWholeCharacter( input.character )


def getInput_step1( input ):
    # The character should have been set.
    assert( hasattr( input , 'character' ) )


def getOutput_step1( input ):
    # Nothing to output.
    return [ ]


def removeOutput_step1( input ):
    # Nothing to remove.
    pass


def getInput_step2( input ):
    # Get the meshes.
    input.meshes = qrGetMeshes( input.character )
    if not input.meshes:
        message = maya.stringTable['y_quickRigUI.kNoMeshErrorMessage' ]
        raise UserException( message )
    
    # Get segmentation method.
    segmentationMethod       = cmds.optionMenu( input.tool.segmentationMethodList , query=True , select=True )
    input.segmentationMethod = { 1 : 0 , 2 : 1 , 3 : 2 , 4 : 3 , 5 : 99 }[ int(segmentationMethod) ]
    
    # Get resolution.
    resolution               = cmds.optionMenu( input.tool.resolutionList         , query=True , select=True )
    input.resolution         = kResolutions[ int(resolution) - 1 ]
    
    # Get symmetry setting.
    symmetryChoice = cmds.optionMenu( input.tool.symmetryList , query=True , select=True )
    input.useSymmetry   = kSymmetryOptions[ symmetryChoice - 1 ][ 1 ]
    input.symmetryJoint = kSymmetryOptions[ symmetryChoice - 1 ][ 2 ]
    
    # Hard-coded symmetry axis.
    input.symmetryAxis = kCharacterSymmetryAxis
    
    # Get skeleton settings.
    input.skeletonParameters = {
        # Center.
        'NeckCount'     : cmds.intField( input.tool.fieldNeck     , query=True , value=True ) ,
        'ShoulderCount' : cmds.intField( input.tool.fieldShoulder , query=True , value=True ) ,
        'SpineCount'    : cmds.intField( input.tool.fieldSpine    , query=True , value=True ) ,
        # Fingers.
        'WantIndexFinger'  : 0 ,
        'WantMiddleFinger' : 0 ,
        'WantRingFinger'   : 0 ,
        'WantPinkyFinger'  : 0 ,
        'WantThumb'        : 0 ,
        # Extra.
        'WantHipsTranslation' : 1 if cmds.checkBox( input.tool.checkboxHipsTranslation , query=True , value=True ) else 0 ,
        }
    
    # IMPME: For now, these are hard-coded values, but there should be a UI for them.
    input.tweakParameters = qrGetDefaultTweakParameters( )


def getOutput_step2( input ):
    objects = [ ]
    
    guidesNode = qrGetGuidesNode( input.character )
    if guidesNode:
        objects.append( 'Guides' )
    
    return objects


def removeOutput_step2( input ):
    qrDeleteGuidesNode( input.character )


def getInput_step3( input ):
    # Get the guides.
    input.guidesNode = qrGetGuidesNode( input.character )
    if not input.guidesNode:
        message = maya.stringTable['y_quickRigUI.kNoEmbeddingErrorMessage' ]
        raise UserException( message )
    
    # Get the bounding box.
    input.boundingBox = qrGetBoundingBoxFromGuidesNode( input.guidesNode )


def getOutput_step3( input ):
    # Nothing to output.
    return [ ]


def removeOutput_step3( input ):
    # Nothing to remove.
    pass


def getInput_step4( input ):
    # Make sure the settings are the same.
    guides = qrGetGuidesNodesFromGuidesNode( input.guidesNode ).keys( )
    guides.sort( )
    requiredGuides = qrGetRequiredGuides( input.skeletonParameters )
    requiredGuides.sort( )
    if guides != requiredGuides:
        message = maya.stringTable['y_quickRigUI.kWrongParametersErrorMessage' ]
        raise UserException( message )
    
    # Get parameters.
    input.useTStanceCorrection = cmds.checkBox( input.tool.checkboxTStanceCorrection , query=True , value=True )
    
    jointOrientsChoice = cmds.optionMenu( input.tool.orientJointsList , query=True , select=True )
    input.useOrientation     = kOrientJointsOptions[ jointOrientsChoice - 1 ][ 1 ]
    input.orientTowardsChild = kOrientJointsOptions[ jointOrientsChoice - 1 ][ 2 ]
    
    input.skeletonControlRig = cmds.optionMenu( input.tool.skeletonControlRigList , query=True , select=True )


def getOutput_step4( input ):
    objects = [ ]
    
    if hikGetControlRig( input.character ):
        objects.append( 'Control rig' )
    
    if hikGetSkeletonGeneratorNode( input.character ):
        objects.append( 'Skeleton generator node' )
    
    if qrGetSkeletonRootNode( input.character ):
        objects.append( 'Skeleton' )
    
    return objects


def removeOutput_step4( input ):
    hikDeleteControlRig( input.character )
    
    skeletonGeneratorNode = hikGetSkeletonGeneratorNode( input.character )
    if skeletonGeneratorNode:
        cmds.delete( skeletonGeneratorNode )
    
    qrDeleteSkeleton( input.character )


def getInput_step5( input ):
    # Get the skeleton.
    input.skeletonRootNode = qrGetSkeletonRootNode( input.character )
    input.skeletonNodes    = hikGetSkeletonNodesMap( input.character ).values( )
    
    if not input.skeletonRootNode or not input.skeletonNodes:
        message = maya.stringTable['y_quickRigUI.kNoSkeletonErrorMessage' ]
        raise UserException( message )
    
    # Bind skin index.
    input.bindSkinIndex = cmds.optionMenu( input.tool.bindingMethodList , query=True , select=True )


def getOutput_step5( input ):
    objects = [ ]
    
    meshes = qrGetMeshes( input.character )
    if meshes:
        if checkIfSkinExists( meshes ):
            objects.append( 'Skin' )
    
    return objects


def removeOutput_step5( input ):
    # Detach existing skin if it exists.
    meshes = qrGetMeshes( input.character )
    if meshes:
        detachSkinFromMesh( meshes )


def getInputs( tool , level , deleteOutput ):
    kGetInputFunctions = [
        getInput_step0 ,
        getInput_step1 ,
        getInput_step2 ,
        getInput_step3 ,
        getInput_step4 ,
        getInput_step5 ,
        ]
    kGetOutputFunctions = [
        getOutput_step0 ,
        getOutput_step1 ,
        getOutput_step2 ,
        getOutput_step3 ,
        getOutput_step4 ,
        getOutput_step5 ,
        ]
    kRemoveOutputFunctions = [
        removeOutput_step0 ,
        removeOutput_step1 ,
        removeOutput_step2 ,
        removeOutput_step3 ,
        removeOutput_step4 ,
        removeOutput_step5 ,
        ]
    
    # Create the input.
    input = createContainer( )
    input.tool = tool
    
    # Get the input up to the level.
    for getInput in kGetInputFunctions[ 0 : level + 1 ]:
        getInput( input )
    
    if deleteOutput:
        # Save the selection.
        selection = cmds.ls( selection=True )
        
        # Get the current output to delete.
        outputs = [ ]
        for getOutput in reversed( kGetOutputFunctions[ level : ] ):
            outputs += getOutput( input )
        
        if outputs:
            # Ask for confirmation before deleting.
            title = 'Confirm deletion'
            message = ( 'Are you sure you want to delete the following object%s:\n' % ( 's' if len( outputs ) > 1 else '' ) )
            for item in outputs:
                message += '\n- ' + item
            
            confirmed = tool.requestConfirmation( title , message )
            if not confirmed:
                # Stop right here.
                return None
            
            # Delete the output.
            for removeOutput in reversed( kRemoveOutputFunctions[ level : ] ):
                removeOutput( input )
        
        # Restore selection.  Some objects might have been deleted.
        selection = [ node for node in selection if cmds.objExists( node ) ]
        cmds.select( selection , replace=True )
    
    return input


def tool_to_input( level , deleteOutput=True ):
    """
    This decorator takes a function which takes "callback input" and wraps it
    into a function which takes the tool as an input.
    
    Callback input is extracted from the character and the tool based on the
    given level required, each level corresponding to a step of the rigging
    process.  The decorator handles making sure that output of further steps is
    deleted if allowed by the user.
    """
    
    # Define the function returned by this decorator.
    def _wrap( f ):
        
        @wraps( f )
        def _decorated_f( *args , **kwargs ):
            try:
                # Extract the tool from the parameter.
                tool = kwargs[ 'tool' ]
                
                # Create the input.
                input = getInputs( tool , level , deleteOutput )
                if not input:
                    return False
                
                # Replace the tool parameter by input.
                assert( 'input' not in kwargs )
                newKwargs = dict( kwargs )
                newKwargs.pop( 'tool' )
                newKwargs[ 'input' ] = input
                
                # Ready to go: execute the actual callback.
                f( *args , **newKwargs )
                
                return True
            
            except UserException as exception:
                tool.handleError( exception.message )
                
                return False
        
        return _decorated_f
    
    return _wrap




###############################################################################
#                                                                             #
#  UI callbacks                                                               #
#                                                                             #
###############################################################################
def callback_step0_UpdateCharacterButtons( tool ):
    character = qruiGetCharacter( tool )
    hikSetCurrentCharacter( character )
    
    tool.updateUI( )


def callback_step0_CreateCharacter( tool ):
    # Save the selection.
    selection = cmds.ls( selection=True )
    
    # Create the character.
    newCharacter = hikCreateCharacter( 'QuickRigCharacter' )
    assert( newCharacter )
    
    # Add the Quick Rig specific info.
    qrAddInfoAttribute( newCharacter )
    
    # Restore selection.
    cmds.select( selection , replace=True )
    
    tool.updateUI( )


def callback_step0_RefreshCharacterList( tool ):
    tool.updateUI( )


def callback_step0_RenameCharacter( tool ):
    character = qruiGetCharacter( tool )
    if not character:
        tool.handleError( maya.stringTable['y_quickRigUI.kRenameCharacterError' ] )
        return
    
    hikRenameDefinition( character )
    
    # The new character name will be current.
    newCharacter = hikGetCurrentCharacter( )
    if character != newCharacter:
        # Rename the guides, if any.
        guidesNode = qrGetGuidesNode( newCharacter )
        if guidesNode:
            # Use Mel to get the exact same renaming results as the other nodes
            # connected to the character.
            newName = mel.eval( 'substitute "%s" "%s" "%s"' % ( character , guidesNode , newCharacter ) )
            cmds.rename( guidesNode , newName )
    
    tool.updateUI( )


@tool_to_input( 0 )
def callback_step0_DeleteCharacter( input ):
    # Nothing to do, output will have been deleted.
    # Update UI.
    input.tool.updateUI( )


def callback_step0_ChangeMode( tool ):
    # OPTME: No need to update the whole UI.
    tool.updateUI( )


@tool_to_input( 1 )
def callback_step1_AddSelectedMeshes( input ):
    # First, check that no nurbs or subdivision surfaces are selected.
    warningShapes = getSelectedShapes( [ 'nurbsSurface' , 'subdiv' ] )
    if warningShapes:
        # Simply display a warning.
        if len( warningShapes ) == 1:
            message = maya.stringTable['y_quickRigUI.kWarningNonMeshShapeSingular' ]
        else:
            message = maya.stringTable['y_quickRigUI.kWarningNonMeshShapePlural' ]
        
        for shape in warningShapes:
            message += '\n- %s' % shape
        
        cmds.warning( message )
    
    # Add the new meshes.
    meshes = qrGetMeshes( input.character )
    
    meshesToAdd = [ mesh for mesh in getSelectedShapes( [ 'mesh' ] ) if mesh not in meshes ]
    qrAddMeshes( input.character , meshesToAdd )
    
    qruiRefreshMeshes( input.tool )


# This callback can work without any pre-condition.
def callback_step1_SelectAllMeshes( tool ):
    # Select all meshes.
    meshes = cmds.ls( type='mesh' ) or []
    cmds.select( meshes , replace=True )


@tool_to_input( 1 )
def callback_step1_ClearMeshes( input ):
    # Clear list.
    qrClearMeshes( input.character )
    qruiRefreshMeshes( input.tool )


# This callback can work without any pre-condition.
def callback_step2_ShowSegmentationHelp( tool ):
    # Get the selected segmentation method.
    segmentationMethod = cmds.optionMenu( tool.segmentationMethodList , query=True , select=True )
    
    # Selection indices are 1-based.
    # These string should be kept in sync with the documentation of the
    # segmentationMethod flag of the skeletonEmbed command.
    helpStrings = {
        1 : {
            'title' : maya.stringTable[ 'y_quickRigUI.kPerfectMeshTitleString'   ] ,
            'help'  : maya.stringTable[ 'y_quickRigUI.kPerfectMeshHelpString'    ]
        } ,
        2 : {
            'title' : maya.stringTable[ 'y_quickRigUI.kWatertightMeshTitleString'   ] ,
            'help'  : maya.stringTable[ 'y_quickRigUI.kWatertightMeshHelpString'    ]
        } ,
        3 : {
            'title' : maya.stringTable[ 'y_quickRigUI.kImperfectMeshTitleString'   ] ,
            'help'  : maya.stringTable[ 'y_quickRigUI.kImperfectMeshHelpString'    ]
        } ,
        4 : {
            'title' : maya.stringTable[ 'y_quickRigUI.kPolygonSoupTitleString'   ] ,
            'help'  : maya.stringTable[ 'y_quickRigUI.kPolygonSoupHelpString'    ]
        } ,
        5 : {
            'title' : maya.stringTable[ 'y_quickRigUI.kNoEmbeddingTitleString'   ] ,
            'help'  : maya.stringTable[ 'y_quickRigUI.kNoEmbeddingHelpString'    ]
        }
    }
    windowTitleString = maya.stringTable['y_quickRigUI.kSegmentationDescription' ]
    
    titleString = helpStrings[ segmentationMethod ][ 'title' ]
    helpString  = helpStrings[ segmentationMethod ][ 'help'  ]
    windowMessageString = titleString + '\n\n' + helpString
    
    # Create window.
    showMessageBox(
        title=windowTitleString ,
        message=windowMessageString ,
        icon="information"
        )


@tool_to_input( 2 )
def callback_step2_CreateGuides( input ):
    # Generate the embedded skeleton.
    try:
        result = cmds.skeletonEmbed(
            *(input.meshes) ,
            segmentationResolution=input.resolution ,
            segmentationMethod=input.segmentationMethod
            )
    except RuntimeError as e:
        message  = maya.stringTable['y_quickRigUI.kEmbeddingErrorMessage1' ]
        message += '\n\n---\n%s---\n\n' % str( e )
        message += maya.stringTable['y_quickRigUI.kEmbeddingErrorMessage2' ]
        raise UserException( message )
    
    # Generate nodes to display the results.
    try:
        embedding = json.loads( result )
    except ValueError as e:
        # This should never happen.
        # It would mean that the output of the skeletonEmbed command is not valid JSON
        # and the command did not return an error.
        message  = maya.stringTable['y_quickRigUI.kJSONErrorMessage' ]
        message += '\n\n---\n%s\n---\n\n' % str( result )
        message += '\n\n---\n%s\n---\n\n' % str( e )
        raise UserException( message )
    
    extendedEmbedding = qrGetGuidesFromEmbedding( input.skeletonParameters , input.tweakParameters , embedding )
    rootTransform = qrCreateGuidesNode( extendedEmbedding )
    guidesNode = cmds.rename( rootTransform , input.character + '_Guides' )
    
    # Set the color.
    guidesColor = qruiGetGuidesColor( input.tool )
    qrSetGuidesColor( guidesNode , guidesColor )
    
    # Store the new result.
    qrSetGuidesNode( input.character , guidesNode )
    
    # Apply symmetry constraints.
    if input.useSymmetry:
        axis = input.symmetryAxis
        
        if input.symmetryJoint:
            # Use this joint (Hips) as symmetry center.
            center = extendedEmbedding[ 'guides' ][ input.symmetryJoint ][ axis ]
        else:
            # No joint, symmetry with regards to bounding box.
            boundingBox = qrGetBoundingBoxFromGuidesNode( guidesNode )
            center      = ( boundingBox.minCorner[ axis ] + boundingBox.maxCorner[ axis ] ) * 0.5
        
        qrAverageGuides( guidesNode , center , axis )
    
    # Select the output.
    cmds.select( guidesNode , replace=True )
    
    # Show the guides by default.
    enableXRayJoints( True )


@tool_to_input( 2 )
def callback_step2_DeleteGuides( input ):
    # Nothing to do, output will have been deleted.
    pass


def callbackUtil_step3_MirrorGuides( input , leftToRight ):
    # Always apply symmetry with regards to the hips.
    axis   = input.symmetryAxis
    joint  = 'Hips'
    
    # OPTME: No need to query all the positions.
    positions = qrGetGuidesPositions( input.character )
    if not joint in positions:
        message = maya.stringTable['y_quickRigUI.kMirroringErrorMessage' ]
        raise UserException( message % joint )
    center = positions[ joint ][ axis ]
    guides = cmds.ls( selection=True )
    qrMirrorGuides( input.guidesNode , center , axis , leftToRight , guides )
    
    # Make sure guides are visible.
    qrSetGuidesVisibility( input.guidesNode , True )


@tool_to_input( 3 )
def callback_step3_MirrorGuidesLeftToRight( input ):
    # Left-to-right when facing character is right-to-left of the character.
    leftToRight = False
    callbackUtil_step3_MirrorGuides( input , leftToRight )


@tool_to_input( 3 )
def callback_step3_MirrorGuidesRightToLeft( input ):
    # Right-to-left when facing character is left-to-right of the character.
    leftToRight = True
    callbackUtil_step3_MirrorGuides( input , leftToRight )


@tool_to_input( 3 , False )
def callback_step3_SelectAllGuides( input ):
    cmds.select( input.guidesNode , replace=True )


@tool_to_input( 3 , False )
def callback_step3_ShowAllGuides( input ):
    qrSetGuidesVisibility( input.guidesNode , True )


@tool_to_input( 3 , False )
def callback_step3_HideAllGuides( input ):
    qrSetGuidesVisibility( input.guidesNode , False )


# This callback can work without any pre-condition.
def callback_step3_EnableXRayJoints( tool ):
    enableXRayJoints( True )


# This callback can work without any pre-condition.
def callback_step3_ChooseGuidesColor( tool ):
    # Get current guides color.
    currentColor = qruiGetGuidesColor( tool )
    
    # Pop-up color chooser.
    cmds.colorEditor( rgbValue=currentColor )
    if not cmds.colorEditor( query=True , result=True ):
        return
    
    newColor = cmds.colorEditor( query=True , rgbValue=True )
    
    # Set the new background color.
    qruiSetGuidesColor( tool , newColor )
    
    # If guides already exist, change their color.
    character = qruiGetCharacter( tool )
    if character:
        guidesNode = qrGetGuidesNode( character )
        if guidesNode:
            qrSetGuidesColor( guidesNode , newColor )


@tool_to_input( 4 )
def callback_step4_CreateSkeleton( input ):
    # We use the skeleton generator node to create the skeleton first,
    # then we extract the hierarchy information from the character definition.
    
    assert( input.skeletonControlRig in [ 1 , 2 ] )
    
    if input.skeletonControlRig >= 1:
        skeletonRoot = createHikSkeleton( input.character , input.skeletonParameters )
        if not skeletonRoot:
            message = maya.stringTable['y_quickRigUI.kSkeletonCreationErrorMessage' ]
            raise UserException( message )
        
        qrSetSkeletonRootNode( input.character , skeletonRoot )
        
        definition           = getCharacterDefiniton( input.character )
        guidesPosition       = qrGetGuidesPositions( input.character )
        useTStanceCorrection = input.useTStanceCorrection
        useOrientation       = input.useOrientation
        orientTowardsChild   = input.orientTowardsChild
        
        
        skeletonNodes    = hikGetSkeletonNodesMap( input.character )
        tStancePositions = computeTStance( definition , guidesPosition , useTStanceCorrection )
        jointOrients     = computeJointOrients( definition.hikInfos , tStancePositions , useOrientation , orientTowardsChild )
        positionHikSkeleton( definition.orderedJoints , skeletonNodes , tStancePositions , jointOrients )
    
    if input.skeletonControlRig >= 2 or useTStanceCorrection:
        # Create the control rig.
        hikCreateControlRig( input.character )
        
        if useTStanceCorrection:
            # Position the control rig to finish T-stance correction.
            positionHikControlRig( definition , guidesPosition )
    
    if input.skeletonControlRig < 2 and useTStanceCorrection:
        # The control rig is not required, but we used it to perform T-stance correction.
        
        # Get the output of the control rig.
        rotations = [ ( node , cmds.getAttr( '%s.rotate' % node )[ 0 ] ) for node in skeletonNodes.values( ) ]
        
        # Delete the control rig.
        hikDeleteControlRig( input.character )
        
        # Place the skeleton back to where it was.
        for node , rotation in rotations:
            cmds.setAttr( '%s.rotate' % node , *rotation )
    
    
    # Hide the guides.
    qrSetGuidesVisibility( input.guidesNode , False )
    
    # Update the tool to make sure characterization is reflected.
    hikUpdateTool( )


@tool_to_input( 4 )
def callback_step4_DeleteSkeleton( input ):
    # Nothing to do, output will have been deleted.
    # Simply show the guides.
    qrSetGuidesVisibility( input.guidesNode , True )


@tool_to_input( 5 )
def callback_step5_BindOptions( input ):
    # Select the bounding box option corresponding to "Current Settings".
    # The index is 0-based, the command takes 1-based.
    cmds.optionMenu( input.tool.bindingMethodList , edit=True , select=kSkinBindingCurrentSettingsIndex+1 )
    
    # Select the meshes and skeleton.
    itemsToSelect = input.meshes + input.skeletonNodes
    cmds.select( itemsToSelect , replace=True )
    
    # Set up the variables for the chosen mode.
    if input.bindSkinIndex == 1:
        # Default GVB.
        setDefaultOptionsGVB( input.resolution )
    elif input.bindSkinIndex == 2:
        # Nothing to do.
        pass
    else:
        assert( False )
    
    # Simply use binding options dialog.
    mel.eval( 'SmoothBindSkinOptions' )


@tool_to_input( 5 )
def callback_step5_BindSkin( input ):
    # Select meshes and skeleton.
    itemsToSelect = input.meshes + input.skeletonNodes
    cmds.select( itemsToSelect , replace=True )
    
    if input.bindSkinIndex == 1:
        # Default GVB.
        setDefaultOptionsGVB( input.resolution )
    elif input.bindSkinIndex == 2:
        # Nothing to do, just use current settings.
        pass
    else:
        assert( False )
    
    # Run the binding.
    mel.eval( 'SmoothBindSkin' )


@tool_to_input( 5 )
def callback_step5_DeleteSkin( input ):
    # Nothing to do, output will have been deleted.
    pass


def callback_scriptJob_deleteAll( tool ):
    # Defensive programming: we want this callback never to report an error.
    try:
        tool.updateUI( )
    except:
        pass


def callback_scriptJob_uiDeleted( tool ):
    # Defensive programming: we want this callback never to report an error.
    try:
        # Unregister the "File -> New" callback.
        cmds.scriptJob( kill=tool.scriptJobFileNew )
    except:
        pass


def callback_AutoRig( tool ):
    # Create a progress bar.
    window = cmds.window( title=maya.stringTable['y_quickRigUI.kAutoRigProgress' ] )
    
    try:
        if qruiGetCharacter( tool ):
            # Clean existing outputs, if any.
            input = getInputs( tool , 1 , True )
            if not input:
                # User did not want to clean existing outputs.
                return
        else:
            # No character selected, create one.
            callback_step0_CreateCharacter( tool=tool )
        
        # Set up progress bar.
        cmds.columnLayout( )
        progressControl = cmds.progressBar( maxValue=5 , width=300 )
        progressText    = cmds.text( label=maya.stringTable['y_quickRigUI.kProgressAutoRig' ] , width=300 )
        cmds.showWindow( window )
        
        # 1) Geometry
        cmds.text( progressText , edit=True , label=maya.stringTable['y_quickRigUI.kProgressGeometry' ] )
        cmds.progressBar( progressControl , edit=True , step=1 )
        if not callback_step1_ClearMeshes( tool=tool ):
            return
        if not callback_step1_AddSelectedMeshes( tool=tool ):
            return
        
        # 2) Guides
        cmds.text( progressText , edit=True , label=maya.stringTable['y_quickRigUI.kProgressGuides' ] )
        cmds.progressBar( progressControl , edit=True , step=1 )
        if not callback_step2_CreateGuides( tool=tool ):
            return
        
        # 3) User Adjustment of Guides
        cmds.text( progressText , edit=True , label=maya.stringTable['y_quickRigUI.kProgressUserAdjustmentOfGuides' ] )
        cmds.progressBar( progressControl , edit=True , step=1 )
        # Nothing actually happens, but in the future it might, and anyway it gives
        # more progress percentage to the guides embedding step, which is a long one.
        
        # 4) Skeleton and Rig Generation
        cmds.text( progressText , edit=True , label=maya.stringTable['y_quickRigUI.kProgressSkeletonAndRigGeneration' ] )
        cmds.progressBar( progressControl , edit=True , step=1 )
        if not callback_step4_CreateSkeleton( tool=tool ):
            return
        
        # 5) Skinning
        cmds.text( progressText , edit=True , label=maya.stringTable['y_quickRigUI.kProgressSkinning' ] )
        cmds.progressBar( progressControl , edit=True , step=1 )
        if not callback_step5_BindSkin( tool=tool ):
            return
        
        # All done!
        cmds.progressBar( progressControl , edit=True , step=1 )
        cmds.text( progressText , edit=True , label=maya.stringTable['y_quickRigUI.kProgressDone' ] )
    finally:
        cmds.deleteUI( window )




###############################################################################
#                                                                             #
#  Quick Rig UI utility tools (methods and classes)                           #
#                                                                             #
#  These are very specific to the way the QuickRig UI is built.               #
#                                                                             #
###############################################################################
def qruiGetCharacter( tool ):
    character = cmds.optionMenu( tool.characterMenu , query=True , value=True )
    character = character if not character == hikNoneString( ) else ''
    quickRigCharacter = character if character in qrGetSceneCharacters( ) else ''
    
    return quickRigCharacter


def qruiRefreshMeshes( tool ):
    character = qruiGetCharacter( tool )
    if not character:
        return
    
    meshes = qrGetMeshes( character ) or []
    uiMeshes = cmds.textScrollList( tool.meshesList , query=True , allItems=True ) or []
    
    if meshes != uiMeshes:
        # Remove everything.
        cmds.textScrollList( tool.meshesList , edit=True , removeAll=True )
        
        # Re-add everything.
        for mesh in meshes:
            cmds.textScrollList( tool.meshesList , edit=True , append=mesh )


def qruiGetGuidesColor( tool ):
    return tool.guidesColor


def qruiSetGuidesColor( tool , color ):
    tool.guidesColor = color
    cmds.button( tool.guidesColorButton , edit=True , backgroundColor=color )


def qruiEnableGuidesColor( tool , enabled ):
    color = tool.guidesColor if enabled else kDisabledGuidesColor
    cmds.button( tool.guidesColorButton , edit=True , backgroundColor=color )


def qruiRefreshGuidesColor( tool ):
    character = qruiGetCharacter( tool )
    if not character:
        return
    
    guidesNode = qrGetGuidesNode( character )
    if not guidesNode:
        return
    
    color = qrGetGuidesColorFromGuidesNode( guidesNode )
    qruiSetGuidesColor( tool , color )




###############################################################################
#                                                                             #
#  Quick Rig utility tools (methods and classes)                              #
#                                                                             #
#  These are tools to handle Quick Rig information stored in the character    #
#  node.                                                                      #
#                                                                             #
###############################################################################
def qrInitialize( ):
    """
    This method makes sure all of the needed dependencies are loaded and
    initialized.
    
    This makes sure skinning shapes scripts are loaded, as well as HumanIK
    scripts.
    """
    
    # Make sure getSkinningShapes( ) is defined.
    mel.eval( 'source createSkinCluster.mel;' )
    # Initialize HumanIK methods.
    hikInitialize( )


def qrAddInfoAttribute( character ):
    """
    This method adds the Quick Rig info attribute to the character node.
    
    This attribute is a compound that holds information about meshes and guides
    associated with this character.
    """
    
    assert( not cmds.attributeQuery( kQuickRigInfoAttributeName , node=character , exists=True ) )
    
    cmds.addAttr( character , longName=kQuickRigInfoAttributeName , attributeType='compound' , readable=False , numberOfChildren=3 )
    cmds.addAttr( character , longName=kMeshesAttributeName       , attributeType='message'  , readable=False , parent=kQuickRigInfoAttributeName , multi=True , indexMatters=False )
    cmds.addAttr( character , longName=kGuidesAttributeName       , attributeType='message'  , readable=False , parent=kQuickRigInfoAttributeName )
    cmds.addAttr( character , longName=kSkeletonAttributeName     , attributeType='message'  , readable=False , parent=kQuickRigInfoAttributeName )


def qrIsCharacter( character ):
    """
    This method checks whether the character was created using the Quick Rig
    tool and therefore can be edited by the tool.
    """
    
    if not character:
        return None
    
    if not cmds.objExists( character ):
        return None
    
    if not cmds.attributeQuery( kQuickRigInfoAttributeName , node=character , exists=True ):
        return False
    
    expectedAttributes = [ kMeshesAttributeName , kGuidesAttributeName , kSkeletonAttributeName ]
    currentAttributes = cmds.attributeQuery( kQuickRigInfoAttributeName , node=character , listChildren=True )
    return expectedAttributes == currentAttributes


def qrGetSceneCharacters( ):
    """
    This method returns a list of names for all HumanIK characters in the
    current scene that have been created using the Quick Rig tool.
    """
    
    return [ character for character in hikGetSceneCharacters( ) if qrIsCharacter( character ) ]


def qrGetMeshes( character ):
    """
    This method returns the list of meshes associated with the given character,
    if any.
    """
    
    if not qrIsCharacter( character ):
        return None
    
    sources = getSourceNodes( character , '%s.%s' % ( kQuickRigInfoAttributeName , kMeshesAttributeName ) , shapes=True )
    
    meshes = []
    for source in sources:
        # Make sure meshes are unique.
        if source in meshes:
            continue
        
        # Make sure meshes are meshes.
        if cmds.nodeType( source ) != 'mesh':
            continue
        
        # This is a proper mesh.
        meshes.append( source )
    
    return meshes


def qrAddMeshes( character , meshesToAdd ):
    """
    This method adds the given meshes to the current character.
    """
    if not meshesToAdd:
        # Nothing to do.
        return
    
    meshAttribute = '%s.%s.%s' % ( character , kQuickRigInfoAttributeName , kMeshesAttributeName )
    lastIndex = getIndexAfterLastValidElement( meshAttribute )
    for mesh in meshesToAdd:
        cmds.connectAttr( '%s.message' % mesh , '%s[%d]' % ( meshAttribute , lastIndex ) )
        lastIndex += 1


def qrClearMeshes( character ):
    """
    This method removes all of the meshes associated with the given character.
    """
    
    if not qrIsCharacter( character ):
        return
    
    meshAttribute = '%s.%s.%s' % ( character , kQuickRigInfoAttributeName , kMeshesAttributeName )
    validIndices = cmds.getAttr( meshAttribute , multiIndices=True )
    if not validIndices:
        return
    
    for i in validIndices:
        cmds.removeMultiInstance( '%s[%d]' % ( meshAttribute , i ) , b=True )


def qrRefreshMeshes( character ):
    """
    This method makes sure meshes associated with the given character are
    stored properly in the character.
    
    It makes sure everything connected is actually a mesh, no mesh is
    duplicated and the mesh array is tightly packed.
    """
    
    meshes = qrGetMeshes( character )
    
    meshAttribute = '%s.%s.%s' % ( character , kQuickRigInfoAttributeName , kMeshesAttributeName )
    lastIndex = getIndexAfterLastValidElement( meshAttribute )
    
    if len( meshes ) == lastIndex:
        # This means the list reflects the connected meshes, nothing to do.
        return
    
    # Recreate the list.
    qrClearMeshes( character )
    
    for i , mesh in enumerate( meshes ):
        cmds.connectAttr( '%s.message' % mesh , '%s[%d]' % ( meshAttribute , i ) )


def qrGetGuidesNode( character ):
    """
    This method returns the name of the guides node associated with the given
    character, if any.
    """
    
    if not qrIsCharacter( character ):
        return None
    
    return getSourceNode( character , '%s.%s' % ( kQuickRigInfoAttributeName , kGuidesAttributeName ) )


def qrDeleteGuidesNode( character ):
    """
    This method deletes the guides from the given character, if any.
    
    It returns True if the guides were deleted, False otherwise.
    """
    
    if not qrIsCharacter( character ):
        return False
    
    guidesNode = qrGetGuidesNode( character )
    if not guidesNode:
        return False
    
    cmds.delete( guidesNode )
    
    return True


def qrSetGuidesNode( character , guidesNode ):
    """
    This method associates the guides node to the given character.
    """
    
    if not qrIsCharacter( character ):
        return False
    
    if qrGetGuidesNode( character ):
        return False
    
    cmds.connectAttr( '%s.message' % guidesNode , '%s.%s.%s' % ( character , kQuickRigInfoAttributeName , kGuidesAttributeName ) )
    
    return True


def qrGetDefaultTweakParameters( ):
    """
    This method returns the default tweak parameters for modifying the result
    of the skeletonEmbed command.
    
    At the moment, these are hard-coded, but eventually they should be
    configurable.
    """
    
    tweakParameters = createContainer( )
    
    spine = createContainer( )
    spine.tweak      = kTweakSpine
    spine.firstRatio = kTweakSpineFirstRatio
    spine.lastRatio  = kTweakSpineLastRatio
    tweakParameters.spine = spine
    
    neck = createContainer( )
    neck.tweak             = kTweakNeck
    neck.firstRatioNoTweak = kTweakNeckFirstRatioNoTweak
    neck.firstRatio        = kTweakNeckFirstRatio
    neck.lastRatio         = kTweakNeckLastRatio
    tweakParameters.neck = neck
    
    shoulder = createContainer( )
    shoulder.tweak = kTweakShoulder
    shoulder.ratio = kTweakShoulderRatio
    tweakParameters.shoulder = shoulder
    
    foot = createContainer( )
    foot.tweak                   = kTweakFoot
    foot.toeRatio                = kTweakFootToeRatio
    foot.ankleRatio              = kTweakFootAnkleRatio
    foot.useCorrectedAnkleForToe = kTweakFootUseCorrectedAnkleForToe
    tweakParameters.foot = foot
    
    hand = createContainer( )
    hand.tweak = kTweakHand
    hand.ratio = kTweakHandRatio
    tweakParameters.hand = hand
    
    return tweakParameters


def qrGetGuidesFromEmbedding( skeletonParameters , tweakParameters , embedding ):
    """
    This method takes the embedding returned by the skeletonEmbed command and
    converts it to the skeleton guides.
    
    It can add spine, neck and shoulder (clavicle) joints if requested.
    """
    
    skeletonJoints = {}
    
    # Add a joint for reference.
    minCorner = Vector3( embedding[ 'boundingBox' ][ 'min' ] )
    maxCorner = Vector3( embedding[ 'boundingBox' ][ 'max' ] )
    referenceJoints = convertReference( minCorner , maxCorner )
    skeletonJoints.update( referenceJoints )
    
    # Convert the spine.
    spineCount = skeletonParameters[ 'SpineCount' ]
    wantHipsTranslation = skeletonParameters[ 'WantHipsTranslation' ]
    hipsPosition = Vector3( embedding[ 'joints' ][ 'hips' ] )
    backPosition = Vector3( embedding[ 'joints' ][ 'back' ] )
    shouldersPosition = Vector3( embedding[ 'joints' ][ 'shoulders' ] )
    spineJoints = convertSpine( tweakParameters.spine , spineCount , wantHipsTranslation , hipsPosition , backPosition , shouldersPosition )
    skeletonJoints.update( spineJoints )
    
    # Convert the neck.
    neckCount = skeletonParameters[ 'NeckCount' ]
    headPosition = Vector3( embedding[ 'joints' ][ 'head' ] )
    neckJoints = convertNeck( tweakParameters.neck , neckCount , shouldersPosition , headPosition , ( minCorner , maxCorner ) )
    skeletonJoints.update( neckJoints )
    
    # Convert the shoulders.
    shoulderCount = skeletonParameters[ 'ShoulderCount' ]
    leftShoulderPosition  = Vector3( embedding[ 'joints' ][ 'left_shoulder' ] )
    rightShoulderPosition = Vector3( embedding[ 'joints' ][ 'right_shoulder' ] )
    shoulderJoints = convertShoulder( tweakParameters.shoulder , shoulderCount , shouldersPosition , leftShoulderPosition , rightShoulderPosition )
    skeletonJoints.update( shoulderJoints )
    
    # Convert the legs.
    for side in [ 'left' , 'right' ]:
        # Copy the side hips directly.
        targetSide = side.capitalize( )
        skeletonJoints[ targetSide + 'UpLeg'  ] = Vector3( embedding[ 'joints' ][ side + '_thigh'  ] )
        
        kneePosition  = Vector3( embedding[ 'joints' ][ side + '_knee'  ] )
        anklePosition = Vector3( embedding[ 'joints' ][ side + '_ankle' ] )
        footPosition  = Vector3( embedding[ 'joints' ][ side + '_foot'  ] )
        footJoints = convertFoot( tweakParameters.foot , kneePosition , anklePosition , footPosition )
        skeletonJoints.update( { targetSide + name : position for name , position in footJoints.iteritems( ) } )
    
    # Convert the arms.
    for side in [ 'left' , 'right' ]:
        elbowPosition = Vector3( embedding[ 'joints' ][ side + '_elbow' ] )
        handPosition  = Vector3( embedding[ 'joints' ][ side + '_hand'  ] )
        handJoints = convertHand( tweakParameters.hand , elbowPosition , handPosition )
        targetSide = side.capitalize( )
        skeletonJoints.update( { targetSide + name : position for name , position in handJoints.iteritems( ) } )
    
   # Copy everything and add the guides.
    guides = { name : [ position.x , position.y , position.z ] for name , position in skeletonJoints.iteritems( ) }
    skeletonGuides = embedding.copy( )
    skeletonGuides[ 'guides' ] = guides
    
    return skeletonGuides


def qrCreateGuidesNode( embedding ):
    """
    This method creates a node in the scene that will store the embedding
    information returned by the skeletonEmbed command.
    
    It will create a root joint to which will be parented one joint for each
    joint in the embedding.  It will also store bounding box information
    as an attribute on that root joint.
    """
    
    # We get all the parameters first, so if some are missing we have an error before we create anything.
    
    # Get the bounding box.
    boundingBox = embedding[ 'boundingBox' ]
    minCorner = boundingBox[ 'min' ]
    maxCorner = boundingBox[ 'max' ]
    # Get the joints / guides.
    skeletonJoints = embedding[ 'guides' ]
    # Get the conversion factor.
    conversionFactorCmToWorld = embedding[ 'conversionFactor' ]
    
    # Create a set of editable nodes in the scene corresponding to the embedding.
    rootJoint = cmds.createNode( 'joint' , name='Root' )
    
    # Add attributes for bounding box.
    for corner in [ 'min' , 'max' ]:
        # Create the attribute.
        attributeName = corner + 'Corner'
        cmds.addAttr( rootJoint , longName=attributeName , attributeType='compound' , numberOfChildren=3 )
        for coord in [ 'X' , 'Y' , 'Z' ]:
            cmds.addAttr( rootJoint , longName=attributeName + coord , attributeType='doubleLinear' , parent=attributeName )
        
        # Set the value.
        value = boundingBox[ corner ]
        cmds.setAttr( '%s.%s' % ( rootJoint , attributeName ) , *value )
    
    # Use the bounding box of the skeleton as a heuristic to estimate the scale of the joints.
    # Even if world units are not cm, the radius must be in cm.
    distance = ( Vector3( minCorner ) - Vector3( maxCorner ) ).length( )
    radius = distance * 0.012 / conversionFactorCmToWorld
    
    # Do not display connections to the root.
    cmds.setAttr( '%s.drawStyle' % rootJoint , 2 )
    cmds.setAttr( '%s.displayHandle' % rootJoint , 1 )
    
    # Add attribute for guides.
    cmds.addAttr( rootJoint , longName=kGuidesAttributeName , numberOfChildren=len( skeletonJoints ) , attributeType='compound' )
    for jointName in skeletonJoints:
        cmds.addAttr( rootJoint , longName=jointName , attributeType='message' , parent=kGuidesAttributeName )
    # We arbitrarily create joints in alphabetical order (the order it will show in the outliner).
    # ANSME: Should we create them in hierarchical order instead (parent before children)?
    for jointName in sorted( skeletonJoints ):
        jointPosition = skeletonJoints[ jointName ]
        joint = cmds.createNode( 'joint' , name=jointName )
        parentedJoints = cmds.parent( joint , rootJoint )
        assert( len( parentedJoints ) == 1 )
        parentedJoint = parentedJoints[ 0 ]
        # Set the right position.
        cmds.xform( parentedJoint , worldSpace=True , translation=jointPosition )
        # Connect so it can be retrieved later.
        cmds.connectAttr( '%s.message' % parentedJoint , '%s.%s.%s' % ( rootJoint , kGuidesAttributeName , jointName ) )
        # Scale the size to fit the skeleton size.
        cmds.setAttr( '%s.radius' % parentedJoint , radius )
    
    return rootJoint


def qrSetGuidesColor( guidesNode , color ):
    """
    This method sets the color on all the guides.
    """
    
    mapGuideToScene = qrGetGuidesNodesFromGuidesNode( guidesNode )
    allGuides = [ guidesNode ] + mapGuideToScene.values( )
    for guide in allGuides:
        # Change the color
        cmds.setAttr( '%s.overrideEnabled' % guide , True )
        cmds.setAttr( '%s.overrideRGBColors' % guide , True )
        cmds.setAttr( '%s.overrideColorRGB' % guide , *color )


def qrGetGuidesColorFromGuidesNode( guidesNode ):
    """
    This method sets the color from the guides node.
    
    It returns the color of the root of all the guides.
    """
    
    return cmds.getAttr( '%s.overrideColorRGB' % guidesNode )[ 0 ]


def qrGetBoundingBoxFromGuidesNode( guidesNode ):
    """
    This method extracts from the guides node an object representing the
    bounding box of the mesh(es) used for embedding.
    """
    
    if False:
        minCorner = cmds.getAttr( '%s.minCorner' % guidesNode )
        maxCorner = cmds.getAttr( '%s.maxCorner' % guidesNode )
    else:
        # FIXME: There is a bug in Maya where getting the whole compound does not do the proper linear conversion.
        #        Not doing it element per element will result wrong values when world unit is not cm.
        minCorner = []
        maxCorner = []
        for coord in [ 'X' , 'Y' , 'Z' ]:
            minCorner.append( cmds.getAttr( '%s.minCorner%s' % ( guidesNode , coord ) ) )
            maxCorner.append( cmds.getAttr( '%s.maxCorner%s' % ( guidesNode , coord ) ) )
        minCorner = [ tuple( minCorner ) ]
        maxCorner = [ tuple( maxCorner ) ]
    
    boundingBox = createContainer( )
    boundingBox.minCorner = minCorner[ 0 ]
    boundingBox.maxCorner = maxCorner[ 0 ]
    
    return boundingBox


def qrGetGuidesNodesFromGuidesNode( guidesNode ):
    """
    This method extracts from the guides node a dictionary associating a guide
    name to the name of the node representing it in the current embedding.
    """
    
    # Get the skeleton joint position back from the node.
    guidesNodes = {}
    
    childAttributes = cmds.attributeQuery( kGuidesAttributeName , node=guidesNode , listChildren=True )
    for childAttribute in childAttributes:
        sourceNode = getSourceNode( guidesNode , '%s.%s' % ( kGuidesAttributeName , childAttribute ) )
        if sourceNode:
            guidesNodes[ childAttribute ] = sourceNode
    
    return guidesNodes


def qrAverageGuides( guidesNode , center , axis ):
    """
    This method averages guides with regards to the center.
    """
    
    mapGuideToScene = qrGetGuidesNodesFromGuidesNode( guidesNode )
    ( averagedJoints , centeredJoints ) = listAveragedJoints( mapGuideToScene )
    averageJoints( center , axis , averagedJoints )
    centerJoints( center , axis , centeredJoints )


def qrMirrorGuides( guidesNode , center , axis , leftToRight , guides ):
    """
    This method mirrors the given guides with regards to the center.
    
    Each guide in the given guides can either be:
    - A center guide (in which case the guide is brought to the center plane)
    - A symmetry guide (in which case it serves at a source that is applied to
      its corresponding symmetric guide)
    - Not a guide (in which case nothing is done)
    """
    
    mapGuideToScene = qrGetGuidesNodesFromGuidesNode( guidesNode )
    ( mirroredJoints , centeredJoints ) = listMirroredJoints( mapGuideToScene , guidesNode , guides , leftToRight )
    mirrorJoints( center , axis , mirroredJoints )
    centerJoints( center , axis , centeredJoints )


def qrSetGuidesVisibility( guidesNode , visible ):
    """
    This method sets the visibility attributes on all the guide nodes.
    """
    
    mapGuideToScene = qrGetGuidesNodesFromGuidesNode( guidesNode )
    allGuides = [ guidesNode ] + mapGuideToScene.values( )
    for guide in allGuides:
        cmds.setAttr( '%s.visibility' % guide , visible )


def qrGetRequiredGuides( skeletonParameters ):
    """
    This method returns a list of the guides corresponding to the given skeleton parameters.
    
    It should be in sync with the output of:
    - qrGetGuidesFromEmbedding( )
    """
    
    guides = [
        'Reference' ,
        'Hips' ,
        'Head' ,
        ]
    guides += [ 'Spine%s' % ( str( i ) if i else '' ) for i in range( skeletonParameters[ 'SpineCount' ] ) ]
    guides += [ 'Neck%s'  % ( str( i ) if i else '' ) for i in range( skeletonParameters[ 'NeckCount'  ] ) ]
    if skeletonParameters[ 'WantHipsTranslation' ]:
        guides.append( 'HipsTranslation' )
    
    sideGuides = [
        'UpLeg' ,
        'Leg' ,
        'Foot' ,
        'ToeBase' ,
        'Arm' ,
        'ForeArm' ,
        'Hand' ,
        ]
    
    shoulderCount = skeletonParameters[ 'ShoulderCount' ]
    clavicleNames = [ 'Shoulder' , 'ShoulderExtra' ]
    assert( shoulderCount <= len( clavicleNames ) )
    sideGuides += clavicleNames[ 0 : shoulderCount ]
    
    guides += [ side + guide for side in [ 'Left' , 'Right' ] for guide in sideGuides ]
    
    return guides


def qrGetGuidesPositions( character ):
    """
    This method returns position of each guide node associated with the given
    character, if any.
    """
    
    if not qrIsCharacter( character ):
        return None
    
    guidesNode = qrGetGuidesNode( character )
    if not guidesNode:
        return None
    
    guides = qrGetGuidesNodesFromGuidesNode( guidesNode )
    if not guides:
        return None
    
    positions = { guide : cmds.xform( node , worldSpace=True , translation=True , query=True ) for guide , node in guides.iteritems() }
    
    return positions


def qrGetSkeletonRootNode( character ):
    """
    This method returns the root node of the skeleton associated with the given
    character, if any.
    """
    
    if not qrIsCharacter( character ):
        return None
    
    return getSourceNode( character , '%s.%s' % ( kQuickRigInfoAttributeName , kSkeletonAttributeName ) )


def qrDeleteSkeleton( character ):
    """
    This method deletes the skeleton from the given character, if any.
    
    It returns True if the skeleton was deleted, False otherwise.
    """
    
    if not qrIsCharacter( character ):
        return False
    
    skeletonRootNode = qrGetSkeletonRootNode( character )
    if not skeletonRootNode:
        return False
    
    cmds.delete( skeletonRootNode )
    
    return True


def qrSetSkeletonRootNode( character , skeletonRootNode ):
    """
    This method associates the skeleton root node to the given character.
    """
    
    if not qrIsCharacter( character ):
        return False
    
    if qrGetSkeletonRootNode( character ):
        return False
    
    cmds.connectAttr( '%s.message' % skeletonRootNode , '%s.%s.%s' % ( character , kQuickRigInfoAttributeName , kSkeletonAttributeName ) )
    
    return True




###############################################################################
#                                                                             #
#  HumanIK utility tools (methods and classes)                                #
#                                                                             #
#  These are very specific to the way HumanIK and its UI works in Maya.       #
#  They are likely to need to be updated if anything changes, the API is not  #
#  public.                                                                    #
#                                                                             #
###############################################################################
def hikInitialize( ):
    """
    This method makes sure the HumanIK tool is loaded and visible.
    """
    
    # Remember current character.
    if mel.eval( 'exists hikGetCurrentCharacter' ):
        character = hikGetCurrentCharacter( )
    else:
        # Getting the current character fails, it's because the scripts have
        # not been loaded yet.  In this case, there is no current character.
        character = ''
    
    # Make sure UI is created.
    mel.eval( 'HIKCharacterControlsTool(); flushIdleQueue;' )
    
    # Set the old character, because HIKCharacterControlsTool() changes it.
    # This requires a UI refresh, but it will happen after.
    hikSetCurrentCharacter( character )


def hikUpdateTool( ):
    """
    This method refreshes the HumanIK tool UI so that it fits the current
    HumanIK character.
    """
    
    melCode = """
        if ( hikIsCharacterizationToolUICmdPluginLoaded() )
        {
            hikUpdateCharacterList();
            hikUpdateSourceList();
            hikUpdateContextualUI();
        }
        """
    mel.eval( melCode )


def hikNoneString( ):
    """
    This method returns the string to display when no character is selected.
    """
    
    return ( mel.eval( 'hikNoneString()' ) or '' )


def hikGetSceneCharacters( ):
    """
    This method returns a list of names for all HumanIK characters in the
    current scene.
    """
    
    return ( mel.eval( 'hikGetSceneCharacters()' ) or [] )


def hikGetCurrentCharacter( ):
    """
    This method returns the name of the current HumanIK character.
    """

    return ( mel.eval( 'hikGetCurrentCharacter()' ) or '' )


def hikGetSkeletonGeneratorNode( character ):
    """
    This method returns the name of the skeleton generator node associated with
    the given HumanIK character if it exists, or the empty string otherwise.
    """
    
    return ( mel.eval( 'hikGetSkeletonGeneratorNode( "%s" )' % character ) or '' )


def hikGetControlRig( character ):
    """
    This method returns the control rig of the given HumanIK character if it
    exists, or the empty string otherwise.
    """
    
    return ( mel.eval( 'hikGetControlRig( "%s" )' % character ) or '' )


def hikGetSkeletonNodesMap( character ):
    """
    This method returns the scene joints for the skeleton associated with the
    given character, if any.
    """
    
    nodes = { }
    for i in range( cmds.hikGetNodeCount( ) ):
        sourceNode = mel.eval( 'hikGetSkNode( "%s" , %d )' % ( character , i ) )
        if sourceNode:
            nodes[ cmds.GetHIKNodeName( i ) ] = sourceNode
    return nodes


def hikCreateCharacter( nameHint ):
    """
    This method creates a new HumanIK character trying to use the given name
    hint to name the new character.
    """
    
    return ( mel.eval( 'hikCreateCharacter( "%s" )' % nameHint ) )


def hikRenameDefinition( character ):
    """
    This method opens the dialog allowing the user to rename the given HumanIK
    character.
    """
    
    melCode = """hikSetCurrentCharacter( "%s" ); hikRenameDefinition();"""
    mel.eval( melCode % character )


def hikSetCurrentCharacter( character ):
    """
    This method sets the given HumanIK character as the global current HumanIK
    character.
    """
    
    return ( mel.eval( 'hikSetCurrentCharacter( "%s" )' % character ) )


def hikDeleteWholeCharacter( character ):
    """
    This method deletes the given HumanIK character.
    
    It deletes its control rig (if any), its skeleton (if any) and its
    character definition.
    """
    
    melCode = """hikSetCurrentCharacter( "%s" ); hikDeleteControlRig(); hikDeleteSkeleton_noPrompt();"""
    mel.eval( melCode % character )


def hikCreateControlRig( character ):
    """
    This method creates a control rig for the given HumanIK character.
    """
    
    melCode = """hikSetCurrentCharacter( "%s" ); hikCreateControlRig();"""
    mel.eval( melCode % character )


def hikDeleteControlRig( character ):
    """
    This method deletes the control rig (if any) for the given HumanIK
    character.
    """
    
    melCode = """hikSetCurrentCharacter( "%s" ); hikDeleteControlRig();"""
    mel.eval( melCode % character )


def hikGetJointNodeName( character , jointName ):
    """
    This method returns the joint node name in the given HumanIK character for
    the given generic HumanIK joint name.
    
    It does so by following the connection to the character node from the the
    required joint node.
    """
    
    # Get the name from the scene.
    return getSourceNodeFromPlug( '%s.%s' % ( character , jointName ) )


def hikGetEffectorNodeName( character , effectorName ):
    """
    This method returns the effector node name in the given HumanIK character
    for the given generic HumanIK effector name.
    """
    
    # FIXME: Find a way to get the effector from the node.
    return character + '_Ctrl_' + effectorName


# This class comes from Red9_General module:
# https://github.com/markj3d/Red9_StudioPack/blob/master/core/Red9_General.py
#import logging as log
class HIKContext(object):
    """
    Simple Context Manager for restoring HIK Animation settings and managing HIK callbacks
    """
    def __init__(self, NodeList):
        self.objs=cmds.ls(sl=True, l=True)
        self.NodeList=NodeList
        self.managedHIK = False

    def __enter__(self):
        try:
            #We set the keying group mainly for the copyKey code, stops the entire rig being
            #manipulated on copy of single effector data
            self.keyingGroups=cmds.keyingGroup(q=True, fil=True)
            if [node for node in self.NodeList if cmds.nodeType(node) == 'hikIKEffector'\
                or cmds.nodeType(node) == 'hikFKJoint']:
                self.managedHIK = True
                
            if self.managedHIK:
                cmds.keyingGroup(fil="NoKeyingGroups")
                #log.info('Processing HIK Mode >> using HIKContext Manager:')
                cmds.select(self.NodeList)
                mel.eval("hikManipStart 1 0")
        except:
            self.managedHIK = False

    def __exit__(self, exc_type, exc_value, traceback):
        if self.managedHIK:
            cmds.keyingGroup(fil=self.keyingGroups)
            cmds.select(self.NodeList)
            mel.eval("hikManipStop")
            #log.info('Exit HIK Mode >> HIKContext Manager:')
        if exc_type:
            #log.exception('%s : %s'%(exc_type, exc_value))

        if self.objs:
            cmds.select(self.objs)
        return True


class HIKManipulationScope:
    """
    This class is a simple manager that sets a manipulation mode when entering
    and resets the previous manipulation mode when exiting.
    """
    
    def __init__( self , manipulationMode ):
        self.newManipulationMode = manipulationMode
        self.oldManipulationMode = None
        if cmds.optionVar( exists='keyFullBody' ):
            self.oldManipulationMode = cmds.optionVar( query='keyFullBody' )
    
    def __enter__( self ):
        self.setManipulationMode( self.newManipulationMode )
    
    def __exit__( self , exc_type , exc_value , traceback ):
        if self.oldManipulationMode is not None:
            self.setManipulationMode( self.oldManipulationMode )
    
    def setManipulationMode( self , mode ):
        # It is (probably) actually not needed to do anything else than setting the optionVar value,
        # but we do the same thing as clicking the button to be safe.
        melCode = 'optionVar -intValue keyFullBody %d; hikSetKeyingMode( ); hikUpdateControlRigButtonState;' 
        mel.eval( melCode % mode )




###############################################################################
#                                                                             #
#  Skeleton generation utility tools (classes and method)                     #
#                                                                             #
#  These are utilities to handle the output of the skeletonEmbed command      #
#  (the result of skeleton embedding) and work with it to create a HumanIK    #
#  skeleton.                                                                  #
#                                                                             #
###############################################################################
class Vector3:
    """
    This class is a minimalist vector class.
    
    It only does the strict minimum needed by this tool and is not meant to be
    a generic vector class.
    """
    
    def __init__( self , *args ):
        if len( args ) == 1:
            # Assume an iterable object.
            assert( len( args[ 0 ] ) == 3 )
            self.x = args[ 0 ][ 0 ]
            self.y = args[ 0 ][ 1 ]
            self.z = args[ 0 ][ 2 ]
        elif len( args ) == 3:
            self.x = args[ 0 ]
            self.y = args[ 1 ]
            self.z = args[ 2 ]
        else:
            raise RuntimeError( maya.stringTable['y_quickRigUI.kInvalidParameterToConstructor' ] )
    
    def __getitem__( self , key ):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise RuntimeError( maya.stringTable['y_quickRigUI.kInvalidParameterToGetItem' ] )
    
    def __setitem__( self , key , value ):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise RuntimeError( maya.stringTable['y_quickRigUI.kInvalidParameterToSetItem' ] )
    
    def __add__( self , other ):
        return Vector3( self.x + other.x , self.y + other.y , self.z + other.z )
    
    def __sub__( self , other ):
        return Vector3( self.x - other.x , self.y - other.y , self.z - other.z )
    
    def __mul__( self , other ):
        return Vector3( self.x * other , self.y * other , self.z * other )
    
    def length( self ):
        return sqrt( self.dot( self ) )
    
    def dot( self , other ):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross( self , other ):
        return Vector3(
            self.y * other.z - self.z * other.y ,
            self.z * other.x - self.x * other.z ,
            self.x * other.y - self.y * other.x
            )
    
    def project( self , target ):
        return self - target * ( self.dot( target ) / float( target.dot( target ) ) )


class PieceWiseLinearFunction:
    """
    This class handles interpolation between an array of points.
    """
    
    def __init__( self , points ):
        self.points = points
        
        vectors = [ ]
        for i in range( len( points ) - 1 ):
            vectors.append( points[ i + 1 ] - points[ i ] )
        
        lengths = [ v.length( ) for v in vectors ]
        totalLength = sum( lengths )
        
        self.ratios = [ ]
        currentLength = 0
        for length in lengths:
            self.ratios.append( currentLength / totalLength )
            currentLength += length
        self.ratios.append( 1.0 )
    
    def evaluate( self , value ):
        if ( value <= 0 ):
            return self.points[ 0 ]
        elif ( value >= 1 ):
            return self.points[ -1 ]
        else:
            for i in range( len( self.ratios ) ):
                if self.ratios[ i + 1 ] > value:
                    break
            factor0 = self.ratios[ i     ]
            factor1 = self.ratios[ i + 1 ]
            
            factor = ( value - factor0 ) / ( factor1 - factor0 )
            
            return self.points[ i ] * ( 1 - factor ) + self.points[ i + 1 ] * factor




#
# Conversion from embedding to skeleton.
#

def convertReference( minCorner , maxCorner ):
    """
    This method takes the position of bounding box corners and maps them to
    a reference joint that HumanIK expects.
    """
    center = ( minCorner + maxCorner ) * 0.5
    center[ kCharacterUpAxis ] = [ minCorner , maxCorner ][ kCharacterDownDirection ][ kCharacterUpAxis ]
    
    return { 'Reference' : center }


def convertSpine( tweakParameters , spineCount , wantHipsTranslation , hipsPosition , backPosition , shouldersPosition ):
    """
    This method takes the position of the spine guides coming out of the
    embedding algorithm (hips, back and shoulders) and maps them to spine
    joints that fits what HumanIK expects.
    """
    
    spineJoints = {}
    
    if tweakParameters.tweak:
        spineFunc = PieceWiseLinearFunction( [ hipsPosition , backPosition , shouldersPosition ] )
        firstSpine = spineFunc.evaluate( tweakParameters.firstRatio )
        lastSpine  = spineFunc.evaluate( tweakParameters.lastRatio  )
    else:
        firstSpine = backPosition
        lastSpine  = shouldersPosition
    
    spineJoints[ 'Hips' ]  = hipsPosition
    spineJoints[ 'Spine' ] = firstSpine
    numberOfSpineJointsToAdd = spineCount - 2
    if numberOfSpineJointsToAdd == -1:
        # This means that we are done, nothing else to add.
        pass
    else:
        assert( numberOfSpineJointsToAdd >= 0 )
        for i in range( numberOfSpineJointsToAdd + 1 ):
            factor = ( i + 1.0 ) / ( numberOfSpineJointsToAdd + 1.0 )
            position = firstSpine * ( 1 - factor ) + lastSpine * ( factor )
            name = 'Spine%d' % ( i + 1 )
            spineJoints[ name ] = position
    
    if wantHipsTranslation:
        spineJoints[ 'HipsTranslation' ] = hipsPosition
    
    return spineJoints


def convertNeck( tweakParameters , neckCount , shouldersPosition , headPosition , boundingBox ):
    """
    This method takes the position of the neck guides coming out of the
    embedding algorithm (shoulders and neck) and maps them to neck joints that
    fits what HumanIK expects.
    """
    
    neckJoints = {}
    
    if tweakParameters.tweak:
        # Bottom of neck.
        factor = tweakParameters.firstRatio
        firstNeck = shouldersPosition * ( 1 - factor ) + headPosition * ( factor )
        
        # Get the top of the head.
        headTopUp   = boundingBox[ kCharacterUpDirection ][ kCharacterUpAxis ]
        shouldersUp = shouldersPosition[ kCharacterUpAxis ]
        headUp      = headPosition[ kCharacterUpAxis ]
        factor = ( headTopUp - shouldersUp ) / ( headUp - shouldersUp )
        if factor <= 0:
            cmds.warning( maya.stringTable[ 'y_quickRigUI.kWarningReverseHead'   ] )
            lastNeck = headPosition
        else:
            headFactor = factor * tweakParameters.lastRatio
            lastNeck = shouldersPosition * ( 1 - headFactor ) + headPosition * headFactor
    else:
        factor = tweakParameters.firstRatioNoTweak
        firstNeck = shouldersPosition * ( 1 - factor ) + headPosition * ( factor )
        lastNeck  = headPosition
    
    for i in range( neckCount ):
        factor = i / float( neckCount )
        position = firstNeck * ( 1 - factor ) + lastNeck * ( factor )
        name = 'Neck%s' % ( str( i ) if i else '' )
        neckJoints[ name ] = position
    neckJoints[ 'Head' ] = lastNeck
    
    return neckJoints


def convertShoulder( tweakParameters , shoulderCount , shouldersPosition , leftShoulderPosition , rightShoulderPosition ):
    """
    This method takes the position of the shoulder guides coming out of the
    embedding algorithm (shoulders and left/right shoulder) and maps them to
    clavicle joints that fits what HumanIK expects.
    """
    
    shoulderJoints = {
        'LeftArm'  : leftShoulderPosition  ,
        'RightArm' : rightShoulderPosition ,
    }
    
    if tweakParameters.tweak:
        shoulderFactor = tweakParameters.ratio
    else:
        # Fist clavicle is 40% between center of shoulders and shoulder.
        shoulderFactor = 0.4
    
    assert( shoulderCount >= 0 )
    if shoulderCount > 0:
        clavicleNames = [ 'Shoulder' , 'ShoulderExtra' ]
        assert( shoulderCount <= len( clavicleNames ) )
        
        factor = shoulderFactor / 2.0
        leftClaviclePosition  = leftShoulderPosition * ( 1 - factor ) + rightShoulderPosition * ( factor     )
        rightClaviclePosition = leftShoulderPosition * ( factor     ) + rightShoulderPosition * ( 1 - factor )
        shoulderJoints[ 'Left'  + clavicleNames[ 0 ] ] = leftClaviclePosition
        shoulderJoints[ 'Right' + clavicleNames[ 0 ] ] = rightClaviclePosition
        for i in range( shoulderCount - 1 ):
            factor = ( i + 1.0 ) / ( shoulderCount )
            
            leftPosition = leftClaviclePosition * ( 1 - factor ) + leftShoulderPosition * ( factor )
            leftName = 'Left' + clavicleNames[ i + 1 ]
            shoulderJoints[ leftName ] = leftPosition
            
            rightPosition = rightClaviclePosition * ( 1 - factor ) + rightShoulderPosition * ( factor )
            rightName = 'Right' + clavicleNames[ i + 1 ]
            shoulderJoints[ rightName ] = rightPosition
    
    return shoulderJoints


def convertFoot( tweakParameters , kneePosition , anklePosition , footPosition ):
    """
    This method takes the position of the foot guides coming out of the
    embedding algorithm (knee, ankle and foot) and maps them to foot joints
    that fits what HumanIK expects.
    """
    
    footJoints = {}
    
    if tweakParameters.tweak:
        kneeUp   = kneePosition [ kCharacterUpAxis ]
        ankleUp  = anklePosition[ kCharacterUpAxis ]
        footUp   = footPosition [ kCharacterUpAxis ]
        
        # Compute the factors from to avoid values too close to one another.
        currentAnkleFactor = ( ankleUp - kneeUp ) / ( footUp - kneeUp )
        targetAnkleFactor  = ( 1 - tweakParameters.ankleRatio )
        if currentAnkleFactor > targetAnkleFactor:
            # The ankle is farther from the knee that we want.
            ankleFactor = targetAnkleFactor / currentAnkleFactor
            newAnklePosition = kneePosition + ( anklePosition - kneePosition ) * ( ankleFactor )
        else:
            newAnklePosition = anklePosition
        
        # Compute the toe adjustment either from the old or new ankle position.
        if tweakParameters.useCorrectedAnkleForToe:
            toeAnklePosition = newAnklePosition
        else:
            toeAnklePosition = anklePosition
        
        footFactor = tweakParameters.toeRatio
        newFootPosition = footPosition * ( 1 - footFactor ) + toeAnklePosition * ( footFactor )
    else:
        # Nothing to do.
        newAnklePosition = anklePosition
        newFootPosition  = footPosition
        pass
    
    footJoints[ 'Leg'     ] = kneePosition
    footJoints[ 'Foot'    ] = newAnklePosition
    footJoints[ 'ToeBase' ] = newFootPosition
    
    return footJoints


def convertHand( tweakParameters , elbowPosition , handPosition ):
    """
    This method takes the position of the hand guides coming out of the
    embedding algorithm (elbow and hand) and maps them to hand joints that
    fits what HumanIK expects.
    """
    
    handJoints = {}
    
    if tweakParameters.tweak:
        handFactor = tweakParameters.ratio
        newHandPosition = handPosition * ( 1 - handFactor ) + elbowPosition * ( handFactor )
    else:
        # Nothing to do.
        newHandPosition = handPosition
    
    handJoints[ 'ForeArm' ] = elbowPosition
    handJoints[ 'Hand'    ] = newHandPosition
    
    return handJoints


#
# Mirroring.
#

def listMirroredJoints( mapGuideToScene , guidesNode , items , leftToRight ):
    """
    This methods creates and returns two lists of joints from the list given as
    'items'.  The first list contains tuples where the first element is the
    source joint and the second element is its mirror counterpart.  The second
    list contains the name of joints that do not have a mirror counterpart,
    i.e. center joints.
    
    The direction of source to destination is determined by the truth value of
    the 'leftToRight' parameter.
    
    This method is used when a set of selected joints must be mirrored to be
    applied to their mirror counterpart.
    """
    
    mirroredJoints = []
    centeredJoints = []
    
    mapSceneToGuide = {}
    mapSceneToGuide.update( reversed( i ) for i in mapGuideToScene.iteritems( ) )
    nodesToProcess = []
    for item in items:
        if item == guidesNode:
            # Add all the guides.
            for node in mapSceneToGuide:
                if not node in nodesToProcess:
                    nodesToProcess.append( node )
        else:
            if not item in mapSceneToGuide:
                # Not a guide.
                continue
            
            if not item in nodesToProcess:
                nodesToProcess.append( item )
    
    for node in nodesToProcess:
        joint = node
        mirroredGuide = None
        guideName = mapSceneToGuide[ joint ]
        if guideName.startswith( 'Left' ):
            if leftToRight:
                mirroredGuide = 'Right' + guideName[4:]
        elif guideName.startswith( "Right" ):
            if not leftToRight:
                mirroredGuide = 'Left' + guideName[5:]
        else:
            mirroredGuide = guideName
        
        if mirroredGuide:
            # Found a valid joint to "fix".
            mirroredJoint = mapGuideToScene[ mirroredGuide ]
            
            if guideName == mirroredGuide:
                # No mirroring
                centeredJoints.append( joint )
            else:
                # Mirroring happened.
                mirroredJoints.append( ( joint , mirroredJoint ) )
    
    return ( mirroredJoints , centeredJoints )


def listAveragedJoints( mapGuideToScene ):
    """
    This methods creates and returns two lists of joints from the list given as
    'items'.  The first list contains unique tuples where the second element is
    the mirror counterpart of the first element.  The second list contains the
    name of joints that do not have a mirror counterpart, i.e. center joints.
    
    This method is used when all of the joints need to be averaged with their
    mirror counterpart, relative to their position with regards to the mirror
    plane.
    """
    
    averagedJoints = []
    centeredJoints = []
    
    mapSceneToGuide = {}
    mapSceneToGuide.update( reversed( i ) for i in mapGuideToScene.iteritems( ) )
    nodesToProcess = []
    for node in mapSceneToGuide:
        joint = node
        mirroredGuide = None
        guideName = mapSceneToGuide[ joint ]
        if guideName.startswith( 'Left' ):
            mirroredGuide = 'Right' + guideName[4:]
        elif guideName.startswith( "Right" ):
            mirroredGuide = 'Left' + guideName[5:]
        else:
            mirroredGuide = guideName
        
        if mirroredGuide:
            # Found a valid joint to "fix".
            mirroredJoint = mapGuideToScene[ mirroredGuide ]
            
            if guideName == mirroredGuide:
                # No mirroring
                if not joint in centeredJoints:
                    centeredJoints.append( joint )
            else:
                # Mirroring happened.
                if joint > mirroredGuide:
                    ( joint , mirroredJoint ) = ( mirroredJoint , joint )
                
                if not ( joint , mirroredJoint ) in averagedJoints:
                    averagedJoints.append( ( joint , mirroredJoint ) )
    
    return ( averagedJoints , centeredJoints )


def mirrorJoints( center , axis , joints ):
    """
    This method applies mirroring to a list of joints.
    """
    
    for ( sourceJoint , destJoint ) in joints:
        sourceJointPosition = cmds.xform( sourceJoint , query=True , worldSpace=True , translation=True )
        
        # Mirror the joint position.
        destJointPosition = sourceJointPosition
        destJointPosition[ axis ] = center - ( destJointPosition[ axis ] - center )
        
        cmds.xform( destJoint , worldSpace=True , translation=destJointPosition )


def centerJoints( center , axis , joints ):
    """
    This method centers a list of joints so they lie directly on the mirror plane.
    """
    
    for joint in joints:
        jointPosition = cmds.xform( joint , query=True , worldSpace=True , translation=True )
        
        # Center the joint to the symmetry plane.
        jointPosition[ axis ] = center
        
        cmds.xform( joint , worldSpace=True , translation=jointPosition )


def averageJoints( center , axis , joints ):
    """
    This method averages a list of joints so that they become perfectly
    symmetric with regards to the mirror plane.
    """
    
    for ( joint0 , joint1 ) in joints:
        jointPosition0 = cmds.xform( joint0 , query=True , worldSpace=True , translation=True )
        jointPosition1 = cmds.xform( joint1 , query=True , worldSpace=True , translation=True )
        
        # Mirror the joint position.
        mirroredJointPosition1 = jointPosition1
        mirroredJointPosition1[ axis ] = center - ( mirroredJointPosition1[ axis ] - center )
        
        # Average to get results.
        targetPosition0 = ( Vector3( jointPosition0 ) + Vector3( mirroredJointPosition1 ) ) * 0.5
        targetPosition0 = [ targetPosition0.x , targetPosition0.y , targetPosition0.z ]
        
        # Mirror the average.
        targetPosition1 = list( targetPosition0 )
        targetPosition1[ axis ] = center - ( targetPosition1[ axis ] - center )
        
        # Set the positions back.
        cmds.xform( joint0 , worldSpace=True , translation=targetPosition0 )
        cmds.xform( joint1 , worldSpace=True , translation=targetPosition1 )


#
# Skeleton construction.
#

def isCloseEnough( a , b , epsilon = 1e-06 ):
    """
    This method checks whether two values are close to one another within a
    given tolerance.
    """
    
    return epsilon > fabs( a - b )


def createReferential( xVector , zTargetVector , zBackupTargetVector ):
    """
    This method create a rotation matrix representing a referential
    described by the given vectors.
    
    The matrix will take a point in the local referential and convert it to
    "world" referential.
    
    The X axis of the referential will be oriented towards the given xVector.
    The Z axis will be oriented towards the given zTargetVector, but it will
    be made orthogonal to the X axis.  The Y axis will be chosen as a
    complement of the two others to create a right-handed system.
    """
    
    # OPTME: Some lengths / dot products are computed more than once.
    
    # X axis is already in the right direction.
    u1 = xVector
    if u1.length( ) == 0:
        u1 = zTargetVector.cross( zBackupTargetVector )
    if u1.length( ) == 0:
        raise RuntimeError( maya.stringTable[ 'y_quickRigUI.kNullXVector'   ] )
    
    # Z axis must be made orthogonal to X axis.
    u3 = zTargetVector.project( u1 )
    if isCloseEnough( u3.length( ) / u1.length( ) , 0 ):
        u3 = zBackupTargetVector.project( u1 )
    if u3.length( ) == 0:
        raise RuntimeError( maya.stringTable[ 'y_quickRigUI.kNullZVector'   ] )
    
    # Y axis is orthogonal to both axis.
    u2 = u3.cross( u1 )
    if u2.length( ) == 0:
        raise RuntimeError( maya.stringTable[ 'y_quickRigUI.kNullYVector'   ] )
    
    u1 *= ( 1.0 / u1.length( ) )
    u2 *= ( 1.0 / u2.length( ) )
    u3 *= ( 1.0 / u3.length( ) )
    
    matrix = [
        u1[ 0 ] , u1[ 1 ] , u1[ 2 ] , 0 ,
        u2[ 0 ] , u2[ 1 ] , u2[ 2 ] , 0 ,
        u3[ 0 ] , u3[ 1 ] , u3[ 2 ] , 0 ,
        0       , 0       , 0       , 1 ,
        ]
    return matrix


def computeNeededJointOrient( targetMatrix , currentMatrix ):
    """
    This method compute the value needed for the joint orient attribute so that
    the given joint orientation is the one given by the target, knowing that
    its current rotation is given by the current matrix.
    """
    
    # Build OpenMaya matrices.
    omTargetMatrix = OpenMaya.MMatrix( )
    OpenMaya.MScriptUtil.createMatrixFromList( targetMatrix , omTargetMatrix )
    omCurrentMatrix = OpenMaya.MMatrix( )
    OpenMaya.MScriptUtil.createMatrixFromList( currentMatrix , omCurrentMatrix )
    
    # Joint orient matrix.
    # To convert a point from local to world space, we have:
    # Pworld = Plocal * targetMatrix = Plocal * orientMatrix * currentMatrix
    # orientMatrix = targetMatrix * currentMatrix^-1
    #
    # Note that target matrix only have rotations, so only read rotations back.
    omJointOrientMatrix = omTargetMatrix * omCurrentMatrix.inverse()
    
    # Get back Euler joint orients.
    omEulerRotation = OpenMaya.MTransformationMatrix( omJointOrientMatrix ).eulerRotation( )
    
    x = degrees( omEulerRotation.x )
    y = degrees( omEulerRotation.y )
    z = degrees( omEulerRotation.z )
    
    return ( x , y , z )


def createHikSkeleton( character , skeletonParameters ):
    """
    This method creates a HumanIK skeleton from a set of parameters
    corresponding to what can be set in the HumanIK skeleton generation tool.
    
    It uses the skeleton generator node, but deletes it when its done.
    """
    
    # Make sure the characterization is not locked.
    cmds.setAttr( '%s.InputCharacterizationLock' % character , 0 )
    
    # This code comes from hikCreateSkeleton().
    
    # First create the node (from hikCreateSkeleton()).
    skeletonGeneratorNode = cmds.createNode( 'HIKSkeletonGeneratorNode' )
    cmds.setAttr( '%s.isHistoricallyInteresting' % skeletonGeneratorNode,  0 )
    cmds.connectAttr( '%s.CharacterNode' % skeletonGeneratorNode , '%s.SkeletonGenerator' % character )
    
    # Reset default attributes (from hikCreateSkeleton()).
    melCode = """
        string $skeletonGeneratorNode = "%s";
        hikReadDefaultCharPoseFileOntoSkeletonGeneratorNode($skeletonGeneratorNode);
        hikSetSkeletonGeneratorDefaults($skeletonGeneratorNode);
        """
    mel.eval( melCode % skeletonGeneratorNode )
    
    # Set the attributes from the skeleton parameters.
    for parameter , value in skeletonParameters.iteritems( ):
        cmds.setAttr( '%s.%s' % ( skeletonGeneratorNode , parameter ) , value )
    
    # Sync the skeleton (from hikSyncSkeletonGeneratorFromUI()).
    melCode = """
        string $character = "%s";
        hikUpdateSkeletonFromSkeletonGeneratorNode( $character, 1.0 );
        """
    mel.eval( melCode % character )
    
    # We can now delete the skeleton generator node.
    cmds.delete( skeletonGeneratorNode )
    
    # We return the root of the skeleton.
    return getSourceNode( character , 'Reference' )


def getCharacterDefiniton( character ):
    """
    This method gets the HumanIK information from the given character.
    
    It uses the character and HumanIK commands to do so, even though all of
    this information would be available from the skeleton settings.
    """
    
    # Get the names of all active joints in the characterization.
    hikJoints = [ cmds.GetHIKNodeName( i ) for i in range( cmds.hikGetNodeCount( ) ) if getSourceNodeFromPlug( cmds.GetHIKNode( character , i ) ) ]
    hikParents = [ cmds.GetHIKNodeName( cmds.GetHIKParentId( character , nodeid=cmds.hikGetNodeIdFromName( joint ) ) ) for joint in hikJoints ]
    
    # Build a list of joints from parent to children.
    orderedJoints = []
    stack = []
    for joint in hikJoints:
        if joint in orderedJoints:
            continue
        
        stack.append( joint )
        while len( stack ) != 0:
            assert( len( stack ) < 100 )
            jointToProcess = stack[ len( stack ) - 1 ]
            
            readyToProcess = True
            parent = hikParents[ hikJoints.index( jointToProcess ) ]
            if parent:
                assert( parent in hikJoints )
                if not parent in orderedJoints:
                    # If a parent has not been processed yet, push it on the stack.
                    stack.append( parent )
                    readyToProcess = False
            
            if readyToProcess:
                assert( jointToProcess == stack[ len( stack ) - 1 ] )
                jointToProcess = stack.pop()
                
                orderedJoints.append( jointToProcess )
    
    assert( sorted( orderedJoints ) == sorted( hikJoints ) )
    
    hikInfos = { }
    skeletonNodes = { }
    for hikName in orderedJoints:
        hikInfo = createContainer( )
        
        hikInfo.name = hikName
        # Indices will refer to ordered joints.
        hikInfo.nameIndex = orderedJoints.index( hikName )
        
        # Set the parent / children.
        hikInfo.children = [ ]
        parent = hikParents[ hikJoints.index( hikName ) ]
        if parent:
            hikInfo.parentName  = parent
            hikInfo.parentIndex = orderedJoints.index( parent )
            hikInfos[ parent ].children.append( hikName )
        else:
            hikInfo.parentName  = None
            hikInfo.parentIndex = None
        
        # Effector ids will be set after.
        hikInfo.effector = None
        hikInfo.parentDirection = None
        
        # Store the info.
        hikInfos[ hikName ] = hikInfo
        
        joint = getSourceNodeFromPlug( cmds.GetHIKNode( character , cmds.hikGetNodeIdFromName( hikInfo.name ) ) )
        assert( joint )
        skeletonNodes[ hikName ] = joint
    
    # Set the target child for each joint.
    for hikInfo in hikInfos.values( ):
        if len( hikInfo.children ) == 0:
            targetChild = None
        elif len( hikInfo.children ) == 1:
            targetChild = hikInfo.children[ 0 ]
        else:
            childrenLeft   = [ ]
            childrenRight  = [ ]
            childrenCenter = [ ]
            for child in hikInfo.children:
                if child.startswith( 'Left' ):
                    childrenLeft.append( child )
                elif child.startswith( 'Right' ):
                    childrenRight.append( child )
                else:
                    childrenCenter.append( child )
            
            if len( childrenCenter ) == 1:
                targetChild = childrenCenter[ 0 ]
            else:
                # We don't know what to do in this case.
                assert( False )
        
        hikInfo.targetChild = targetChild
        
        if targetChild:
            name = hikInfo.name
            
            kOrientLeftAxis  = (  1 ,  0 ,  0 )
            kOrientFrontAxis = (  0 ,  0 ,  1 )
            kOrientDownAxis  = (  0 , -1 ,  0 )
            kOrientUpAxis    = (  0 ,  1 ,  0 )
            
            secondaryVector = None
            flipSecondaryVector = False
            if name == 'Reference':
                # Reference is a transform, not a joint: it cannot be oriented.
                hikInfo.targetChild = None
            elif name == 'HipsTranslation':
                # HipsTranslation keeps world orientation.
                hikInfo.targetChild = None
            elif name == 'Hips' or name.startswith( 'Spine' ) or name.startswith( 'Neck' ):
                secondaryVector = kOrientLeftAxis
            elif name in [ side + joint for side in [ 'Left' , 'Right' ] for joint in [ 'Shoulder' , 'ShoulderExtra' ] ]:
                secondaryVector = kOrientFrontAxis
                flipSecondaryVector = True
            elif name in [ 'Left' + joint for joint in [ 'Arm' , 'ForeArm' ] ]:
                secondaryVector = kOrientDownAxis
                flipSecondaryVector = True
            elif name in [ 'Right' + joint for joint in [ 'Arm' , 'ForeArm' ] ]:
                secondaryVector = kOrientUpAxis
            elif name in [ side + joint for side in [ 'Left' , 'Right' ] for joint in [ 'UpLeg' , 'Leg' , 'Foot' ] ]:
                secondaryVector = kOrientLeftAxis
            else:
                # We don't know what to do here.
                assert( False )
            
            hikInfo.secondaryVector     = secondaryVector
            hikInfo.flipSecondaryVector = flipSecondaryVector
    
    # Hard-coded sets of effectors to be manipulated together.
    effectorGroups = [
        [ 'LeftKneeEffector'  , 'LeftAnkleEffector'  , 'LeftFootEffector'  ] ,
        [ 'RightKneeEffector' , 'RightAnkleEffector' , 'RightFootEffector' ] ,
        [ 'LeftElbowEffector'  , 'LeftWristEffector'  ] ,
        [ 'RightElbowEffector' , 'RightWristEffector' ] ,
        ]
    allEffectors = [ effector for group in effectorGroups for effector in group ]
    
    effectorNodes  = { }
    effectorJoints = { }
    for effector in allEffectors:
        joint = cmds.GetHIKNodeName( cmds.GetFKIdFromEffectorId( cmds.hikGetEffectorIdFromName( effector ) ) )
        assert( joint in hikInfos )
        
        hikInfo = hikInfos[ joint ]
        # Set the effector name.
        hikInfo.effector = effector
        
        # Compute the "T-stance" target direction.
        currentPos = cmds.xform( skeletonNodes[ hikInfo.name ] , query=True , worldSpace=True , translation=True )
        parentPos  = cmds.xform( skeletonNodes[ hikInfo.parentName ] , query=True , worldSpace=True , translation=True )
        direction  = Vector3( currentPos ) - Vector3( parentPos )
        
        hikInfo.parentDirection = [ direction.x , direction.y , direction.z ]
        
        # Update effector node.
        effectorNodes[ effector ] = hikGetEffectorNodeName( character , effector )
        # Update effector scene node.
        effectorJoints[ effector ] = joint
    
    definition = createContainer( )
    definition.orderedJoints  = orderedJoints
    definition.hikInfos       = hikInfos
    definition.effectorGroups = effectorGroups
    definition.skeletonNodes  = skeletonNodes
    definition.effectorNodes  = effectorNodes
    definition.effectorJoints = effectorJoints
    
    return definition


def computeTStance( definition , positions , useTStanceCorrection ):
    """
    This method computes the T-stance position for a given character, given
    the position of the guides.
    
    It leaves the joints that can be corrected using effectors in their current
    direction, but adjusts the bone length to match the guides.
    
    It returns a map of HumanIK / guide names to the T-stance position.
    """
    
    if not useTStanceCorrection:
        # Nothing to do, keep the current positions.
        return dict( positions )
    
    jointPositions = { }
    for joint in definition.orderedJoints:
        hikInfo = definition.hikInfos[ joint ]
        if not hikInfo.effector:
            # Nothing to do, take the position directly.
            position = positions[ joint ]
        else:
            # There is an effector, so just resize to the right length.
            assert( hikInfo.parentName )
            
            targetWorldPos       = Vector3( positions[ hikInfo.name       ] )
            targetParentWorldPos = Vector3( positions[ hikInfo.parentName ] )
            
            computedParentWorldPos = Vector3( jointPositions[ hikInfo.parentName ] )
            
            directionVector = Vector3( hikInfo.parentDirection )
            directionLength = directionVector.length( )
            
            targetBoneVector = targetWorldPos - targetParentWorldPos
            targetBoneLength = targetBoneVector.length( )
            
            # Fix to angle the toes properly.
            if joint in [ 'LeftToeBase' , 'RightToeBase' ]:
                Ty = targetBoneVector[ kCharacterUpAxis ]
                Tl = targetBoneLength
                Oy = directionVector[ kCharacterUpAxis ]
                Ol = directionLength
                
                Ny = Ty * sqrt( ( Ol*Ol - Oy*Oy ) / ( Tl*Tl - Ty*Ty ) )
                
                directionVector[ kCharacterUpAxis ] = Ny
                directionLength = directionVector.length( )
            
            newPos = computedParentWorldPos + directionVector * ( targetBoneLength / directionLength )
            position = [ newPos.x , newPos.y , newPos.z ] 
        
        jointPositions[ joint ] = position
    
    return jointPositions


def computeJointOrients( hikInfos , positions , useOrientation , orientTowardsChild ):
    """
    This method computes the joint orientations for a given character, given
    the position of the guides.
    
    It returns a map of HumanIK / guide names to the desired referential.
    """
    
    if not useOrientation:
        # Nothing to do, no joint to orient.
        return { }
    
    jointOrients = {}
    for joint in positions:
        hikInfo = hikInfos[ joint ]
        if not hikInfo.targetChild:
            continue
        
        # Get the target vector.
        targetChild     = hikInfo.targetChild
        targetPosition  = positions[ targetChild ]
        currentPosition = positions[ joint ]
        xVector         = Vector3( targetPosition ) - Vector3( currentPosition )
        
        # Check if we need to invert it.
        invertX = False
        if hikInfo.name.startswith( 'Left' ):
            if not orientTowardsChild[ 0 ]:
                invertX = True
        elif hikInfo.name.startswith( 'Right' ):
            if not orientTowardsChild[ 1 ]:
                invertX = True
        if invertX:
            xVector = xVector * -1
        
        # Get the secondary vectors.
        assert( hikInfo.secondaryVector )
        zTargetVector = Vector3( hikInfo.secondaryVector )
        if invertX and hikInfo.flipSecondaryVector:
            zTargetVector = zTargetVector * -1
        # For the second vector, just take a different one, it will be
        # kind of meaningless if it gets used anyways.
        zBackupTargetVector = Vector3( zTargetVector.y , zTargetVector.z , zTargetVector.x )
        
        referential = createReferential( xVector , zTargetVector , zBackupTargetVector )
        
        jointOrients[ joint ] = referential
    
    return jointOrients


def positionHikSkeleton( orderedJoints , skeletonNodes , positions , jointOrients ):
    """
    This method sets the positions and joint orientations for a HumanIK skeleton.
    """
    
    for name in orderedJoints:
        joint = skeletonNodes[ name ]
        
        # Set the position.
        cmds.xform( joint , worldSpace=True , translation=positions[ name ] )
        
        # Set the orientation.
        if name in jointOrients:
            cmds.setAttr( '%s.rotate' % joint , 0 , 0 , 0 )
            cmds.setAttr( '%s.jointOrient' % joint , 0 , 0 , 0 )
            
            targetReferential = jointOrients[ name ]
            currentMatrix = cmds.xform( joint , query=True , worldSpace=True , matrix=True )
            jointOrient = computeNeededJointOrient( targetReferential , currentMatrix )
            
            cmds.setAttr( '%s.jointOrient' % joint , *jointOrient )


def positionHikControlRig( definition , positions ):
    """
    This method sets the positions of the HumanIK control rig effectors.
    """
    
    # This could be rewritten as a comprehension, but this makes it simpler.
    effectorsToSet = [ ]
    for effectorGroup in definition.effectorGroups:
        effectors = [ ]
        for effector in effectorGroup:
            effectors.append( ( definition.effectorNodes[ effector ] , positions[ definition.effectorJoints[ effector ] ] ) )
        effectorsToSet.append( effectors )
    
    # Update effectors.
    # FIXME: This hack iterates several times to get the effectors as close as possible.
    with HIKManipulationScope( 2 ):
        for i in range( 10 ):
            for effectors in effectorsToSet:
                with HIKContext( [ x[0] for x in effectors ] ):
                    for ( effectorNode , position ) in effectors:
                        cmds.xform( effectorNode , worldSpace=True , translation=position )




#############################################################################
#                                                                           #
#  Utility methods                                                          #
#                                                                           #
#############################################################################
def createContainer( ):
    """
    This method creates a container object which fields can be assigned
    dynamically.
    
    For instance, the object returned by this method will allow:
    
    obj = createContainer()
    obj.newAttribute = 'my new attribute value'
    """
    
    # Way to create temporary structure.
    return type( 'TempStruct' , ( object , ) , {} )


def getSelectedShapes( shapeTypes=None ):
    """
    This method returns the list of all currently selected shapes.
    
    It returns the actual shapes, i.e. the name of the shape nodes, not the
    transform nodes.
    """
    
    shapes = []
    skinningShapes = mel.eval( 'getSkinningShapes' )
    for shape in skinningShapes:
        childShapes = cmds.ls( shape , leaf=True , dag=True )
        for child in childShapes:
            # We only add chosen shape types.
            if shapeTypes:
                if cmds.nodeType( child ) not in shapeTypes:
                    continue
            # We don't add intermediate object ("Orig" shapes).
            if cmds.getAttr( child + '.intermediateObject' ):
                continue
            # We won't add shapes twice.
            if child in shapes:
                continue
            
            # Add the mesh.
            shapes.append( child )
    
    return shapes


def getSelectedMeshes( ):
    """
    This method returns the list of all currently selected meshes.
    
    It returns the actual meshes, i.e. the name of the shape nodes, not the
    transform nodes.
    """
    
    return getSelectedShapes( [ 'mesh' ] )


def enableXRayJoints( enabled ):
    """
    This method enables "X-Ray Joints" option on all viewports.
    """
    
    panels = cmds.getPanel( allPanels=True )
    modelEditors = [ panel for panel in panels if cmds.modelEditor( panel , query=True , exists=True ) ]
    for panel in modelEditors:
        cmds.modelEditor( panel , edit=True , jointXray=enabled )


def checkIfSkinExists( meshes ):
    """
    This method returns True if any of the mesh in the given list has an
    associated skin cluster, False otherwise.
    """
    
    for mesh in meshes:
        if mel.eval( 'findRelatedSkinCluster( "%s" )' % mesh ):
            return True
    
    return False


def detachSkinFromMesh( meshes ):
    """
    This method unbinds the skin for all the meshes in the given list, if any.
    """
    
    if checkIfSkinExists( meshes ):
        cmds.select( meshes , replace=True )
        mel.eval( 'doDetachSkin "2" { "1","0" }' )


def setDefaultOptionsGVB( resolution ):
    """
    This method sets the necessary variables to have reasonable default
    parameters to perform geodesic voxel binding that gives good results on a
    wide majority of cases.
    """
    
    # Simply use binding options dialog.
    melOptionsSettingCode = """
        // Bind to: Joint hierarchy
        optionVar -intValue bindTo 1;
        // Bind method: Geodesic Voxel
        optionVar -intValue bindMethod 4;
        // Skinning method: Dual quaternion
        optionVar -intValue skinMethod 1;
        // Normalize weights: Interactive
        optionVar -intValue normalizeWeights 2;
        // Weight distribution: Distance
        optionVar -intValue weightDistribution 1;
        // Allow multiple bind poses: checked
        optionVar -intValue multipleBindPosesOpt 1;
        // Max influences: 50
        optionVar -intValue maxInfl 5;
        // Maintain max influences: checked
        optionVar -intValue obeyMaxInfl 1;
        // Dropoff rate: 4.0
        optionVar -floatValue dropoff 4.0;
        // Remove unused influences: checked
        optionVar -intValue removeUnusedInfluences 1;
        // Colorize skeleton: checked
        optionVar -intValue colorizeSkeleton 1;
        // Include hidden selections on creation: checked
        optionVar -intValue bindIncludeHiddenSelections 0;
        // Heatmap falloff: 0.68
        optionVar -floatValue heatmapFalloff 0.68;
        // Falloff: 0.20
        optionVar -floatValue geodesicFalloff 0.2;
        // Resolution: given parameter.
        optionVar -intValue geodesicRes %d;
        // Validate voxel state: checked
        optionVar -intValue geodesicPostVoxelCheck 1;
        """
    
    kResolutionToCommand = {
        1024 : 1 ,
        512  : 2 ,
        256  : 3 ,
        128  : 4 ,
        64   : 5 ,
        }
    
    # Setup the values.
    mel.eval( melOptionsSettingCode % kResolutionToCommand[ resolution ] )




def OpenQuickRigUI( ):
    """
    This method is the entry point of the Quick Rig tool.
    
    It creates the Quick Rig tool window and brings it up.
    """
    
    tool = QuickRigTool( )
    tool.create( )
# ===========================================================================
# Copyright 2016 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
