#!/bin/python
# coding:utf-8
import wx
import threading


class NewWindows():

    def __init__(self, panel):
        self.InitGridBag(panel)

    def InitGridBag(self, panel):
        self.infosb = wx.StaticBox(
            panel,
            label=u' Software Information ',
            pos=(200, 100),
            size=(400, 200))
        rect = self.infosb.Rect
        wx.StaticText(
            panel,
            label=u'有问题请联系:756661204@qq.com',
            pos=((rect[0] + rect[2] - 50) / 2, rect[1] + rect[3] - 30))


'''
        self.staticb=wx.StaticBox(
            panel,
            label=u'',
            pos  =(100,340),
            size =(600, 180))
        rect = self.staticb.Rect
        self.multtext = wx.TextCtrl(panel,-1,u'你的建议是：',
            pos=(rect[0]+10,rect[1]+20),size=(580,120),
            style=(wx.TE_MULTILINE | wx.TE_AUTO_SCROLL | wx.TE_DONTWRAP | wx.TE_RICH2))
'''
