import FreeCAD
import warnings

class DocumentObject(object):
    def __init__(self):
        object.__setattr__(self,'__object__',None)
        object.__setattr__(self,'__vobject__',None)
        self.birth = list()

        """
App.newDocument()
App.setActiveDocument("Unnamed")
App.ActiveDocument=App.getDocument("Unnamed")
Gui.ActiveDocument=Gui.getDocument("Unnamed")
from SurfaceEditing import SMesh
m = SMesh()
"""
    def __getattribute__(self,name):
        #FreeCAD.Console.PrintMessage("getattr %s\n"%name)
        try:
            return object.__getattribute__(self,name)
        except AttributeError:
            pass
        try:
            try:
                o = object.__getattribute__(self,'__object__')
            except AttributeError:
                #FIXME workaround for deserialisation split
                o = object.__getattribute__(self,'__vobject__')
                o = o.Object
            return getattr(o,name)
        except AttributeError:
            pass
        try:
            try:
                o = object.__getattribute__(self,'__vobject__')
            except AttributeError:
                #FIXME workaround for deserialisation split
                o = object.__getattribute__(self,'__object__')
                o = o.ViewObject
            return getattr(o,name)
        except AttributeError:
            if name == '__vobject__':
                return None
            else:
                raise AttributeError("no such attribute: %s"%name)
        
    def __setattr__(self,name,value):
        try:
            if getattr(self,'__object__',False):
                #FIXME deserialisation split
                setattr(self.__object__,name,value)
            else:
                setattr(self.__vobject__.Object,name,value)
            return
        except AttributeError:
            pass
        try:
            if getattr(self,'__vobject__',False):
                #FIXME deserialisation split
                setattr(self.__vobject__,name,value)
            else:
                setattr(self.__object__.ViewObject,name,value)
            return
        except AttributeError:
            pass
        object.__setattr__(self, name, value)
        
    def getParentByType(self,tname):
        for p in self.InList:
            prox=getattr(p,'Proxy',None)
            if prox and prox.pytype == tname:
                return prox
        for p in self.InList:
            prox=getattr(p,'Proxy',None)
            pp = prox.getParentByType(tname)
            if pp:
                return pp
        return None
            
        
    def getobj(self):
        warnings.warn("getobj should not exist", DeprecationWarning)
        return self.__object__

    def getvobj(self):
        warnings.warn("getcobj should not exist", DeprecationWarning)
        return self.__vobject__

    def onChanged(self,prop,attaching=False):
        #FreeCAD.Console.PrintMessage("base.onchanged %s %s %s\n"%(id(self), prop, attaching))
        if attaching == 'Proxy':
            #FreeCAD.Console.PrintMessage("attaching %s\n"%(prop))
            object.__setattr__(self,'__object__',prop)
            return
        return

    def attach(self,obj=False):
        #FreeCAD.Console.PrintMessage("attached %s\n"%(self))
        if obj:
            object.__setattr__(self,'__vobject__',obj)
        return

    def execute(self):
        FreeCAD.Console.PrintMessage("execute %s\n"%(self))
        try:
            mesh = self.getParentByType('SMesh')
            for op in self.birth:
                mesh.redoop(op,op.sources)
        except:
            prtb()
        return

    def __getstate__(self):
        return "spam"

    def __setstate__(self,value):
        return

    def addBirth(self,op):
        #FIXME if self.birth: two operations resulted the same mesh element
        #if this keeps this way, then no problem. Solving the problem of a future split
        #is a too complicated one, so let's just record all ones for now
        bases=getattr(self,'Bases',None)
        if not bases:
            self.addProperty("App::PropertyLinkList","Bases","Base", "base objects of this one")
        self.birth.append(op)
        self.Bases += map(lambda x: FreeCAD.ActiveDocument.getObject(x),op.sources)

    def claimChildren(self):
        bases=getattr(self,'Bases',list())
        return bases

import sys, traceback

def prtb():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    for i in traceback.format_exception(exc_type, exc_value,exc_traceback):
        FreeCAD.Console.PrintMessage(i)

