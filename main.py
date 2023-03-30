#!usr/bin/env python
#-*- coding:utf-8 -*-
import typing
import mouse
import keyboard
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import yaml
from PIL import ImageGrab

with open('./config.yml', 'r', encoding='utf-8') as f:
    frame_config = yaml.load(f.read(), Loader=yaml.FullLoader)

class FrameWindow(QWidget):
    def __init__(self,capture_width ,capture_height, color,stroke ,parent=None):
        super(FrameWindow, self).__init__(parent)
        self.capture_width, self.capture_height = capture_width, capture_height
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # 去除界面边框，保持在顶层
        self.setAttribute(Qt.WA_TranslucentBackground) # 背景透明
        self.setWindowTitle('文文。截图')
        self.stroke = stroke
        self.color = color
        self.scale = 1.0
        self.shown = False
        self.focus_x = 0
        self.focus_y = 0
        
    def show(self,n=0) -> None:
        mouse.hook(self.mouseControl)
        self.focusPosition(*mouse.get_position())
        super().show()
        self.shown = True
        return super().show()
        
    
    def hide(self) -> None:
        mouse.unhook_all()
        self.shown = False
        return super().hide()
    
    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setPen(QPen(QBrush(QColor(self.color)),self.stroke))
        painter.drawRect(self.stroke,self.stroke,self.width()-2*self.stroke,self.height()-2*self.stroke)
    
    
        
    def focusPosition(self,x,y):
        self.focus_x = x
        self.focus_y = y
        
    def changeZoom(self,zoom):
        self.scale = zoom
        
    def mouseControl(self,event):
        if type(event) == mouse.MoveEvent:
            self.focusPosition(event.x,event.y)
            
        if not keyboard.is_pressed('F8'):
            return True
        
        if type(event) == mouse.WheelEvent:
            self.changeZoom(self.scale + event.delta * 0.1 * self.scale)

        if type(event) == mouse.ButtonEvent and event.event_type == 'down':
            if event.button == 'left':
                self.shown = False
                img = ImageGrab.grab(bbox=(self.x()+2*self.stroke,self.y()+2*self.stroke,self.x()+self.width()-2*self.stroke,self.y()+self.height()-2*self.stroke),all_screens=True)
                img = img.resize((self.capture_width,self.capture_height))
                img.show()
                
            if event.button == 'right':
                self.shown = False
        
        return True
        

class FrameUpdater(QTimer):
    def __init__(self,target: FrameWindow,parent: typing.Optional[QObject] = ...) -> None:
        self.target = target
        super().__init__(parent)
    def timerEvent(self, a0: QTimerEvent) -> None:
        if not self.target.shown and not self.target.isVisible():
            return super().timerEvent(a0)
        self.target.resize(int(self.target.capture_width*self.target.scale)+4*self.target.stroke,int(self.target.capture_height*self.target.scale)+4*self.target.stroke)
        self.target.move(self.target.focus_x-self.target.width()//2,self.target.focus_y-self.target.height()//2)
        if self.target.isVisible()!=self.target.shown:
            if self.target.shown:
                self.target.show()
            else:
                self.target.hide()
        return super().timerEvent(a0)

class MainWindow(QWidget):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint )
        self.setFixedSize(200,100)
        self.setWindowTitle('文文。截图')
        self.captureFrame = FrameWindow(**frame_config)
        self.frameUpdater = FrameUpdater(self.captureFrame,self)
        self.frameUpdater.start(10)
        
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("点击开启取景框\nF8+滚轮调整大小\nF8+左键截图\nF8+右键取消"))
        self.setLayout(vbox)
        
    def mousePressEvent(self, a0) -> None:
        self.captureFrame.shown = True
        return super().mousePressEvent(a0)
    def closeEvent(self, a0) -> None:
        self.frameUpdater.stop()
        self.captureFrame.close()
        return super().closeEvent(a0)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    
    m = MainWindow()
    m.show()
    
    sys.exit(app.exec_())