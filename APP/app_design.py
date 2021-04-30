# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\WinSys\PROJECTS\WORMCHAN\WormChan\WormChan\APP\app_design.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(984, 1170)
        MainWindow.setMinimumSize(QtCore.QSize(984, 1036))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.app_pages = QtWidgets.QStackedWidget(self.centralwidget)
        self.app_pages.setGeometry(QtCore.QRect(20, 10, 941, 1151))
        self.app_pages.setMinimumSize(QtCore.QSize(941, 1151))
        self.app_pages.setObjectName("app_pages")
        self.login_page = QtWidgets.QWidget()
        self.login_page.setObjectName("login_page")
        self.gridLayoutWidget = QtWidgets.QWidget(self.login_page)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(160, 400, 631, 271))
        self.gridLayoutWidget.setMinimumSize(QtCore.QSize(631, 271))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.login_grid = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.login_grid.setContentsMargins(0, 0, 50, 0)
        self.login_grid.setVerticalSpacing(0)
        self.login_grid.setObjectName("login_grid")
        self.login_label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.login_label.setMinimumSize(QtCore.QSize(75, 20))
        self.login_label.setObjectName("login_label")
        self.login_grid.addWidget(self.login_label, 1, 0, 1, 1)
        self.submit_data = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.submit_data.setMinimumSize(QtCore.QSize(75, 23))
        self.submit_data.setObjectName("submit_data")
        self.login_grid.addWidget(self.submit_data, 3, 0, 1, 1)
        self.password_label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.password_label.setMinimumSize(QtCore.QSize(75, 20))
        self.password_label.setObjectName("password_label")
        self.login_grid.addWidget(self.password_label, 2, 0, 1, 1)
        self.login_input = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.login_input.setObjectName("login_input")
        self.login_grid.addWidget(self.login_input, 1, 1, 1, 1)
        self.password_input = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.password_input.setObjectName("password_input")
        self.login_grid.addWidget(self.password_input, 2, 1, 1, 1)
        self.app_pages.addWidget(self.login_page)
        self.image_page = QtWidgets.QWidget()
        self.image_page.setObjectName("image_page")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.image_page)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 921, 1131))
        self.gridLayoutWidget_2.setMinimumSize(QtCore.QSize(921, 1131))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.image_grid = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.image_grid.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.image_grid.setContentsMargins(0, 0, 0, 0)
        self.image_grid.setObjectName("image_grid")
        self.next_btn = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.next_btn.setMinimumSize(QtCore.QSize(302, 23))
        self.next_btn.setObjectName("next_btn")
        self.image_grid.addWidget(self.next_btn, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(303, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.image_grid.addItem(spacerItem, 0, 1, 1, 1)
        self.save_btn = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.save_btn.setMinimumSize(QtCore.QSize(302, 23))
        self.save_btn.setObjectName("save_btn")
        self.image_grid.addWidget(self.save_btn, 4, 0, 1, 1)
        self.pepe_btn = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.pepe_btn.setMinimumSize(QtCore.QSize(302, 23))
        self.pepe_btn.setObjectName("pepe_btn")
        self.image_grid.addWidget(self.pepe_btn, 4, 2, 1, 1)
        self.rescan_btn = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.rescan_btn.setMinimumSize(QtCore.QSize(303, 23))
        self.rescan_btn.setObjectName("rescan_btn")
        self.image_grid.addWidget(self.rescan_btn, 3, 1, 1, 1)
        self.previous_btn = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.previous_btn.setMinimumSize(QtCore.QSize(302, 23))
        self.previous_btn.setObjectName("previous_btn")
        self.image_grid.addWidget(self.previous_btn, 3, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(303, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.image_grid.addItem(spacerItem1, 2, 1, 1, 1)
        self.image_view = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.image_view.setMinimumSize(QtCore.QSize(919, 950))
        self.image_view.setObjectName("image_view")
        self.image_grid.addWidget(self.image_view, 1, 0, 1, 3)
        self.cache_index = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.cache_index.setMinimumSize(QtCore.QSize(302, 23))
        self.cache_index.setObjectName("cache_index")
        self.image_grid.addWidget(self.cache_index, 5, 0, 1, 1)
        self.app_pages.addWidget(self.image_page)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.app_pages.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.login_label.setText(_translate("MainWindow", "Login"))
        self.submit_data.setText(_translate("MainWindow", "Submit"))
        self.password_label.setText(_translate("MainWindow", "Password"))
        self.next_btn.setText(_translate("MainWindow", "next"))
        self.save_btn.setText(_translate("MainWindow", "save"))
        self.pepe_btn.setText(_translate("MainWindow", "mark PEPE"))
        self.rescan_btn.setText(_translate("MainWindow", "rescan"))
        self.previous_btn.setText(_translate("MainWindow", "previous"))
        self.image_view.setText(_translate("MainWindow", "TextLabel"))
        self.cache_index.setText(_translate("MainWindow", "save index"))
