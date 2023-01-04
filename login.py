# 登录界面
import hashlib

import pymysql
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QPixmap, QRegExpValidator, QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt5.uic import loadUi

from register import Register
from staff import Staff
from win import Main


class Login(QWidget):
    def __init__(self):
        super(Login, self).__init__()

        # 加载ui界面
        loadUi('resource/ui/login.ui', self)
        # self.setupUi(self) # 设置写好的ui转py

        self.register = Register(self)
        self.main = Main(self)
        self.staff = Staff(self)

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
                self.staff.show()
                self.hide()
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
                        self.main.show()
                        self.close()

    # 注册事件触发，进入注册界面
    def click_register(self):
        # 展示注册窗口
        self.register.show()
        # 隐藏登录窗口
        self.hide()

if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon('resource/picture/燃气.png'))
    login = Login()
    login.show()

    # main = Main()
    # main.show()

    app.exec_()