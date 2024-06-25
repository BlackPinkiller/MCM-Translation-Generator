from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QDialog, QVBoxLayout, QWidget
import LangLoader
import SettingManager
import MsgHandler

class SettingsWindow(QDialog):
    restart_UI = pyqtSignal()
    lang_codes = ['En','Cn','Ja','Fr','De','It','Ru','Es','EsMx','Pi','PtBr']
    Setting_menu = {}
    # closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        # self.setFixedSize(450,385)
        
        self.setWindowTitle(LangLoader.text("Setting_Menu_Title", "Setting Menu"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.Setting_menu = SettingManager.getSetting()

        # Layouts
        self.main_layout = QVBoxLayout()
        self.UIlang_layout = QVBoxLayout()
        self.lang_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()


        
        # interface language layout
        self.UIlang_group_box = QGroupBox(LangLoader.text("Setting_UIlang_label","UI Language"), self)
        self.UIlang_group_box.setLayout(self.UIlang_layout)

        uilang_codes = LangLoader.languages.keys()
        self.UIlang_droplist = QComboBox(self)
        self.UIlang_droplist.addItems(uilang_codes)
        self.UIlang_droplist.setCurrentText(self.Setting_menu.get("current_UILang"))
        self.UIlang_droplist.currentTextChanged.connect(self.selectionChanged)
        self.UIlang_droplist.setStyleSheet("color: #333333; ")
        self.UIlang_layout.addWidget(self.UIlang_droplist)
        
        self.main_layout.addStretch()  # add strech to push the buttons to the bottom

        
        # Lang code selection for generate translation text files
        self.lang_group_box = QGroupBox(LangLoader.text("Setting_Lang_Header", "Translation Text"),self)
        self.lang_group_box.setLayout(self.lang_layout)
        self.lang_label = QLabel(LangLoader.text("Setting_Lang_Label", "Translation text you want to generate.\nExample: ExampleMod_en.txt"),self)
        self.lang_layout.addWidget(self.lang_label)
        
        activated_codes = self.Setting_menu.get("lang_codes")
        for i, code in enumerate(self.lang_codes):
            checkbox = QCheckBox(code, self)
            checkbox.setStyleSheet("color: #333333; ")
            checkbox.stateChanged.connect(self.checkbox_state_changed)
            # 5 in a row
            row = i // 5
            col = i % 5  
            if code in activated_codes:
                checkbox.setCheckState(Qt.Checked)
            self.grid_layout.addWidget(checkbox, row, col)

        self.lang_layout.addLayout(self.grid_layout)


        self.main_layout.addWidget(self.UIlang_group_box)
        self.main_layout.addWidget(self.lang_group_box)
        self.main_layout.addStretch()  # add strech to push the buttons to the bottom
        spacer = QWidget()  # 或者 QLabel("")
        spacer.setFixedSize(10, 10)
        self.main_layout.addWidget(spacer)

        # Button Layout
        button_layout = QHBoxLayout()

        self.save_button = QPushButton(LangLoader.text("Setting_Apply", "Apply"), self)
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton(LangLoader.text("Setting_Cancel", "Cancel"), self)
        self.cancel_button.setDefault(True)
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        

        self.main_layout.addLayout(button_layout)  # 添加按钮布局到主布局

        self.setLayout(self.main_layout)
    

    def selectionChanged(self, index):
        selected_text = self.UIlang_droplist.currentText()
        if self.Setting_menu and "current_UILang" in self.Setting_menu.keys():
            self.Setting_menu["current_UILang"] = selected_text
        

    def checkbox_state_changed(self, state):
        sender = self.sender()
        if isinstance(sender, QCheckBox):
            label_text = sender.text()
            activated_codes = self.Setting_menu.get("lang_codes")
            if state == Qt.Checked:
                if label_text not in activated_codes:
                    activated_codes.append(label_text)
                    print(f"{label_text} Checked!")
            else:
                if label_text in activated_codes:
                    activated_codes.remove(label_text)
                    print(f"{label_text} Unchecked!")
        

    def save_settings(self):
        # 执行保存设置的操作
        is_confirmed = MsgHandler.showConfirmBox(self, LangLoader.text("Setting_Apply_Confirm", "Apply"), LangLoader.text("Setting_Apply_Confirm_Text", "Do you want to apply the changes?"))
        if is_confirmed:
            current_lang = SettingManager.loaded_setting.get("current_UILang")
            changed_lang = self.Setting_menu.get("current_UILang")

            is_lang_restart = False
            if current_lang != changed_lang:
                is_lang_restart = MsgHandler.showConfirmBox(self, LangLoader.text("Setting_Lang_Restart", "Restart"), LangLoader.text("Setting_Lang_Restart_Text", "Seems you hanve changed UI language, \nDo you want to restart now?"))
            
            SettingManager.saveSetting(self.Setting_menu)
            print(f"Setting Window: {self.Setting_menu} Saved!")
            if is_lang_restart:
                self.restart_UI.emit()  # 发射信号
            self.close()
        else: 
            print("保存取消")

    def resizeEvent(self, event):
        # 在 resize 事件中设置窗口的固定大小，以当前大小为准
        self.setFixedSize(self.size())
        super().resizeEvent(event)

    # def closeEvent(self, event):
    #     self.closed.emit()  # 发送关闭信号
    #     super().closeEvent(event) 

