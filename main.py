import pygame
import math
import os
from pygame.locals import *
from sys import exit
from data import DATA
from data import list_len
from data import Bc
from data import BHz
from math import pi


print("准备输出")                                                                                                   # 设置
WINDOW_W = 1080
WINDOW_H = 680
one_time = 1  # 点/帧
scale = 1  # 固定视角初始缩放
scale_Vt = 8  # 跟踪视角初始缩放
scale_ex = 1.1  # 缩放系数
FPS = 30  # 帧率
Vt = 0  # 初始是否视角跟踪
start_xy_Vton = (WINDOW_W // 2 - 0, WINDOW_H // 2 - 0)  # 跟踪视角尾向量的位置
start_xy_Vtoff = (WINDOW_W // 2 - 0, WINDOW_H // 2 - 0)  # 固定视角第首向量的位置
cir_count = 80000  # 向量数
bg_cor = (8, 8, 8)  # 背景色
b_color = (166, 166, 225)  # 向量的默认颜色(半径)
b_length = list_len * 0.985  # 轨迹持续帧数
fourier_list = DATA[:]  # 导入数据
fourier_list = sorted(fourier_list, key=lambda x: abs(x[0]), reverse=True)  # 排序
pygame.init()  # 初始化
pygame.mixer.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10, 70)
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.DOUBLEBUF, 32)  # 创建窗口
pygame.display.set_caption("傅里叶级数绘图")
font = pygame.font.SysFont('simhei', 16)
k = len(fourier_list) / min(cir_count, len(fourier_list))  # 纠错系数
Move_x = 0  # 平移
Move_y = 0
Move_k = 20  # 平移系数
Vt_cir_0 = 0  # 以第几个节点为跟踪视角的中心,默认则为0
if Vt_cir_0 == 0:
    Vt_cir_0 = cir_count
print("轨迹保留", b_length, "帧(自动)")
print("使用了", min(cir_count, len(fourier_list)), "个向量")
print("最大精度需要", len(fourier_list), "个向量")
print("步长:", Bc, "像素/步")


class Circle:                                                                                                  # 创建向量
    x, y = 0, 0
    r = 0
    angle = 0
    angle_v = 0
    color = (0, 0, 0)
    father = None

    def __init__(self, r, angle_v, angle, color=None, father=None):
        self.r = r
        self.angle_v = angle_v
        self.angle = angle
        self.father = father
        if color is None:
            self.color = (0, 0, 0)
        else:
            self.color = color

    def set_xy(self, xy):
        self.x, self.y = xy

    def set_xy_by_angle(self):
        if Vt:
            self.x = self.father.x + self.r * math.cos(self.angle) * scale_Vt
            self.y = self.father.y + self.r * math.sin(self.angle) * scale_Vt
        else:
            self.x = self.father.x + self.r * math.cos(self.angle) * scale
            self.y = self.father.y + self.r * math.sin(self.angle) * scale

    def run(self, step_time):
        if self.father is not None:
            self.angle += self.angle_v * step_time
            self.set_xy_by_angle()

    def draw(self, draw_screen, draw_i):
        if self.father is not None:
            if Vt:
                pygame.draw.aaline(draw_screen, (((draw_i / min(cir_count, len(fourier_list))) ** 1.8) * 255,
                                                 ((draw_i / min(cir_count, len(fourier_list))) ** 3) * 255,
                                                 ((draw_i / min(cir_count, len(fourier_list))) ** 1) * 255), (self.father.x - L_x + start_xy_Vton[0], self.father.y - L_y + start_xy_Vton[1]), (self.x - L_x + start_xy_Vton[0], self.y - L_y + start_xy_Vton[1]), 2)  # 绘制半径
            else:
                Vtoff_RGB = (((draw_i / min(cir_count, len(fourier_list))) ** 0.25) * 255,
                             ((draw_i / min(cir_count, len(fourier_list))) ** 0.25) * 255,
                             ((draw_i / min(cir_count, len(fourier_list))) ** 0.25) * 255)
                pygame.draw.circle(draw_screen, Vtoff_RGB, (self.father.x + Move_x, self.father.y + Move_y), float(abs(self.r) * scale), 1)  # 圆轮廓线宽度
                pygame.draw.aaline(draw_screen, Vtoff_RGB, (self.father.x + Move_x, self.father.y + Move_y), (self.x + Move_x, self.y + Move_y), 1)  # 绘制半径


