import os

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from resource.tcn.tcn import TCN

TIME_STEPS = 30  # 用几天来预测

PRED_SIZE = 0  # 预测天数
BATCH_SIZE = 64

INPUT_SIZE = 50
EPOCH = 200
DILA = [1, 2, 4, 8, 16, 32]
FILTER_NUMS = 256
KERNEL_SIZE = 2


def alter_global_data(pred_size):
    global PRED_SIZE
    PRED_SIZE = pred_size


class KerasMultiTCN(object):

    def __init__(self, filter_nums, kernel_size, time_steps, input_size, pred_size, batch_size, dilations):
        self.filter_nums = filter_nums
        self.kernel_size = kernel_size
        self.time_steps = time_steps
        self.input_size = input_size
        self.pred_size = pred_size
        self.batch_size = batch_size
        self.dilations = dilations

    def model(self):
        self.model = Sequential()
        self.model.add(TCN(nb_filters=self.filter_nums, kernel_size=self.kernel_size,
                           activation='relu',
                           input_shape=(self.time_steps, self.input_size),
                           dilations=self.dilations))
        self.model.add(Dropout(0.25))
        self.model.add(Dense(self.pred_size))
        self.model.compile(metrics=['mae'], loss='mean_squared_error', optimizer='adam')
        self.model.summary()

    def train(self, x_train, y_train, epochs, filename, pred_size):
        history = self.model.fit(x_train, y_train, epochs=epochs, batch_size=self.batch_size).history
        self.model.save("resource/model/" + str(pred_size) + "_TCN_model" + filename)

        return history


def get_train_data(path):
    df = pd.read_excel(path)
    return df


def get_test_data(path):
    df = pd.read_excel(path)
    return df


def MAPE(pre, ori):
    return np.mean(np.abs((pre - ori) / ori))


def RMSE(pre, ori):
    return np.sqrt(((pre - ori) ** 2).mean())


