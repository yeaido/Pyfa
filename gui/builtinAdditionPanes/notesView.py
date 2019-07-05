# noinspection PyPackageRequirements
import wx

from service.fit import Fit
import gui.globalEvents as GE
import gui.mainFrame
from gui.utils.helpers_wxPython import HandleCtrlBackspace


class NotesView(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.lastFitId = None
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.editNotes = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.BORDER_NONE, )
        mainSizer.Add(self.editNotes, 1, wx.EXPAND)
        self.SetSizer(mainSizer)
        self.mainFrame.Bind(GE.FIT_CHANGED, self.fitChanged)
        self.Bind(wx.EVT_TEXT, self.onText)
        self.editNotes.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.saveTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.delayedSave, self.saveTimer)

    def OnKeyDown(self, event):
        if event.RawControlDown() and event.GetKeyCode() == wx.WXK_BACK:
            HandleCtrlBackspace(self.editNotes)
        else:
            event.Skip()

    def fitChanged(self, event):
        event.Skip()
        activeFitID = self.mainFrame.getActiveFit()
        if activeFitID is not None and event.fitID is not None and event.fitID != activeFitID:
            return

        sFit = Fit.getInstance()
        fit = sFit.getFit(event.fitID)

        self.saveTimer.Stop()  # cancel any pending timers

        self.Parent.Parent.DisablePage(self, not fit or fit.isStructure)

        # when switching fits, ensure that we save the notes for the previous fit
        if self.lastFitId is not None:
            sFit.editNotes(self.lastFitId, self.editNotes.GetValue())

        if event.fitID is None and self.lastFitId is not None:
            self.lastFitId = None
            return
        elif event.fitID != self.lastFitId:
            self.lastFitId = event.fitID
            self.editNotes.SetValue(fit.notes or "")

    def onText(self, event):
        # delay the save so we're not writing to sqlite on every keystroke
        self.saveTimer.Stop()  # cancel the existing timer
        self.saveTimer.Start(1000, True)

    def delayedSave(self, event):
        sFit = Fit.getInstance()
        sFit.editNotes(self.lastFitId, self.editNotes.GetValue())