class Boxin:
    xys = []

    def add_point(self, xy):
        self.xys.append(xy)
        if len(self.xys) > b_length:
            self.xys.pop(0)

    def draw(self, draw_screen):
        bl = len(self.xys)
        if Vt:
            for ii in range(bl - 1):  # 着色点颜色，线宽
                if ((self.xys[ii][0] - self.xys[ii + 1][0]) ** 2 + (
                        self.xys[ii][1] - self.xys[ii + 1][1]) ** 2) ** 0.5 < Bc * 4 * scale_Vt * k:  # 路径优化
                    pygame.draw.aaline(draw_screen, (250, 250, 250), (Boxin.xys[ii - 0][0] - L_x + start_xy_Vton[0], Boxin.xys[ii - 0][1] - L_y + start_xy_Vton[1]), (self.xys[ii + 1][0] - L_x + start_xy_Vton[0], self.xys[ii + 1][1] - L_y + start_xy_Vton[1]), 2)  # 抗锯齿直线
        else:
            for ii in range(bl - 1):  # 着色点颜色，线宽
                if ((self.xys[ii][0] - self.xys[ii + 1][0]) ** 2 + (
                        self.xys[ii][1] - self.xys[ii + 1][1]) ** 2) ** 0.5 < Bc * 4 * scale * k:  # 路径优化
                    pygame.draw.aaline(draw_screen, (250, 250, 250), (self.xys[ii][0] + Move_x, self.xys[ii][1] + Move_y), (self.xys[ii + 1][0] + Move_x, self.xys[ii + 1][1] + Move_y), 2)  # 抗锯齿直线


super_circle = Circle(0, 0, 0, color=b_color)
if Vt:
    super_circle.set_xy(start_xy_Vton)
else:
    super_circle.set_xy(start_xy_Vtoff)
circle_list = [super_circle]
for i in range(min(cir_count, len(fourier_list))):
    p = fourier_list[i]
    circle_list.append(Circle(p[0], p[1], p[2], color=b_color, father=circle_list[i]))
bx = Boxin()
clock = pygame.time.Clock()
print("正在运行")


