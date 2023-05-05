import math
import os

import openpyxl
from PyQt5.QtCore import pyqtSignal, QRect, Qt, QPoint
from PyQt5.QtGui import QImage, QPainter, QPen, QColor, QPixmap
from PyQt5.QtMultimedia import QAbstractVideoSurface, QVideoFrame, QAbstractVideoBuffer
from PyQt5.QtWidgets import QLabel, QMessageBox, QWidget, QHBoxLayout

import time


# 重写QAbstractVideoSurface
class myVideoSurface(QAbstractVideoSurface):
    # 自定义槽函数，传递类型为QImage图像
    frame_available = pyqtSignal(QImage)
    capture_available = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frame = None
        self.cnt = 0
        self.switch0 = 1

    # 返回支持的像素格式
    def supportedPixelFormats(self, type=None):
        support_format = [
            QVideoFrame.Format_ARGB32,
            QVideoFrame.Format_ARGB32_Premultiplied,
            QVideoFrame.Format_ARGB8565_Premultiplied,
            QVideoFrame.Format_AYUV444,
            QVideoFrame.Format_AYUV444_Premultiplied,
            QVideoFrame.Format_BGR24,
            QVideoFrame.Format_BGR32,
            QVideoFrame.Format_BGR555,
            QVideoFrame.Format_BGR565,
            QVideoFrame.Format_BGRA32,
            QVideoFrame.Format_BGRA32_Premultiplied,
            QVideoFrame.Format_BGRA5658_Premultiplied,
            QVideoFrame.Format_CameraRaw,
            QVideoFrame.Format_IMC1,
            QVideoFrame.Format_IMC2,
            QVideoFrame.Format_IMC3,
            QVideoFrame.Format_IMC4,
            QVideoFrame.Format_Jpeg,
            QVideoFrame.Format_NV12,
            QVideoFrame.Format_NV21,
            QVideoFrame.Format_RGB24,
            QVideoFrame.Format_RGB32,
            QVideoFrame.Format_RGB555,
            QVideoFrame.Format_RGB565,
            QVideoFrame.Format_User,
            QVideoFrame.Format_UYVY,
            QVideoFrame.Format_Y16,
            QVideoFrame.Format_Y8,
            QVideoFrame.Format_YUV420P,
            QVideoFrame.Format_YUV444,
            QVideoFrame.Format_YUYV,
            QVideoFrame.Format_YV12,
        ]
        return support_format

    # 获取输入进来的一帧视频流，进行处理
    def present(self, frame: QVideoFrame):
        if frame.isValid():
            # 克隆一个视频帧
            clone_frame = QVideoFrame(frame)
            # map将视频帧的内容映射到系统（CPU可寻址）内存
            clone_frame.map(QAbstractVideoBuffer.ReadOnly)
            # 构造具有给定宽度、高度和格式的图像，将视频流转换为图像
            image = QImage(clone_frame.bits(), frame.width(), frame.height(), frame.bytesPerLine(),
                           QVideoFrame.imageFormatFromPixelFormat(frame.pixelFormat()))
            # 映射返回
            clone_frame.unmap()
            # image.save("frame.jpg")
            # 读取截图数目
            if self.switch0 == 1:
                wb = openpyxl.load_workbook(r'progressbar_TempData/num_marks.xlsx')
                sh = wb["Sheet1"]  # 根据表单名称，选择sheet（表单）
                self.num_marks = sh.cell(1, 1).value  # 读数据
                wb.save(r'progressbar_TempData/num_marks.xlsx')
                wb.close()
                self.switch0 = 0
            # 释放信号，进入auto_detect函数中处理图像
            self.frame_available.emit(image)
            self.cnt += 1
            if self.cnt != self.num_marks:
                time.sleep(1)
                self.capture_available.emit()
            else:
                self.cnt = 0
                self.switch0 = 1
        if self.surfaceFormat().pixelFormat() != frame.pixelFormat() or \
                self.surfaceFormat().frameSize() != frame.size():
            self.setError(QAbstractVideoSurface.IncorrectFormatError)
            self.stop()
            return False
        else:
            self.current_frame = frame
            # self.widget.repaint(self.target_rect)
            # print("present finished: Return True")
            return True


