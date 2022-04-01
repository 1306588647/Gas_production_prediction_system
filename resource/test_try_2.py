import numpy as np
import pandas as pd
import os
from sklearn.cluster import AffinityPropagation  # 无参数聚类
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import math
from scipy.linalg import sqrtm  # 用于矩阵开平方
import matplotlib.pyplot as plt

# 解决中文问题

color = ['k', 'grey', 'r', 'coral', 'saddlebrown', 'bisque', 'darkgoldenrod', 'khaki', 'lawngreen', 'b', 'm', 'pink']

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

scaler = MinMaxScaler(feature_range=(0, 1))
scaler_stand = StandardScaler()
# 标准化
zscore = StandardScaler()


def Var(data, u):
    m, n = np.shape(data)
    # print(data, u)
    u = np.mat(u)
    u = u.T  # 变成一列
    num = np.zeros((n, n))  # 返回的是n*n 的矩阵
    for i in range(m):
        data_i = data[i, :]
        c = np.mat(data_i)
        a = c.T - u
        b = a.T
        num = num + np.dot(a, b)
        # print('num:', num)
        # print(num)
    return np.mat(num / m)


def fun_u_E(data):  # 求均值和协方差，data是m*3
    u = np.mean(data, axis=0)  # 返回1*n的矩阵
    E = Var(data, u)
    return u, E


def Set_max_likelihood(labes, num, num_N, Data):
    # dict_ = Set_max_likelihood(labels, files_name_all, len(cluster_centers), n, data_oragin)
    # n是维度
    '''

    :param labes: 标签（没有顺序）
    :param files: 标签对应的井
    :param num: 多少类
    :return: 一个字典，对应每一类的u，E 参数
    '''
    classifacation_machin = {}
    test_data = np.zeros((num * 4, num_N))
    index_test_data = np.zeros((num * 4, 1))  # 每一类提取四个出来
    test_index = 0
    for i in range(num):
        index = np.where(labes == i)[0]
        # print('index:', index)
        # print(index[0])
        m = len(index)  # 属于该口井的数量
        # print('属于%d类的数量有：%d' %(i, m))
        n = num_N
        data = np.zeros((m - 4, n))
        for j in range(m):
            if j >= m - 4:
                test_data[i * 4 + test_index, :] = Data[index[j], :]
                index_test_data[i * 4 + test_index, 0] = index[j]
                test_index = test_index + 1
            else:
                data[j, :] = Data[index[j], :]  # 建立这一类的矩阵
        # print('这是', data)
        test_index = 0
        u, E = fun_u_E(data)
        classifacation_machin[i] = u, E
    return classifacation_machin, test_data, index_test_data


def Get_p_values(X, u, E, D, num):
    '''

    :param X: 需要分类的对象
    :param u: 均值
    :param E: 方差
    :param D: 属性的列数
    :return: 概率值
    '''
    E = np.array(E)
    # print('E', np.linalg.det(E))
    E_inv = np.linalg.inv(E)  # 协方差的逆矩阵
    # print('举证的你举证',np.linalg.det(np.dot(E, E_inv)))
    a = 1 / math.pow(2 * np.pi, D / 2)
    b = 1 / np.sqrt(np.abs(np.linalg.det(E)))
    X = np.mat(X)  # 行向量
    u = np.mat(u)  # 行向量
    # print(X, u)
    # print('x - u', X - u)
    # print(np.dot((X-u), E_inv))
    u_E = np.dot(np.dot((X - u), E_inv), np.mat(X.T - u.T))
    # print(u_E)
    d = -1 / 2 * u_E
    # print(d)
    c = math.exp(d)
    print(d)
    return np.round(a * b * c, 20), d


def Classfication_max_likelihood_2(X, dict, num):
    '''
    分类器
    :param X: 需要分类的对象
    :param dict: 是一个字典，键是第几类，键值是u，E（方差)
    :param num: 类数
    :return:
    '''
    D = len(X)  # 获取维度数
    # print('D', D)
    p = np.zeros((num, 2))
    num_p0 = 0
    for i in range(num):
        u = dict[i][0]
        E = dict[i][1]
        p_value, p_index = Get_p_values(X, u, E, D, i)
        print(i, p_value)
        # print('属于第%d类的概率密度为%f'%(i, p_value))
        p[i, 0] = p_value
        p[i, 1] = p_index
        if p_value == 0.0:
            num_p0 = num_p0 + 1
    max_index = np.argmax(p[:, 0])
    if np.argmax(p[:, 0]) == np.argmin(p[:, 0]):
        print(11111)
        return np.argmax(p[:, 1])
    else:
        return max_index