while 1:                                                                                                           # 输出
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按下退出按钮
            print("结束运行")
            exit()
        elif event.type == KEYDOWN:  # 键盘按下
            if event.key == K_ESCAPE:  # ESC
                print("结束运行")
                exit()
            elif event.key == K_SPACE:  # 按下空格
                start_xy_Vton = (WINDOW_W / 2, WINDOW_H / 2)
            elif event.key == K_BACKSPACE:
                Boxin.xys.clear()  # 清空屏幕
            elif event.key == K_v:  # 跟踪视角与固定视角转换
                Vt = not Vt
                if Vt:
                    for i in range(len(Boxin.xys)):
                        Boxin.xys[i] = [((Boxin.xys[i][0] - start_xy_Vton[0]) / scale) * scale_Vt + start_xy_Vton[0],
                                        ((Boxin.xys[i][1] - start_xy_Vton[1]) / scale) * scale_Vt + start_xy_Vton[1]]
                else:
                    for i in range(len(Boxin.xys)):
                        Boxin.xys[i] = [((Boxin.xys[i][0] - start_xy_Vtoff[0]) / scale_Vt) * scale + start_xy_Vtoff[0],
                                        ((Boxin.xys[i][1] - start_xy_Vtoff[1]) / scale_Vt) * scale + start_xy_Vtoff[1]]
            elif event.key == K_TAB:  # 按下TAB键
                one_time *= -1
    if pygame.key.get_pressed():
        if pygame.key.get_pressed()[pygame.K_PLUS] or pygame.key.get_pressed()[pygame.K_EQUALS]:  # 是否按下+或=
            if Vt:
                scale_Vt *= scale_ex
                for i in range(len(Boxin.xys)):
                    Boxin.xys[i] = [(Boxin.xys[i][0] - start_xy_Vton[0]) * scale_ex + start_xy_Vton[0],
                                    (Boxin.xys[i][1] - start_xy_Vton[1]) * scale_ex + start_xy_Vton[1]]
            else:
                scale *= scale_ex
                for i in range(len(Boxin.xys)):  # 放大/缩小
                    Boxin.xys[i] = [(Boxin.xys[i][0] - start_xy_Vtoff[0]) * scale_ex + start_xy_Vtoff[0],
                                    (Boxin.xys[i][1] - start_xy_Vtoff[1]) * scale_ex + start_xy_Vtoff[1]]  # 坐标变换
        elif pygame.key.get_pressed()[pygame.K_MINUS] and scale_Vt > 0.1:
            if Vt:
                scale_Vt /= scale_ex
                for i in range(len(Boxin.xys)):
                    Boxin.xys[i] = [(Boxin.xys[i][0] - start_xy_Vton[0]) / scale_ex + start_xy_Vton[0],
                                    (Boxin.xys[i][1] - start_xy_Vton[1]) / scale_ex + start_xy_Vton[1]]
            else:
                scale /= scale_ex
                for i in range(len(Boxin.xys)):
                    Boxin.xys[i] = [(Boxin.xys[i][0] - start_xy_Vtoff[0]) / scale_ex + start_xy_Vtoff[0],
                                    (Boxin.xys[i][1] - start_xy_Vtoff[1]) / scale_ex + start_xy_Vtoff[1]]
        elif pygame.key.get_pressed()[pygame.K_UP] and start_xy_Vton[1] > WINDOW_H * 0.01:
            if Vt:
                dt_l = ((start_xy_Vton[0] - WINDOW_W * 0.01) / WINDOW_W) / scale
                dt_r = ((WINDOW_W * 0.99 - start_xy_Vton[0]) / WINDOW_W) / scale
                dt_u = ((start_xy_Vton[1] - WINDOW_H * 0.01) / WINDOW_H) / scale
                dt_d = ((WINDOW_H * 0.99 - start_xy_Vton[1]) / WINDOW_H) / scale
                start_xy_Vton = (start_xy_Vton[0], start_xy_Vton[1] - (Move_k * (dt_u * 0.5)))
            else:
                Move_y -= Move_k * scale ** 0.5
        elif pygame.key.get_pressed()[pygame.K_DOWN] and start_xy_Vton[1] < WINDOW_H * 0.99:
            if Vt:
                dt_l = ((start_xy_Vton[0] - WINDOW_W * 0.01) / WINDOW_W) / scale
                dt_r = ((WINDOW_W * 0.99 - start_xy_Vton[0]) / WINDOW_W) / scale
                dt_u = ((start_xy_Vton[1] - WINDOW_H * 0.01) / WINDOW_H) / scale
                dt_d = ((WINDOW_H * 0.99 - start_xy_Vton[1]) / WINDOW_H) / scale
                start_xy_Vton = (start_xy_Vton[0], start_xy_Vton[1] + (Move_k * (dt_d * 0.5)))
            else:
                Move_y += Move_k * scale ** 0.5
        elif pygame.key.get_pressed()[pygame.K_LEFT] and start_xy_Vton[0] > WINDOW_W * 0.01:
            if Vt:
                dt_l = ((start_xy_Vton[0] - WINDOW_W * 0.01) / WINDOW_W) / scale
                dt_r = ((WINDOW_W * 0.99 - start_xy_Vton[0]) / WINDOW_W) / scale
                dt_u = ((start_xy_Vton[1] - WINDOW_H * 0.01) / WINDOW_H) / scale
                dt_d = ((WINDOW_H * 0.99 - start_xy_Vton[1]) / WINDOW_H) / scale
                start_xy_Vton = (start_xy_Vton[0] - (Move_k * (dt_l * 0.5)), start_xy_Vton[1])
            else:
                Move_x -= Move_k * scale ** 0.5
        elif pygame.key.get_pressed()[pygame.K_RIGHT] and start_xy_Vton[0] < WINDOW_W * 0.99:
            if Vt:
                dt_l = ((start_xy_Vton[0] - WINDOW_W * 0.01) / WINDOW_W) / scale
                dt_r = ((WINDOW_W * 0.99 - start_xy_Vton[0]) / WINDOW_W) / scale
                dt_u = ((start_xy_Vton[1] - WINDOW_H * 0.01) / WINDOW_H) / scale
                dt_d = ((WINDOW_H * 0.99 - start_xy_Vton[1]) / WINDOW_H) / scale
                start_xy_Vton = (start_xy_Vton[0] + (Move_k * (dt_r * 0.5)), start_xy_Vton[1])
            else:
                Move_x += Move_k * scale ** 0.5
    last_circle = circle_list[min(cir_count, len(fourier_list)) - 1]  # 最后一个点
    Vtlast_circle = circle_list[min(Vt_cir_0, len(fourier_list)) - 1]
    screen.fill(bg_cor)  # 画背景
    for i, circle in enumerate(circle_list[:min(cir_count, len(fourier_list))]):  # 运行
        circle.run(one_time)
        circle.draw(screen, i)
    bx.add_point((last_circle.x, last_circle.y))
    bx.draw(screen)
    pygame.display.update()
    L_x = Vtlast_circle.x
    L_y = Vtlast_circle.y
    time_passed = clock.tick(FPS)
