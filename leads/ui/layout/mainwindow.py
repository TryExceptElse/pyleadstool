# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/user3/PycharmProjects/pyleadstool/ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 600)
        MainWindow.setStyleSheet("/* WIDGET + MAINWINDOW/DIALOG STYLE */\n"
"\n"
"QWidget {\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"    border-radius: -0px;\n"
"    padding: 2px;\n"
"    font: 10pt \"Lato\";\n"
"}\n"
"\n"
"QWidget#MainWindow, QWidget#Dialog{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgb(255, 255, 255), stop:1 rgb(193, 193, 193));\n"
"}\n"
"\n"
"/* \n"
"##########################\n"
"OTHERS, SORTED ALPHABETICALLY\n"
"##########################\n"
"/*\n"
"\n"
"/* COMBO BOX */\n"
"\n"
"QComboBox{\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    border-radius: -0px;\n"
"}\n"
"\n"
"QComboBox::down-arrow{\n"
"   background-color: rgba(0, 0, 0, 0);\n"
"    image: url(resources/arrow-down-16.png);\n"
"    border-radius: -0px;\n"
"}\n"
"\n"
"QComboBox:Hover{\n"
"    background-color: rgba(0, 0, 0, 15);\n"
"}\n"
"\n"
"/* DATE-TIME EDIT */\n"
"\n"
"QDateTimeEdit {\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"}\n"
"\n"
"QDateTimeEdit::drop-down{\n"
"    border-radius: -0px;\n"
"}\n"
"\n"
"QDateTimeEdit:hover {\n"
"    background-color: rgba(0, 0, 0, 15);\n"
"}\n"
"\n"
"/* DATE EDIT */\n"
"\n"
"QDateEdit{\n"
"     background-color: qlineargradient(spread:reflect, x2:0.262, y2:0.573773, x1:1, y1:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(220, 223, 220, 250));\n"
"    border-radius: -0px;\n"
"}\n"
"\n"
"QDateEdit:hover{\n"
"      background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(220, 223, 220, 120));\n"
"}\n"
"\n"
"QDateEdit::down-arrow:hover {\n"
"    image: url(noimg);\n"
"}\n"
"\n"
"QDateEdit::down-arrow:hover {\n"
"    image: url(resources/arrow-down-16.png);\n"
"}\n"
"\n"
"/* HORIZONTAL + VERTICAL LINES*/\n"
"\n"
"QFrame[frameShape=\"4\"], QFrame[frameShape=\"5\"]{\n"
"    background-color: rgba(8, 120, 0, 255);\n"
"}\n"
"\n"
"/* LABEL */\n"
"\n"
"QLabel {\n"
"    background-color: qlineargradient(spread:reflect, x1:0.607246, y1:0.346, x2:0.623037, y2:1, stop:0 rgba(8, 120, 0, 0), stop:1 rgba(15, 76, 0, 0));\n"
"    font: 12pt \"Lato\";\n"
"    color: rgb(24, 24, 24);\n"
"}\n"
"\n"
"/* LINE EDIT */\n"
"\n"
"QLineEdit {\n"
"    background-color: rgba(0, 0, 0, 00);\n"
"}\n"
"\n"
"QLineEdit:hover {\n"
"    background-color: rgba(0, 0, 0, 15);\n"
"}\n"
"\n"
"/* LIST */\n"
"\n"
"QListView::item:selected{\n"
"    background-color:  rgb(131, 175, 255);\n"
"}\n"
"\n"
"/* MESSAGE BOX */\n"
"\n"
"QMessageBox{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgb(255, 255, 255), stop:1 rgb(220, 220, 220));\n"
"}\n"
"\n"
"/* MENU */\n"
"\n"
"QMenuBar {\n"
"    border-radius: 1px;\n"
"    background-color: qlineargradient(spread:reflect, x1:0.607246, y1:0.346, x2:0.623037, y2:1, stop:0 rgba(8, 120, 0, 255), stop:1 rgba(15, 76, 0, 255));\n"
"    color: rgb(240, 240, 240);\n"
"}\n"
"\n"
"QMenu {\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgb(255, 255, 255), stop:1 rgb(230, 230, 230));\n"
"    color: rgb(12, 12, 12);\n"
"}\n"
"\n"
"QMenu::item:hover{\n"
"    background-color: rgba(0, 0, 0, 15);\n"
"    color: rgb(12, 12, 12);\n"
"}\n"
"\n"
"QMenu::item:selected{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgb(230, 230, 230), stop:1 rgb(255, 255, 255));\n"
"    color: rgb(12, 12, 12);\n"
"}\n"
"\n"
"/* PUSH BUTTON */\n"
"\n"
"QPushButton{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(193, 193, 193, 120));\n"
"    padding-left: 8px;\n"
"    padding-right: 8px;\n"
"    padding-top: 4px;\n"
"    padding-bottom: 4px;\n"
"    font: 12pt \"Lato\";\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(240, 243, 240, 120));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"     background-color: qlineargradient(spread:reflect, x2:0.262, y2:0.573773, x1:1, y1:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(220, 223, 220, 120));\n"
"}\n"
"\n"
"/* STATUS BAR */\n"
"\n"
"QStatusBar {\n"
"    border-radius: 1px;\n"
"    background-color: qlineargradient(spread:reflect, x1:0.607246, y1:0.346, x2:0.623037, y2:1, stop:0 rgba(8, 120, 0, 255), stop:1 rgba(15, 76, 0, 255));\n"
"    color: rgb(240, 240, 240);\n"
"}\n"
"\n"
"/* TABLE + HEADER STYLES */\n"
"\n"
"QTableWidget{\n"
"    color: rgba(0, 0, 0, 0);\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"    alternate-background-color: rgba(0,0,0,20);\n"
"}\n"
"\n"
"QTableView{\n"
"    color: rgba(0, 0, 0, 0);\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"    alternate-background-color: rgba(0,0,0,15);\n"
"}\n"
"\n"
"QHeaderView::section{\n"
"    border-radius: 4px solid black;\n"
"    font: 10pt \"Lato\";\n"
"    min-width: 180; \n"
"    min-height: 32;\n"
"}\n"
"\n"
"QHeaderView {\n"
"    border-radius: 4px solid black;\n"
"    min-height: 16;\n"
"}\n"
"\n"
"QTableCornerButton::section  {\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"}\n"
"\n"
"/* TOOL TIP */\n"
"\n"
"QToolTip{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 130), stop:1 rgba(230, 230, 230, 130));\n"
"    border-radius: -0px;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sideBar = QtWidgets.QVBoxLayout()
        self.sideBar.setObjectName("sideBar")
        self.sheetsLabel = QtWidgets.QLabel(self.centralwidget)
        self.sheetsLabel.setObjectName("sheetsLabel")
        self.sideBar.addWidget(self.sheetsLabel)
        self.openSheetsULine = QtWidgets.QFrame(self.centralwidget)
        self.openSheetsULine.setFrameShape(QtWidgets.QFrame.HLine)
        self.openSheetsULine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.openSheetsULine.setObjectName("openSheetsULine")
        self.sideBar.addWidget(self.openSheetsULine)
        self.sheetsList = QtWidgets.QListView(self.centralwidget)
        self.sheetsList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.sheetsList.setObjectName("sheetsList")
        self.sideBar.addWidget(self.sheetsList)
        self.campaignLabel = QtWidgets.QLabel(self.centralwidget)
        self.campaignLabel.setObjectName("campaignLabel")
        self.sideBar.addWidget(self.campaignLabel)
        self.ULine = QtWidgets.QFrame(self.centralwidget)
        self.ULine.setFrameShape(QtWidgets.QFrame.HLine)
        self.ULine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.ULine.setObjectName("ULine")
        self.sideBar.addWidget(self.ULine)
        self.campaignList = QtWidgets.QListView(self.centralwidget)
        self.campaignList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.campaignList.setObjectName("campaignList")
        self.sideBar.addWidget(self.campaignList)
        self.horizontalLayout.addLayout(self.sideBar)
        self.assocTableLayout = QtWidgets.QVBoxLayout()
        self.assocTableLayout.setObjectName("assocTableLayout")
        self.assocLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Lato")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.assocLabel.setFont(font)
        self.assocLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.assocLabel.setObjectName("assocLabel")
        self.assocTableLayout.addWidget(self.assocLabel)
        self.assocULine = QtWidgets.QFrame(self.centralwidget)
        self.assocULine.setFrameShape(QtWidgets.QFrame.HLine)
        self.assocULine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.assocULine.setObjectName("assocULine")
        self.assocTableLayout.addWidget(self.assocULine)
        self.assocTable = QtWidgets.QTableView(self.centralwidget)
        self.assocTable.setAlternatingRowColors(True)
        self.assocTable.setShowGrid(False)
        self.assocTable.setObjectName("assocTable")
        self.assocTable.horizontalHeader().setSortIndicatorShown(False)
        self.assocTableLayout.addWidget(self.assocTable)
        self.horizontalLayout.addLayout(self.assocTableLayout)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 5)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionApplyTranslations = QtWidgets.QAction(MainWindow)
        self.actionApplyTranslations.setObjectName("actionApplyTranslations")
        self.actionCheck = QtWidgets.QAction(MainWindow)
        self.actionCheck.setObjectName("actionCheck")
        self.searchAction = QtWidgets.QAction(MainWindow)
        self.searchAction.setObjectName("searchAction")
        self.viewRecordsAction = QtWidgets.QAction(MainWindow)
        self.viewRecordsAction.setObjectName("viewRecordsAction")
        self.toolBar.addAction(self.actionApplyTranslations)
        self.toolBar.addAction(self.actionCheck)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.viewRecordsAction)
        self.toolBar.addAction(self.searchAction)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.sheetsLabel.setText(_translate("MainWindow", "Open Sheets"))
        self.campaignLabel.setText(_translate("MainWindow", "Campaigns"))
        self.assocLabel.setText(_translate("MainWindow", "Associations"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionApplyTranslations.setText(_translate("MainWindow", "Apply"))
        self.actionApplyTranslations.setToolTip(_translate("MainWindow", "Move values from source sheet to target, while checking for duplicates or whitespace."))
        self.actionCheck.setText(_translate("MainWindow", "Check"))
        self.actionCheck.setToolTip(_translate("MainWindow", "Check selected translations for duplicates and/or whitespace, determined by settings."))
        self.searchAction.setText(_translate("MainWindow", "Search Records"))
        self.searchAction.setToolTip(_translate("MainWindow", "search records for a specific value"))
        self.viewRecordsAction.setText(_translate("MainWindow", "View Records"))
        self.viewRecordsAction.setToolTip(_translate("MainWindow", "View records by date and campaign"))
