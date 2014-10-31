__author__ = 'IBM-cuiwc'
import wx


def OnWarning(mess, title):
    dlg = wx.MessageDialog(None, mess, title, wx.OK | wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_OK:
        dlg.Destroy()
