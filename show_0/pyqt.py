from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QImage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from desgner import Ui_Form
from video import MyModel
import sys
import cv2


class QmyWidget(QWidget):  # 继承QMainWindow类
    def __init__(self, parent=None):
        super(QmyWidget, self).__init__(parent)  # 调用父类的构造方法
        self.ui = Ui_Form()  # 创建类的私有属性ui
        self.ui.setupUi(self)  # 自身self就是一个实例，传入构造所有的组件
        self.ui.file.setFixedSize(60, 60)
        self.ui.pt.setFixedSize(60, 60)


        self.resize(QSize(800, 600))

        self.module = MyModel()
        self.module.showImageSignal.connect(lambda x: self.show_image(x, self.ui.video))
        self.module.wait_model_if.connect(self.wait_model_show)
        self.module.total_sta.connect(self.show_results)


    @staticmethod
    def show_image(image, label):
        try:
            ih, iw, _ = image.shape
            w = label.geometry().width()
            h = label.geometry().height()
            # 保持纵横比
            # 找出长边
            if iw > ih:
                scal = w / iw
                nw = w
                nh = int(scal * ih)
                img_src_ = cv2.resize(image, (nw, nh))

            else:
                scal = h / ih
                nw = int(scal * iw)
                nh = h
                img_src_ = cv2.resize(image, (nw, nh))

            frame = cv2.cvtColor(img_src_, cv2.COLOR_BGR2RGB)
            img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[2] * frame.shape[1],
                         QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(img))

        except Exception as e:
            print(repr(e))

    @pyqtSlot()
    def on_file_clicked(self):
        cur_path = QDir.currentPath()
        title = '选择视频文件'
        filt = '视频文件(*.wmv *.avi *.mp4);;所有文件(*.*)'
        fileName, flt = QFileDialog.getOpenFileNames(self, title, cur_path, filt)
        if fileName:  # 判空是为了防止选视频时点了退出
            fileName = fileName[0]
        else:
            return
        self.ui.file_location.setText(fileName)  # 在“当前视频位置”那里进行显示
        self.module.source = fileName
        if self.module.wait_model:
            self.ui.video.setText('\t\t\t\t正在加载模型......')
        self.module.start()

    def wait_model_show(self, state):  # 将显示的内容置为空，表明已经加载好了模型
        if state:
            self.ui.video.setText('')
        self.module.wait_model = False

    @pyqtSlot()
    def on_module_finished(self):
        self.module.wait_model = True

    @pyqtSlot()
    def on_start_clicked(self):
        if self.module.video_pause:
            self.module.video_continue = True
            self.module.video_pause = False

    @pyqtSlot()
    def on_pause_clicked(self):
        self.module.video_pause = True

    @pyqtSlot()
    def on_end_clicked(self):
        self.module.video_break = True

    @pyqtSlot(int)
    def on_iou_valueChanged(self, value):
        self.ui.iou_show.setText(str(value / 100))
        self.module.iou = value / 100

    @pyqtSlot(int)
    def on_confidence_valueChanged(self, value):
        self.ui.con_show.setText(str(value / 100))
        self.module.confidence = value / 100

    def on_pt_clicked(self):  # 改变权重
        cur_path = QDir.currentPath()
        title = '选择权重文件'
        filt = '权重文件(.pt)'
        fileName, flt = QFileDialog.getOpenFileNames(self, title, cur_path, filt)
        if fileName:
            fileName = fileName[0]
        else:
            return
        self.module.weights = fileName

    def show_results(self, content):
        self.ui.results.setPlainText(content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./pic/yolo.png'))  # 设置图标
    myWidget = QmyWidget()

    # 读取qss文件，美化窗口
    file = QFile('./beauty.qss')
    file.open(QFile.ReadOnly)
    qt_bytes = file.readAll()
    py_bytes = qt_bytes.data()
    style_str = py_bytes.decode('utf-8')
    app.setStyleSheet(style_str)
    myWidget.show()
    sys.exit(app.exec_())
