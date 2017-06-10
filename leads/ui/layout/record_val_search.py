# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/user3/PycharmProjects/pyleadstool/ui/record_val_search.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 400)
        Dialog.setLayoutDirection(QtCore.Qt.LeftToRight)
        Dialog.setStyleSheet("QWidget {\n"
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
"     background-color: qlineargradient(spread:reflect, x1:0.262, y1:0.573773, x2:1, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(240, 243, 240, 120));\n"
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
"    alternate-background-color: rgba(0,0,0,10);\n"
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
"QLineEdit {\n"
"    background-color: rgba(0, 0, 0, 00);\n"
"}\n"
"\n"
"QLineEdit:hover {\n"
"    background-color: rgba(0, 0, 0, 20);\n"
"}\n"
"\n"
"QDateTimeEdit {\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"}\n"
"\n"
"QDateTimeEdit:hover {\n"
"    background-color: rgba(0, 0, 0, 20);\n"
"}\n"
"\n"
"QComboBox{\n"
"}\n"
"\n"
"QComboBox:Hover{\n"
"    background-color: rgba(0, 0, 0, 20);\n"
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerLabel = QtWidgets.QLabel(Dialog)
        self.headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.headerLabel.setObjectName("headerLabel")
        self.verticalLayout.addWidget(self.headerLabel)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.valColLabel = QtWidgets.QLabel(Dialog)
        self.valColLabel.setObjectName("valColLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.valColLabel)
        self.valColEdit = QtWidgets.QLineEdit(Dialog)
        self.valColEdit.setObjectName("valColEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.valColEdit)
        self.valueLabel = QtWidgets.QLabel(Dialog)
        self.valueLabel.setObjectName("valueLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.valueLabel)
        self.valueEdit = QtWidgets.QLineEdit(Dialog)
        self.valueEdit.setObjectName("valueEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.valueEdit)
        self.campaignLabel = QtWidgets.QLabel(Dialog)
        self.campaignLabel.setObjectName("campaignLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.campaignLabel)
        self.startDateLabel = QtWidgets.QLabel(Dialog)
        self.startDateLabel.setObjectName("startDateLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.startDateLabel)
        self.startDateTimeEdit = QtWidgets.QDateTimeEdit(Dialog)
        self.startDateTimeEdit.setObjectName("startDateTimeEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.startDateTimeEdit)
        self.endDateLabel = QtWidgets.QLabel(Dialog)
        self.endDateLabel.setObjectName("endDateLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.endDateLabel)
        self.endDateTimeEdit = QtWidgets.QDateTimeEdit(Dialog)
        self.endDateTimeEdit.setObjectName("endDateTimeEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.endDateTimeEdit)
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setObjectName("comboBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.resultsTable = QtWidgets.QTableView(Dialog)
        self.resultsTable.setObjectName("resultsTable")
        self.verticalLayout.addWidget(self.resultsTable)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.headerLabel.setText(_translate("Dialog", "Searching All Records"))
        self.valColLabel.setText(_translate("Dialog", "Column:"))
        self.valColEdit.setToolTip(_translate("Dialog", "Enter name of column in which to search for values"))
        self.valColEdit.setPlaceholderText(_translate("Dialog", "Column Name"))
        self.valueLabel.setText(_translate("Dialog", "Value:"))
        self.valueEdit.setPlaceholderText(_translate("Dialog", "Value to Find"))
        self.campaignLabel.setText(_translate("Dialog", "Campaign"))
        self.startDateLabel.setText(_translate("Dialog", "Earliest Date"))
        self.endDateLabel.setText(_translate("Dialog", "Latest Date"))

