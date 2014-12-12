#!/bin/python
# coding:utf-8

import devicessh
import globalvalue
import listctrl

import wx
import re
import Queue
import socket
import threading
import time
import os
import platform
import struct

ipformat = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
lanformat = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(x|X)\b"
Waitinstall = False
Safeflag = False


class ReportThread(threading.Thread):
    def __init__(self, scanb, installb, grid):
        threading.Thread.__init__(self)
        self.scanb = scanb
        self.installb = installb
        self.scan_out = globalvalue.QNewReport
        self.grid = grid

    # task "{'ip':'ok.'}"
    def run(self):
        while globalvalue.RunFlag:
            try:
                task = self.scan_out.get(False)
                if task == 'scan over':
                    self.scanb.Enable()
                    continue
                elif task == 'install over':
                    self.installb.Enable()
                    continue
                wx.CallAfter(self.grid.UpdateData, task)
            except Queue.Empty:
                time.sleep(1)
                continue
        print 'out check'


def GetLocal():
    operation = platform.system()
    localip = '127.0.0.1'
    if operation == 'Windows':
        localip = socket.gethostbyname(socket.gethostname())
    elif operation == 'Linux':
        import fcntl

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        localip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', 'eth0'))[20:24])

    i = localip.rfind(".")
    return localip[0:i + 1] + 'x'


