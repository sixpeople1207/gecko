import pandas as pd
import sqlite3
import math
import glob
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QThread, pyqtSignal
import PyQt5.QtGui
import time
import asyncio
import sys
import os
import openpyxl

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path('form.ui')
db_path = resource_path('CoinData.db')

form_class = uic.loadUiType(form)[0]

# QDialog 인자를 ui.ui의 class와 동일한 객체를 집어넣어줘야한다. 기본 예제들은 모두 QMainWindow이다.

class WindowClass(QDialog, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.index = 0
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(100)
        # self.openBtn.clicked.connect(self.btn_fun_FileLoad)
        self.savePathBtn.clicked.connect(self.btn_fun_FileSave)
        self.saveBtn.clicked.connect(self.save_Excel)
        self.fromDate.setDateRange(QDate(2020, 11, 5), QDate(2023, 8, 5))
        self.endDate.setDateRange(QDate(2020, 12, 5), QDate(2023, 8, 5))
        # ok_btn = QDialogButtonBox("buttonBox", self)
        # self.buttonBox.accepted.connect(self.save_Excel)   

    
        # if self.saveBtn.clicked:     
        #     asyncio.run(self.save_Excel())
        #     print("눌럿음")

    def update_progress_Bar(self):
        # self.thread = MyThread()
        # self.thread.change_value.connect(self.setProgressValue)
        # self.thread.start()
        self.progressBar.setValue(self.index)

    # def setProgressValue(self):
        # self.progressBar.setValue(self.index)

    def save_Excel(self):
        # pd.set_option('display.max_rows', None)
        displayDateVar_fromDate = self.fromDate.date()
        displayDateVar_endDate = self.endDate.date()
        # db_path = resource_path(self.openPath.text())
        try:
            conn = sqlite3.connect(db_path)
            coinlist = pd.read_sql("SELECT * FROM CoinList", conn)
            history = pd.read_sql("SELECT * FROM CoinHistory", conn)
            fromDate = displayDateVar_fromDate.toString(
                "yyyy-MM-dd")+' 09:00:00'
            endDate = displayDateVar_endDate.toString(
                "yyyy-MM-dd")+' 09:00:00'
            columns = ['Name', 'FromPrice', 'MaxPrice', 'Per']

            df = pd.DataFrame(columns=columns)
            self.progressBar.setRange(0,len(coinlist['Name']))
            self.write_dataFrame(df=df, coinlist=coinlist, history=history, fromDate=fromDate, endDate=endDate)
        except Exception as e:
            QMessageBox.about(self, "error message", str(e))
    
    def write_dataFrame(self, df, coinlist, history, fromDate, endDate):
        for coin in coinlist['Name']:
            self.index += 1
            self.update_progress_Bar()
            indexPrice = history[(history['Name'] == coin) &
                                (history['Date'] == fromDate)]
            sliceHistory = history.loc[(history['Name'] == coin) &
                                    (history['Date'] < endDate)]
            maxPrice = sliceHistory.max(axis=0)
            if(len(indexPrice) > 0):
                per = round(
                    float(maxPrice['Price']/indexPrice['Price'].values), 1)*100
                df = df.append(
                    {'Name': coin, 'FromPrice': indexPrice['Price'].values[0], 'MaxPrice': maxPrice['Price'], 'Per': per}, ignore_index=True)
            else:
                per = "-"
                df = df.append(
                    {'Name': coin, 'FromPrice': "없음", 'MaxPrice': maxPrice['Price'], 'Per': per}, ignore_index=True)
        df.to_excel(excel_writer=self.savePath.text(), index=False, engine='openpyxl')
        # with pd.ExcelWriter('./per.xlsx', engine='xlsxwriter') as writer:
        #     df.to_excel(writer, index=False)
        #     ws = writer.sheets['코인캑코']
        # ## 칼럼 폭 조절
        # for i, col in enumerate(df.columns):
        #     width = '30'
        #     ws.set_column(i, i, width+1) ## 여백을 위해 1 추가
        #     ws.autofilter(0, 0, df.shape[0] - 1, df.shape[1] - 1) ## 첫 행 필터 추가
        #     ws.freeze_panes(1, 0) ## 첫 행 고정
        QMessageBox.about(self, "", "저장이 완료 되었습니다.")
    
    def btn_fun_FileSave(self):
        # fname = QFileDialog.getOpenFileName(self, '', '', '', "Excel(*.xlsx)")
        fname = QFileDialog.getSaveFileName(
            self, 'coinAnalisys', "coinHistory.xlsx")
        print(fname[0])
        print(fname[1])
        self.savePath.setText(fname[0])

    def btn_fun_FileLoad(self):
        # fname = QFileDialog.getOpenFileName(self, '', '', '', "Excel(*.xlsx)")
        fname = QFileDialog.getOpenFileName(
            self, 'coinAnalisys', "CoinData.db")
        print(fname[0])
        print(fname[1])
        self.openPath.setText(fname[0])
    
class MyThread(QThread):
    change_value = pyqtSignal(int)
    def run(self):
        cnt = 0
        while cnt < 300:
            cnt += 1
            time.sleep(0.1)
            self.change_value.emit(cnt)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())
