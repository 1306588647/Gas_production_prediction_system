# 注册界面
import hashlib

import pymysql
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.uic import loadUi


class Register(QWidget):
    def __init__(self,login):
        super(Register, self).__init__()
        # 加载ui界面
        loadUi('resource/ui/register.ui', self)

        self.login = login

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
        self.login.show()
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