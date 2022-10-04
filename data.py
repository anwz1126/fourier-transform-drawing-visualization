import numpy as np
from numpy.fft import fft
import matplotlib.pyplot as plt
from math import factorial


# 请将路径数据复制到path中                                                                                         # 输入数据
path = """"""

print("正在准备，请耐心等待")


def is_zm(c):  # 判断字母
    return c in "LlMmHhVvBbCczNnMmHhLlQWERTYUIOPKJGFDSAZXCVBNMqwertyuiopkjgfdsazxcvbn"  # 祖传代码改了报错


def fun_2xy(a, b):
    ret = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    return ret


def fun_L_xy(a, b, c, d):  # 求4点距离和
    ret = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 + ((b[0] - c[0]) ** 2 + (b[1] - c[1]) ** 2) ** 0.5 + (
                (c[0] - d[0]) ** 2 + (c[1] - d[1]) ** 2) ** 0.5
    return ret


# 剔除无效字符串
path = path.replace(
    '''<path style="fill-rule:evenodd;clip-rule:evenodd;" d="''',
    "")
path = path.replace('z"/>', "z")
path = path.replace('"/>', "z")
path = path.replace(' ', "")
path = path.replace('\n/>', "")
path = path.replace('\t/>', "")
path = path.replace(':', "")
path = path.replace(';', "")
path = path.replace(
    '''<line style="fill:none;stroke:#000000;stroke-width:0.48;stroke-linecap:round;" x1="558.81" y1="458.55" x2="558.81" y2="458.54"/>''',
    "")
path = path.replace('<', "")
path = path.replace('>', "")
path = path.replace('"', "")
path = path.replace('z', "")
path_len = len(path)
BHz = 1  # 贝塞尔曲线的精度,根据电脑的配置酌量调小
Bc = 10  # 图像步长(像素/步)，数值越小图像的精度越好
lv = 0  # 过滤(不建议调)
l_list = []  # 存放路径的列表
i = 0

print("正在解析")
while i <= path_len:                                                                                        # 生成指令列表
    if is_zm(path[i]):
        j = i  # 字母位置
        i += 1
        while i < path_len and not is_zm(path[i]):  # 移动i
            i += 1
        if i == path_len:
            i += 1
        if i != j:  # 不等
            s = path[j:i].strip()  # 切片
            a = s[0]  # a字母
            b = s[1:]  # b数字
            if a in "HhVv":
                l_list.append([a, float(b)])  # [字母,数]
            elif a in "MmLl":
                b_list = b.replace("-", ",-").split(",")  # 分割
                b_list = [float(bb) for bb in b_list if len(bb) != 0]
                assert len(b_list) == 2  # 断言列表b有两个元素
                l_list.append([a, *b_list])  # 添加b 格式[l,x坐标,y坐标]
            elif a in "Cc":  # 贝塞尔曲线
                b_list = b.replace("-", ",-").split(",")  # 分割
                b_list = [float(bb) for bb in b_list if len(bb) != 0]
                assert len(b_list) == 6  # 断言b列表有6个参数
                l_list.append([a, *b_list])  # 添加
            elif a in "Ss":  # 贝塞尔曲线
                b_list = b.replace("-", ",-").split(",")  # 分割
                b_list = [float(bb) for bb in b_list if len(bb) != 0]
                assert len(b_list) == 4  # 断言b列表有4个参数
                l_list.append([a, *b_list])  # 添加
            else:
                l_list.append(["z", l_list[-1]])
    else:
        i += 1  # 把标识移到下一个字符

# print(l_list)  # 打印读取结果
point_list = []  # 坐标列表
last_list = []
px = 0, 0

