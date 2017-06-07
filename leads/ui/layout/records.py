# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/user3/PycharmProjects/pyleadstool/ui/records.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("QWidget {\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"    border-radius: 4px;\n"
"    padding: 2px;\n"
"    font: 10pt \"Lato\";\n"
"}\n"
"\n"
"QWidget#MainWindow, QWidget#Dialog{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgb(255, 255, 255), stop:1 rgb(193, 193, 193));\n"
"}\n"
"\n"
"QLabel {\n"
"    background-color: qlineargradient(spread:reflect, x1:0.607246, y1:0.346, x2:0.623037, y2:1, stop:0 rgba(8, 120, 0, 0), stop:1 rgba(15, 76, 0, 0));\n"
"    font: 12pt \"Lato\";\n"
"    color: rgb(24, 24, 24);\n"
"}\n"
"\n"
"QMenuBar {\n"
"    border-radius: 1px;\n"
"    background-color: qlineargradient(spread:reflect, x1:0.607246, y1:0.346, x2:0.623037, y2:1, stop:0 rgba(8, 120, 0, 255), stop:1 rgba(15, 76, 0, 255));\n"
"    color: rgb(240, 240, 240);\n"
"}\n"
"\n"
"QStatusBar {\n"
"    border-radius: 1px;\n"
"    background-color: qlineargradient(spread:reflect, x1:0.607246, y1:0.346, x2:0.623037, y2:1, stop:0 rgba(8, 120, 0, 255), stop:1 rgba(15, 76, 0, 255));\n"
"    color: rgb(240, 240, 240);\n"
"}\n"
"\n"
"QFrame[frameShape=\"4\"], QFrame[frameShape=\"5\"]{\n"
"    background-color: rgba(8, 120, 0, 255);\n"
"}\n"
"\n"
"QPushButton{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(193, 193, 193, 120));\n"
"    padding-left: 4px;\n"
"    padding-right: 4px;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(220, 223, 220, 120));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"     background-color: qlineargradient(spread:reflect, x2:0.262, y2:0.573773, x1:1, y1:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(220, 223, 220, 120));\n"
"}\n"
"\n"
"QDateEdit{\n"
"     background-color: qlineargradient(spread:reflect, x2:0.262, y2:0.573773, x1:1, y1:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(220, 223, 220, 250));\n"
"}\n"
"\n"
"QDateEdit:hover{\n"
"      background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(220, 223, 220, 120));\n"
"}\n"
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
"    alternate-background-color: rgba(0,0,0,20);\n"
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
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.startDateLabel = QtWidgets.QLabel(Dialog)
        self.startDateLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.startDateLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.startDateLabel.setObjectName("startDateLabel")
        self.horizontalLayout_4.addWidget(self.startDateLabel)
        self.startDate = QtWidgets.QDateEdit(Dialog)
        self.startDate.setObjectName("startDate")
        self.horizontalLayout_4.addWidget(self.startDate)
        self.endDateLabel = QtWidgets.QLabel(Dialog)
        self.endDateLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endDateLabel.setObjectName("endDateLabel")
        self.horizontalLayout_4.addWidget(self.endDateLabel)
        self.endDate = QtWidgets.QDateEdit(Dialog)
        self.endDate.setObjectName("endDate")
        self.horizontalLayout_4.addWidget(self.endDate)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.campaignCol = QtWidgets.QVBoxLayout()
        self.campaignCol.setObjectName("campaignCol")
        self.campaignListLabel = QtWidgets.QLabel(Dialog)
        self.campaignListLabel.setObjectName("campaignListLabel")
        self.campaignCol.addWidget(self.campaignListLabel)
        self.campaignULine = QtWidgets.QFrame(Dialog)
        self.campaignULine.setFrameShape(QtWidgets.QFrame.HLine)
        self.campaignULine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.campaignULine.setObjectName("campaignULine")
        self.campaignCol.addWidget(self.campaignULine)
        self.campaignList = QtWidgets.QListView(Dialog)
        self.campaignList.setObjectName("campaignList")
        self.campaignCol.addWidget(self.campaignList)
        self.horizontalLayout_3.addLayout(self.campaignCol)
        self.dateCol = QtWidgets.QVBoxLayout()
        self.dateCol.setObjectName("dateCol")
        self.dateListLabel = QtWidgets.QLabel(Dialog)
        self.dateListLabel.setObjectName("dateListLabel")
        self.dateCol.addWidget(self.dateListLabel)
        self.dateULine = QtWidgets.QFrame(Dialog)
        self.dateULine.setFrameShape(QtWidgets.QFrame.HLine)
        self.dateULine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.dateULine.setObjectName("dateULine")
        self.dateCol.addWidget(self.dateULine)
        self.dateList = QtWidgets.QListView(Dialog)
        self.dateList.setObjectName("dateList")
        self.dateCol.addWidget(self.dateList)
        self.horizontalLayout_3.addLayout(self.dateCol)
        self.recordCol = QtWidgets.QVBoxLayout()
        self.recordCol.setObjectName("recordCol")
        self.recordListLabel = QtWidgets.QLabel(Dialog)
        self.recordListLabel.setObjectName("recordListLabel")
        self.recordCol.addWidget(self.recordListLabel)
        self.recordULine = QtWidgets.QFrame(Dialog)
        self.recordULine.setFrameShape(QtWidgets.QFrame.HLine)
        self.recordULine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.recordULine.setObjectName("recordULine")
        self.recordCol.addWidget(self.recordULine)
        self.recordList = QtWidgets.QListView(Dialog)
        self.recordList.setObjectName("recordList")
        self.recordCol.addWidget(self.recordList)
        self.horizontalLayout_3.addLayout(self.recordCol)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.startDateLabel.setText(_translate("Dialog", "Start Date:"))
        self.startDate.setToolTip(_translate("Dialog", "<html><head/><body><p>Select earliest date to display</p></body></html>"))
        self.endDateLabel.setText(_translate("Dialog", "End Date:"))
        self.endDate.setToolTip(_translate("Dialog", "<html><head/><body><p>Enter latest date to display</p></body></html>"))
        self.campaignListLabel.setText(_translate("Dialog", "Campaign"))
        self.dateListLabel.setText(_translate("Dialog", "Date"))
        self.recordListLabel.setText(_translate("Dialog", "Record"))

