import sys
import unittest
from unittest.mock import Mock
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import PyQtTesting
from Graphics import TrayActions


app = QApplication(sys.argv)

class TestLoginDialog(unittest.TestCase):
    def setUp(self):
        self.dialog = TrayActions.InputDialog(self)

    def test_editInputs(self):
        self.dialog.username.clear()
        self.dialog.email.clear()
        self.dialog.password.clear()
        QTest.keyClicks(self.dialog.username, 'Test')
        QTest.keyClicks(self.dialog.email, 'Test')
        QTest.keyClicks(self.dialog.password, 'Test')
        self.assertEqual(self.dialog.username.text(), 'Test')
        self.assertEqual(self.dialog.email.text(), 'Test')
        self.assertEqual(self.dialog.password.text(), 'Test')

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.gui = PyQtTesting.UI()
        self.checkUserStatus = self.gui.checkUserStatus

    def test_default_login(self):
        menuProfile = self.gui.menuProfile
        signIn = menuProfile.actions()[0]
        signIn.trigger()
        self.dialog = TrayActions.InputDialog(self)
        signInBttn = self.dialog.signinbttn
        QTest.mouseClick(signInBttn, Qt.LeftButton)


if __name__ == '__main__':
    unittest.main()