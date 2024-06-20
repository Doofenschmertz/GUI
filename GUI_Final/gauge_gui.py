from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import math
import socket
import subprocess
import win32gui
import time

"""

To run the code, make sure that client.py and logo.jpg are in the same folder as this program

Directly run gauge_gui.py, no need to run the client.py code, as that will open automatically

"""
class Gauge(QWidget):
    def __init__(self, title, min_value, max_value,gauge_or_rpm):
        super().__init__()
        self.title = title
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value 
        self.gauge_or_rpm = gauge_or_rpm


    def set_value(self, value):
        if self.min_value <= value <= self.max_value:
            self.value = value
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_gauge(painter)
        
    def draw_gauge(self, painter):
        center = self.rect().center()
        radius = 350

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(center)
        painter.setPen(Qt.NoPen)
    
 
        painter.setBrush(QColor(100, 100, 100))
        painter.drawEllipse(QPointF(0, 0), radius, radius)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(QPointF(0, 0), radius-5, radius-5)

  
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Bebas Neue", 12))
        painter.drawText(QPointF(-30, -radius - 10), self.title)

        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor(255, 255, 255))
        increment = self.max_value // 10

        if self.gauge_or_rpm==0:
            increment = self.max_value//8
        
        for i in range(self.min_value, self.max_value + 1, increment):
            angle = 240 - ((i - self.min_value) * 240 / (self.max_value - self.min_value))
            x = math.cos(math.radians(angle)) * radius * 0.85
            y = -math.sin(math.radians(angle)) * radius * 0.85
            if self.gauge_or_rpm:
                painter.drawText(QPointF(x - 15, y + 5), str(i))
            else:
                painter.drawText(QPointF(x , y ), str(int(i/1000)))
            if self.gauge_or_rpm ==0:
                x = math.cos(math.radians(angle)) * radius * 0.8
                y = -math.sin(math.radians(angle)) * radius * 0.8
                tick_x = math.cos(math.radians(angle)) * radius * 0.78
                tick_y = -math.sin(math.radians(angle)) * radius * 0.78
            else:
                x = math.cos(math.radians(angle)) * radius * 0.8
                y = -math.sin(math.radians(angle)) * radius * 0.8
                tick_x = math.cos(math.radians(angle)) * radius * 0.76
                tick_y = -math.sin(math.radians(angle)) * radius * 0.76
            painter.drawLine(QPointF(tick_x, tick_y), QPointF(x, y))
            
            if i == self.min_value or i== self.max_value:
                continue

        num_intervals = 80

        if self.gauge_or_rpm:
            num_intervals = 100
        
        for j in range(1, num_intervals ):
            small_angle = 240 - j * (240 / num_intervals)
            x_small = math.cos(math.radians(small_angle)) * radius * 0.8
            y_small = -math.sin(math.radians(small_angle)) * radius * 0.8
            tick_x_small = math.cos(math.radians(small_angle)) * radius * 0.79  # Adjust small notch length as needed
            tick_y_small = -math.sin(math.radians(small_angle)) * radius * 0.79  # Adjust small notch length as needed
            painter.drawLine(QPointF(tick_x_small, tick_y_small), QPointF(x_small, y_small))

        # Draw needle
        needle_angle = 240 - ((self.value - self.min_value) * 240 / (self.max_value - self.min_value))
        painter.setPen(QPen(QColor(255, 0, 0),3))
        painter.setBrush(QColor(255, 0, 0))
        needle = [
            QPointF(0, 0),
            QPointF(math.cos(math.radians(needle_angle)) * radius * 0.8,
                    -math.sin(math.radians(needle_angle)) * radius * 0.8)
        ]
        painter.drawPolygon(QPolygon([needle[0].toPoint(), needle[1].toPoint()]))

        # Draw center circle
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(QPointF(0, 0), radius * 0.05, radius * 0.05)
        
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Helvetica", 8))
        if self.gauge_or_rpm:
            value_text = "km/hr"
        else:
            value_text = "  x1000rpm" 
        text_rect = painter.boundingRect(QRectF(-30, radius * 0.2, 60, 30), Qt.AlignCenter, value_text)
        painter.drawText(text_rect, Qt.AlignCenter, value_text)

