from pygame.locals import *
import pygame
from data import list_len
from data import DATA
from numba import jit
from sys import exit
from data import Bc
import numpy as np
import pygame
import os


print("准备输出")
# 运行首选项（根据需求调参数，可以默认）
FPS = 120  # 帧率
WINDOW_W = 1080 * 2  # 窗口宽
WINDOW_H = 720 * 2  # 窗口高
cir_count = 80000  # 最小向量数
bg_cor = (10, 20, 30)  # 背景色
b_color = (188, 188, 244)  # 向量的默认颜色(半径)
b_length = list_len * 0.995  # 轨迹持续的帧数
Vt = False  # 初始摄像机跟踪
Perspective = False  # 透视投影
scale_ex = 1.018  # 缩放倍率系数
z_change = .13 * list_len / (WINDOW_W + WINDOW_H)  # 深度缩放
window_center = (WINDOW_W / 2 - 0, WINDOW_H / 2 - 0)  # 摄像机中心
Move_k = 20  # 平移系数
one_time = 1  # 运行速度（点/帧）
nomat = True  # 不使用矩阵渲染,仅预览(极大加快运行速度)
# 导入数据
fourier_list = DATA[:]
fourier_list = sorted(fourier_list, key=lambda x: abs(x[0]), reverse=True)  # 排序
# 初始化
pygame.init()
pygame.mixer.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10, 70)
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.DOUBLEBUF, 32)  # 创建窗口
pygame.display.set_caption("傅里叶级数3D实时动画")
font = pygame.font.SysFont('simhei', 16)
# 声明
len_fourier_list = len(fourier_list)
z = 0  # 声明向量深度
ang_change = 0.02  # 声明角速度(弧度制)
transform_matrix_now = np.array([[1, 0, 0, 0],
                              [0, 1, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]])  # 声明当前变换矩阵
a = np.array([[1, 0, 0, - window_center[0]],
            [0, 1, 0, - window_center[1]],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])
c = np.linalg.inv(a)

