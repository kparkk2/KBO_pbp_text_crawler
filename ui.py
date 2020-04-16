# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import datetime

now = datetime.datetime.now()

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        Dialog.resize(500, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(500, 300))
        Dialog.setMaximumSize(QtCore.QSize(500, 300))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        Dialog.setFont(font)
        self.startDateEdit = QtWidgets.QDateEdit(Dialog)
        self.startDateEdit.setGeometry(QtCore.QRect(20, 40, 110, 24))
        self.startDateEdit.setDate(QtCore.QDate(int(now.year), int(now.month), int(now.day)))
        self.startDateEdit.setObjectName("startDateEdit")
        self.endDateEdit = QtWidgets.QDateEdit(Dialog)
        self.endDateEdit.setGeometry(QtCore.QRect(260, 40, 110, 24))
        self.endDateEdit.setDate(QtCore.QDate(int(now.year), int(now.month), int(now.day)))
        self.endDateEdit.setObjectName("endDateEdit")
        self.startDateLabel = QtWidgets.QLabel(Dialog)
        self.startDateLabel.setGeometry(QtCore.QRect(20, 20, 91, 16))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        self.startDateLabel.setFont(font)
        self.startDateLabel.setObjectName("startDateLabel")
        self.endDateLabel = QtWidgets.QLabel(Dialog)
        self.endDateLabel.setGeometry(QtCore.QRect(260, 20, 91, 16))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        self.endDateLabel.setFont(font)
        self.endDateLabel.setObjectName("endDateLabel")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(30, 250, 441, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.checkDebug = QtWidgets.QCheckBox(Dialog)
        self.checkDebug.setGeometry(QtCore.QRect(20, 170, 131, 20))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        self.checkDebug.setFont(font)
        self.checkDebug.setObjectName("checkDebug")
        self.checkPlayoff = QtWidgets.QCheckBox(Dialog)
        self.checkPlayoff.setGeometry(QtCore.QRect(20, 140, 131, 20))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        self.checkPlayoff.setFont(font)
        self.checkPlayoff.setObjectName("checkPlayoff")
        self.checkJoinCSV = QtWidgets.QCheckBox(Dialog)
        self.checkJoinCSV.setGeometry(QtCore.QRect(20, 110, 341, 20))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        self.checkJoinCSV.setFont(font)
        self.checkJoinCSV.setObjectName("checkJoinCSV")
        self.startDateCalendarButton = QtWidgets.QToolButton(Dialog)
        self.startDateCalendarButton.setGeometry(QtCore.QRect(130, 40, 26, 22))
        self.startDateCalendarButton.setObjectName("startDateCalendarButton")
        self.endDateCalendarButton = QtWidgets.QToolButton(Dialog)
        self.endDateCalendarButton.setGeometry(QtCore.QRect(370, 40, 26, 22))
        self.endDateCalendarButton.setObjectName("endDateCalendarButton")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(400, 210, 81, 32))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.startDateCalendar = QtWidgets.QCalendarWidget(Dialog)
        self.startDateCalendar.setVisible(False)
        self.startDateCalendar.setEnabled(True)
        self.startDateCalendar.setGeometry(QtCore.QRect(20, 70, 224, 173))
        self.startDateCalendar.setMaximumSize(QtCore.QSize(224, 173))
        self.startDateCalendar.setAutoFillBackground(True)
        self.startDateCalendar.setMinimumDate(QtCore.QDate(2005, 1, 1))
        self.startDateCalendar.setMaximumDate(QtCore.QDate(2050, 12, 31))
        self.startDateCalendar.setGridVisible(True)
        self.startDateCalendar.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.startDateCalendar.setObjectName("startDateCalendar")
        self.endDateCalendar = QtWidgets.QCalendarWidget(Dialog)
        self.endDateCalendar.setVisible(False)
        self.endDateCalendar.setEnabled(True)
        self.endDateCalendar.setGeometry(QtCore.QRect(260, 70, 224, 173))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endDateCalendar.sizePolicy().hasHeightForWidth())
        self.endDateCalendar.setSizePolicy(sizePolicy)
        self.endDateCalendar.setMaximumSize(QtCore.QSize(224, 173))
        self.endDateCalendar.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.endDateCalendar.setAutoFillBackground(True)
        self.endDateCalendar.setMinimumDate(QtCore.QDate(2005, 1, 1))
        self.endDateCalendar.setMaximumDate(QtCore.QDate(2050, 12, 31))
        self.endDateCalendar.setGridVisible(True)
        self.endDateCalendar.setHorizontalHeaderFormat(QtWidgets.QCalendarWidget.ShortDayNames)
        self.endDateCalendar.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.endDateCalendar.setObjectName("endDateCalendar")
        self.savePathButton = QtWidgets.QPushButton(Dialog)
        self.savePathButton.setGeometry(QtCore.QRect(380, 180, 101, 32))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Gothic")
        self.savePathButton.setFont(font)
        self.savePathButton.setObjectName("savePathButton")
        self.pathDialog = QtWidgets.QFileDialog()
        self.pathDialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        self.retranslateUi(Dialog)
        self.pushButton.clicked.connect(Dialog.accept)
        self.startDateCalendar.clicked['QDate'].connect(self.startDateEdit.setDate)
        self.startDateCalendarButton.clicked.connect(self.toggleStartDateCalendar)
        self.startDateCalendar.clicked['QDate'].connect(self.startDateCalendar.hide)
        self.endDateCalendarButton.clicked.connect(self.toggleEndDateCalendar)
        self.endDateCalendar.clicked['QDate'].connect(self.endDateEdit.setDate)
        self.endDateCalendar.clicked['QDate'].connect(self.endDateCalendar.hide)
        self.startDateEdit.objectNameChanged['QString'].connect(self.startDateCalendar.hide)
        self.startDateEdit.dateChanged['QDate'].connect(self.startDateCalendar.setSelectedDate)
        self.endDateEdit.dateChanged['QDate'].connect(self.endDateCalendar.setSelectedDate)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.savePathButton.clicked.connect(self.getSavePath)

        self.timerVar = QtCore.QTimer()
        self.timerVar.setInterval(1000)
        self.timerVar.timeout.connect(self.progressBarTimer)
        self.timerVar.start()

    def progressBarTimer(self):
        self.time = self.progressBar.value()
        self.time += 1
        self.progressBar.setValue(self.time)

        if self.time >= self.progressBar.maximum() :
            self.timerVar.stop()

    def printValue(self) :
        print(self.progressBar.value())


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("PBP", "PBP"))
        self.startDateLabel.setText(_translate("Dialog", "Game Date >="))
        self.endDateLabel.setText(_translate("Dialog", "Game Date <="))
        self.checkDebug.setText(_translate("Dialog", "디버그 메시지 출력"))
        self.checkPlayoff.setText(_translate("Dialog", "포스트시즌 포함"))
        self.checkJoinCSV.setText(_translate("Dialog", "연도별 묶음 파일 생성(기존 파일은 삭제)"))
        self.startDateCalendarButton.setText(_translate("Dialog", "..."))
        self.endDateCalendarButton.setText(_translate("Dialog", "..."))
        self.pushButton.setText(_translate("Dialog", "다운로드!"))
        self.savePathButton.setText(_translate("Dialog", "저장 위치 선택"))

    def toggleStartDateCalendar(self):
        isVisible = self.startDateCalendar.isVisible()
        if isVisible:
            self.startDateCalendar.hide()
        else:
            self.startDateCalendar.show()

    def toggleEndDateCalendar(self):
        isVisible = self.endDateCalendar.isVisible()
        if isVisible:
            self.endDateCalendar.hide()
        else:
            self.endDateCalendar.show()

    def getSavePath(self):
        dirname = self.pathDialog.getExistingDirectory()
        if dirname:
            print(dirname)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