def Classfication_max_likelihood(X, dict, num, num_X):
    '''
    分类器
    :param X: 需要分类的对象
    :param dict: 是一个字典，键是第几类，键值是u，E（方差)
    :param num: 类数
    :return:
    '''
    D = len(X)  # 获取维度数
    # print('D', D)
    p = np.zeros((num, 2))
    num_p0 = 0
    for i in range(num):
        u = dict[i][0]
        E = dict[i][1]
        p_value, p_index = Get_p_values(X, u, E, D, i)
        print(i, p_value)
        # print('属于第%d类的概率密度为%f'%(i, p_value))
        p[i, 0] = p_value
        p[i, 1] = p_index
        if p_value == 0.0:
            num_p0 = num_p0 + 1
    max_index = np.argmax(p[:, 0])
    # print('应该属于第%d类：'%max_index)
    # print(max_index, num_X)
    if max_index == num_X:
        # print('Ture')
        return 1
    else:
        # print('Fales')
        return 0


def Max_min(a, b):
    if a < b:
        return (b - a) / b
    else:
        return -(a - b) / a


def Absolut(data):
    m = len(data)
    num = 0
    for i in range(m - 1):
        num1 = Max_min(data[i], data[i + 1])
        num = num + num1
    return num


def Absolut1(data):
    m = len(data)
    num = 0
    for i in range(m - 1):
        num1 = np.abs(Max_min(data[i], data[i + 1]))
        num = num + num1
    return num


def Q_b(data):
    # https://zhidao.baidu.com/question/491732823686971972.html
    y = data
    m = len(y)
    x = range(1, m + 1)
    xy = 0
    xx = 0
    for i in range(m):
        xy = xy + x[i] * y[i]
        xx = xx + x[i] * x[i]
    b = (xy - m * np.mean(y) * np.mean(x)) / (xx - m * np.mean(x) * np.mean(x))
    return b / np.mean(y)


def Count_labels_num(labels, num):
    datingLabels = np.array(labels)
    for i in range(num):
        num_i = np.where(datingLabels == i)[0][:]
        print('第%d有%d个' % (i, len(num_i)), num_i)


def midir(path):
    path = path.strip()  # 去除首位空格
    path = path.rstrip('\\')  # 去除尾部\符号

    # 判断路径是否存在
    # 存在  True
    # 不存在 Fals
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        os.makedirs(path)  # 创建目录
        print(path + '创建成功')
        return True
    else:
        print(path + '已经存在')
        return False


def Set_trainortest(i_name, path_i,train_path):
    path = train_path+'/'
    df = pd.read_excel(path + i_name + '.xlsx')
    m, n = np.shape(df)
    data = df.iloc[m - 228:, :]
    # print(data)
    data.to_excel(path_i + '\\' + i_name + '.xlsx', index=False)


def Set_xlsx(lei, center_lei, all_name, ms,train_path):
    path_all = 'resource/临时数据/聚类中心'
    midir(path_all)
    for i in range(len(lei)):
        path_i = path_all + '\\' + '第' + str(i) + '类'
        midir(path_i)  # 建立文件
        label_i_name = all_name[center_lei[i]]  # 获得名字
        Set_trainortest(label_i_name, path_i,train_path)

    # 发送信号给主线程
    ms.text_print.emit('已建立聚类中心文件！')
    ms.text_print.emit('文件位于：' + '临时数据/聚类中心')
    return path_all


def Q_A_k(data):
    y_mean = np.mean(data)
    m = len(data)
    count = 0
    for i in range(m - 1):
        count = data[i + 1] - data[i] + count
    return count / y_mean