# 设置数据集
def set_datas(df, train=True, sc=None):
    if train:
        sc = MinMaxScaler(feature_range=(0, 1))
        training_set = sc.fit_transform(df)
    else:
        # 测试集，也需要使用原Scaler归一化
        if sc == None:
            sc = MinMaxScaler(feature_range=(0, 1))
            training_set = sc.fit_transform(df)
        else:
            training_set = sc.transform(df)

    # 按时序长度构造数据集
    def get_train_batch(trainX_data, trainY_data):
        train_len = len(trainX_data) - TIME_STEPS - PRED_SIZE
        X = np.zeros((train_len, TIME_STEPS, INPUT_SIZE))
        Y = np.zeros((train_len, PRED_SIZE))
        trainrows = range(0, train_len)
        for i, row in enumerate(trainrows):
            X[i, :, :] = trainX_data[row: row + TIME_STEPS]
            Y[i] = trainY_data[row + TIME_STEPS: row + TIME_STEPS + PRED_SIZE]
        return X, Y

    def get_test_batch(testX_data, testY_data):
        test_len = (testX_data.shape[0] - TIME_STEPS) // PRED_SIZE * PRED_SIZE
        X = np.zeros((test_len // PRED_SIZE + 1, TIME_STEPS, INPUT_SIZE))
        Y = np.zeros((test_len // PRED_SIZE + 1, PRED_SIZE))
        testrows = range(0, test_len + PRED_SIZE, PRED_SIZE)
        for i, row in enumerate(testrows):
            X[i, :, :] = testX_data[row: row + TIME_STEPS]

        return X, Y

    # 返回训练集
    if train:
        X, Y = get_train_batch(training_set, training_set[:, 0])
    # 返回测试集
    else:
        X, Y = get_test_batch(training_set, training_set[:, 0])
    return X, Y, training_set, sc, df


def train(path, model_name, pred_size):
    alter_global_data(pred_size)
    df = get_train_data(path)
    X, Y, z, sc, df = set_datas(df, True)
    model = KerasMultiTCN(FILTER_NUMS, KERNEL_SIZE, TIME_STEPS, INPUT_SIZE, PRED_SIZE, BATCH_SIZE, DILA)
    model.model()
    model.train(X, Y, EPOCH, model_name, pred_size)


# 反归一化的时候要用原始test样本数量（因为时间步的存在，所以一定有最开始时间步的样本没有预测结果）（预测结果都是从时间步之后开始）
def get_versePred(y, z, path):
    df = get_test_data(path)
    X, Y, training_set, sc, df = set_datas(df, False)
    Y_len = Y.shape[0] * Y.shape[1]
    coushu = df.shape[0] - Y_len
    tail = Y_len + TIME_STEPS - df.shape[0]
    testY_data = z[:, 0]
    coushu_pred = np.concatenate((testY_data[:coushu], y), axis=0)
    coushu_pred_2 = np.expand_dims(coushu_pred, axis=1)
    yy = np.concatenate((coushu_pred_2, z[:, 1:]), axis=1)
    inversePred = sc.inverse_transform(yy)
    return inversePred, coushu, tail


def test(Test_file, model_name, file_name, LEI, feature_1, feature_2, ms, i, pred_size):
    alter_global_data(pred_size)
    df = get_test_data(Test_file)
    X, Y, z, sc, df = set_datas(df, False)
    model = load_model(model_name)
    pred = model.predict(X)
    y = pred.flatten('F')
    inversePred, coushu, tail = get_versePred(y, z, Test_file)
    # 反归一化之后将时间步的预测结果去掉，才是最后的预测，分别与原始未处理的油压、经过归一化处理的油压 进行对比
    # 预测y
    Y_prenext = inversePred[coushu:, 0]
    PredY = inversePred[coushu:-tail, 0]
    # #原始未处理过的y

    RealY = df.iloc[TIME_STEPS:, 0].values
    # 输出最后一条样本
    last_rel = RealY[-TIME_STEPS:]
    # last_pre = Y_prenext[-(PRED_SIZE + TIME_STEPS):]
    last_pre = Y_prenext[-(PRED_SIZE + TIME_STEPS):]
    pre_ = Y_prenext[-(PRED_SIZE):]

    # 计算三者之间的误差
    PR_lossMAPE = MAPE(PredY, RealY)
    PR_lossRMSE = RMSE(PredY, RealY)

    # ##输出到csv文件
    # output = pd.DataFrame()
    # output['prediction'] = PredY
    # output['real'] = RealY
    # output.to_csv('def_TCN_pre_rel')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.figsize'] = (8.5, 4)
    plt.title(file_name + ' ' + '类别:' + str(LEI) + ' ' + 'MAPE:' + str(PR_lossMAPE))  # 加标签

    # 获取最大值
    relmax = np.max(last_rel)
    premax = np.max(last_pre)
    top = max(relmax, premax)

    x_rel = np.arange(TIME_STEPS)
    x_pre = np.arange(TIME_STEPS, TIME_STEPS + PRED_SIZE)

    plt.plot(x_rel, last_rel, label='原始')

    plt.plot(x_pre, pre_, label='预测')

    dic = {'预测天数': np.arange(1, len(pre_) + 1),
           '日产气 (m^3)': pre_}

    export_data = pd.DataFrame(dic)
    if not os.path.exists('resource/result'):
        os.mkdir('resource/result/')
    export_data.to_excel('resource/result/' + file_name + '.xlsx', index=False)

    plt.ylim([0, top * 1.3])

    plt.legend()
    plt.savefig('resource/picture/predict/' + file_name + '.png', bbox_inches='tight')
    # 重新画一张新的
    plt.clf()

    # 把序号i和文件名字传过去
    ms.predict_return.emit(str(i) + '/' + file_name)
    ms.progress_return2.emit(i)
    return PR_lossRMSE, PR_lossMAPE


def main(TRAIN=True):
    if TRAIN:
        train()
    test()


if __name__ == '__main__':
    main()
