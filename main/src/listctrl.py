__author__ = 'IBM-cuiwc'
#!/bin/python
# coding:utf-8

import wx
import globalvalue
import os
import log


class ListCtrlCreate():

    def __init__(self, panel, rect):
        self.panel = panel

        self.lstSucceedResults = wx.ListCtrl(
            panel,
            pos=(rect[0] + 10, rect[1] + 20),
            style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES,
            size=(rect[2] - 20, rect[3] - 30)
        )
        w = self.lstSucceedResults.Rect[2]

        headings = globalvalue.ListTitle
        widths = [w * 0.16, w * 0.15, w * 0.0,
                  w * 0.0, w * 0.2, w * 0.3, w * 0.15]
        for i, string in enumerate(headings):
            self.lstSucceedResults.InsertColumn(
                col=i, heading=string, width=widths[i])
        self.lstSucceedResults.Bind(
            wx.EVT_LIST_ITEM_ACTIVATED, self.OnDoubleLeftClick, self.lstSucceedResults)

        self.menu = wx.Menu()
        self.copymenu = wx.Menu()
        for text in globalvalue.ListTitle:
            item = self.copymenu.Append(-1, text)
            self.panel.Bind(wx.EVT_MENU, self.OnCopyItemSelected, item)
        self.menu.AppendMenu(-1, 'Copy..', self.copymenu)
        for text in ['Refesh']:
            item = self.menu.Append(-1, text)
            self.panel.Bind(wx.EVT_MENU, self.OnMenuItemSelected, item)
        self.menu.AppendSeparator()
        self.lstSucceedResults.Bind(
            wx.EVT_CONTEXT_MENU, self.OnRightClick, self.lstSucceedResults)

    def OnDoubleLeftClick(self, event):
        index = event.GetIndex()
        logfile = globalvalue.LogPath + os.path.sep + self.GetItem(index, col=0) + '-' + self.GetItem(index,
                                                                                                      col=1) + '.Log'
        try:
            os.startfile(logfile)
        except:
            log.OnWarning(logfile, 'open log file err.')

    def OnRightClick(self, event):
        # index = event.GetIndex()
        pos = event.GetPosition()
        pos = self.panel.ScreenToClient(pos)
        self.panel.PopupMenu(self.menu, pos)

    def OnMenuItemSelected(self, event):
        menu = self.menu.FindItemById(event.GetId()).GetText()
        indexs = self.GetSelectedIndexs()
        if indexs == None:
            return
        for index in indexs:
            self.MenuExec(index, menu)

    def OnCopyItemSelected(self, event):
        menu = self.copymenu.FindItemById(event.GetId()).GetText()
        indexs = self.GetSelectedIndexs()
        if indexs == None:
            return
        text = ''
        for index in indexs:
            text += self.MenuExec(index, menu) + ';;'
        self.OnCopyClipboard(text)

    def OnCopyClipboard(self, text):
        print text
        data = wx.TextDataObject(str(text))
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        else:
            log.OnWarning("Unable to open the clipboard", "Error")

    def MenuExec(self, index, item):
        if item in globalvalue.ListTitle:
            i = globalvalue.ListTitle.index(item)
            return self.GetItem(index, i)
        elif item == "Refresh":
            print 'Refresh'

    def GetSelectedIndexs(self):
        selectid = self.GetFirstSelected()
        if selectid == -1:
            return None
        indexs = []
        while selectid != -1:
            indexs.append(selectid)
            selectid = self.GetNextSelected(selectid)
        return indexs

    def GetItemCount(self):
        return self.lstSucceedResults.GetItemCount()

    def GetItem(self, index, col):
        return self.lstSucceedResults.GetItem(index, col=col).GetText()

    def GetSelectedItemCount(self):
        return self.lstSucceedResults.GetSelectedItemCount()

    def GetFirstSelected(self):
        return self.lstSucceedResults.GetFirstSelected()

    def GetNextSelected(self, item):
        return self.lstSucceedResults.GetNextSelected(item)

    def UpdateData(self, task):
        index = self.isExist(task.get('type'), task.get('ip'))
        if index != None:
            self.changeItem(index, task)
        else:
            self.lstSucceedResults.Append(self.itemformat(task))
        pass

    def SetStringItem(self, index, col, str):
        self.lstSucceedResults.SetStringItem(index, col, str, -1)

    def DeleteSelectItem(self):
        for i in range(self.lstSucceedResults.GetSelectedItemCount()):
            self.lstSucceedResults.DeleteItem(
                self.lstSucceedResults.GetFirstSelected())

    def isExist(self, type, ip):
        for i in range(self.lstSucceedResults.GetItemCount()):
            if ip == self.lstSucceedResults.GetItem(i, col=1).GetText() and type == self.lstSucceedResults.GetItem(i,
                                                                                                                   col=0).GetText():
                return i
        return None

    def changeItem(self, index, task):
        try:
            for col, string in enumerate(self.itemformat(task)):
                self.lstSucceedResults.SetStringItem(index, col, string, -1)
        except:
            log.OnWarning('changeItem format error', 'Warnning')
            pass

    def itemformat(self, task):
        return [task.get('type', ''), task.get('ip', ''), task.get('user', ''), task.get('passwd', ''),
                task.get('mac', ''), task.get('status', ''), task.get('version', '')]