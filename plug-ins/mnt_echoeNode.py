import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaRender as OpenMayaRender

from functools import partial

maya_useNewAPI = True

def maya_useNewAPI():
    pass

class Mnt_echoeNode(OpenMaya.MPxNode):
    kPluginNodeName = 'mnt_echoe'
    id              = OpenMaya.MTypeId( 0xDAE9 )

    firstObjectCallback     = None
    secondObjectCallback    = None

    def __init__(self):
        OpenMaya.MPxNode.__init__(self)

    @staticmethod
    def creator():
        return Mnt_echoeNode()

    @staticmethod
    def initialize():
        # Defines node input attributes
        messageAttrFn = OpenMaya.MFnMessageAttribute()
        numericAttrFn = OpenMaya.MFnNumericAttribute()

        Mnt_echoeNode.firstCTRL_attr    = messageAttrFn.create('firstController', 'First_Controller')
        messageAttrFn.hidden            = False
        messageAttrFn.writable          = True
        messageAttrFn.connectable       = True
        Mnt_echoeNode.addAttribute(Mnt_echoeNode.firstCTRL_attr)

        Mnt_echoeNode.secondCTRL_attr   = messageAttrFn.create('secondController', 'Second_Controller')
        messageAttrFn.hidden            = False
        messageAttrFn.writable          = True
        messageAttrFn.connectable       = True
        Mnt_echoeNode.addAttribute(Mnt_echoeNode.secondCTRL_attr)

        Mnt_echoeNode.useTRSAttr = numericAttrFn.create('Use_Transform_Attributes', 'Use_Transform_Attributes', OpenMaya.MFnNumericData.kBoolean, False)
        numericAttrFn.hidden = False
        numericAttrFn.writable = True
        numericAttrFn.connectable = True
        numericAttrFn.channelBox = True
        numericAttrFn.keyable = True
        Mnt_echoeNode.addAttribute(Mnt_echoeNode.useTRSAttr)
        # _____________________________

        return
    
    def connectionMade(self, plug, otherPlug, asSrc):
        if plug.attribute() == Mnt_echoeNode.firstCTRL_attr:
            self.firstObjectCallback = OpenMaya.MEventMessage.addEventCallback('idle', self.firstObjectCallbackFn)
        return
    
    def connectionBroken(self, plug, otherPlug, asSrc):
        if plug.attribute() == Mnt_echoeNode.firstCTRL_attr:
            OpenMaya.MMessage.removeCallback(self.firstObjectCallback)
        return
    
    def setDependentsDirty(self, plug, plugArray):
        return
    
    def compute(self, plug, dataBlock):
        dataBlock.setClean(plug)
        return
    
    def firstObjectCallbackFn(self, *args):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()

        nodeDnFn                = OpenMaya.MFnDependencyNode(self.thisMObject())
        firstControllerPlug     = nodeDnFn.findPlug('firstController', False)
        firstControllerObj      = firstControllerPlug.source().node()
        firstControllerObjPath  = OpenMaya.MDagPath().getAPathTo(firstControllerObj)

        secondControllerPlug    = nodeDnFn.findPlug('secondController', False)
        secondControllerObj     = secondControllerPlug.source().node()
        
        try:
            secondControllerObjPath  = OpenMaya.MDagPath().getAPathTo(secondControllerObj)
        except:
            return
        
        if selectionList.hasItem(firstControllerObjPath):
            self.transferAttributesValues(firstControllerObj, secondControllerObj)
            
        if selectionList.hasItem(secondControllerObjPath):
            self.transferAttributesValues(secondControllerObj, firstControllerObj)

        return

    def transferAttributesValues(self, firstNodeObj, secondNodeObj):
        useTRSAttrPlugValue = OpenMaya.MFnDependencyNode(self.thisMObject()).findPlug('Use_Transform_Attributes', False).asBool()
        firstNodeDnFn           = OpenMaya.MFnDependencyNode(firstNodeObj)
        secondNodeDnFn          = OpenMaya.MFnDependencyNode(secondNodeObj)

        firstNodeAttrList = cmds.listAttr(firstNodeDnFn.name(), k = True)

        for attr in firstNodeAttrList:
            if useTRSAttrPlugValue == False:
                if 'translate' in attr or 'rotate' in attr or 'scale' in attr:
                    continue
            else:
                pass

            value = firstNodeDnFn.findPlug(attr, False).asMDataHandle()
            try:
                plug = secondNodeDnFn.findPlug(attr, False)
                plug.setMDataHandle(value)
            except:
                pass

        return True

def initializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj, "Florian Delarque", "0.1.1", "Any")

    try:
        plugin.registerNode(Mnt_echoeNode.kPluginNodeName, Mnt_echoeNode.id, Mnt_echoeNode.creator, Mnt_echoeNode.initialize, OpenMaya.MPxNode.kDependNode)
    except:
        OpenMaya.MGlobal.displayError('Failed to register node\n')
        raise

def uninitializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)

    try:
        plugin.deregisterNode(Mnt_echoeNode.id)
    except:
        OpenMaya.MGlobal.displayError('Failed to deregister node\n')
        pass