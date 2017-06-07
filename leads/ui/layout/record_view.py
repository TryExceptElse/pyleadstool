# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/user3/PycharmProjects/pyleadstool/ui/record_view.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(512, 512)
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
        self.translationRecordLabel = QtWidgets.QLabel(Dialog)
        self.translationRecordLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.translationRecordLabel.setObjectName("translationRecordLabel")
        self.verticalLayout.addWidget(self.translationRecordLabel)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.dateTimeLabel = QtWidgets.QLabel(Dialog)
        self.dateTimeLabel.setObjectName("dateTimeLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.dateTimeLabel)
        self.dateTimeReadout = QtWidgets.QLabel(Dialog)
        self.dateTimeReadout.setObjectName("dateTimeReadout")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.dateTimeReadout)
        self.nEntriesLabel = QtWidgets.QLabel(Dialog)
        self.nEntriesLabel.setObjectName("nEntriesLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.nEntriesLabel)
        self.nEntriesReadout = QtWidgets.QLabel(Dialog)
        self.nEntriesReadout.setObjectName("nEntriesReadout")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.nEntriesReadout)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.colNamesLayout = QtWidgets.QVBoxLayout()
        self.colNamesLayout.setObjectName("colNamesLayout")
        self.colNamesLabel = QtWidgets.QLabel(Dialog)
        self.colNamesLabel.setObjectName("colNamesLabel")
        self.colNamesLayout.addWidget(self.colNamesLabel)
        self.fieldsDeliminator = QtWidgets.QFrame(Dialog)
        self.fieldsDeliminator.setFrameShape(QtWidgets.QFrame.HLine)
        self.fieldsDeliminator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.fieldsDeliminator.setObjectName("fieldsDeliminator")
        self.colNamesLayout.addWidget(self.fieldsDeliminator)
        self.fieldsList = QtWidgets.QListView(Dialog)
        self.fieldsList.setObjectName("fieldsList")
        self.colNamesLayout.addWidget(self.fieldsList)
        self.horizontalLayout.addLayout(self.colNamesLayout)
        self.entriesListLayout = QtWidgets.QVBoxLayout()
        self.entriesListLayout.setObjectName("entriesListLayout")
        self.displayedFieldLayout = QtWidgets.QHBoxLayout()
        self.displayedFieldLayout.setObjectName("displayedFieldLayout")
        self.entriesLabel = QtWidgets.QLabel(Dialog)
        self.entriesLabel.setObjectName("entriesLabel")
        self.displayedFieldLayout.addWidget(self.entriesLabel)
        self.displayedFieldLabel = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily("Lato")
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.displayedFieldLabel.setFont(font)
        self.displayedFieldLabel.setStyleSheet("font: 8pt \"Lato\";")
        self.displayedFieldLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.displayedFieldLabel.setObjectName("displayedFieldLabel")
        self.displayedFieldLayout.addWidget(self.displayedFieldLabel)
        self.displayedFieldSelector = QtWidgets.QComboBox(Dialog)
        self.displayedFieldSelector.setStyleSheet("font: 10pt \"Lato\"")
        self.displayedFieldSelector.setObjectName("displayedFieldSelector")
        self.displayedFieldLayout.addWidget(self.displayedFieldSelector)
        self.displayedFieldLayout.setStretch(2, 1)
        self.entriesListLayout.addLayout(self.displayedFieldLayout)
        self.entriesDeliminator = QtWidgets.QFrame(Dialog)
        self.entriesDeliminator.setFrameShape(QtWidgets.QFrame.HLine)
        self.entriesDeliminator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.entriesDeliminator.setObjectName("entriesDeliminator")
        self.entriesListLayout.addWidget(self.entriesDeliminator)
        self.entriesList = QtWidgets.QListView(Dialog)
        self.entriesList.setObjectName("entriesList")
        self.entriesListLayout.addWidget(self.entriesList)
        self.horizontalLayout.addLayout(self.entriesListLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.actionBar = QtWidgets.QHBoxLayout()
        self.actionBar.setContentsMargins(0, -1, -1, -1)
        self.actionBar.setObjectName("actionBar")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.actionBar.addItem(spacerItem)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setObjectName("pushButton_2")
        self.actionBar.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton.setObjectName("pushButton")
        self.actionBar.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.actionBar)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.translationRecordLabel.setText(_translate("Dialog", "Translation Record"))
        self.dateTimeLabel.setText(_translate("Dialog", "Date and Time"))
        self.dateTimeReadout.setText(_translate("Dialog", "DateTime placeholder"))
        self.nEntriesLabel.setText(_translate("Dialog", "# Entries"))
        self.nEntriesReadout.setText(_translate("Dialog", "Number Placeholder"))
        self.colNamesLabel.setText(_translate("Dialog", "Fields"))
        self.entriesLabel.setText(_translate("Dialog", "Entries"))
        self.displayedFieldLabel.setText(_translate("Dialog", "listed by:"))
        self.pushButton_2.setToolTip(_translate("Dialog", "<html><head/><body><p>Search entries in translation record for a specific value</p></body></html>"))
        self.pushButton_2.setText(_translate("Dialog", "Search Record"))
        self.pushButton.setToolTip(_translate("Dialog", "<html><head/><body><p>View record as a table of values by entry and column.</p></body></html>"))
        self.pushButton.setText(_translate("Dialog", "View Record as Table"))

