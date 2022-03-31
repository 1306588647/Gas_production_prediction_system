import shutil

import numpy as np
import pandas as pd

import os

from resource import prednext_TCN

from resource import test_try_2
from resource import dconv

path_all = ""
dict_ = ""




def Remove_classification(path, num):
    shutil.rmtree(path)
    # for i in range(num):
    #     dir_name = 'TCN_model' + '第' + i + '类'
    #     shutil.rmtree(dir_name)


def main(ms,pred_size):
    path = 'resource/划分数据/聚类中心'
    files = os.listdir(path)

    for i in range(len(files)):
        model_i = files[i]  # 模型i的名字如：第0类
        files_i_path = path + '\\' + model_i
        files_i = os.listdir(files_i_path)  # 得到第i类下的训练数据
        # 卷
        dconv_Train = dconv.main(files_i_path + '\\' + files_i[0], path + '\\' + files_i[0])
        prednext_TCN.train(dconv_Train, model_i,pred_size)  # 训练模型，并保存模型
        os.remove(dconv_Train)  # 删除卷积后的文件

        # 发送到主线程显示在框框中
        ms.text_print.emit(f'第{i + 1}类模型建立完成')
        # 设置进度条完成进度
        ms.progress_return.emit(6+i)


def cluster(ms, train_data_path,pred_size):
    """
    对井进行聚类，对每一类训练一个tcn模型
    :return:
    """
    # 聚类中心地址，返回字典
    global path_all, dict_
    path_all, dict_ = test_try_2.main(ms, train_data_path)

    ms.text_print.emit('模型建立中，该过程耗时较长，请耐心等待......')
    # 训练三个模型
    main(ms,pred_size)
    ms.text_print.emit('模型建立完成！')
    ms.text_print.emit('模型位于：resource/model')


def predict(ms, predict_data_path,pred_size):
    """
    对新井进行预测
    :return:
    """
    # 对新井进行分类 + 预测：

    # 对新井进行分类 + 预测：
    path = predict_data_path
    files = os.listdir(path)
    test_time = 60  # 六十天的数据用于测试

    RMSE = 0
    MAPE = 0
    for i in range(len(files)):
        # 读取数据
        data_i = pd.read_excel(path + '\\' + files[i])
        # 分类
        X = np.zeros((1, 2))
        data = data_i.iloc[:, 5].values.reshape(-1, 1)
        data = data[::-1]
        data = data[0:228]
        X[0, 0] = test_try_2.Q_b(data)  # 斜率
        X[0, 1] = test_try_2.Absolut1(data)  # 波动大小
        # X[0, 0] = -0.00206
        # X[0, 1] = 2.35
        lei = test_try_2.Classfication_max_likelihood_2(X, dict_, 3)
        print('应该属于:%d类' % (lei))
        # break
        # 导入模型预测
        model_name = 'resource/model/TCN_model第' + str(lei) + '类'
        dconv_test_path = 'resource/划分数据/卷积后测试数据/' + files[i]  # 卷积后文件的位置
        dconv_test = dconv.main(path + '/' + files[i], dconv_test_path)

        # 预测+正确率
        tcn_rmse, tcn_mape = prednext_TCN.test(dconv_test, model_name, str(files[i]).split('.')[0], lei, X[0, 0],
                                               X[0, 1], ms, i,pred_size)
        os.remove(dconv_test)  # 删除卷积后的表
        RMSE = RMSE + tcn_rmse
        MAPE = MAPE + tcn_mape
    path_classification = 'resource/划分数据/训练数据'
    # Remove_classification(path_classification, len(dict_))  #删除每个类别
    print('RMSE:', RMSE / len(files))
    print('MAPE:', MAPE / len(files))


# if __name__ == '__main__':
#
#     #聚类，返回字典
#     path_all, dict_ = test_try_2.main()
#
#     #训练三个模型
#     main()
#
#     #对新井进行分类 + 预测：
#     path = '划分数据\\测试数据'
#     files = os.listdir(path)
#     test_time = 60  #六十天的数据用于测试
#
#     RMSE = 0
#     MAPE = 0
#     for i in range(len(files)):
#         #读取数据
#         data_i = pd.read_excel(path + '\\' + files[i])
#         #分类
#         X = np.zeros((1,2))
#         data = data_i.iloc[:, 5].values.reshape(-1, 1)
#         data = data[::-1]
#         data = data[0:228]
#         X[0, 0] = test_try_2.Q_b(data)  #斜率
#         X[0, 1] = test_try_2.Absolut1(data) #波动大小
#         # X[0, 0] = -0.00206
#         # X[0, 1] = 2.35
#         lei = test_try_2.Classfication_max_likelihood_2(X, dict_, 3)
#         print('应该属于:%d类'%(lei))
#         # break
#         #导入模型预测
#         model_name = 'TCN_model第' + str(lei) + '类'
#         dconv_test_path = '划分数据\\卷积后测试数据\\' + files[i]   #卷积后文件的位置
#         dconv_test = dconv.main(path + '\\' + files[i], dconv_test_path)
#
#         #预测+正确率
#         tcn_rmse, tcn_mape = def_TCN.test(dconv_test, model_name, str(files[i]).split('.')[0], lei, X[0, 0], X[0, 1])
#         os.remove(dconv_test)  #删除卷积后的表
#         RMSE = RMSE + tcn_rmse
#         MAPE = MAPE + tcn_mape
#     path_classification = '划分数据\\训练数据'
#     # Remove_classification(path_classification, len(dict_))  #删除每个类别
#     print('RMSE:', RMSE/len(files))
#     print('MAPE:', MAPE/len(files))
#     plt.show()
#