# 重写QLabel
class MyLabel(QLabel):
    signal_order = pyqtSignal(int)
    # 初始化
    begin = QPoint()
    end = QPoint()
    flag = False
    ####记录颜色id元组值
    color_id = (
        ("1",), ("2",), ("3",), ("4",), ("5",), ("a",), ("b",), ("c",), ("d",),
        ("e",))  # 定义边缘框id
    ####
    color_dict = {"red": Qt.red, "black": Qt.black, "yellow": Qt.yellow, "blue": Qt.blue, "green": Qt.green,
                  "gray": Qt.gray,
                  "white": Qt.white, "cyan": Qt.cyan, "magenta": Qt.magenta,
                  "orange": QColor(255, 140, 0), "11": QColor(107, 142, 35)}  # 定义矩形框颜色
    color_flag = [0 for i in range(10)]
    color_dict_keys = list(color_dict.keys())

    def __init__(self, order=None):
        super(MyLabel, self).__init__()
        self.order = order  # 代表第几个Label
        self.rectangles = []
        self.rect_attribute = [0 for i in range(10)]  # 定义边缘框所有属性列表
        self.rect_id = []  # 定义边缘框ID
        self.rect_position = [0 for i in range(10)]  # 定义边缘框位置
        self.cnt = 0  # 计数
        self.attrcnt = 0
        self.extra = 1  # 最大上限矩形框提醒开关
        self.setStyleSheet("border-width: 2px; border-style: solid; border-color: gray")

    # 鼠标点击事件
    def mousePressEvent(self, event):
        self.flag = True
        self.begin = self.end = event.pos()  # 获取鼠标的位置
        self.signal_order.emit(self.order)  # 释放图像索引位置信号，用于在lineeEdit上显示  1
        self.update()

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.flag:
            self.end = event.pos()
            self.update()
    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        self.flag = False
        # 创建规范化矩阵
        rect = QRect(self.begin, self.end).normalized()
        self.rectangles.append(rect)
        # 获取每一个边缘框的位置，id，文件信息和动作类型 ,
        # rect_attribute 填充算法 解决索引不一致问题
        while self.attrcnt < 10:
            if self.color_dict[self.color_dict_keys[self.attrcnt]] != None:
                tuple_pos = rect.getCoords()
                sca_x = 1280 / 600
                sca_y = 720 / 500
                tuple_pos = (int(tuple_pos[0] * sca_x), int(tuple_pos[1] * sca_y), int(tuple_pos[2] * sca_x),
                             int(tuple_pos[3] * sca_y),)
                self.rect_attribute[self.attrcnt] = tuple_pos # 获取边缘框位置
                self.rect_position[self.attrcnt] = rect.getCoords()
                self.attrcnt += 1
                break
            else:
                self.attrcnt += 1
        self.begin = self.end = QPoint()
        self.update()

    # 鼠标滑轮事件
    def wheelEvent(self, event):
        self.signal_order.emit(self.order)  # 释放图像索引位置信号，用于在lineeEdit上显示  1

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        color_list = []
        # 刷新矩形框
        for i in self.color_dict.values():
            if i != None:
                color_list.append(i)
        # 显示矩形框
        for ind, rectangle in enumerate(self.rectangles):
            painter.setPen(QPen(color_list[ind], 2, Qt.SolidLine))  # 设置画笔颜色
            painter.drawRect(rectangle)  # 绘制矩形框
        # 实现可以从右下角往左上角绘图 很重要
        if not self.begin.isNull() and not self.end.isNull():
            painter.drawRect(QRect(self.begin, self.end).normalized())
