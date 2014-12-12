#!/bin/python
# coding:utf-8
import wx
import newpanel
import installpanel
import infopanel
import Queue
import globalvalue
import log

[wxID_FRAME1, wxID_PANEL1, wxID_PANEL2, wxID_PANEL3, wxID_PANEL4] = [
    wx.NewId() for _init_ctrls in range(5)]


class Window(wx.Frame):
    def __init__(self):
        self.initUI()

    def initUI(self):
        wx.Frame.__init__(
            self,
            parent=None,
            id=wxID_FRAME1,
            title=u"Device Control Installer",
            size=(900, 600),
            style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.Center()
        self.boxall = wx.BoxSizer(wx.VERTICAL)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.AppLogo = wx.Icon("icon//manager.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.AppLogo)

        self.panel1 = wx.Panel(self, id=wxID_PANEL1, pos=(0, 0), size=(
            100, 600), style=wx.TAB_TRAVERSAL, name='panel1')
        self.panel1.Show(True)

        self.panel2 = wx.Panel(
            self, id=wxID_PANEL2, pos=(100, 0), size=(800, 600), name='panel2')
        self.panel2.Hide()
        self.panel3 = wx.Panel(self, id=wxID_PANEL3, pos=(100, 0), size=(
            800, 600), style=wx.TAB_TRAVERSAL, name='panel3')
        self.panel3.Hide()

        self.panel4 = wx.Panel(self, id=wxID_PANEL4, pos=(100, 0), size=(
            800, 600), style=wx.TAB_TRAVERSAL, name='panel4')
        self.panel4.Hide()

        self.menuCreate()
        self.newCreate()
        self.installCreate()
        self.infoCreate()
        self.panel2.Show()
        self.listmenu[0].Disable()
        self.newwindow.scanb.SetFocus()

    def menuCreate(self):
        self.groupmenubox = wx.StaticBox(
            self.panel1,
            label=u'分类',
            pos=(10, 80),
            size=(80, 400))
        self.menuimage = [
            'icon//newbutton.png',
            'icon//installed.png',
            'icon//info.png']
        self.listmenu = []
        menulabel = [
            u'添加',
            u'管理',
            u'关于']
        rect = self.groupmenubox.Rect
        x, y = rect[0] + (rect[2] - 40) / 2, rect[1] * 3
        for i in range(len(self.menuimage)):
            tempImg = wx.Image(self.menuimage[i], wx.BITMAP_TYPE_ANY)
            w, h = tempImg.GetSize()
            img = tempImg.Scale(w * 0.4, h * 0.4)
            self.listmenu.append(
                wx.BitmapButton(
                    self.panel1,
                    bitmap=img.ConvertToBitmap(),
                    pos=(x, rect[1] + rect[3] / 4 * (i + 1) - 20)
                )
            )
            wx.StaticText(self.panel1,
                          label=menulabel[i],
                          pos=(x + 10, rect[1] + rect[3] / 4 * (i + 1) + 30)
            )

        self.Bind(wx.EVT_BUTTON, self.newPanel, self.listmenu[0])
        self.Bind(wx.EVT_BUTTON, self.installPanel, self.listmenu[1])
        self.Bind(wx.EVT_BUTTON, self.infoPanel, self.listmenu[2])

    def newPanel(self, event):
        self.panel3.Hide()
        self.panel4.Hide()
        self.panel2.Show()
        self.newwindow.scanb.SetFocus()
        self.listmenu[0].Disable()
        self.listmenu[1].Enable()
        self.listmenu[2].Enable()

    def newCreate(self):
        self.newwindow = newpanel.NewWindows(self.panel2)

    def installPanel(self, event):
        self.panel2.Hide()
        self.panel4.Hide()
        self.panel3.Show()
        self.listmenu[0].Enable()
        self.listmenu[1].Disable()
        self.listmenu[2].Enable()
        self.installwindow.startb.SetFocus()

    def installCreate(self):
        self.installwindow = installpanel.InstallWindows(
            self.panel3)

    def infoPanel(self, event):
        self.panel2.Hide()
        self.panel3.Hide()
        self.panel4.Show()
        self.listmenu[0].Enable()
        self.listmenu[1].Enable()
        self.listmenu[2].Disable()

    def infoCreate(self):
        self.infowindow = infopanel.InfoWindows(self.panel4)

    def OnExit(self, event):
        self.newwindow.OnExit()
        self.installwindow.OnExit()
        globalvalue.RunFlag = False
        self.Destroy()


class MyApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False, filename=r"Runlog.txt")

    def OnInit(self):
        plugindict = globalvalue.Plugin
        if plugindict.GetPlugin() == {}:
            log.OnWarning(u"no plugin exist", u"Warning")
            return False
        frame = Window()
        frame.Show(True)
        return True


def main():
    app = MyApp()
    app.MainLoop()


if __name__ == "__main__":
    main()
