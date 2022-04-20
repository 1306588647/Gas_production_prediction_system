import os
import shutil

from threading import Thread

import hashlib

from PyQt5.QtCore import pyqtSignal, QObject, Qt, QRegExp
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QMainWindow, QFileDialog, QLabel, QTableWidgetItem, \
    QMenu
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap, QRegExpValidator
import pymysql  # 数据库控制

from resource import gas_predict


# 自定义信号源对象类型，一定要继承自 QObject
class MySignals(QObject):
    # 定义一种信号，两个参数 类型分别是： QTextBrowser 和 字符串
    # 调用 emit方法 发信号时，传入参数 必须是这里指定的 参数类型

    text_print = pyqtSignal(str)

    # 子线程给主线程发送聚类个数
    type_return = pyqtSignal(int)

    # 子线程给主线程发送进度条完成进度
    progress_return = pyqtSignal(int)
    progress_return2 = pyqtSignal(int)

    # 每当预测文件图片生成，则向主线程发射信号，让主线程将图片显示出来
    predict_return = pyqtSignal(str)


# 登录界面
class Login(QWidget):
    def __init__(self):
        super(Login, self).__init__()

        # 加载ui界面
        loadUi('resource/ui/login.ui', self)
        # self.setupUi(self) # 设置写好的ui转py

        # 设置背景图片
        self.Background_png = QPixmap('resource/picture/background.png')
        self.Background.setPixmap(self.Background_png)

        # 图片自适应
        self.Background.setScaledContents(True)

        # 设置图标
        self.gas_ico_png = QPixmap('resource/picture/燃气.png')
        self.gas_ico.setPixmap(self.gas_ico_png)
        self.gas_ico.setScaledContents(True)

        # 登录按钮关联
        self.btn_login.clicked.connect(self.click_login)
        # 注册按钮关联
        self.btn_register.clicked.connect(self.click_register)

        # 设置输入框只能输入非中文字符
        self.text_user.setValidator(QRegExpValidator(QRegExp("[^\u4e00-\u9fa5]{16}"), self))
        self.text_password.setValidator(QRegExpValidator(QRegExp("[^\u4e00-\u9fa5]{16}"), self))

    # 登录事件触发
    def click_login(self):
        # 获取账号和密码文本框内容
        username = self.text_user.text().strip()
        password = self.text_password.text().strip()
        # 判断输入情况是否合法
        if username == '' or password == '':  # 账号或密码为空
            QMessageBox.information(self,
                                    "提示",
                                    "账号或密码为空!")
        else:
            # 如果是管理员账户则登陆管理员账户
            if username == 'root' and password == 'root':
                staff.show()
                login.close()
            else:
                # 创建md5对象
                hl = hashlib.md5()
                # Tips
                # 此处必须声明encode
                # 若写法为hl.update(str) 报错为： Unicode-objects must be encoded before hashing
                # 对密码进行md5加密
                hl.update(password.encode(encoding='utf-8'))
                # 获取加密密码
                password = hl.hexdigest()
                # 打开数据库连接
                db = pymysql.connect(host="localhost", user="root", password="root", database="userinfo")
                cursor = db.cursor()

                # 查询是否有该用户
                sql = f"select * from user where username =\'{username}\'"
                cursor.execute(sql)
                result = cursor.fetchall()

                # 判断数据库中是否存在当前用户
                if len(result) == 0:
                    QMessageBox.information(self,
                                            "提示",
                                            "登录失败，系统无该用户，请先注册！")
                else:
                    sql = f"select * from user where username =\'{username}\' and password = \'{password}\'"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if len(result) == 0:
                        QMessageBox.information(self,
                                                "提示",
                                                '密码错误，请重新输入!')
                    else:
                        QMessageBox.information(self,
                                                "提示",
                                                '登录成功!')
                        cursor.close()
                        db.close()

                        # 登录成功后显示主界面
                        main.show()
                        self.close()

    # 注册事件触发，进入注册界面
    def click_register(self):
        # 展示注册窗口
        register.show()
        # 隐藏登录窗口
        self.hide()

