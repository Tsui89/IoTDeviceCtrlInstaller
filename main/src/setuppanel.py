__author__ = 'IBM-cuiwc'
#!/bin/python
# coding:utf-8
import wx
import plugin
import globalvalue


class Setup(wx.Frame):

    def __init__(self, parent, pluginType):
        self.parent = parent
        self.pluginType = pluginType
        self.initUI()

    def initUI(self):
        wx.Frame.__init__(
            self,
            self.parent,
            id=-1,
            title=u"Plugin Setup",
            size=(400, 600),
            style=wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP | wx.FRAME_FLOAT_ON_PARENT)
        self.Center()
