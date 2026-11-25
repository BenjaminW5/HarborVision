from utils.augmentations import letterbox
from pathlib import Path
import numpy as np
import torch
import argparse
import re
from collections import Counter
import os
import sys
from pathlib import Path

import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_boxes, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync
from utils.general import cv2

from PyQt5.QtCore import *


class MyModel(QThread):
    showImageSignal = pyqtSignal(np.ndarray)
    wait_model_if = pyqtSignal(bool)
    total_sta = pyqtSignal(str)

    def __init__(self):
        super(MyModel, self).__init__()
        self.weights = '../runs/train/exp/weights/best.pt'
        self.data = '../shipdata/ship_parameter.yaml'
        self.confidence = 0.25
        self.iou = 0.45
        self.source = './people.mp4'

        self.video_break = False
        self.video_pause = False
        self.video_continue = False
        self.wait_model = True

    @torch.no_grad()
    def run(
            self,
            imgsz=(640, 640),  # inference size (height, width)
            max_det=1000,  # maximum detections per image
            device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
            view_img=False,  # show results
            save_txt=False,  # save results to *.txt
            save_conf=False,  # save confidences in --save-txt labels
            save_crop=False,  # save cropped prediction boxes
            nosave=False,  # do not save images/videos
            classes=None,  # filter by class: --class 0, or --class 0 2 3
            agnostic_nms=False,  # class-agnostic NMS
            augment=False,  # augmented inference
            visualize=False,  # visualize features
            update=False,  # update all models
            project=ROOT / 'runs/detect',  # save results to project/name
            name='exp',  # save results to project/name
            exist_ok=False,  # existing project/name ok, do not increment
            line_thickness=3,  # bounding box thickness (pixels)
            hide_labels=False,  # hide labels
            hide_conf=False,  # hide confidences
            half=False,  # use FP16 half-precision inference
            dnn=False,  # use OpenCV DNN for ONNX inference
    ):
        source = str(self.source)  # 被检测图片的文件夹
        path = Path(source)
        form = path.absolute().parent
        last = path.suffix
        name = path.name.split('.')[0] + '_detect_'
        path_save = os.path.join(form, name, last)

        save_img = not nosave and not source.endswith('.txt')  # 只有在nosave为False并且source文件夹不以.txt结尾的时候对图片进行存储
        is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)  # suffix应该是用来获取文件的后缀名的，这句话是在判断source是不是图片或视频路径
        is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
        webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)  # isnumeric用于检测字符串是否只包含数字
        if is_url and is_file:
            source = check_file(source)  # download

        # Directories  就是在创建输出文件夹
        save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
        (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

        # Load model
        device = select_device(device)  # 选择进行检测的设备
        model = DetectMultiBackend(self.weights, device=device, dnn=dnn, data=self.data, fp16=half)
        stride, names, pt = model.stride, model.names, model.pt
        imgsz = check_img_size(imgsz, s=stride)  # check image size imgsz:[640, 640]

        # Dataloader
        if webcam:  # 好像是去网上下载
            view_img = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
            bs = len(dataset)  # batch_size
        else:
            dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)  # 重点看数据集的制作！！！！！
            bs = 1  # batch_size
        vid_path, vid_writer = [None] * bs, [None] * bs

        # Run inference
        model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup self.jit和self.fp16等都用在这里进行模型的预热(warm up)
        dt, seen = [0.0, 0.0, 0.0], 0
        for path, im, im0s, vid_cap, s in dataset:
            # path是图片的路径，im是经过resize和pad后的图像，im0s是原始的图像，vid_cap是None，s是字符串用于展示图片信息
            # 对每一张图片进行处理，得到可以进行forward的tensor
            if self.video_break:
                self.quit()
                break
            if self.video_pause:
                while True:
                    self.sleep(1)
                    if self.video_continue:
                        break

            t1 = time_sync()
            im = torch.from_numpy(im).to(device)  # 把numpy转为tensor并传入GPU
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0  # 进行归一化处理
            if len(im.shape) == 3:  # 只有三个维度
                im = im[
                    None]  # expand for batch dim 增加一个新的维度(bath_size的维度)，比如此时im:tensor(1, 3, 384, 640) -> (batch_size, channels, w, h)
            t2 = time_sync()
            dt[0] += t2 - t1

            # Inference  前向推理
            visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
            pred = model(im, augment=augment, visualize=visualize)  # 进行前馈，得到预测值
            t3 = time_sync()
            dt[1] += t3 - t2

            # NMS 非极大值抑制
            pred = non_max_suppression(pred, self.confidence, self.iou, classes, agnostic_nms, max_det=max_det)
            dt[2] += time_sync() - t3


            # Process predictions
            for i, det in enumerate(pred):
                # 每一张图片预测的结果, 这里的pred是一个列表，里面只有多个tensor
                # .eg:pred只有一个tensor,说明只预测出了一个物体,此tensor的shape为(1, 6)，这个物体的类别概率存储在那6列中
                seen += 1
                if webcam:  # batch_size >= 1
                    p, im0, frame = path[i], im0s[i].copy(), dataset.count
                    s += f'{i}: '
                else:
                    p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)  # getattr用于获取对象的属性

                p = Path(p)  # to Path
                save_path = str(save_dir / p.name)  # im.jpg
                txt_path = str(save_dir / 'labels' / p.stem) + (
                    '' if dataset.mode == 'image' else f'_{frame}')  # im.txt
                s += '%gx%g ' % im.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1,
                                              0]]  # normalization gain whwh 返回的是一个tensor[width, height, width, height], .eg:[1920, 1080, 1920, 1080]
                imc = im0.copy() if save_crop else im0  # for save_crop
                annotator = Annotator(im0, line_width=line_thickness, example=str(names))  # ？？？？输出了每一张图片的结果
                # im 是一个ndarray，lw应该是绘制的线的宽度，pil是是否有特殊字符（如中文）
                if len(det):
                    # Rescale boxes from img_size to im0 size 由于存在缩放的问题，所以将训练的图片的大小返回到原始的图片大小
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    # Write results
                    string_content = ''
                    for *xyxy, conf, cls in reversed(det):
                        if save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                            with open(txt_path + '.txt', 'a') as f:
                                f.write(('%g ' * len(line)).rstrip() % line + '\n')
                        if save_img or save_crop or view_img:  # Add bbox to image在图像上绘制预测框和概率
                            c = int(cls)  # integer class
                            label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                            # 这里label存储的是预测出的类别和对应的概率，如：ore carrier 0.90

                            string_content += (label + '\n')

                            annotator.box_label(xyxy, label, color=colors(c, True))
                            # 在图像上进行绘制，color是一个类，返回了一个有三个元素的tuple，xyxy对应四个坐标，label代表的是类别和概率
                            if save_crop:
                                save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)
                    names_content = [re.sub(r'\d+.\d+', '', content) for content in string_content.split('\n')]
                    dic = Counter(names_content)
                    contents = [key + str(value) for key, value in dic.items()]
                    content = '\n'.join(contents)
                    self.total_sta.emit(content)

                # Stream results
                im0 = annotator.result()  # 此时im0变成ndarray,其实也就是图片
                if self.wait_model:
                    self.wait_model_if.emit(True)
                self.showImageSignal.emit(im0)
                if view_img:
                    cv2.imshow(str(p), im0)
                    cv2.waitKey(1)  # 1 millisecond

                # Save results (image with detections)  保存绘制好的图片
                if save_img:
                    if dataset.mode == 'image':
                        cv2.imwrite(save_path, im0)  # 用opencv来保存图片，这里保存的是im0
                    else:  # 'video' or 'stream'
                        if vid_path[i] != save_path:  # new video
                            vid_path[i] = save_path
                            if isinstance(vid_writer[i], cv2.VideoWriter):
                                vid_writer[i].release()  # release previous video writer
                            if vid_cap:  # video
                                fps = vid_cap.get(cv2.CAP_PROP_FPS)
                                w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            else:  # stream
                                fps, w, h = 30, im0.shape[1], im0.shape[0]
                            save_path = str(Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                            # vid_writer[i] = cv2.VideoWriter(path_save, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                        # vid_writer[i].write(im0)

            # Print time (inference-only)
            LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')

        # Print results
        t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
        LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
        # if save_txt or save_img:
        # s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        # LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
        if update:
            strip_optimizer(self.weights)  # update model (to fix SourceChangeWarning)


if __name__ == '__main__':
    model = MyModel()
    model.run()
