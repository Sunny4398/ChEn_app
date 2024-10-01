from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox 
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import matplotlib.image as mpimg
import pyqtgraph as pg
from math import ceil
import pandas as pd
import sqlite3
from sqlite3 import Error
import sys
import os
 
class TableModel(QtCore.QAbstractTableModel):
 
    def __init__(self, data):
        super(TableModel, self).__init__()
        
        self._data = data
 
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()] #pandas's iloc method
            return str(value)
 
        if role == Qt.ItemDataRole.TextAlignmentRole:          
            return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignHCenter
         
        if role == Qt.ItemDataRole.BackgroundRole and (index.row()%2 == 0):
            return QtGui.QColor('#d8ffdb')
 
    def rowCount(self, index):
        return self._data.shape[0]
 
    def columnCount(self, index):
        return self._data.shape[1]
 
    # Add Row and Column header
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole: # more roles
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
 
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
 
class AnotherWindow(QtWidgets.QMainWindow):
    # create a customized signal 
    submitted = QtCore.pyqtSignal(str) # "submitted" is like a component name 
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    #Slot


        
     
class MainWindow(QtWidgets.QMainWindow):
 
    def __init__(self):
        super().__init__()
        uic.loadUi('Translate_SQL.ui', self)
        self.table = self.tableView
        
        self.database = r"D:/Python/statapp/database/pythonsqlite.db"
        # create a database connect
        self.conn = create_connection(self.database)
        self.setWindowTitle('System')
        
        # Signals
        self.actionEXIT.triggered.connect(self.appEXIT)
        self.lineEdit_title.returnPressed.connect(self.searchByTitle)
        self.p_But_by_title.clicked.connect(self.searchByTitle)
        self.p_But_firstpage.clicked.connect(self.firstpage)
        self.p_But_uppage.clicked.connect(self.uppage)
        self.p_But_downpage.clicked.connect(self.downpage)
        self.p_But_lastpage.clicked.connect(self.lastpage)
        self.comboBox_page.currentIndexChanged.connect(self.changepage)
        
        #self.checkBox_edit.stateChanged.connect(self.edit)

        self.actionSave_Data.triggered.connect(self.saveData)
        

    

    def searchByTitle(self):
        if self.lineEdit_title.text() != '':
            title_key = self.lineEdit_title.text()
            # sql = "select id, title, eventtype, abstract from papers where title like '%"+title_key+"%'"
            sql = "select Chinese ,English"
            
            
            if self.comboBox.currentText()=='中文':
                select = " from Translate where Chinese like '%"+title_key+"%'"
            elif self.comboBox.currentText()=='英文':
                select = " from Translate where English like '%"+title_key+"%'"

            
            sql = sql + select
            self.hi = 20
            self.lo = 0
            with self.conn:
                self.rows = SQLExecute(self, sql)
                if len(self.rows) > 0: 
                    names = [description[0] for description in self.cur.description]# extract column names
                    self.df = pd.DataFrame(self.rows)
                    self.df.columns = names
                    self.col = ['Chinese', 'English']
                    self.df.index = range(1, len(self.rows)+1)
                    self.comboBox_page.clear()
                    self.npage = ceil(len(self.rows)/20)
                    self.comboBox_page.addItems([str(i) for i in range(1,self.npage+1)])
                    self.page.setText('頁數：1')
                    self.page.setFont(QFont('PMingLiU',18))
                    self.page.setStyleSheet('color: rgb(0, 0, 0)')
                    ToTableView(self, self.df[self.col].iloc[self.lo:self.hi])
                    self.total.setText('總筆數：'+str(len(self.rows)))
            
    
    def firstpage(self):
        self.comboBox_page.setCurrentText('1')
    
    def uppage(self):
        self.comboBox_page.setCurrentText(str(int(self.comboBox_page.currentText())-1))
    def downpage(self):
        self.comboBox_page.setCurrentText(str(int(self.comboBox_page.currentText())+1))
    def lastpage(self):
        self.comboBox_page.setCurrentText(str(self.npage))
        
    def changepage(self):
        #print(self.comboBox_page.currentText())
        self.page.setText('頁數：'+str(self.comboBox_page.currentText()))
        high = self.hi+self.comboBox_page.currentIndex()*20
        low = self.lo+self.comboBox_page.currentIndex()*20
        ToTableView(self, self.df[self.col].iloc[low:high])
    
    def saveData(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', 
            "", "EXCEL files (*.xlsx)")
        if len(fname) != 0:
            self.df.to_excel(fname)
 
    def appEXIT(self):
        self.conn.close() # close database
        self.close() # close app
     
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn
 
def SQLExecute(self, SQL):
    """
    Execute a SQL command
    :param conn: SQL command
    :return: None
    """
    self.cur = self.conn.cursor()
    self.cur.execute(SQL)
    rows = self.cur.fetchall()
 
    if len(rows) == 0: # nothing found
        # raise a messageBox here
        dlg = QMessageBox(self)
        dlg.setWindowTitle("SQL Information: ")
        dlg.setText("No data match the query !!!")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('OK')
        dlg.setIcon(QMessageBox.Icon.Information)
        button = dlg.exec()
        # return
    return rows
 
def ToTableView(self, dataframe):
    """
    Display rows on the TableView in pandas format
    """
    
    self.model = TableModel(dataframe)
    self.table.setModel(self.model)
    
     
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()