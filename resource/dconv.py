import tensorflow as tf
import pandas as pd
import numpy as np

# Input_file = '101-9test.csv'
# Out_flie = '101-9-1dconv.csv'

# Input_file = '9-3train.csv'
# Out_flie = '9-3-1dconv.csv'
#
# Input_file = '12-0test2.csv'
# Out_flie = '12-0-1dconv.csv'
# Input_file = '9-3train.csv'
# Out_flie = '9-6-train_end.xlsx'
# Out_flie = '9-9-train_end.xlsx'
feature_index = [5,6,9,10,13,14,17,18,21,22,23,24,25,26,27,28,29]


def get_convdata(Input_file):
    df = pd.read_excel(Input_file).iloc[:,feature_index]
    df = df[::-1]
    df = df.iloc[:228,:]
    return df

def get_label():
    label = pd.read_csv(Input_file)
    return label

def frame_to_tensor(df):
    df_array = np.array(df)
    df_re = df_array.reshape(df.shape[0], df.shape[1], 1)
    df_tensor = tf.convert_to_tensor(df_re)
    return df_tensor


def conv1d(data,kernel_size,stride):
    conv1D = tf.keras.layers.Conv1D(1, kernel_size, padding='valid',strides=stride)  # 1是输出通道数，3是卷积核大小，不使用边界填充
    max_pool_1d = tf.keras.layers.MaxPooling1D(pool_size=4, strides=1, padding='valid')
    y = conv1D(data)
    y = max_pool_1d(y)
    return y

def tensor_to_frame(y):
    y_array = np.array(y)
    y_back = y_array.reshape(y_array.shape[0], y_array.shape[1])
    y_pd = pd.DataFrame(y_back)
    return y_pd


def concerate(Input_file, path):
    df = get_convdata(Input_file)
    print(np.shape(df))
    data1 = frame_to_tensor(df)
    y = conv1d(data1,2,1)
    y_pd = tensor_to_frame(y)
    res = np.concatenate((df,y_pd),axis=1)
    res = pd.DataFrame(res)

    data2 = frame_to_tensor(res)
    y2 = conv1d(data2,4,2)
    y2_pd = tensor_to_frame(y2)
    res2 = np.concatenate((res,y2_pd),axis=1)
    res2 = pd.DataFrame(res2)

    data3 = frame_to_tensor(res2)
    y3 = conv1d(data3, 6, 3)
    y3_pd = tensor_to_frame(y3)
    res3 = np.concatenate((res2, y3_pd), axis=1)
    res3 = pd.DataFrame(res3)
    #
    # data4 = frame_to_tensor(res3)
    # y4 = conv1d(data4, 8, 4)
    # y4_pd = tensor_to_frame(y4)
    # res4 = np.concatenate((res3, y4_pd), axis=1)
    # res4 = pd.DataFrame(res4)

    # data5 = frame_to_tensor(res4)
    # y5 = conv1d(data5, 10, 5)
    # y5_pd = tensor_to_frame(y5)
    # res5 = np.concatenate((res4, y5_pd), axis=1)
    # res5 = pd.DataFrame(res5)
    Out_flie =str(path).split('.')[0] + '_end.xlsx'
    res3.to_excel(Out_flie, index=False)
    return Out_flie

def main(name, path):
    Input_file = name
    return concerate(Input_file, path)
# if __name__ == '__main__':
#     a = main(name,path)