# 画散点图
def draw(labels, Data, files, path, ms):
    """

    :param labels: 每个井属于0,1,2的标签，如：如：[0 2 2 0 0 2 0 0 0 0 0 2 2 1 0 1 0 0 2 2 0 2 1 1 0 1 1 2 1 1 1 1 0 1 1 1 1
    #  0 2 1 1 1 0 1 1 1 2 0 1 1 0 0 2 1 0 2 2 2 1 0 2]
    :param Data: 所有井的两个参数，斜率和波动率
    :param files: 所有井的文件名字
    :return:
    """
    files = np.array(files)
    # 总共有几类
    type_num = len(set(labels))
    # 将labels转换成numpy对象
    array_list = np.array(labels)

    list_index = []  # 里面装每一类中,井对应的序号
    list_files = []  # 里面装每一类中，井的文件名称
    for i in range(type_num):
        index = np.where(array_list == i)  # 返回label类型为i的井序列标号
        list_index.append(index)

        index_name = files[index]  # 返回每一类中的文件名字
        list_files.append(index_name)

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.figsize'] = (6, 5)

    # 画散点图
    for i in range(type_num):
        data_type_i = Data[list_index[i]]
        plt.scatter(data_type_i[:, 0], data_type_i[:, 1], label=f'类别{i + 1}')
    plt.legend()
    plt.savefig(r'resource/picture/scatter/scatter.png', bbox_inches='tight')
    # 重新画一张新的
    plt.clf()
    # 发送信号给主进程进度条完成度,完成第2步
    ms.progress_return.emit(2)
    ms.text_print.emit('聚类散点图已生成！')
    ms.text_print.emit('散点图位于：resource/picture/scatter')

    for i in range(type_num):
        for j in range(len(list_files[i])):
            df = pd.read_excel(path + '\\' + list_files[i][j])

            data = df.iloc[:, 5].values.reshape(-1, 1)  # 获取日产气量数据，并转换成列向量
            data = data[::-1]  # 倒置
            data = data[0:228]  # 取228个数据
            y = data
            x = np.arange(0, 228)
            plt.plot(x, y, label=list_files[i][j].split('.')[0])
        # 将标签放在右下
        plt.legend(bbox_to_anchor=(1.01, 0), loc=3, borderaxespad=0, fontsize=8)
        plt.xlabel("天数")
        plt.ylabel("产气量")
        # 调整标签显示不全
        # plt.subplots_adjust(right=0.75)
        plt.savefig(f'resource/picture/line/type{i + 1}.png', bbox_inches='tight')
        # 重新画一张新的
        plt.clf()

        # 发送信号给主进程进度条完成度,完成第3,4,5步
        ms.progress_return.emit(3 + i)
        ms.text_print.emit(f'第{i + 1}类产气量折线图已生成！')
    ms.text_print.emit('折线图位于：resource/picture/line')


def fun1(path, ms):
    '''

    :param path:进行聚类的数据位置
    :return:
    '''

    files = os.listdir(path)
    Data = np.zeros((len(files), 2))  # 每个表两个参数
    files_name_all = []  # 保存所有表的名字
    for i in range(len(files)):
        files_name_all.append(str(files[i]).split('.')[0])
        df = pd.read_excel(path + '\\' + files[i])
        data = df.iloc[:, 5].values.reshape(-1, 1)
        data = data[::-1]  # 倒置
        data = data[0:228]  # 取228个数据
        Data[i, 0] = Q_b(data)  # 求斜率
        Data[i, 1] = Absolut1(data)  # 波动大小

    end_data = zscore.fit_transform(Data)  # 标准化

    # 发送信号给主线程
    ms.text_print.emit('聚类中......')

    # 无参数聚类
    # print(Data)
    af = AffinityPropagation(damping=0.5, max_iter=200, convergence_iter=50, \
                             copy=True, preference=-20, affinity='euclidean', verbose=False).fit(end_data)

    # 发送聚类中心个数
    ms.type_return.emit(len(af.cluster_centers_))
    # 发送信号给主线程
    ms.text_print.emit('聚类已完成！')
    # 发送信号给主进程进度条完成度,完成第一步
    ms.progress_return.emit(1)


    cluster_centers = af.cluster_centers_
    labels = af.labels_

    # 画图
    draw(labels, Data, files, path, ms)

    print(cluster_centers, labels)
    print(len(cluster_centers))
    for z in range(len(cluster_centers)):
        print('第%d类聚类中心井为：%s:', z, files[af.cluster_centers_indices_[z]])

    # 发送信号给主线程
    ms.text_print.emit('建立极大似然函数中......')

    # 建立字典，键值对应u，E
    dict_, test_data, index_test = Set_max_likelihood(labels, len(cluster_centers), 2, Data)
    # 发送信号给主线程
    ms.text_print.emit('测试极大似然函数中......')
    # 对新井分类
    num_sure = 0
    for i in range(len(test_data)):
        X = test_data[i]
        d = Classfication_max_likelihood(X, dict_, len(cluster_centers), labels[index_test[i].astype('int64')])
        num_sure = num_sure + d

    num_sure = float(num_sure) / len(test_data)
    # 发送信号给主线程
    ms.text_print.emit('聚类测试数据正确率为：%.2f%%' % (num_sure * 100))
    print('正确率为：%f' % (float(num_sure / len(test_data))))  # 分类准确率

    # 建立表格
    return Set_xlsx(cluster_centers, af.cluster_centers_indices_, files_name_all, ms,path), dict_


def main(ms, train_data_path):
    path = train_data_path

    return fun1(path, ms)


if __name__ == '__main__':
    # 聚类
    name = main()
