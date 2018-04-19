# -*- coding: utf-8 -*-

# Copyright (C) 2011 Chris Dekter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from PyKDE4.kdeui import *
from PyKDE4.kio import KFileDialog
from PyKDE4.kdecore import i18n, KAutostart
from PyQt4.QtGui import *

from .. import configmanager as cm
from .dialogs import GlobalHotkeyDialog

from . import generalsettings, specialhotkeysettings, enginesettings

class GeneralSettings(QWidget, generalsettings.Ui_Form):
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        generalsettings.Ui_Form.__init__(self)
        self.setupUi(self)

        self.promptToSaveCheckbox.setChecked(cm.ConfigManager.SETTINGS[cm.PROMPT_TO_SAVE])
        self.showTrayCheckbox.setChecked(cm.ConfigManager.SETTINGS[cm.SHOW_TRAY_ICON])
        #self.allowKbNavCheckbox.setChecked(cm.ConfigManager.SETTINGS[cm.MENU_TAKES_FOCUS])
        self.allowKbNavCheckbox.setVisible(False)
        self.sortByUsageCheckbox.setChecked(cm.ConfigManager.SETTINGS[cm.SORT_BY_USAGE_COUNT])
        self.enableUndoCheckbox.setChecked(cm.ConfigManager.SETTINGS[cm.UNDO_USING_BACKSPACE])
        
    def save(self):
        cm.ConfigManager.SETTINGS[cm.PROMPT_TO_SAVE] = self.promptToSaveCheckbox.isChecked()
        cm.ConfigManager.SETTINGS[cm.SHOW_TRAY_ICON] = self.showTrayCheckbox.isChecked()
        #cm.ConfigManager.SETTINGS[cm.MENU_TAKES_FOCUS] = self.allowKbNavCheckbox.isChecked()
        cm.ConfigManager.SETTINGS[cm.SORT_BY_USAGE_COUNT] = self.sortByUsageCheckbox.isChecked()
        cm.ConfigManager.SETTINGS[cm.UNDO_USING_BACKSPACE] = self.enableUndoCheckbox.isChecked()


class SpecialHotkeySettings(QWidget, specialhotkeysettings.Ui_Form):
    
    KEY_MAP = GlobalHotkeyDialog.KEY_MAP
    REVERSE_KEY_MAP = GlobalHotkeyDialog.REVERSE_KEY_MAP    

    def __init__(self, parent, configManager):
        QWidget.__init__(self, parent)
        specialhotkeysettings.Ui_Form.__init__(self)
        self.setupUi(self)
        
        self.configManager = configManager
        
        self.showConfigDlg = GlobalHotkeyDialog(parent)
        self.toggleMonitorDlg = GlobalHotkeyDialog(parent)
        
        self.useConfigHotkey = self.__loadHotkey(configManager.configHotkey, self.configKeyLabel, 
                                                    self.showConfigDlg, self.clearConfigButton)
        self.useServiceHotkey = self.__loadHotkey(configManager.toggleServiceHotkey, self.monitorKeyLabel, 
                                                    self.toggleMonitorDlg, self.clearMonitorButton)
        
    def __loadHotkey(self, item, label, dialog, clearButton):
        dialog.load(item)
        if item.enabled:
            # key = str(item.hotKey.encode("utf-8"))
            key = item.hotKey
            label.setText(item.get_hotkey_string(key, item.modifiers))
            clearButton.setEnabled(True)
            return True
        else:
            label.setText(i18n("(None configured)"))
            clearButton.setEnabled(False)
            return False

        
    def save(self):
        configHotkey = self.configManager.configHotkey
        toggleHotkey = self.configManager.toggleServiceHotkey
        
        if configHotkey.enabled:
            self.configManager.app.hotkey_removed(configHotkey)            
        configHotkey.enabled = self.useConfigHotkey
        if self.useConfigHotkey:
            self.showConfigDlg.save(configHotkey)        
            self.configManager.app.hotkey_created(configHotkey)

        if toggleHotkey.enabled:
            self.configManager.app.hotkey_removed(toggleHotkey)                
        toggleHotkey.enabled = self.useServiceHotkey
        if self.useServiceHotkey:
            self.toggleMonitorDlg.save(toggleHotkey)        
            self.configManager.app.hotkey_created(toggleHotkey)
        
    # ---- Signal handlers
    
    def on_setConfigButton_pressed(self):    
        self.showConfigDlg.exec_()
        
        if self.showConfigDlg.result() == QDialog.Accepted:
            self.useConfigHotkey = True
            key = self.showConfigDlg.key
            modifiers = self.showConfigDlg.build_modifiers()
            self.configKeyLabel.setText(self.showConfigDlg.targetItem.get_hotkey_string(key, modifiers))
            self.clearConfigButton.setEnabled(True)
            
    def on_clearConfigButton_pressed(self):
        self.useConfigHotkey = False
        self.clearConfigButton.setEnabled(False)
        self.configKeyLabel.setText(i18n("(None configured)"))
        self.showConfigDlg.reset()


    def on_setMonitorButton_pressed(self):
        self.toggleMonitorDlg.exec_()
        
        if self.toggleMonitorDlg.result() == QDialog.Accepted:
            self.useServiceHotkey = True
            key = self.toggleMonitorDlg.key
            modifiers = self.toggleMonitorDlg.build_modifiers()
            self.monitorKeyLabel.setText(self.toggleMonitorDlg.targetItem.get_hotkey_string(key, modifiers))
            self.clearMonitorButton.setEnabled(True)
            
    def on_clearMonitorButton_pressed(self):
        self.useServiceHotkey = False
        self.clearMonitorButton.setEnabled(False)
        self.monitorKeyLabel.setText(i18n("(None configured)"))
        self.toggleMonitorDlg.reset()

from .enginesettings import EngineSettings


class SettingsDialog(KPageDialog):
    
    def __init__(self, parent):
        KPageDialog.__init__(self, parent)
        self.app = parent.topLevelWidget().app # Used by GlobalHotkeyDialog
        
        self.genPage = self.addPage(GeneralSettings(self), i18n("General"))
        self.genPage.setIcon(KIcon("preferences-other"))
        
        self.hkPage = self.addPage(SpecialHotkeySettings(self, parent.app.configManager), i18n("Special Hotkeys"))
        self.hkPage.setIcon(KIcon("preferences-desktop-keyboard"))
        
        self.ePage = self.addPage(EngineSettings(self, parent.app.configManager), i18n("Script Engine"))
        self.ePage.setIcon(KIcon("text-x-script"))
        
        self.setCaption(i18n("Settings"))
        
    def slotButtonClicked(self, button):
        if button == KDialog.Ok:
            self.genPage.widget().save()
            self.hkPage.widget().save()
            self.ePage.widget().save()
            self.app.configManager.config_altered(True)
            self.app.update_notifier_visibility()
            
        KDialog.slotButtonClicked(self, button)
        