# 注册界面
class Register(QWidget):
    def __init__(self):
        super(Register, self).__init__()
        # 加载ui界面
        loadUi('resource/ui/register.ui', self)

        # 返回按钮关联
        self.btn_return.clicked.connect(self.click_return)

        # 注册按钮关联
        self.btn_register.clicked.connect(self.click_register)

        # 设置输入框只能输入非中文字符
        self.text_user.setValidator(QRegExpValidator(QRegExp("[^\u4e00-\u9fa5]{16}"), self))
        self.text_password.setValidator(QRegExpValidator(QRegExp("[^\u4e00-\u9fa5]{16}"), self))
        self.text_password_is.setValidator(QRegExpValidator(QRegExp("[^\u4e00-\u9fa5]{16}"), self))
        self.text_phone.setValidator(QRegExpValidator(QRegExp("^[0-9]+$"), self))

    # 返回按钮触发
    def click_return(self):
        # 展示登录窗口
        login.show()
        # 隐藏注册窗口
        self.close()

    # 注册按钮触发
    def click_register(self):
        # 获取输入框信息
        username = self.text_user.text().strip()
        password = self.text_password.text().strip()
        password_is = self.text_password_is.text().strip()
        staff_name = self.text_name.text().strip()
        phone = self.text_phone.text().strip()

        # 当账号或密码或确认密码为空，则提示为空
        if username == '' or password == '' or password_is == '' or staff_name == '' and phone == '':
            QMessageBox.information(self,
                                    "提示",
                                    "输入框不得为空！")
        # 当密码和确认密码不同，提示
        elif password != password_is:
            QMessageBox.information(self,
                                    "提示",
                                    "密码与确认密码不同！")
        # 用户名和密码不得少于6位
        elif len(username) < 6 or len(password) < 6:
            QMessageBox.information(self,
                                    "提示",
                                    "账号和密码都不得少于6位！")
        # 输入的数据都合法
        else:

            # 打开数据库连接
            db = pymysql.connect(host="localhost", user="root", password="root", database="userinfo")
            cursor = db.cursor()
            sql = f"select username from user where username =\'{username}\'"
            cursor.execute(sql)
            # 抓取结果
            result = cursor.fetchall()

            # 当查询到数据库中存在该账号，提示已存在
            if len(result) != 0:
                QMessageBox.information(self,
                                        "提示",
                                        "账号已存在，请重新输入！")
            # 如果没有该账号，则查询内部人员表，是否内部人员
            else:
                sql = f"select stname,phone from staff where stname = \'{staff_name}\' and phone = \'{phone}\'"
                cursor.execute(sql)
                # 抓取结果
                result = cursor.fetchall()
                # 当查询到数据库中存在该账号，提示已存在
                if len(result) == 0:
                    QMessageBox.information(self,
                                            "提示",
                                            staff_name + "非内部人员，禁止注册！")

                else:

                    # 创建md5对象
                    hl = hashlib.md5()
                    # Tips
                    # 此处必须声明encode
                    # 若写法为hl.update(str) 报错为： Unicode-objects must be encoded before hashing
                    # 对密码进行md5加密
                    hl.update(password.encode(encoding='utf-8'))
                    # 获取加密密码
                    password = hl.hexdigest()

                    sql = f"insert into user (username,password,phone) values(\'{username}\',\'{password}\',\'{phone}\')"
                    cursor.execute(sql)
                    # 提交数据库
                    db.commit()
                    cursor.close()
                    db.close()
                    QMessageBox.information(self,
                                            "提示",
                                            "注册成功！")
                    # 返回登录界面
                    self.click_return()

# 管理员界面
class Staff(QWidget):
    def __init__(self):
        super(Staff, self).__init__()
        # 加载ui界面
        loadUi('resource/ui/admin.ui', self)

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


