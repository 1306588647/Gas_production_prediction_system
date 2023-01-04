import pymysql
from PyQt5.QtWidgets import QWidget, QMenu, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QRegExp

# 管理员界面
class Staff(QWidget):
    def __init__(self,login):
        super(Staff, self).__init__()
        # 加载ui界面
        loadUi('resource/ui/admin.ui', self)

        self.login = login

        # 设置变量是否加载数据完成
        self.is_read = False
        self.is_add = False
        self.read_data()

        # 行名称不显示
        self.tableWidget.verticalHeader().setVisible(False)

        # 表格控件宽度 随着父窗口的缩放自动缩放
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        # 允许右键产生子菜单
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # 右键菜单
        self.tableWidget.customContextMenuRequested.connect(self.tableWidget_menu)

        self.tableWidget.cellChanged.connect(self.item_changed)

    # 显示右击菜单
    def tableWidget_menu(self, pos):
        menu = QMenu()  # 实例化菜单
        item1 = menu.addAction(u"添加")
        item2 = menu.addAction(u"删除")

        action = menu.exec_(self.tableWidget.mapToGlobal(pos))

        if action == item1:
            self.add_data()

        elif action == item2:
            self.remove_data()

    # 从数据库读取数据
    def read_data(self):
        self.is_read = False
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        # 数据库连接对象
        db = pymysql.connect(host="localhost", user="root", password="root", database="userinfo")
        # 游标对象
        cursor = db.cursor()
        # 查询语句
        sql = "SELECT * FROM staff"
        cursor.execute(sql)
        result = cursor.fetchall()
        # 设置表格有多少行
        self.tableWidget.setRowCount(len(result))
        # 行初始化0，列初始化0
        row = 0
        # 依次遍历元组，并显示到界面上
        for items in result:
            colum = 0
            for item in items:
                # 获取插入内容
                context = QTableWidgetItem(str(item))
                # 如果是id数据，则不可修改
                if colum == 0:
                    # 插入内容不可修改
                    context.setFlags(Qt.ItemIsEnabled)
                self.tableWidget.setItem(row, colum, context)
                colum = colum + 1
            row = row + 1
        cursor.close()
        db.close()
        # 数据读取完毕
        self.is_read = True

    # 添加数据
    def add_data(self):
        stname = ""
        phone = ""
        # 数据库连接对象
        db = pymysql.connect(host="localhost", user="root", password="root", database="userinfo")
        # 游标对象
        cursor = db.cursor()
        # 查询语句
        sql = f"insert into staff (stname,phone) values(\'{stname}\',\'{phone}\')"
        cursor.execute(sql)
        db.commit()
        sql = f"select id from staff where stname = \'{stname}\' and phone = \'{phone}\'"
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

        self.read_data()

    # 删除数据
    def remove_data(self):
        '''
        删除某一行的数据信息
        :return:
        '''
        # 获取被选中的数据item
        row_select = self.tableWidget.selectedItems()
        # 如果选中数据
        if len(row_select) != 0:
            # 获取行号
            row = row_select[0].row()
            # 获取删除的id号
            id = self.tableWidget.item(row, 0).text()
            self.tableWidget.removeRow(row)
            # 更新数据库
            # 数据库连接对象
            db = pymysql.connect(host="localhost", user="root", password="root",
                                 database="userinfo")
            # 游标对象
            cursor = db.cursor()
            # 查询语句
            sql = f"delete from staff where id = {id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            db.commit()
            db.close()
            QMessageBox.information(self, "提示", "删除成功！")
        else:
            QMessageBox.information(self, "提示", "请先选择要删除数据的姓名！")

    # 修改数据
    def item_changed(self, row, column):
        if self.is_read == True:
            id = int(self.tableWidget.item(row, 0).text())
            stname = self.tableWidget.item(row, 1).text()
            phone = self.tableWidget.item(row, 2).text()

            # 数据库连接对象
            db = pymysql.connect(host="localhost", user="root", password="root",
                                 database="userinfo")
            # 游标对象
            cursor = db.cursor()
            # 查询语句
            sql = f"update staff set stname = \'{stname}\',phone = \'{phone}\' where id = {id}"
            cursor.execute(sql)
            cursor.close()
            db.commit()
            db.close()


    def closeEvent(self, event):
        """Shuts down application on close."""
        self.login.show()