transform_matrix_zl = np.array([[np.cos(-ang_change), -np.sin(-ang_change), 0, 0],
                    [np.sin(-ang_change), np.cos(-ang_change), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])  # 纯旋转矩阵
transform_matrix_zl = np.dot(c,np.dot(transform_matrix_zl,a))  # 旋转矩阵
transform_matrix_zr = np.array([[np.cos(ang_change), -np.sin(ang_change), 0, 0],
                    [np.sin(ang_change), np.cos(ang_change), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])  # 纯旋转矩阵
transform_matrix_zr = np.dot(c,np.dot(transform_matrix_zr,a))
transform_matrix_yl = np.array([[np.cos(ang_change), 0, -np.sin(ang_change), 0],
            [0, 1, 0, 0],
            [np.sin(ang_change), 0,  np.cos(ang_change), 0],
            [0, 0, 0, 1]])  # 纯旋转矩阵
transform_matrix_yl = np.dot(c,np.dot(transform_matrix_yl,a))  # 旋转矩阵
transform_matrix_yr = np.array([[np.cos(-ang_change), 0, -np.sin(-ang_change), 0],
            [0, 1, 0, 0],
            [np.sin(-ang_change), 0,  np.cos(-ang_change), 0],
            [0, 0, 0, 1]])  # 纯旋转矩阵
transform_matrix_yr = np.dot(c,np.dot(transform_matrix_yr,a))  # 旋转矩阵
transform_matrix_xl = np.array([[1, 0, 0, 0],
            [0,np.cos(ang_change),  -np.sin(ang_change), 0],
            [0, np.sin(ang_change),  np.cos(ang_change), 0],
            [0, 0, 0, 1]])  # 纯旋转矩阵
transform_matrix_xl = np.dot(c,np.dot(transform_matrix_xl,a))  # 旋转矩阵
transform_matrix_xr = np.array([[1, 0, 0, 0],
            [0,np.cos(-ang_change),  -np.sin(-ang_change), 0],
            [0, np.sin(-ang_change),  np.cos(-ang_change), 0],
            [0, 0, 0, 1]])  # 纯旋转矩阵
transform_matrix_xr = np.dot(c,np.dot(transform_matrix_xr,a))  # 旋转矩阵
transform_matrix_up = np.array([[1, 0, 0, 0],
            [0, 1, 0,  -Move_k],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])  # 平移矩阵
transform_matrix_up = np.dot(c,np.dot(transform_matrix_up,a))  # 平移矩阵
transform_matrix_down = np.array([[1, 0, 0, 0],
            [0, 1, 0,  Move_k],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])  # 平移矩阵
transform_matrix_down = np.dot(c,np.dot(transform_matrix_down,a))  # 平移矩阵
transform_matrix_left = np.array([[1, 0, 0, -Move_k],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])  # 平移矩阵
transform_matrix_left = np.dot(c,np.dot(transform_matrix_left,a))  # 平移矩阵
transform_matrix_right = np.array([[1, 0, 0, Move_k],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])  # 平移矩阵
transform_matrix_right = np.dot(c,np.dot(transform_matrix_right,a))  # 平移矩阵
mat_big = [[scale_ex, 0, 0, 0],
[0, scale_ex, 0, 0],
[0, 0, scale_ex, 0],
[0, 0, 0, 1]]
mat_big = np.dot(c,np.dot(mat_big,a))  # 放大矩阵
mat_small = [[1 / scale_ex, 0, 0, 0],
[0, 1 / scale_ex, 0, 0],
[0, 0, 1 / scale_ex, 0],
[0, 0, 0, 1]]
mat_small = np.dot(c,np.dot(mat_small,a))  # 缩小矩阵
fovy = 150  # 视野
aspect = WINDOW_W / WINDOW_H  # 屏幕宽高比
Znear = 10
Zfar = 100
Perspective_matrix = np.array([[Zfar, 0, 0, 0],
                              [0, Zfar, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 1, 0]])  # 声明透视矩阵
Perspective_matrix = np.dot(c,np.dot(Perspective_matrix,a))
print("轨迹保留", b_length, "帧(自动)")
print("步长", Bc, "像素")
print("向量数", len_fourier_list)
print("达到最大精度需要", len(fourier_list), "个向量")
father_x = WINDOW_W // 2 - 0
father_y = WINDOW_H // 2 - 0
@jit(nopython = True)
def anglecos(a,r,c):
    return a + r * np.cos(c)
@jit(nopython = True)
def anglesin(a,r,c):
    return a + r * np.sin(c)
@jit(nopython = True)
def func_add(a,b,c):
    return a + b * c
class Circle:
    x, y = 0, 0
    r = 0
    angle = 0
    angle_v = 1
    color = (0, 0, 0)
    father = None
    def __init__(self, r, angle_v, angle, color=None, father=None):
        self.r = r
        self.angle_v = angle_v
        self.angle = angle
        self.father = father
        self.color = color
xys = []
super_circle = Circle(0, 0, 0, color=b_color)
super_circle.x, super_circle.y = window_center
circle_list = [super_circle] 
for i in range(len_fourier_list):
    p = fourier_list[i]
    circle_list.append(Circle(p[0], p[1], p[2], color=b_color, father=circle_list[i]))
clock = pygame.time.Clock()
len_xys = 0
xys0_translated = []
xys1_translated = []
while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按下退出按钮
            print("结束")
            exit()
        elif event.type == KEYDOWN:  # 键盘按下
            if event.key == K_ESCAPE:  # ESC
                print("结束")
                exit()
            elif event.key == K_SPACE:  # 按下空格
                transform_matrix_now = np.array([[1, 0, 0, 0],
                              [0, 1, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]])
            elif event.key == K_BACKSPACE:
                xys.clear()
                xys = [list(window_center)]  # 清空屏幕
            elif event.key == K_v:  # 跟踪视角与固定视角坐标转换
                Vt = not Vt
            elif event.key == K_TAB:  # 反向
                one_time *= -1
            elif event.key == K_n:  # 预览模式(禁用矩阵)
                nomat = not nomat
            elif event.key == K_r:  # 右侧视图(侧视)
                b = np.array([[np.cos(-np.pi / 2), 0, -np.sin(-np.pi / 2), 0],
                            [0, 1, 0, 0],
                            [np.sin(-np.pi / 2), 0,  np.cos(-np.pi / 2), 0],
                            [0, 0, 0, 1]])  # 纯旋转矩阵
                transform_matrix_now = np.dot(c,np.dot(b,a))  # 旋转矩阵
            elif event.key == K_t:  # 顶视图(俯视)
                b = np.array([[1, 0, 0, 0],
                            [0,np.cos(-np.pi / 2),  -np.sin(-np.pi / 2), 0],
                            [0, np.sin(-np.pi / 2),  np.cos(-np.pi / 2), 0],
                            [0, 0, 0, 1]])  # 纯旋转矩阵
                transform_matrix_now = np.dot(c,np.dot(b,a))  # 旋转矩阵
            elif event.key == K_f:  # 正视图(正视)
                transform_matrix_now = np.array([[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])  # 旋转矩阵
            elif pygame.key.get_pressed()[pygame.K_g]:  # 透视|平行投影转换
                Perspective = not Perspective
    if pygame.key.get_pressed():
        if pygame.key.get_pressed()[pygame.K_PLUS] or pygame.key.get_pressed()[pygame.K_EQUALS]:  # 缩放
            transform_matrix_now = np.dot(mat_big,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_MINUS]:
            transform_matrix_now = np.dot(mat_small,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_UP]:    # 上下左右平移
            transform_matrix_now = np.dot(transform_matrix_up,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            transform_matrix_now = np.dot(transform_matrix_down,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            transform_matrix_now = np.dot(transform_matrix_left,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            transform_matrix_now = np.dot(transform_matrix_right,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_q]:  # 顺时针旋转(绕z轴)
            transform_matrix_now = np.dot(transform_matrix_zl,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_e]:  # 逆时针旋转(绕z轴)
            transform_matrix_now = np.dot(transform_matrix_zr,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_a]:  # 左旋转(绕y轴)
            transform_matrix_now = np.dot(transform_matrix_yl,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_d]:  # 右旋转(绕y轴)
            transform_matrix_now = np.dot(transform_matrix_yr,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_w]:  # 上旋转(绕x轴)
            transform_matrix_now = np.dot(transform_matrix_xl,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_s]:  # 下旋转(绕x轴)
            transform_matrix_now = np.dot(transform_matrix_xr,transform_matrix_now)
        if pygame.key.get_pressed()[pygame.K_u]:  # 
            z_change *= 1.1
        if pygame.key.get_pressed()[pygame.K_i]:  # 
            z_change /= 1.1
    screen.fill(bg_cor)  # 画背景
    for i in range(len_xys):
        xys[i][2] = (len_xys - i) * z_change
    Vtlast1_circle = circle_list[- 1]
    last_circle = circle_list[len_fourier_list - 1]  # 最后一个对象
    xys.append([last_circle.x, last_circle.y, z, 1])
    if nomat:
        if Vt:
            for ii in range(1,len_xys):
                pygame.draw.aaline(screen, (200,70,50), (xys[ii - 1][0] - xys[-1][0] + window_center[0], xys[ii - 1][1] - xys[-1][1] + window_center[1]),
                                (xys[ii][0]- xys[-1][0] + window_center[0], xys[ii][1] - xys[-1][1] + window_center[1]), 1)
        else:
            for ii in range(1,len_xys):
                pygame.draw.aaline(screen, (200,70,50), (xys[ii - 1][0], xys[ii - 1][1]),(xys[ii][0], xys[ii][1]), 1)
    else:
        len_xys = len(xys)
        for ii in range(1,len_xys):  # 着色点颜色，线宽
            xys_ii_0 = xys[ii - 1][0]  # 避免多次调用
            xys_ii_1= xys[ii - 1][1]
            xys_iinext_0 = xys[ii][0]
            xys_iinext_1= xys[ii][1]
            if ((xys_ii_0 - xys_iinext_0) ** 2 + (
                    xys_ii_1 - xys_iinext_1) ** 2) ** 0.5 < Bc * 10:  # 路径优化 
                rgb = min((ii / len_xys) * 5000, 255)
                RGB = (rgb,rgb,rgb)
                if Vt:
                    xys0_translated = np.dot(last_M,[xys_ii_0 - xys[-1][0] + window_center[0],xys_ii_1 - xys[-1][1] + window_center[1],xys[ii - 1][2],1])
                    xys1_translated = np.dot(last_M,[xys_iinext_0 - xys[-1][0] + window_center[0],xys_iinext_1 - xys[-1][1] + window_center[1],xys[ii][2],1])
                else:
                    xys0_translated = np.dot(last_M,xys[ii - 1])
                    xys1_translated = np.dot(last_M,xys[ii])
                pygame.draw.aaline(screen, RGB, (xys0_translated[0], xys0_translated[1]), (xys1_translated[0], xys1_translated[1]), 1)  # 抗锯齿直线
    if Perspective:  # 透视
        last_M = np.dot(Perspective_matrix,transform_matrix_now)
    else:
        last_M = transform_matrix_now
    if len_xys >= b_length:
        xys.pop(0)
    len_xys = len(xys)
    rline_list = []
    for i, circle in enumerate(circle_list[:len_fourier_list]):  # 运行
        circle_father = circle.father
        if circle_father is not None:
            r = circle.r
            circle.angle = func_add(circle.angle, circle.angle_v,one_time)
            selfangle = circle.angle
            father_x = circle.father.x
            father_y = circle.father.y
            circle.x = anglecos(father_x, r, selfangle)
            circle.y = anglesin(father_y, r, selfangle)
            #rline_list.append([father_x, father_y,circle.x, circle.y])
            rline_list.append([circle.x, circle.y])
            if nomat and not Vt:
                pygame.draw.circle(screen, (80,70,60), (father_x,father_y), float(abs(r)), 1)  # 圆轮廓线宽度
            if i == len_fourier_list - 1:  # 末端点坐标
                L1_x = circle.x
                L1_y = circle.y
        else:
            rline_list.append([WINDOW_W / 2, WINDOW_H / 2])
    if Vt:  # 末端点居中
        for i in range(len(rline_list)):
            rline_list[i][0] -= L1_x - window_center[0]
            rline_list[i][1] -= L1_y - window_center[1]
    if nomat:
        pygame.draw.aalines(screen, (0,50,255), False, rline_list, blend=1)
    else:
        for i in range(len(rline_list)):
            temp1 = [rline_list[i-1][0],rline_list[i-1][1],0,1]
            temp1 = np.dot(last_M,temp1)
            temp2 = [rline_list[i][0],rline_list[i][1],0,1]
            temp2 = np.dot(last_M,temp2)
            i_k = i / len(rline_list)
            lineRGB = (50 + i_k ** 0.2 * 200,
                            50 + i_k ** 0.3 * 200,
                            50 + i_k ** 0.4 * 200)
            pygame.draw.aaline(screen, lineRGB, (temp1[0],temp1[1]), (temp2[0],temp2[1]), 1)  # 绘制半径
        X1 = [window_center[0] - 300,window_center[1],0,1]
        X2 = [window_center[0] + 300,window_center[1],0,1]
        Y1 = [window_center[0],window_center[1] - 300,0,1]
        Y2 = [window_center[0],window_center[1] + 300,0,1]
        Z1 = [window_center[0],window_center[1],-300,1]
        Z2 = [window_center[0],window_center[1],300,1]
        X1 = np.dot(last_M,X1)
        Y1 = np.dot(last_M,Y1)
        Z1 = np.dot(last_M,Z1)
        X2 = np.dot(last_M,X2)
        Y2 = np.dot(last_M,Y2)
        Z2 = np.dot(last_M,Z2)
        pygame.draw.aaline(screen, (180,90,90), (X1[0],X1[1]), (X2[0],X2[1]), 1)  # 绘制坐标轴
        pygame.draw.aaline(screen, (90,180,90), (Y1[0],Y1[1]), (Y2[0],Y2[1]), 1)  # 绘制坐标轴
        pygame.draw.aaline(screen, (90,90,180), (Z1[0],Z1[1]), (Z2[0],Z2[1]), 1)  # 绘制坐标轴
    timer_passed = clock.tick(FPS)
    pygame.display.update()
