#!/bin/python
# coding:utf-8
# -*- coding: cp936 -*-
import wx
import threading
import Queue
import time
import devicessh
import globalvalue
import os
import csv
import listctrl

Flag = True
Waitexec = False


class ReportThread(threading.Thread):

    def __init__(self, grid, scan_out):
        threading.Thread.__init__(self)
        self.scan_out = scan_out
        self.grid = grid

    # task "{'ip':'ok.'}"
    def run(self):
        global Flag, Waitexec
        while Flag:
            try:
                task = self.scan_out.get(False)
                print task
                if task == 'exec over':
                    Waitexec = False
                    continue
                wx.CallAfter(self.grid.UpdateData, task)
            except Queue.Empty:
                time.sleep(1)
                continue
        print 'out check'


class InstallWindows():

    def __init__(self, panel, queue):
        self.exec_in = Queue.Queue()
        self.queue = queue
        self.plugin = globalvalue.Plugin
        self.devices = devicessh.DeviceSsh(
            exec_in=self.exec_in, out=self.queue)
        self.InitGridBag(panel)
        self.reportthread()

    def reportthread(self):
        t = ReportThread(self.lstSucceedResults, self.queue)
        t.start()

    def InitGridBag(self, panel):
        self.groupSucceedBox = wx.StaticBox(  # 静态框
                                              panel,
                                              label=u'Device List',
                                              pos=(40, 20),
                                              size=(720, 510)
        )
        rect = self.groupSucceedBox.Rect

        self.lstSucceedResults = listctrl.ListCtrlCreate(panel, rect)
        self.inputb = wx.Button(
            panel, label=u"导入", pos=(rect[0] + 10, rect[1] + rect[3] + 5), size=(40, 20))
        self.outputb = wx.Button(
            panel, label=u"导出", pos=(rect[0] + 60, rect[1] + rect[3] + 5), size=(40, 20))
        self.delb = wx.Button(
            panel, label="Del", pos=(rect[0] + 110, rect[1] + rect[3] + 5), size=(40, 20))

        self.startb = wx.Button(
            panel, label="Start", pos=(rect[0] + rect[2] - 300, rect[1] + rect[3] + 5))
        self.stopb = wx.Button(
            panel, label="Stop", pos=(rect[0] + rect[2] - 200, rect[1] + rect[3] + 5))
        self.uninstallb = wx.Button(
            panel, label="Uninstall", pos=(rect[0] + rect[2] - 100, rect[1] + rect[3] + 5))

        self.startb.Bind(wx.EVT_BUTTON, self.OnStart, self.startb)
        self.stopb.Bind(wx.EVT_BUTTON, self.OnStop, self.stopb)
        self.inputb.Bind(wx.EVT_BUTTON, self.OnInput, self.inputb)
        self.outputb.Bind(wx.EVT_BUTTON, self.OnOutput, self.outputb)
        self.delb.Bind(wx.EVT_BUTTON, self.OnDel, self.delb)
        self.uninstallb.Bind(wx.EVT_BUTTON, self.OnUninstall, self.uninstallb)

    def OnInput(self, event):
        dlg = wx.FileDialog(None, "Open csv file...",
                            os.getcwd(),
                            style=wx.OPEN,
                            wildcard="CSV files (*.csv)|*.csv")
        if dlg.ShowModal() == wx.ID_OK:
            uipath = dlg.GetPath()
            reader = csv.reader(file(uipath, 'rb'))
            dictinput = {}
            for line in reader:
                dictinput['type'] = line[0]
                dictinput['ip'] = line[1]
                dictinput['user'] = line[2]
                dictinput['passwd'] = line[3]
                dictinput['mac'] = line[4]
                dictinput['status'] = line[5]
                dictinput['version'] = line[6]
                self.lstSucceedResults.UpdateData(dictinput)
        dlg.Destroy()

    def OnOutput(self, event):
        fieldnames = globalvalue.ListTitle
        dlg = wx.FileDialog(None,
                            "Save paint as ...",
                            os.getcwd(),
                            style=wx.SAVE | wx.OVERWRITE_PROMPT,
                            wildcard="CSV files (*.csv)|*.csv")
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:  # 如果没有文件名后缀
                filename = filename + '.csv'

            writer = csv.DictWriter(
                file(filename, 'wb'), fieldnames=fieldnames)
            dictcsv = []
            for i in range(self.lstSucceedResults.GetItemCount()):
                dictoutput = {}
                for j, title in enumerate(globalvalue.ListTitle):
                    dictoutput[title] = self.lstSucceedResults.GetItem(
                        i, col=j)
                dictcsv.append(dictoutput)
            writer.writerows(dictcsv)
        dlg.Destroy()

    def OnDel(self, event):
        self.lstSucceedResults.DeleteSelectItem()

    def OnStart(self, event):
        self.ExecScript('Start')

    def OnStop(self, event):
        self.ExecScript('Stop')

    def ExecScript(self, script):
        global Waitexec
        if Waitexec == True:
            self.OnWarning(
                u"The Last Exec is running,please wait!", u"Warning")
            return
        else:
            Waitexec = True
        i = self.lstSucceedResults.GetFirstSelected()
        if i == -1:
            self.OnWarning(u"Please Select item !", u"Warning")
            Waitexec = False
            return
        dlg = wx.TextEntryDialog(None, "input parameter and select ok or cancel this exec", 'Parameter',
                                 self.plugin.GetPluginParameter(self.lstSucceedResults.GetItem(i, col=0), script))
        if dlg.ShowModal() == wx.ID_OK:
            response = dlg.GetValue()
        else:
            Waitexec = False
            return
        task = []
        while i != -1:
            dictstart = {}
            dictstart['type'] = self.lstSucceedResults.GetItem(i, col=0)
            dictstart['ip'] = self.lstSucceedResults.GetItem(i, col=1)
            dictstart['user'] = self.lstSucceedResults.GetItem(i, col=2)
            dictstart['passwd'] = self.lstSucceedResults.GetItem(i, col=3)
            dictstart['mac'] = self.lstSucceedResults.GetItem(i, col=4)
            self.lstSucceedResults.SetStringItem(i, 5, script + 'ing')
            dictstart['version'] = self.plugin.GetPluginVersion(
                self.lstSucceedResults.GetItem(i, col=0))
            dictstart['path'] = self.plugin.GetPluginPackage(
                self.lstSucceedResults.GetItem(i, col=0))
            dictstart['script'] = self.plugin.GetPluginScript(
                self.lstSucceedResults.GetItem(i, col=0), script)
            dictstart['parameter'] = response
            i = self.lstSucceedResults.GetNextSelected(i)
            task.append(dictstart)
        task.append("exec over")
        for item in task:
            self.exec_in.put(item)
        self.devices.execScript(len(task))
        pass

    def OnUninstall(self, event):
        self.ExecScript('Uninstall')

    def OnExit(self):
        global Flag
        Flag = False

    def OnWarning(self, mess, title):
        dlg = wx.MessageDialog(None, mess, title, wx.OK | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
