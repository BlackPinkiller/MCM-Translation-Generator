from PyQt5.QtWidgets import QMessageBox
import LangLoader

def errorBox(errorType,ErrorMessage):
    """
    Display an error message box.

    :param errorType: The title of the error message box.
    :param ErrorMessage: The error message to be displayed.
    """
    msg_box = QMessageBox(icon=QMessageBox.Critical)
    msg_box.setWindowTitle(errorType)
    msg_box.setText(str(ErrorMessage))
    msg_box.exec()

def msgBox(title, text):
    """
    Display a message box with the given title and text.

    :param title: The title of the message box.
    :param text: The content or message to be displayed in the message box.
    """
    msg_box = QMessageBox(icon=QMessageBox.information)
    msg_box.setWindowTitle(title)
    msg_box.setText(str(text))
    msg_box.exec()


def showConfirmBox(self, title_text, info_text, confirm_text = None, cancel_text = None):
    """
    showConfirmBox show a confirm box

    :param title_text: title text
    :param info_text: information text
    :param confirm_text: confirm button text, if not defaults to LangLoader.text("msgBox_Confirm", "Confirm")
    :param cancel_text: cencel button text,if not defaults to LangLoader.text("MsgBox_Cancel", "Cancel")
    :return: show a confirm box to let use choose, with custom title and text and button
    """
    msgBox = QMessageBox(self)
    msgBox.setWindowTitle(title_text)
    msgBox.setText(info_text)
    if not confirm_text:
        confirm_text = LangLoader.text("msgBox_Confirm", "Confirm")
    if not cancel_text:
        cancel_text = LangLoader.text("MsgBox_Cancel", "Cancel")
    noButton = msgBox.addButton(cancel_text, QMessageBox.NoRole)
    yesButton = msgBox.addButton(confirm_text, QMessageBox.YesRole)



    msgBox.setDefaultButton(noButton)
    
    msgBox.exec_()
    
    if msgBox.clickedButton() == yesButton:
        return True
    else:
        return False