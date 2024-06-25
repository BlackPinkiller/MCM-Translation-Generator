import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QDesktopWidget, QFileDialog, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMenu, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget
import MsgHandler
import JsonHandler
import LangLoader
from SettingWindow import SettingsWindow
import SettingManager

class MainWindow(QMainWindow):
    loaded_json = None
    converted_json = None
    opend_file_path = None
    mod_name = None
    modified_lang_text = {}
    modified_items = {}

    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
        
    

    def initUI(self):
        # Load Language and Settings
        excute_path = os.path.dirname(sys.argv[0])

        setting_path = os.path.normpath(os.path.join(excute_path,'Config.toml'))
        lang_path = os.path.normpath(os.path.join(excute_path,'lang'))
        SettingManager.config_path = setting_path
        SettingManager.loadSettings()
        LangLoader.load_files(lang_path)

        app = QApplication.instance()
        font = QFont()
        font.setFamily('Microsoft YaHei')
        font.setPointSize(9) 
        app.setFont(font)

        # Window Initiate
        QApplication.setWindowIcon(QIcon(self.resource_path('Icon.ico')))
        # Allows the window to accept drag-and-drop files
        self.setAcceptDrops(True)  
        # initiate window state
        self.setWindowTitle(LangLoader.text("Window_Title", "MCM Language File Generator"))
        self.MoveWindowtoSavedPos()
        self.statusBar().showMessage(LangLoader.text("Ready", "Ready!"))
        # initiate window componennts and layouts
        self.initMenuBar()
        self.mainInterface()
        self.updateTable()

    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)


    def initMenuBar(self):
        # create menu bar
        menubar = self.menuBar()

        # add window menus
        file_menu = menubar.addMenu(LangLoader.text("Menu_File", "File"))
        option_menu = menubar.addMenu(LangLoader.text("Menu_Options", "Options"))
        # help_menu = menubar.addMenu(LangLoader.text("Menu_Help", "Help"))

        # add file open action button
        open_action = QAction(LangLoader.text("Open", "Open"), self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip(LangLoader.text("Open_Tip", "Open a file"))
        open_action.triggered.connect(self.open_file)
        # add file save action button
        save_action = QAction(LangLoader.text("Save", "Save"), self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip(LangLoader.text("Save_Tip", "Save Json and translation file"))
        save_action.triggered.connect(self.save_file)
        # add file save as action button
        save_as_action = QAction(LangLoader.text("Save_As", "Save as..."), self)
        save_as_action.setStatusTip(LangLoader.text("Save_As_Tip", "Save Config and translation file as..."))
        save_as_action.triggered.connect(self.save_as_file)
        # exit button
        exit_action = QAction(LangLoader.text("Exit", "Exit"), self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip(LangLoader.text("Exit_Tip", "Exit application"))
        exit_action.triggered.connect(self.close)
        # option action
        option_action = QAction(LangLoader.text("Options", "Options"),self)
        option_action.setStatusTip(LangLoader.text("Options_Tip", "Open settings menu"))
        option_action.triggered.connect(self.option_menu)

        # add about action
        about_action = QAction(LangLoader.text("About", "About"), self)
        about_action.setStatusTip(LangLoader.text("About_Tip", "About the application"))
        about_action.triggered.connect(self.show_about)

        

        # add actions to window menu
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addActions([save_action,save_as_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        option_menu.addAction(option_action)
        # help_menu.addAction(about_action)

    def mainInterface(self):
        
        
        # self.mod_name_label = QLabel(LangLoader.text("Keyword_Prefix","Keyword Prefix"), self)
        self.mod_name_label = QGroupBox(LangLoader.text("Keyword_Prefix","Keyword Prefix"), self)
        self.mod_name_label.setToolTip(LangLoader.text("Keyword_Prefix_More","Since MCM only recognizes keywords, not .txt file names, you need a prefix for it to identify which mod it is for."))
        self.mod_name_label.hide()
        self.mod_name_label_more = QLabel(LangLoader.text("Keyword_Prefix_More","Since MCM only recognizes keywords, not .txt file names, you need a prefix for it to identify which mod it is for."), self)
        self.mod_name_label_more.hide()

        self.mod_name_edit = QLineEdit()
        self.mod_name_edit.setPlaceholderText(LangLoader.text("Edit_Mod_Name","Mod Name..."))
        self.mod_name_edit.textChanged.connect(self.on_mod_name_changed)
        self.mod_name_edit.hide()
        self.mod_name_btn = QPushButton(LangLoader.text("Edit_Mod_Name_Update","Update!") ,self)
        self.mod_name_btn.clicked.connect(self.on_mod_name_update)
        self.mod_name_btn.hide()


        self.table_form = QTableWidget()
        self.table_form.itemChanged.connect(self.on_item_changed)
        self.table_form.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_form.customContextMenuRequested.connect(self.show_context_menu)
        self.initTable()
        self.table_form.hide()

        

        # 创建一个标签来显示文本
        self.label = QLabel(LangLoader.text("Drag_Drop_Label", "Drag and drop the Config.json\n MCM file to window to generate translation text"), self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 26px; color: black;")

         # 创建一个覆盖标签来显示“Drag and Drop”文本
        self.overlay_label = QLabel(LangLoader.text("Drag_And_Drop", "Drag And Drop"), self)
        self.overlay_label.setGeometry(50,50,200,200)
        self.overlay_label.setAlignment(Qt.AlignCenter)
        self.overlay_label.setStyleSheet("border: 1.5px dashed grey; font-size: 26px; color: grey; background-color: rgba(255, 255, 255, 0.8);")

        # 创建布局并添加标签
        self.header_box_layout = QHBoxLayout()
        group_box_layout = QVBoxLayout()
        layout = QVBoxLayout()
        

        
        layout.addWidget(self.label)
        layout.addWidget(self.mod_name_label)
        self.mod_name_label.setLayout(group_box_layout)
        group_box_layout.addWidget(self.mod_name_label_more)
        self.header_box_layout.addWidget(self.mod_name_edit)
        self.header_box_layout.addWidget(self.mod_name_btn)
        group_box_layout.addLayout(self.header_box_layout)
        layout.addLayout(group_box_layout)
        layout.addWidget(self.table_form)
        layout.addWidget(self.overlay_label)
        container = QWidget()

        container.setLayout(layout)
        self.setCentralWidget(container)

        # 默认隐藏覆盖标签
        self.overlay_label.hide()


    def initTable(self):
        self.table_form.clear()
        self.table_form.setColumnCount(2)
        self.table_form.setHorizontalHeaderLabels([LangLoader.text("Table_Original", "Original"), LangLoader.text("Table_Converted", "Converted")])
        header = self.table_form.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)


    def on_mod_name_changed(self):
        text = self.mod_name_edit.text()
        if text:
            self.mod_name = text

    def on_mod_name_update(self):
        self.jsonLoader(self.opend_file_path)

    def on_item_changed(self, item):
        row = item.row()
        column = item.column()
        if column != 1:
            return
        
        key_item = self.table_form.item(row, 1)
        if key_item:
            key = key_item.text()
            # Update the dictionary based on the changed item
            old_key = list(self.modified_lang_text.keys())[row]
            if not key.startswith('$'):
                key = '$'+ key
            self.modified_lang_text = self.replaceKey(self.modified_lang_text, old_key, key)
            key_item.setBackground(QColor(125, 200, 125))
            key_item.setText(key)
            consist_key = key_item.toolTip().split('\n')[0]
            self.modified_items[consist_key] = key

    
    def replaceKey(self, t_dict, old_key, new_key):
        temp_dict = {}
        if t_dict and old_key and new_key:
            for key, value in t_dict.items():
                if key == old_key:
                    temp_dict[new_key] = value
                else:
                    temp_dict[key] = value
        return temp_dict


    def showTable(self, data = {}):
        if not data:
            MsgHandler.errorBox(LangLoader.text("Msg_No_Data_Title", "No Data"), LangLoader.text("Msg_No_Data_Title_Text", "No data converted."))
        self.table_form.itemChanged.disconnect(self.on_item_changed)
        self.table_form.show()
        self.table_form.setRowCount(len(data))
        for index, (key, value) in enumerate(data.items()):
            item_original = QTableWidgetItem(str(value))
            item_converted = QTableWidgetItem(str(key))
            item_original.setFlags(item_original.flags() & ~Qt.ItemIsEditable)
            key_stats = 0
            if key in JsonHandler.mcm_lang_key_stats.keys():
                key_stats = JsonHandler.mcm_lang_key_stats[key]

            item_original.setToolTip(str(value))
            item_converted.setBackground(self.get_color(key_stats))
            item_converted.setToolTip(f"{str(key)}\n\n{self.get_tooltip(key_stats)}")

            self.table_form.setItem(index,0,item_original)
            self.table_form.setItem(index,1,item_converted)
        self.table_form.itemChanged.connect(self.on_item_changed)
        self.statusBar().showMessage(LangLoader.text("Table_Complete_Tip", "The colors represents keyword type, White=id, Yellow=type, Light Cyan=Option, Red=other, Red is the worst."))
 

    def get_color(self, id_good_stats):
        if id_good_stats == 1:
            return QColor(255, 255, 200)# Yellow
        elif id_good_stats == 2:
            return QColor(255, 200, 200)# Red
        elif id_good_stats == 3:
            return QColor(224, 255, 255)# Light Cyan
        else:
            return QColor(255, 255, 255)# White
    def get_tooltip(self, id_good_stats = 0):
        if id_good_stats == 1:
            return LangLoader.text("Stats_Type", "This keyword is generatored by type")
        elif id_good_stats == 2:
            return LangLoader.text("Stats_Worst", "This keyword is generatored by page/content/text.\nyou may change it if you want")
        elif id_good_stats == 3:
            return LangLoader.text("Stats_Option", "This keyword is an option")
        else:
            return LangLoader.text("Stats_ID", "This keyword is generatored by ID")
        
    def show_context_menu(self, pos):
        # Create context menu
        context_menu = QMenu(self)
        
        # Add actions to context menu
        undo_action = QAction(LangLoader.text("Undo_Button", "Undo"), self)
        delete_action = QAction(LangLoader.text("Delete_Button", "Delete"), self)
        undo_action.triggered.connect(self.undo_selected_items)
        delete_action.triggered.connect(self.delete_selected_items)
        context_menu.addAction(undo_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        # Show context menu at the global position
        global_pos = self.table_form.viewport().mapToGlobal(pos)
        context_menu.exec_(global_pos)

    def delete_selected_items(self):
        selected_items = self.table_form.selectedItems()
        if not selected_items:
            return
        rows_to_delete = set()
        for item in selected_items:
            rows_to_delete.add(item.row())
        for row in rows_to_delete:
            item = self.table_form.item(row, 1)
            text = self.table_form.item(row, 0).text()
            self.modified_lang_text.pop(item.text())
            self.converted_json = self.delete_value_from_json(self.converted_json, item.text(), text)
            self.table_form.removeRow(item.row())
        self.table_form.clearSelection()

    def delete_value_from_json(self, data, target, original, path=None,):
        if path is None:
            path = []
        if isinstance(data, dict):
            temp_dict = {}
            for key, value in data.items():
                if not value == target:
                    temp_dict[key] = self.delete_value_from_json(value, target, original, path + [key])
                else:
                    temp_dict[key] = original
            return temp_dict 
        elif isinstance(data, list):
            temp_list = []
            for index, item in enumerate(data):
                if not item == target:
                    temp_list.append(self.delete_value_from_json(item, target, original, path + [index]))
                else:
                    temp_list.append(original)
            return temp_list
        return data


    def undo_selected_items(self):
        self.table_form.itemChanged.disconnect(self.on_item_changed)
        selected_items = self.table_form.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            if item.column() == 1:
                original_text = item.toolTip().split('\n')[0]
                original_color = self.get_color(JsonHandler.mcm_lang_key_stats.get(original_text))
                self.modified_lang_text = self.replaceKey(self.modified_lang_text, item.text(), original_text)
                if original_text in self.modified_items.keys():
                    self.modified_items.pop(original_text)
                item.setText(original_text)
                item.setBackground(original_color)
        self.table_form.itemChanged.connect(self.on_item_changed)
        
    
    # menu bar functions 
    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, LangLoader.text("Dialog_Open_File", "Open File"), "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            self.opend_file_path = None
            self.jsonLoader(file_path)

    def save_file(self):
        if self.opend_file_path and self.loaded_json:
            file_path = os.path.abspath(self.opend_file_path)
            self.saveJsonFile(file_path, self.loaded_json, self.converted_json)
            self.saveLanguageFile(file_path)
        else:
            MsgHandler.errorBox(LangLoader.text("Msg_Save_Failed", "Save Failed!"),LangLoader.text("Msg_Save_Failed_Text", "Seems like there is no data to save."))

    def save_as_file(self):
        if self.opend_file_path and self.loaded_json:
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            file_path = QFileDialog.getExistingDirectory(self, LangLoader.text("Dialog_Select_Directory", "Select Directory"), options=options)
            if file_path:
                self.saveJsonFile(file_path, self.loaded_json, self.converted_json)
                self.saveLanguageFile(file_path)
        else:
            MsgHandler.errorBox(LangLoader.text("Msg_Save_Failed", "Save Failed!"),LangLoader.text("Msg_Save_Failed_Text", "Seems like there is no data to save."))

    def show_about(self):
        MsgHandler.msgBox(LangLoader.text("Msg_About", "About"),LangLoader.text("Msg_About_Text", "This is the help information placeholder"))

    def option_menu(self):
        self.settings_window = SettingsWindow()
        self.settings_window.restart_UI.connect(self.handle_restart_signal)
        self.centerWindow(self.settings_window)
        self.settings_window.exec()

    
    def handle_restart_signal(self):
        # 这里可以添加主窗口对保存设置的响应逻辑
        print('收到重启信号')
        MainWindow.restart()
        self.settings_window.close()
        self.close()


    def MoveWindowtoSavedPos(self):
        # Get the screen size and the app window size
        
        last_pos = SettingManager.loaded_setting.get('window_pos')
        is_last_pos_ok = True
        if not(last_pos and len(last_pos) > 3):
            is_last_pos_ok = False
        if is_last_pos_ok:
            for pos in last_pos:
                if pos == -1:
                    is_last_pos_ok = False

        if is_last_pos_ok:
            x = last_pos[0]
            y = last_pos[1]
            w = last_pos[2]
            h = last_pos[3]
            self.setGeometry(x,y,w,h)
        else:
            self.setGeometry(0, 0, 1000, 700)
            screen = QDesktopWidget().screenGeometry()
            window_size = self.geometry()
            # Calculate the center display position
            x = (screen.width() - window_size.width()) // 2
            y = (screen.height() - window_size.height()) // 2
            self.move(x, y)

    def moveEvent(self, event):
        if 'window_pos' in SettingManager.loaded_setting.keys():
            SettingManager.loaded_setting['window_pos'] = self.geometry().getRect()

    def resizeEvent(self, event):
        if 'window_pos' in SettingManager.loaded_setting.keys():
            SettingManager.loaded_setting['window_pos'] = self.geometry().getRect()

    def closeEvent(self, event):
        SettingManager.saveSetting(SettingManager.loaded_setting)


    def centerWindow(self, sub_window):
        main_window_rect = self.geometry()
        sub_window_rect = sub_window.geometry()
        x = int(main_window_rect.x() + (main_window_rect.width() - sub_window_rect.width()) / 2)
        y = int(main_window_rect.y() + (main_window_rect.height() - sub_window_rect.height()) / 2)
        sub_window.move(x, y)


    def updateTable(self):
        if self.loaded_json:
            self.label.hide()
            self.mod_name_label.show()
            self.mod_name_label_more.show()
            self.mod_name_edit.show()
            self.mod_name_btn.show()
            self.table_form.show()
        else:
            self.label.show()
            self.mod_name_label.hide()
            self.mod_name_label_more.hide()
            self.mod_name_edit.hide()
            self.mod_name_btn.hide()
            self.table_form.hide()


    def dragEnterEvent(self, event):
        """
        Handle the drag enter event to accept dragged files.

        :param event: The drag enter event.
        """
        self.overlay_label.show()
        # Check if the dragged data contains URLs (files)
        if event.mimeData().hasUrls():
            # Accept the proposed action for the drag event
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.overlay_label.hide()
        self.updateTable()

    def dropEvent(self, event):
        """
        Handle the drop event to process dropped files.

        :param event: The drop event.
        """
        self.overlay_label.hide()
        # Iterate over all URLs in the drop event
        for url in event.mimeData().urls():
            file_path = url.toLocalFile() # Convert the URL to a local file path
            if file_path:
                self.opend_file_path = None
                self.mod_name = None
                self.jsonLoader(file_path)
        event.acceptProposedAction()
    
    def jsonLoader(self, file_path):
        global converted_json
        # check file extension
        if  not file_path.endswith('.json'):
            print("file type not supported")
            MsgHandler.errorBox(LangLoader.text("Msg_File_Not_Supported", "File Type Not Supported!"),LangLoader.text("Msg_File_Not_Supported_Text", "Please drop only .Json file!"))
            return None
        # reading json file using json handler function
        data = JsonHandler.read_json_file(file_path)
        if data:
            self.opend_file_path = os.path.normpath(file_path)
            self.loaded_json = data
            # conver original json file to linked translation file
            # "text": "some text here"
            #       --to-- 
            # "text": "$text"
            this_mod_name, _, _ = self.getModNameAndPath(self.opend_file_path)
            if not self.mod_name:
                self.mod_name = this_mod_name
                self.mod_name_edit.setText(self.mod_name)
            self.mod_name = self.mod_name.replace(" ","_")
            self.converted_json = JsonHandler.readMCM(data,self.mod_name)
            self.modified_lang_text = JsonHandler.mcm_lang_text
            self.showTable(self.modified_lang_text)

            """ 
            # save json file and back up using time now
            bak_path = os.path.join(file_path.rsplit('json', 1)[0] + JsonHandler.getTimeTag())
            JsonHandler.saveJson(bak_path, data)
            JsonHandler.saveJson(file_path, converted)

            # save language text file
            lang_path = os.path.join(folder_path,"lang_en.txt")
            JsonHandler.saveLangText(lang_path, JsonHandler.mcm_lang_text) 
            """
        else:
            print("no data")
            MsgHandler.errorBox(LangLoader.text("Msg_No_Data", "No Data!"), LangLoader.text("Msg_No_Data_Text", "This file does not contain any data, it might be empty."))
        self.updateTable()

    def saveJsonFile(self, file_path, original_data, converted_data):
        # save json file and back up using time now
        if not os.path.isfile(file_path):
            file_name = os.path.basename(self.opend_file_path)
            file_path = os.path.join(file_path, file_name)
        if self.modified_items:
            converted_data = JsonHandler.replaceModifiedKey(converted_data, self.modified_items)
        
        bak_path = os.path.join(file_path.rsplit('json', 1)[0] + JsonHandler.getTimeTag())
        JsonHandler.saveJson(bak_path, original_data)
        JsonHandler.saveJson(file_path, converted_data)

    def saveLanguageFile(self, file_path):
        # save language text file
        mod_name, data_folder, is_data_folder = self.getModNameAndPath(file_path)
        if 'lang_codes' in SettingManager.loaded_setting.keys():
            for lang_code in SettingManager.loaded_setting.get('lang_codes'):
                translation_path = self.generateInterfacePath(data_folder, mod_name, lang_code, is_data_folder)
                JsonHandler.saveLangText(translation_path, self.modified_lang_text) 
        else:
            translation_path = self.generateInterfacePath(data_folder, mod_name, 'en', is_data_folder)
            JsonHandler.saveLangText(translation_path, self.modified_lang_text) 

    
    def getModNameAndPath(self,file_path):
        """
        Extract the mod name and the path to the data folder from a given file path.

        This method normalizes the given file path, splits it into its components,
        and searches for the "MCM" folder. If the "MCM" folder is found, it extracts
        the mod name and the path to the data folder (the folder containing the "MCM" folder).

        :param file_path: The full path to the file.
                      Example: "D:/Games/Fallout 4/Data/MCM/Config/abc/config.json"
        :type file_path: str
        :return: A tuple containing the mod name and the path to the data folder.
             If the "MCM" folder is not found, both elements in the tuple will be None.
             Example: ("abc", "D:/Games/Fallout 4/Data")
        :rtype: tuple
        """
        # normalize path
        folder_path = file_path
        if os.path.isfile(file_path):
            folder_path, _ = os.path.split(file_path)
        split_path = folder_path.split(os.path.sep)
        mod_name = "translation"
        data_folder = folder_path
        is_data_folder = False
        if "MCM" in split_path:
            mod_name = split_path[-1]
            mcm_index = split_path.index("MCM")
            data_folder = os.path.normpath('\\'.join(split_path[:mcm_index]))
            is_data_folder = True
        print(f"mod Name: {mod_name}, data folder: {data_folder}, isDataFolder: {is_data_folder}")
        return mod_name, data_folder, is_data_folder
    
    def generateInterfacePath(self, data_path, mod_name, lang_code = "En", is_data_Folder = True):
        """
        Generate the interface translation file path for a given mod.

        This method constructs the path to the translation file for the specified mod and language code.
        The path is generated based on the provided data path, mod name, and language code.

        :param data_path: The base path to the data folder containing the mod.
                      Example: "D:/Games/Fallout 4/Data"
        :param mod_name: The name of the mod.
                     Example: "abc"
        :param lang_code: The language code for the translation file, defaults to 'en'.
                      Example: "en"
        :return: The full path to the translation file.
             Example: "D:/Games/Fallout 4/Data/Interface/Translations/abc_en.txt"
        """
        if data_path and mod_name:
            if is_data_Folder:
                translation_path = os.path.join(data_path,"Interface", "Translations", mod_name + f'_{lang_code}.txt')
            else:
                translation_path = os.path.join(data_path, mod_name + f'_{lang_code}.txt')
        return translation_path
        
    def restart():
        MainWindow.singleton = MainWindow()

if __name__ == '__main__':
    app = QApplication([])
    MainWindow.restart()
    sys.exit(app.exec_())