class NewWindows():
    def __init__(self, panel):

        self.plugin = globalvalue.Plugin
        self.InitDevice()
        self.InitGridBag(panel)
        self.reportthread()

    def InitDevice(self):

        self.scandev = devicessh.DeviceSsh()
        self.instdev = devicessh.DeviceSsh()
        self.plugintype = self.plugin.GetPluginType()
        # print self.plugin
        print self.plugintype

    def reportthread(self):
        t = ReportThread(
            self.scanb, self.installb, self.lstSucceedResults)
        t.start()

    def InitGridBag(self, panel):
        self.plugininfo = wx.StaticBox(
            panel,
            label=u' Plugin Info ',
            pos=(40, 20),
            size=(300, 150))
        rect = self.plugininfo.Rect
        label = ["Type", "User", "Password"]
        for i in range(3):
            wx.StaticText(
                panel, label=label[i], pos=(rect[0] + 25, rect[1] + 25 + i * 30))
        self.Chdev = wx.Choice(
            panel, -1, choices=self.plugintype, pos=(rect[0] + 100, rect[1] + 25), size=globalvalue.WidgetSize)
        self.Chdev.SetSelection(0)
        self.tcuser = wx.TextCtrl(panel, -1, self.plugin.GetPluginUser(self.plugintype[self.Chdev.GetSelection()]),
                                  pos=(rect[0] + 100, rect[1] + 55), size=globalvalue.WidgetSize)
        self.tcpwd = wx.TextCtrl(panel, -1, self.plugin.GetPluginPasswd(self.plugintype[self.Chdev.GetSelection()]),
                                 pos=(rect[0] + 100, rect[1] + 85), size=globalvalue.WidgetSize, style=wx.TE_PASSWORD)
        self.saveb = wx.Button(
            panel, label="Save", pos=(rect[0] + 210, rect[1] + 115), size=globalvalue.ButtunMaxSize)
        self.laninfo = wx.StaticBox(
            panel,
            label=u' LAN ',
            pos=(rect[0] + 360, rect[1]),
            size=(300, 150))
        rectlan = self.laninfo.Rect
        wx.StaticText(
            panel, label=u'Ip Range', pos=(rectlan[0] + 25, rectlan[1] + 25))
        wx.StaticText(panel, label=u'(example: 192.168.1.4 or 192.168.1.x )', pos=(
            rectlan[0] + 30, rectlan[1] + 55))
        self.tcip = wx.TextCtrl(
            panel, -1, GetLocal(), pos=(rectlan[0] + 100, rectlan[1] + 25), size=globalvalue.WidgetSize)
        self.scanb = wx.Button(
            panel, label="Scan", pos=(rectlan[0] + 210, rect[1] + 115), size=globalvalue.ButtunMaxSize)
        self.groupSucceedBox = wx.StaticBox(  # 静态框
                                              panel,
                                              label=u'Scan List',
                                              pos=(
                                                  rect[0], rect[1] + rect[3] + 20),
                                              size=(720, 340)
        )
        rect = self.groupSucceedBox.Rect

        self.lstSucceedResults = listctrl.ListCtrlCreate(panel, rect)
        self.deleteb = wx.Button(
            panel, label="Del", pos=(rect[0] + 10, rect[1] + rect[3] + 5), size=globalvalue.ButtunMinSize)
        self.installb = wx.Button(
            panel, label="Install", pos=(rect[0] + rect[2] - 100, rect[1] + rect[3] + 5),
            size=globalvalue.ButtunMaxSize)

        self.Chdev.Bind(wx.EVT_CHOICE, self.DevChoice, self.Chdev)
        self.scanb.Bind(wx.EVT_BUTTON, self.OnScan, self.scanb)
        self.saveb.Bind(wx.EVT_BUTTON, self.OnSave, self.saveb)
        self.deleteb.Bind(wx.EVT_BUTTON, self.OnDelete, self.deleteb)
        self.installb.Bind(wx.EVT_BUTTON, self.OnInstall, self.installb)

    def DevChoice(self, event):
        print event.GetSelection()
        self.tcuser.ChangeValue(
            self.plugin.GetPluginUser(self.plugintype[self.Chdev.GetSelection()]))
        self.tcpwd.ChangeValue(
            self.plugin.GetPluginPasswd(self.plugintype[self.Chdev.GetSelection()]))

    def OnWarning(self, mess, title):
        dlg = wx.MessageDialog(None, mess, title, wx.OK | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    def OnSave(self, event):
        self.plugin.SetPluginConfSave(self.plugintype[self.Chdev.GetSelection()], self.tcuser.GetLineText(0),
                                      self.tcpwd.GetLineText(0))

    def OnScan(self, event):
        if re.match(ipformat, self.tcip.GetLineText(0)) == None and re.match(lanformat,
                                                                             self.tcip.GetLineText(0)) == None:
            self.OnWarning(u"Ip or Ip Range format error.", u"Warning")
            return
        dlg = wx.SingleChoiceDialog(
            None, 'How long timeout are you using?', 'Single Choice', ['1s', '2s', '3s', '4s'])
        if dlg.ShowModal() == wx.ID_OK:
            print dlg.GetSelection()
            socket.setdefaulttimeout(dlg.GetSelection() + 1)
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        dictscan = {}
        if re.match(ipformat, self.tcip.GetLineText(0)):
            dictscan['type'] = self.plugintype[self.Chdev.GetSelection()]
            dictscan['user'] = self.tcuser.GetLineText(0)
            dictscan['passwd'] = self.tcpwd.GetLineText(0)
            dictscan['ip'] = self.tcip.GetLineText(0)
            self.scandev.AddJob(dictscan.copy())
        elif re.match(lanformat, self.tcip.GetLineText(0)):
            i = self.tcip.GetLineText(0).rfind(".")
            ip = self.tcip.GetLineText(0)[0:i + 1]
            for i in range(1, 255):
                dictscan['type'] = self.plugintype[self.Chdev.GetSelection()]
                dictscan['user'] = self.tcuser.GetLineText(0)
                dictscan['passwd'] = self.tcpwd.GetLineText(0)
                dictscan['ip'] = ip + str(i)
                self.scandev.AddJob(dictscan.copy())
        self.scandev.AddJob("scan over")
        self.scandev.scan(10)
        self.scanb.Disable()
        print 'scan'

    def OnDelete(self, event):
        global Safeflag
        if Safeflag:
            self.OnWarning(u"task is loading ,please wait", u"Warnning")
            return
        self.lstSucceedResults.DeleteSelectItem()

    def OnInstall(self, event):
        global Safeflag
        i = self.lstSucceedResults.GetFirstSelected()
        if i == -1:
            self.OnWarning(u"Please Select item !", u"Warning")
            return
        dlg = wx.TextEntryDialog(None, "input parameter and select 'ok' or 'cancel' this exec", 'Parameter',
                                 self.plugin.GetPluginParameter(self.plugintype[self.Chdev.GetSelection()], 'Install'))
        response = ''
        if dlg.ShowModal() == wx.ID_OK:
            response = dlg.GetValue()
        else:
            return

        self.plugin.PutTarfile()
        Safeflag = True
        while i != -1:
            dictinstall = {}
            if self.lstSucceedResults.GetItem(i, col=0) != "":
                dictinstall['type'] = self.lstSucceedResults.GetItem(i, col=0)
                dictinstall['ip'] = self.lstSucceedResults.GetItem(i, col=1)
                dictinstall['user'] = self.lstSucceedResults.GetItem(i, col=2)
                dictinstall['passwd'] = self.lstSucceedResults.GetItem(
                    i, col=3)
                dictinstall['mac'] = self.lstSucceedResults.GetItem(i, col=4)
                dictinstall['version'] = self.plugin.GetPluginVersion(
                    self.lstSucceedResults.GetItem(i, col=0))
                self.lstSucceedResults.SetStringItem(i, 5, 'Installing...')
                dictinstall['package'] = self.plugin.GetPluginPath(
                    self.lstSucceedResults.GetItem(i, col=0)) + os.path.sep + self.plugin.GetPluginPackage(
                    self.lstSucceedResults.GetItem(i, col=0)) + '.tar.gz'
                dictinstall['tar'] = self.plugin.GetPluginPackage(
                    self.lstSucceedResults.GetItem(i, col=0)) + '.tar.gz'
                dictinstall['script'] = self.plugin.GetPluginScript(
                    self.lstSucceedResults.GetItem(i, col=0), 'Install')
                dictinstall['path'] = self.plugin.GetPluginPackage(
                    self.lstSucceedResults.GetItem(i, col=0))
                dictinstall['parameter'] = response
                self.scandev.AddJob(dictinstall.copy())
            i = self.lstSucceedResults.GetNextSelected(i)
        Safeflag = False
        self.scandev.AddJob("install over")

        self.instdev.install(self.lstSucceedResults.GetSelectedItemCount())
        self.installb.Disable()

    def OnExit(self):
        pass