print("生成坐标列表")
# 大写绝对定位 小写相对定位
for line in l_list:  # 遍历                                                                                     # 计算坐标
    a = line[0]  # 切片
    x, y = 0, 0
    if a == "L":  # 对直线按照预先设定的步长(Bc)分割
        U = (((line[1] - point_list[-1][0]) ** 2 + (line[2] - point_list[-1][1]) ** 2) ** 0.5) / Bc
        for i in range(U + 0):
            point_list.append(line[1] + (i / U) * (line[1] - point_list[-1][0]), line[2] + (i / U) * (line[1] - point_list[-1][1]))  # 第二，三个元素切片，以元组放进p列表(xy坐标的初始位置)
    elif a == "l":
        U = (((line[1] - point_list[-1][0]) ** 2 + (line[2] - point_list[-1][1]) ** 2) ** 0.5) / Bc
        for i in range(U + 0):
            point_list.append((point_list[-1][0] + line[1] + (i / U) * (line[1] - point_list[-1][0]),
                               point_list[-1][1] + line[2] + (i / U) * (line[1] - point_list[-1][1])))  # 记录下一时刻的xy坐标
    elif a == "M":
        point_list.append((line[1], line[2]))  # 第二，三个元素切片，以元组放进p列表(xy坐标的初始位置)
    elif a == "m":
        point_list.append((point_list[-1][0] + line[1], point_list[-1][1] + line[2]))  # 记录下一时刻的xy坐标
    elif a == "h":
        point_list.append((point_list[-1][0] + line[1], point_list[-1][1]))  # 记录下一时刻的xy坐标
    elif a == "H":
        point_list.append((line[1], point_list[-1][1]))
    elif a == "v":
        point_list.append((point_list[-1][0], point_list[-1][1] + line[1]))  # 记录下一时刻的xy坐标
    elif a == "V":
        point_list.append((point_list[-1][0], line[1]))  # 画到一个y坐标处
    elif a == "c":
        p1 = point_list[-1][0] + line[1], point_list[-1][1] + line[2]  # line[1: 3]
        p2 = point_list[-1][0] + line[3], point_list[-1][1] + line[4]  # line[3: 5]
        p3 = point_list[-1][0] + line[5], point_list[-1][1] + line[6]  # line[5: 7]
        point = [point_list[-1], p1, p2, p3]
        px = p3[0] * 2 - p2[0], p3[1] * 2 - p2[1]  # s指令的起始控制点
        N = len(point)
        n = N - 1  # n阶贝塞尔曲线
        for T in range(int(fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)):  # 曲线每BHz像素计算一次
            t = T / (fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)  # 小hit
            x, y = 0, 0
            for i in range(N):
                B = factorial(n) * t ** i * (1 - t) ** (n - i) / (factorial(i) * factorial(n - i))  # 套用贝塞尔曲线公式
                x += point[i][0] * B  # 加权自增
                y += point[i][1] * B
            point_list.append((x, y))  # 加入列表
        point_list.append(point[-1])  # 不能删，否则图画出来偏移  后续坐标是在前面的坐标基础上运算的，所以加上最后一个点
        # point_list.append((point_list[-1][0] + line[5], point_list[-1][1] + line[6]))  # 省略控制杆 这些注释掉的都是原始代码
    elif a == "C":
        p1 = line[1], line[2]  # line[1: 3]
        p2 = line[3], line[4]  # line[3: 5]
        p3 = line[5], line[6]  # line[5: 7]
        point = [point_list[-1], p1, p2, p3]
        px = p3[0] * 2 - p2[0], p3[1] * 2 - p2[1]  # s指令的起始控制点
        N = len(point)
        n = N - 1
        for T in range(int(fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)):
            t = T / (fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)
            x, y = 0, 0
            for i in range(N):
                B = factorial(n) * t ** i * (1 - t) ** (n - i) / (factorial(i) * factorial(n - i))
                x += point[i][0] * B
                y += point[i][1] * B
            point_list.append((x, y))
        point_list.append(point[-1])
    elif a == "s":
        p1 = point_list[-1][0] + line[1], point_list[-1][1] + line[2]  # line[1: 3]
        p2 = point_list[-1][0] + line[3], point_list[-1][1] + line[4]  # line[3: 5]
        point = [point_list[-1], px, p1, p2]
        px = p2[0] * 2 - p1[0], p2[1] * 2 - p1[1]
        N = len(point)
        n = N - 1
        for T in range(int(fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)):
            t = T / (fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)
            x, y = 0, 0
            for i in range(N):
                B = factorial(n) * t ** i * (1 - t) ** (n - i) / (factorial(i) * factorial(n - i))
                x += point[i][0] * B
                y += point[i][1] * B
            point_list.append((x, y))
        point_list.append(point[-1])
        # point_list.append((point_list[-1][0] + line[3], point_list[-1][1] + line[4]))  # 省略控制杆
    elif a == "S":
        p1 = line[1], line[2]  # line[1: 3]
        p2 = line[3], line[4]  # line[3: 5]
        point = [point_list[-1], px, p1, p2]
        px = p2[0] * 2 - p1[0], p2[1] * 2 - p1[1]
        N = len(point)
        n = N - 1
        for T in range(int(fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)):
            t = T / (fun_L_xy(point[0], point[1], point[2], point[3]) / BHz)
            x, y = 0, 0
            for i in range(N):
                B = factorial(n) * t ** i * (1 - t) ** (n - i) / (factorial(i) * factorial(n - i))
                x += point[i][0] * B
                y += point[i][1] * B
            point_list.append((x, y))
        point_list.append(point[-1])
    elif a == "z":
        pass  # f = len(point_list)  # f:提笔坐标索引

i = 0
while 1:  # 删去距离过近的坐标点，因为贝塞尔曲线不均匀                                                             # 删除部分坐标
    if i >= len(point_list) - 1:
        break
    if fun_2xy(point_list[i], point_list[i + 1]) < Bc:
        point_list.pop(i + 1)
    else:
        i += 1

# print(point_list)
ex_x = 0                                                                                                  # 校准首向量中心
ex_y = 0
for i in range(len(point_list)):
    ex_x += point_list[i][0]
    ex_y += point_list[i][1]
ex_x /= len(point_list)  # 首圆坐标
ex_y /= len(point_list)
for i in range(len(point_list)):
    point_list[i] = (point_list[i][0] - ex_x, point_list[i][1] - ex_y)  # 校准
y = [complex(p[0], p[1]) for p in point_list]  # 遍历，生成复数坐标
y_matrix = np.array(point_list)  # 建立数组
y_len = len(y)
yy = fft(y)
plt.scatter(y_matrix[:, 0], -y_matrix[:, 1], .2)  # 打印点

DATA = []                                                                                                   # 输出路径数据
n = min(y_len, y_len)
for i, v in enumerate(yy[:n]):  # 向量数
    # print("频率", i, "系数", v)
    if (v.real ** 2 + v.imag ** 2) ** 0.5 < lv:
        v = complex(0, 0)
    c = -2 * np.pi * i / n
    if v != complex(0, 0):
        DATA.append([v.real / n, c, 0])
        DATA.append([v.imag / n, c, np.pi / 2])
DATA.sort(key=lambda x: abs(x[0]), reverse=True)
print("曲线精度", BHz, "像素/步长")
print("过滤阈值", lv)
print("每周期共", len(point_list), "帧")
list_len = len(point_list)

if __name__ == "__main__":  # 若直接运行data
    plt.show()
