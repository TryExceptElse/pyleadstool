from unittest import TestCase
from PyQt5.Qt import QApplication
from time import sleep
from threading import Thread

from leadmacro import LogDlg


class TestLogDlg(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.log_dlg = LogDlg(settings={})

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        cls.app = None

    def test_log_dlg_returns_false_when_declined(self):
        def call_back_method():
            sleep(0.2)
            self.log_dlg.back()
        Thread(
            group=None,
            target=call_back_method,
            name='control_thread'
        ).start()
        self.assertFalse(self.log_dlg.exec())

    def test_log_dlg_returns_true_when_accepted(self):
        def call_accept_method():
            sleep(0.2)
            self.log_dlg.accept()
        Thread(
            group=None,
            target=call_accept_method,
            name='control_thread'
        ).start()
        self.assertTrue(self.log_dlg.exec())
