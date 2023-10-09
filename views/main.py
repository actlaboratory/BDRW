# -*- coding: utf-8 -*-
# main view
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>

import wx

import constants
import globalVars
import update
import menuItemsStore

from .base import *
from simpleDialog import *

from views import globalKeyConfig
from views import sample
from views import settingsDialog
from views import versionDialog

from byte import Byte
import os

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.events = Events(self, self.identifier)
		title = constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier, "sizeX", 800, 400),
			self.app.config.getint(self.identifier, "sizeY", 600, 300),
			self.app.config.getint(self.identifier, "positionX", 50, 0),
			self.app.config.getint(self.identifier, "positionY", 50, 0)
		)
		self.InstallMenuEvent(Menu(self.identifier), self.events.OnMenuSelect)
		creator = views.ViewCreator.ViewCreator(self.viewMode, self.creator.GetPanel(), self.creator.GetSizer())
		self.byteList,dummy = creator.virtualListCtrl(_("内容"), proportion=1, sizerFlag=wx.EXPAND)
		self.byteList.AppendColumn(_("位置"))
		self.byteList.AppendColumn(_("データ"))
		self.byteList.AppendColumn(_("アスキーコード"))
		self.datalist = []
		self.datalist.append(Byte(b'G', 0))
		self.datalist.append(Byte(b'U', 1))
		self.datalist.append(Byte(b'R', 2))
		self.datalist.append(Byte(b'E', 3))
		self.datalist.append(Byte(b'D', 4))
		self.datalist.append(Byte(b'O', 5))
		self.datalist.append(Byte(b'R', 6))
		self.datalist.append(Byte(b'A', 7))
		self.byteList.setList(self.datalist)
		self.byteList.GetColumnCount()




class Menu(BaseMenu):
	def Apply(self, target):
		"""指定されたウィンドウに、メニューを適用する。"""

		# メニュー内容をいったんクリア
		self.hMenuBar = wx.MenuBar()

		# メニューの大項目を作る
		self.hFileMenu = wx.Menu()
		self.hOptionMenu = wx.Menu()
		self.hHelpMenu = wx.Menu()

		# ファイルメニュー
		self.RegisterMenuCommand(self.hFileMenu, {
			"FILE_OPEN": self.parent.events.open,
			"FILE_EXAMPLE": self.parent.events.example,
			"FILE_EXIT": self.parent.events.exit,
		})

		# オプションメニュー
		self.RegisterMenuCommand(self.hOptionMenu, {
			"OPTION_OPTION": self.parent.events.option,
			"OPTION_KEY_CONFIG": self.parent.events.keyConfig,
		})

		# ヘルプメニュー
		self.RegisterMenuCommand(self.hHelpMenu, {
			"HELP_UPDATE": self.parent.events.checkUpdate,
			"HELP_VERSIONINFO": self.parent.events.version,
		})

		# メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu, _("ファイル(&F))"))
		self.hMenuBar.Append(self.hOptionMenu, _("オプション(&O)"))
		self.hMenuBar.Append(self.hHelpMenu, _("ヘルプ(&H)"))
		target.SetMenuBar(self.hMenuBar)


class Events(BaseEvents):
	_lastBinContentCursor = 0
	_lastAsciiContentCursor = 0

	def open(self, evt):
		d = wx.FileDialog(None, _("変換元ファイルの選択"), style = wx.FD_OPEN)
		r = d.ShowModal()
		if r == wx.ID_CANCEL: return

	def monitorBinContent(self, evt):
		cursor = self.parent.binContent.GetInsertionPoint()
		if cursor != self._lastBinContentCursor:
			dummy, x, y = self.parent.binContent.PositionToXY(cursor)
			current = x//3
			self._lastAsciiContentCursor = self.parent.asciiContent.XYToPosition(current, y)
			self.parent.asciiContent.SetInsertionPoint(self._lastAsciiContentCursor)
			self._lastBinContentCursor = cursor

	def monitorAsciiContent(self, event):
		cursor = self.parent.asciiContent.GetInsertionPoint()
		if cursor != self._lastAsciiContentCursor:
			dummy, x, y = self.parent.asciiContent.PositionToXY(cursor)
			current = x*3
			self._lastBinContentCursor = self.parent.binContent.XYToPosition(current, y)
			self.parent.binContent.SetInsertionPoint(self._lastBinContentCursor)
			self._lastAsciiContentCursor = cursor

	def onEnterInBinContent(self, event):
		self.monitorBinContent(None) #カーソル位置を同期させておく
		self.parent.binContent.WriteText("\n")
		self.parent.asciiContent.WriteText("\n")


	def example(self, event):
		d = sample.Dialog()
		d.Initialize()
		r = d.Show()

	def onExit(self, event):
		super().OnExit()
		self.parent.binContentTimer.Stop()
		self.parent.binContentTimer.Destroy()
		event.Skip()

	def exit(self, event):
		self.parent.hFrame.Close()

	def option(self, event):
		d = settingsDialog.Dialog()
		d.Initialize()
		d.Show()

	def keyConfig(self, event):
		if self.setKeymap(self.parent.identifier, _("ショートカットキーの設定"), filter=keymap.KeyFilter().SetDefault(False, False)):
			# ショートカットキーの変更適用とメニューバーの再描画
			self.parent.menu.InitShortcut()
			self.parent.menu.ApplyShortcut(self.parent.hFrame)
			self.parent.menu.Apply(self.parent.hFrame)

	def checkUpdate(self, event):
		update.checkUpdate()

	def version(self, event):
		d = versionDialog.dialog()
		d.Initialize()
		r = d.Show()

	def setKeymap(self, identifier, ttl, keymap=None, filter=None):
		if keymap:
			try:
				keys = keymap.map[identifier.upper()]
			except KeyError:
				keys = {}
		else:
			try:
				keys = self.parent.menu.keymap.map[identifier.upper()]
			except KeyError:
				keys = {}
		keyData = {}
		menuData = {}
		for refName in defaultKeymap.defaultKeymap[identifier].keys():
			title = menuItemsDic.getValueString(refName)
			if refName in keys:
				keyData[title] = keys[refName]
			else:
				keyData[title] = _("なし")
			menuData[title] = refName

		d = globalKeyConfig.Dialog(keyData, menuData, [], filter)
		d.Initialize(ttl)
		if d.Show() == wx.ID_CANCEL:
			return False

		keyData, menuData = d.GetValue()

		# キーマップの既存設定を置き換える
		newMap = ConfigManager.ConfigManager()
		newMap.read(constants.KEYMAP_FILE_NAME)
		for name, key in keyData.items():
			if key != _("なし"):
				newMap[identifier.upper()][menuData[name]] = key
			else:
				newMap[identifier.upper()][menuData[name]] = ""
		newMap.write()
		return True
