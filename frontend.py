import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import mediapipe as mp
import pyautogui
import time

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def run(self):
        cam = cv2.VideoCapture(0)
        face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        screen_w, screen_h = pyautogui.size()
        while True:
            ret, cv_img = cam.read()
            if ret:
                cv_img = cv2.flip(cv_img, 1)
                rgb_frame = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                output = face_mesh.process(rgb_frame)
                landmark_points = output.multi_face_landmarks
                if landmark_points and landmark_points[0]:
                    landmarks = landmark_points[0].landmark
                    for id, landmark in enumerate(landmarks[474:478]):
                        x = int(landmark.x * cv_img.shape[1])
                        y = int(landmark.y * cv_img.shape[0])
                        cv2.circle(cv_img, (x, y), 3, (0, 255, 0), -1)
                        if id == 1:
                            screen_x = screen_w * landmark.x
                            screen_y = screen_h * landmark.y
                            pyautogui.moveTo(screen_x, screen_y)
                    left = [landmarks[145], landmarks[159]]
                    for landmark in left:
                        x = int(landmark.x * cv_img.shape[1])
                        y = int(landmark.y * cv_img.shape[0])
                        cv2.circle(cv_img, (x, y), 3, (0, 255, 255), -1)
                    if (left[0].y - left[1].y) < 0.004:
                        pyautogui.click()
                        time.sleep(1)
                convert_to_qt_format = QImage(cv_img.data, cv_img.shape[1], cv_img.shape[0], QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                self.change_pixmap_signal.emit(p)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eye Controlled Mouse")
        self.disply_width = 640
        self.display_height = 480
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        self.btn = QPushButton('Start/Stop', self)
        self.btn.clicked.connect(self.control_device)
        self.btn.resize(self.btn.sizeHint())
        self.btn.move(260, 500)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.btn)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_image(self, cv_img):
        qt_img = QPixmap.fromImage(cv_img)
        self.image_label.setPixmap(qt_img)

    def control_device(self):
        # You can add functionality to start/stop the tracking here.
        pass

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())