class Indicator(QWidget):
    def __init__(self, direction):
        super().__init__()
        self.direction = direction
        self.active = False
        self.setFixedSize(250, 250) 

    def set_active(self, active):
        self.active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_indicator(painter)

    def draw_indicator(self, painter):
        rect = self.rect()
        painter.setRenderHint(QPainter.Antialiasing)

        
        if self.active:
            painter.setBrush(QColor(0, 255, 0))
        else:
            painter.setBrush(QColor(255, 0, 0))

        center_x = rect.center().x()
        center_y = rect.center().y()
        arrow_size = min(rect.width(), rect.height()) // 8  

        if self.direction == 'L':
            points = [
                QPointF(center_x - arrow_size, center_y),
                QPointF(center_x + arrow_size, center_y - arrow_size),
                QPointF(center_x + arrow_size, center_y - arrow_size/2),
                QPointF(center_x + 3*arrow_size, center_y - arrow_size/2),
                QPointF(center_x + 3*arrow_size, center_y + arrow_size/2),
                QPointF(center_x + arrow_size, center_y + arrow_size/2),
                QPointF(center_x + arrow_size, center_y + arrow_size)
                
            ]
        else:
            points = [
                QPointF(center_x + arrow_size, center_y),
                QPointF(center_x - arrow_size, center_y + arrow_size),
                QPointF(center_x - arrow_size, center_y + arrow_size/2),
                QPointF(center_x - 3*arrow_size, center_y + arrow_size/2),
                QPointF(center_x - 3*arrow_size, center_y - arrow_size/2),
                QPointF(center_x - arrow_size, center_y - arrow_size/2),
                QPointF(center_x - arrow_size, center_y - arrow_size)
            ]

        painter.drawPolygon(QPolygon([point.toPoint() for point in points]))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image = QPixmap("logo.jpg")
        self.image = self.image.scaled(self.image.width() // 3, self.image.height() // 3, Qt.KeepAspectRatio)

    def initUI(self):
        self.setWindowTitle('Analog Gauges with Indicators')
        self.setGeometry(0, 0, 800, 600)  # Initial size before fullscreen

        # Calculate screen dimensions
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)
        self.setStyleSheet('background-color : rgb(0, 0, 30);')

        main_layout = QVBoxLayout()
        indicators_layout = QHBoxLayout()
        gauges_layout = QHBoxLayout()

        self.left_indicator = Indicator('L')
        self.right_indicator = Indicator('R')
        indicators_layout.addWidget(self.left_indicator)
        indicators_layout.addWidget(self.right_indicator)
        
        self.speedometer = Gauge("SPEED", 0, 180,1)
        self.rpm_gauge = Gauge("RPM", 0, 8000,0)
        gauges_layout.addWidget(self.speedometer)
        gauges_layout.addWidget(self.rpm_gauge)

        main_layout.addLayout(indicators_layout)
        main_layout.addLayout(gauges_layout)
        self.setLayout(main_layout)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        

        border_rect = QRect(25, 25, self.width() - 50, self.height() - 50)
        border_radius = 20  

        painter.setPen(QPen(Qt.white, 0.8)) 
        painter.setBrush(Qt.NoBrush) 
        painter.drawRoundedRect(border_rect, border_radius, border_radius)

        rect = self.rect()
        center_x = rect.center().x()
        center_y = rect.center().y()

        image_x = int(center_x - (self.image.width() / 2))
        image_y = int(center_y - (self.image.height() / 2)) - 300

        

        painter.drawPixmap(image_x, image_y, self.image)


        super().paintEvent(event)

class InputThread(QThread):
    speed_changed = pyqtSignal(int)
    rpm_changed = pyqtSignal(int)
    left_indicator_changed = pyqtSignal(bool)
    right_indicator_changed = pyqtSignal(bool)

    def run(self):
        left_indicator_state = False
        right_indicator_state = False

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 65432))
        server_socket.listen(1)

        print("Server started. Waiting for connections...")

        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                print(f"Received data: {data}")
                
                if data == "exit":
                    QApplication.quit()
                parts = data.split(',')
                if len(parts) == 2:
                    command, value = parts
                    if command == 'speed':
                        speed = int(value)
                        if 0 <= speed <= 180:
                            self.speed_changed.emit(speed)
                        else:
                            print("Invalid speed! Enter a number between 0 and 180.")
                    elif command == 'rpm':
                        rpm = int(value)
                        if 0 <= rpm <= 8000:
                            self.rpm_changed.emit(rpm)
                        else:
                            print("Invalid RPM! Enter a number between 0 and 8000.")
                    elif command == 'left_indicator':
                        if value == 'toggle':
                            left_indicator_state = not left_indicator_state
                            self.left_indicator_changed.emit(left_indicator_state)
                    elif command == 'right_indicator':
                        if value == 'toggle':
                            right_indicator_state = not right_indicator_state
                            self.right_indicator_changed.emit(right_indicator_state)
                    else:
                        print("Invalid command!")
                else:
                    print("Invalid input format! Expected 'command,value'.")
            except ValueError:
                print("Invalid input! Ensure correct format and values.")
            except socket.error as e:
                print(f"Socket error: {e}")
                break

        client_socket.close()
        server_socket.close()

def launch_client_script():
    subprocess.Popen(['start', 'cmd', '/k', 'python', 'client.py'], shell=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()

    QTimer.singleShot(200, launch_client_script)
    
    
    input_thread = InputThread()
    input_thread.speed_changed.connect(main_window.speedometer.set_value)
    input_thread.rpm_changed.connect(main_window.rpm_gauge.set_value)
    input_thread.left_indicator_changed.connect(main_window.left_indicator.set_active)
    input_thread.right_indicator_changed.connect(main_window.right_indicator.set_active)
    input_thread.start()

    sys.exit(app.exec_())