# 主界面
class Main(QMainWindow):

    def __init__(self):
        super(Main, self).__init__()
        # 加载ui界面

        loadUi('resource/ui/main.ui', self)

        # 建立线程变量
        self.thread = None

        # 实例化信号
        self.ms = MySignals()

        # 初始化导出散点图、导出聚类折线图、导出预测折线图,导出预测数据，导出模型，导出字典都不可用，因为没有进行聚类和预测
        self.action_export_scatter.setEnabled(False)
        self.action_export_line.setEnabled(False)
        self.action_export_predict_png.setEnabled(False)
        self.action_export_predict_data.setEnabled(False)
        self.action_export_model.setEnabled(False)
        self.action_export_dict.setEnabled(False)

        # 初始化聚类中心为0
        self.center_num = 0

        # 设置预测最大值最小值
        self.spinBox.setRange(1, 30)

        # 初始化时，模型训练前，聚类分析不可用
        self.tabWidget.setTabEnabled(1, False)

        # 进度条初始化为0
        self.progressBar.setValue(0)
        self.progressBar_2.setValue(0)

        # 初始化聚类分析左侧list item数量为1，必有聚类散点图一个
        self.leftlist_num = 1

        # 预测天数
        self.pred_size = 0

        # 所有预测文件的数量
        self.all_predict_data_num = 0

        # 用来装聚类分析中右侧stack中每一个widget的列表（每个widget中装一个图片）
        self.stack_type_picture_widget = []
        # 用来装模型预测中右侧stack中每一个widget的列表（每个widget中装一个图片）
        self.stack_predict_picture_widget = []

        # 按钮点击触发事件
        self.btn_import_train.clicked.connect(self.click_import_train_data)  # 点击导入训练数据按钮触发事件
        self.btn_start_train.clicked.connect(self.click_start_train_data)  # 点击开始训练按钮触发事件
        self.btn_clear_data.clicked.connect(self.click_clear_train_data)  # 点击清空训练数据按钮触发事件
        self.btn_import_model.clicked.connect(self.click_btn_import_model_data)  # 点击导入模型文件按钮触发事件
        self.btn_import_dict.clicked.connect(self.click_btn_import_dict_data)  # 点击导入字典文件按钮触发事件
        self.btn_import_predata.clicked.connect(self.click_import_predict_data)  # 点击导入预测文件按钮触发事件
        self.btn_start_predict.clicked.connect(self.click_start_predict_data)  # 点击开始预测按钮触发事件
        self.btn_clear_predata.clicked.connect(self.click_clear_predict_data)  # 点击清空预测数据按钮触发事件

        # 进程发送信号
        self.ms.text_print.connect(self.print_info)  # 自定义信号处理函数，当子线程发控制台信息，让print_info来处理
        self.ms.type_return.connect(self.get_center_num)  # 自定义信号处理函数，当子线程发聚类中心个数，让get_center_num来处理
        self.ms.progress_return.connect(self.alter_progressbar)  # 自定义信号处理函数，当子线程发进度完成情况，让alter_progressbar来处理
        self.ms.progress_return2.connect(self.alter_progressbar2)  # 自定义信号处理函数，当子线程发进度完成情况，让alter_progressbar来处理
        # 自定义信号处理函数，当子线程保存一口井的预测图片后，交给add_list_picture来添加左侧item和右侧图片
        self.ms.predict_return.connect(self.add_item_picture)

        # 打开默认显示第0个页，也就是导入训练数据页面
        self.tabWidget.setCurrentIndex(0)

        # 当tabWidget切换时触发（切换到了聚类分析，添加左边item和右边widget空间）
        self.tabWidget.currentChanged.connect(self.add_list_widget)

        # 当左边list改变时,切换右边的stack
        self.leftlist.currentRowChanged.connect(self.display_1)
        self.listWidget.currentRowChanged.connect(self.display_2)

        # 点击菜单栏选项
        self.action_export_scatter.triggered.connect(self.export_scatter)  # 点击菜单栏导出散点图触发
        self.action_export_line.triggered.connect(self.export_line)  # 点击菜单栏导出聚类折线图
        self.action_export_predict_png.triggered.connect(self.export_predict_png)  # 点击菜单栏导出预测后的折线图
        self.action_export_predict_data.triggered.connect(self.export_predict_data)  # 点击菜单栏导出预测数据
        self.action_export_model.triggered.connect(self.export_model)  # 点击菜单栏导出模型
        self.action_export_dict.triggered.connect(self.export_dict)  # 点击菜单栏导出模型
        self.action_exit.triggered.connect(self.app_exit)  # 点击菜单栏退出
        self.action_version.triggered.connect(self.app_version)  # 点击菜单栏版本号

    # 选择训练数据目录按钮触发
    def click_import_train_data(self):
        # 选择训练数据文件夹并将其路径显示在左侧text_train_path中
        directory = QFileDialog.getExistingDirectory(self, "选取文件夹", "C:/Users/13065/Desktop/训练数据")
        if directory != '':  # 如果选择路径不是空
            if len(os.listdir(directory)) != 0:  # 如果选择的文件夹中数据量不是0
                self.text_train_path.setText(directory)

    # 点击开始训练模型按钮触发
    def click_start_train_data(self):
        # 获取训练数据文件夹路径
        train_data_path = self.text_train_path.text()
        if train_data_path == '':  # 如果目录为空，则提示
            QMessageBox.information(self, "提示", "请先选择训练数据路径！")
        else:
            # 如果训练数据和预测数据都清空了则可执行
            if self.exam_is_train_clear():
                self.textBrowser.append('程序运行中，请稍等......')

                # 模型建立总共需要8步（自定义）
                self.progressBar.setRange(0, 6)

                # 训练模型中，按钮禁用第一个页面三个按钮
                self.btn_start_train.setEnabled(False)
                self.btn_import_train.setEnabled(False)
                self.btn_clear_data.setEnabled(False)

                # 训练模型中，tab不可切换，不可切换到2页和3页
                self.tabWidget.setTabEnabled(1, False)
                self.tabWidget.setTabEnabled(2, False)

                # 设置预测天数
                self.pred_size = int(self.spinBox.value())

                # 选择预测天数不可用
                self.spinBox.setEnabled(False)
                # 创建子线程，建立模型，参数是ms和训练文件选择路径
                self.thread = Thread(target=gas_predict.cluster, args=(self.ms, train_data_path, self.pred_size),
                                     kwargs={})
                self.thread.start()
            else:
                QMessageBox.information(self, "提示", "请先清空数据！")

    # 点击清除训练数据按钮触发
    def click_clear_train_data(self):
        # 进度条设置为0
        self.progressBar.setValue(0)

        # 选择路径框清空
        self.text_train_path.clear()
        # 输出框清空
        self.textBrowser.clear()

        # 删除生成的数据
        if os.path.exists('resource/model'):
            shutil.rmtree('resource/model')  # 删除生成的模型
        self.del_file('resource/picture/line')  # 删除散点图和每一类的折线图
        self.del_file('resource/picture/scatter')  # 删除散点图和每一类的折线图
        if os.path.exists('resource/dict'):
            shutil.rmtree('resource/dict')  # 删除聚类字典
        if os.path.exists('resource/临时数据'):
            shutil.rmtree('resource/临时数据')

        # 清空左边list中的item
        self.leftlist.clear()
        # 清空右边的栈中的所有widget
        for stack_widget in self.stack_type_picture_widget:
            self.stack.removeWidget(stack_widget)

        # 右边的栈中的所有widget列表设置为空
        self.stack_type_picture_widget = []

        # 设置聚类数为0
        self.center_num = 0

        # 如果训练的模型数据被清除，那么预测数据也要被清除
        self.click_clear_predict_data()

        # 更改一些可用和不可用
        self.alter_available_clear_train()

    # 选择需要字典文件按钮触发
    def click_btn_import_dict_data(self):
        # 选择文件夹并显示
        directory = QFileDialog.getOpenFileName(self, "选取聚类字典文件", "resource/dict", "字典类型 (*.pkl)")
        if directory[0] != '':  # 如果选择路径不为空
            # 左侧文本框显示路径
            self.text_dict_path.setText(directory[0])

    # 选择需要模型所在的的文件夹按钮触发
    def click_btn_import_model_data(self):
        # 选择文件夹并显示
        directory = QFileDialog.getExistingDirectory(self, "选取模型所在文件夹", "resource/model")
        if directory != '':  # 如果选择路径不为空
            # 获得有多少个预测文件
            file_num = len(os.listdir(directory))
            if file_num == 0:  # 如果文件个数等于0，则提示
                QMessageBox.information(self,
                                        "提示",
                                        "该目录为空，请重新选择预测文件目录!")
            else:
                # 左侧文本框显示路径
                self.text_model_path.setText(directory)

    # 选择需要预测的文件夹按钮触发
    def click_import_predict_data(self):
        # 选择文件夹并显示
        directory = QFileDialog.getExistingDirectory(self, "选取文件夹", "C:/Users/13065/Desktop/测试数据")
        if directory != '':  # 如果选择路径不为空
            # 获得有多少个预测文件
            file_num = len(os.listdir(directory))
            if file_num == 0:  # 如果文件个数等于0，则提示
                QMessageBox.information(self,
                                        "提示",
                                        "该目录为空，请重新选择预测文件目录!")
            else:
                # 总共有多少个预测文件，设置需要预测文件步骤，用来设置进度条
                self.all_predict_data_num = file_num
                # 设置进度条范围
                self.progressBar_2.setRange(0, file_num)
                # 左侧文本框显示路径
                self.text_predict_path.setText(directory)

    # 点击开始预测按钮触发
    def click_start_predict_data(self):
        # 获取测试数据文件夹路径
        predict_data_path = self.text_predict_path.text()
        text_model_path = self.text_model_path.text()
        text_dict_path = self.text_dict_path.text()

        if predict_data_path == '' or text_model_path == '' or text_dict_path == '':
            QMessageBox.information(self, "提示", "请先选择预测模型、聚类字典文件、预测文件路径！")
        else:
            # 检查预测数据是否清空
            if self.exam_is_predict_clear():
                # 训练预测中，按钮禁用：导入预测模型，导入聚类数据，导入预测文件，清除数据
                self.btn_import_predata.setEnabled(False)
                self.btn_start_predict.setEnabled(False)
                self.btn_clear_predata.setEnabled(False)
                self.btn_import_model.setEnabled(False)
                self.btn_import_dict.setEnabled(False)

                # 训练模型中，tab不可切换
                self.tabWidget.setTabEnabled(0, False)
                self.tabWidget.setTabEnabled(1, False)

                # 获取模型所在地址和字典所在地址
                model_path = self.text_model_path.text()
                dict_path = self.text_dict_path.text()
                # 创建子线程，建立模型，参数为ms和预测数据路径
                self.thread = Thread(target=gas_predict.predict,
                                     args=(self.ms, predict_data_path, model_path, dict_path))
                # 调用子线程
                self.thread.start()
            else:
                QMessageBox.information(self, "提示", "请先清空数据！")

    # 清空预测数据
    def click_clear_predict_data(self):

        # 路径框清空
        self.text_model_path.clear()
        self.text_dict_path.clear()
        self.text_predict_path.clear()
        # 进度条设置为0
        self.progressBar_2.setValue(0)

        # 删除生成的预测图片和和卷积数据
        self.del_file('resource/picture/predict')
        if os.path.exists('resource/result'):
            shutil.rmtree('resource/result/')

        # 清空左边list中的item
        self.listWidget.clear()
        # 清空右边的栈
        for stack_widget in self.stack_predict_picture_widget:
            self.stack.removeWidget(stack_widget)
        self.stack_predict_picture_widget = []

        # 所有预测文件的数量
        self.all_predict_data_num = 0

        self.pred_size = 0

        # 更改一些可用和不可用
        self.alter_available_clear_predict()

        # 由于清除右边的stack后，还会显示当前图，因此选用一张空白图作为占位，然后再删除
        blank_space_occupation = QLabel()
        blank_space_occupation_png = QPixmap('resource/picture/blank.png')
        blank_space_occupation.setPixmap(blank_space_occupation_png)
        blank_space_occupation.setAlignment(Qt.AlignCenter)
        blank_space_occupation.setScaledContents(True)
        self.stackedWidget.insertWidget(0, blank_space_occupation)
        self.stackedWidget.setCurrentIndex(0)
        self.stack.removeWidget(blank_space_occupation)

        QMessageBox.information(self, "提示", "数据清除成功！")

    # 将text内容追加到文字显示框中
    def print_info(self, text):
        """
        子线程发送控制台信号后，处理函数
        :param text: 为子线程向主线程发送的信号
        :return:
        """
        # 将text内容追加到文字显示框中
        self.textBrowser.append(str(text))
        # 自动向下滚动
        self.textBrowser.ensureCursorVisible()

    # 获取子线程传来的聚类数目
    def get_center_num(self, num):
        """
        获取子线程传来的聚类数目
        :param num: 子线程传来的聚类数量
        :return:
        """
        self.center_num = num
        self.progressBar.setRange(0, 5 + num)

    # 修改进度条值
    def alter_progressbar(self, num):
        """
        获取子线程发来的进度，修改进度条1
        :param num:
        :return:
        """
        # 修改进度条值
        self.progressBar.setValue(num)
        # 如果8个进度全部执行完，则清除数据按钮可用，另外两个tab也可用
        if num == 5 + self.center_num:
            self.btn_clear_data.setEnabled(True)

            # 模型训练完成，tab可切换状态
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setTabEnabled(2, True)

            # 导出散点图和聚类折线图，聚类字典，模型可用
            self.action_export_scatter.setEnabled(True)
            self.action_export_line.setEnabled(True)
            self.action_export_model.setEnabled(True)
            self.action_export_dict.setEnabled(True)

    # 获取子线程发来的进度，修改进度2
    def alter_progressbar2(self, num):
        """
        获取子线程发来的进度，修改进度2
        :param num:
        :return:
        """
        self.progressBar_2.setValue(num + 1)
        # 如果模型建立完成，则恢复清除按钮
        if num + 1 == self.all_predict_data_num:
            self.btn_clear_predata.setEnabled(True)

            # 模型训练完成，tab可切换状态
            self.tabWidget.setTabEnabled(0, True)
            self.tabWidget.setTabEnabled(1, True)

            # 导出预测折线图和结果可用
            self.action_export_predict_png.setEnabled(True)
            self.action_export_predict_data.setEnabled(True)

    # 子线程预测完一个数据，就把序号和文件名发送给主线程添加list和画图
    def add_item_picture(self, text):
        """
        子线程预测完一个数据，就把序号和文件名发送给主线程添加list和画图
        :param text: 格式：序号/文件名
        :return:
        """
        num = text.split('/')[0]  # 获取序号
        name = text.split('/')[1]  # 获取文件名

        # 左侧在num位置添加name的item
        self.listWidget.insertItem(int(num), name)

        picture_predict_png = QPixmap('resource/picture/predict/' + name + '.png')
        picture_predict = QLabel()
        picture_predict.setPixmap(picture_predict_png)
        picture_predict.setAlignment(Qt.AlignCenter)
        # 图片自适应
        picture_predict.setScaledContents(True)
        # 将图片widget空间添加到stack_predict_picture_widget，用来清空按钮依次清空
        self.stack_predict_picture_widget.append(picture_predict)
        # 添加widget空间到右侧stack中
        self.stackedWidget.insertWidget(int(num), picture_predict)
        self.stackedWidget.setCurrentIndex(int(num))

    # 添加聚类中心散点图和聚类后每个类的折线产气图
    def add_list_widget(self, x):
        """
        添加聚类中心散点图和聚类后每个类的折线产气图
        :param x: 当前在第几页
        :return:
        """
        # 如果选择第二个框并且聚类中心发生了改变，不是0，并且当前list数量不等于聚类中心+lsit初始值个，那么创建list
        # 下标从0开始
        if x == 1 and self.center_num != 0 and self.leftlist.count() != (self.center_num + self.leftlist_num):
            # listwidget添加item
            self.leftlist.insertItem(0, '聚类散点图')
            # 获取Qlabel对象，用来装图片
            picture_scatter = QLabel()
            # 获取图片对象
            picture_scatter_png = QPixmap('resource/picture/scatter/scatter.png')
            # 图片对象装入Qlabel
            picture_scatter.setPixmap(picture_scatter_png)
            # 设置居中显示
            picture_scatter.setAlignment(Qt.AlignCenter)
            # 图片自适应
            picture_scatter.setScaledContents(True)
            # 将qlabel装入列表中，后续删除按钮将依次删除
            self.stack_type_picture_widget.append(picture_scatter)
            # 将图片放在右侧stackwidget中第一个位置
            self.stack.insertWidget(0, picture_scatter)

            # 依次添加聚类过后，每个类型井产气量图
            for i in range(self.center_num):
                # 添加左侧list项目
                self.leftlist.insertItem(i + 1, f'聚类{i + 1}折线图')
                picture_well_png = QPixmap(f'resource/picture/line/type{i + 1}.png')
                picture_well = QLabel()
                picture_well.setPixmap(picture_well_png)
                picture_well.setAlignment(Qt.AlignCenter)
                # 图片自适应
                picture_well.setScaledContents(True)
                # 将qlabel装入列表中，后续删除按钮将依次删除
                self.stack_type_picture_widget.append(picture_well)
                self.stack.insertWidget(i + 1, picture_well)

    # 设置当前可见的选项卡的索引
    def display_1(self, i):
        """
        设置当前可见的选项卡的索引
        :param i: 左边list切换到了第几个
        :return:
        """
        if i >= 0:
            self.stack.setCurrentIndex(i)

    # 设置当前可见的选项卡的索引
    def display_2(self, i):
        """
        设置当前可见的选项卡的索引
        :param i: 左边list切换到了第几个
        :return:
        """
        if i >= 0:
            self.stackedWidget.setCurrentIndex(i)

    # 保存散点图
    def export_scatter(self):
        """
        保存散点图
        :return:
        """
        # 获取保存路径
        filePath = QFileDialog.getExistingDirectory(self, "选择存储路径")
        if filePath != '':
            # 保存到所选路径
            shutil.copyfile('resource/picture/scatter/scatter.png', filePath + '/' + 'scatter.png')
            QMessageBox.information(self,
                                    '导出成功',
                                    "文件位于：" + filePath)

    # 保存聚类折线图
    def export_line(self):
        """
        保存聚类折线图
        :return:
        """
        # 获取保存路径
        filePath = QFileDialog.getExistingDirectory(self, "选择存储路径")
        if filePath != '':
            # 保存到所选路径
            files = os.listdir('resource/picture/line')
            for file in files:
                shutil.copyfile('resource/picture/line/' + file, filePath + '/' + file)
            QMessageBox.information(self,
                                    '导出成功',
                                    "文件位于：" + filePath)

    # 保存预测过后的折线图
    def export_predict_png(self):
        """
        保存预测过后的折线图
        :return:
        """
        # 获取保存路径
        filePath = QFileDialog.getExistingDirectory(self, "选择存储路径")
        if filePath != '':
            # 保存到所选路径
            files = os.listdir('resource/picture/predict')
            for file in files:
                shutil.copyfile('resource/picture/predict/' + file, filePath + '/' + file)
            QMessageBox.information(self,
                                    '导出成功',
                                    "文件位于：" + filePath)

    # 导出预测数据
    def export_predict_data(self):
        """
        导出预测数据
        :return:
        """
        # 获取保存路径
        filePath = QFileDialog.getExistingDirectory(self, "选择存储路径")
        # 保存到所选路径
        if filePath != '':
            files = os.listdir('resource/result')
            for file in files:
                shutil.copyfile('resource/result/' + file, filePath + '/' + file)
            QMessageBox.information(self,
                                    '导出成功',
                                    "文件位于：" + filePath)

    # 导出模型
    def export_model(self):
        """
        导出模型
        :return:
        """
        # 获取保存路径
        filePath = QFileDialog.getExistingDirectory(self, "选择存储路径")
        if filePath != '':
            # 保存到所选路径
            files = os.listdir('resource/model')
            for file in files:
                shutil.copytree('resource/model/' + file, filePath + '/' + file)
            QMessageBox.information(self,
                                    '导出成功',
                                    "文件位于：" + filePath)

    # 导出聚类字典数据
    def export_dict(self):
        """
        导出预测数据
        :return:
        """
        # 获取保存路径
        filePath = QFileDialog.getExistingDirectory(self, "选择存储路径")
        if filePath != '':
            # 保存到所选路径
            files = os.listdir('resource/dict')
            for file in files:
                shutil.copyfile('resource/dict/' + file, filePath + '/' + file)
            QMessageBox.information(self,
                                    '导出成功',
                                    "文件位于：" + filePath)

    # 退出主窗口进入登录窗口
    def app_exit(self):
        """
        退出主窗口进入登录窗口
        :return:
        """
        self.close()
        login.show()

    # 点击菜单版本号显示版本号
    def app_version(self):
        """
        点击菜单版本号显示版本号
        :return:
        """
        QMessageBox.information(self,
                                "版本号",
                                "Version1.0")

    # 删除某路径下的所有文件
    def del_file(self, filepath):
        """
        删除某一目录下的所有文件或文件夹
        :param filepath: 路径
        :return:
        """
        del_list = os.listdir(filepath)
        for f in del_list:
            file_path = os.path.join(filepath, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    # 当点击清除训练数据按钮修改一些可用和不可用
    def alter_available_clear_train(self):
        """
        当点击清除训练数据按钮修改一些可用和不可用
        :return:
        """
        # 那么聚类分析
        self.tabWidget.setTabEnabled(1, False)

        # 导入训练数据按钮可用，开始训练按钮可用
        self.btn_import_train.setEnabled(True)
        self.btn_start_train.setEnabled(True)

        # 导入预测数据按钮可用，开始预测按钮可用
        self.btn_import_predata.setEnabled(True)
        self.btn_start_predict.setEnabled(True)

        # 导出皆不可用
        self.action_export_scatter.setEnabled(False)
        self.action_export_line.setEnabled(False)
        self.action_export_predict_png.setEnabled(False)
        self.action_export_model.setEnabled(False)
        self.action_export_dict.setEnabled(False)

        # 选择预测天数可用
        self.spinBox.setEnabled(True)

    # 当点击清除预测数据按钮，可用和不可用更改
    def alter_available_clear_predict(self):
        """
        当点击清除预测数据按钮，可用和不可用更改
        :return:
        """
        # 导入预测数据按钮可用，开始预测按钮可用，导入预测模型可用，导入聚类数据可用
        self.btn_import_predata.setEnabled(True)
        self.btn_start_predict.setEnabled(True)
        self.btn_import_model.setEnabled(True)
        self.btn_import_dict.setEnabled(True)

        # 导出预测图和结果不可用
        self.action_export_predict_png.setEnabled(False)
        self.action_export_predict_data.setEnabled(False)

    # 检测训练数据和预测数据是否清空
    def exam_is_train_clear(self):
        """
        检测训练数据和预测数据是否清空asdasd
        :return:
        """
        model_num = 0
        dict_num = 0
        if os.path.exists('resource/model'):
            model_num = len(os.listdir('resource/model'))  # 模型文件数量
        line_num = len(os.listdir('resource/picture/line'))  # 聚类折线图文件数量
        scatter_num = len(os.listdir('resource/picture/scatter'))  # 散点图数量
        if os.path.exists('resource/model'):
            dict_num = len(os.listdir('resource/dict'))  # 字典数量

        # 如果都为0，且预测数据也为0则返回真
        if model_num == 0 and line_num == 0 and scatter_num == 0 and dict_num == 0 and self.exam_is_predict_clear():
            return True
        return False

    # 检测预测数据是否清空
    def exam_is_predict_clear(self):
        """
        检测预测数据是否清空
        :return:
        """
        predict_export_data_num = 0
        predict_picture_num = len(os.listdir('resource/picture/predict'))  # 预测折线图文件数量
        if os.path.exists('resource/result'):
            predict_export_data_num = len(os.listdir('resource/result'))  # 卷积后的测试数据文件数量
        # 如果文件都为空则返回真
        if predict_picture_num == 0 and predict_export_data_num == 0:
            return True
        return False


if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon('resource/picture/燃气.png'))
    login = Login()
    login.show()
    register = Register()
    main = Main()
    staff = Staff()
    app.exec_()
