# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/user3/PycharmProjects/pyleadstool/ui/campaign_del.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainLabel = QtWidgets.QLabel(Dialog)
        self.mainLabel.setWordWrap(True)
        self.mainLabel.setObjectName("mainLabel")
        self.verticalLayout.addWidget(self.mainLabel)
        self.separatorLine = QtWidgets.QFrame(Dialog)
        self.separatorLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.separatorLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.separatorLine.setObjectName("separatorLine")
        self.verticalLayout.addWidget(self.separatorLine)
        self.promptLabel = QtWidgets.QLabel(Dialog)
        self.promptLabel.setWordWrap(True)
        self.promptLabel.setObjectName("promptLabel")
        self.verticalLayout.addWidget(self.promptLabel)
        self.nameField = QtWidgets.QLineEdit(Dialog)
        self.nameField.setObjectName("nameField")
        self.verticalLayout.addWidget(self.nameField)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBar = QtWidgets.QHBoxLayout()
        self.buttonBar.setObjectName("buttonBar")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonBar.addItem(spacerItem1)
        self.delButton = QtWidgets.QPushButton(Dialog)
        self.delButton.setObjectName("delButton")
        self.buttonBar.addWidget(self.delButton)
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setObjectName("cancelButton")
        self.buttonBar.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.buttonBar)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.mainLabel.setText(_translate("Dialog", "Are you sure that you wish to delete the campaign \'{}\' ?\n"
"\n"
"This cannot be undone."))
        self.promptLabel.setText(_translate("Dialog", "To ensure that the correct campaign is being deleted, type the name of the campaign below to confirm deletion of all records and settings."))
        self.nameField.setPlaceholderText(_translate("Dialog", "Name of campaign to delete"))
        self.delButton.setText(_translate("Dialog", "Delete {}"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))

