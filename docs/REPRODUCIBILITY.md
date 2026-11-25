# Reproduction notes / 复现说明

[English README](../README.md) · [中文 README](../README.zh-CN.md)

## English

**Environment status:** the historical environment was not locked, and the original `requirements.txt` contains minimum versions. The release preserves those requirements; it is not a verified compatibility matrix for current Python/PyTorch releases. The source loads serialized model objects using `torch.load`; environments that default to weights-only loading may need a reviewed compatibility adjustment. Only load trusted checkpoints. No new training, inference, or GUI execution was performed when preparing this archive.

### Dataset availability

The dataset is **not included**. Its original source and redistribution terms were not established from the supplied files, and the available copy is incomplete:

| Item | Project report | Local archive inspection |
| --- | ---: | ---: |
| Training images | 4,678 | 4,663 |
| Validation images | 1,157 | 1,157 |
| Training label files | — | 4,678; 15 have no matching training image |
| Validation label directory | — | Missing |

The historical project report describes 5,835 images in total. The inspected copy has 5,820. These counts describe different evidence sources; they do not establish which exact files were used in the recorded run. **Restore the missing images and validation labels before attempting to reproduce the metrics.** Do not interpret absent validation annotations as empty ground truth.

Prepare YOLO labels (`class_id x_center y_center width height`, normalized to 0–1) with this layout:

```text
shipdata/datasets/
├── images/
│   ├── train/
│   └── valid/
└── labels/
    ├── train/
    └── valid/
```

Once a complete dataset and the original initial checkpoint are available, the following command reflects the recorded settings. The initial `yolov5s.pt` is not bundled; obtain the intended checkpoint separately. Re-running is not guaranteed to reproduce the original metrics exactly.

```bash
python train.py --weights yolov5s.pt --cfg shipdata/ship_model.yaml --data shipdata/ship_parameter.yaml --hyp runs/train/exp/hyp.yaml --epochs 40 --batch-size 1 --imgsz 640 --workers 0 --optimizer SGD --seed 0 --name harborvision
python val.py --weights runs/train/exp/weights/best.pt --data shipdata/ship_parameter.yaml --imgsz 640 --batch-size 1
```


## 中文

**环境说明：**原项目没有锁定完整环境，`requirements.txt` 主要声明依赖的最低版本。本仓库保留原始依赖，不代表已验证其与当前所有 Python/PyTorch 版本兼容。代码通过 `torch.load` 加载序列化模型对象；默认仅加载权重的环境可能需要经过检查的兼容性调整，请仅加载可信权重。本次归档整理没有重新执行训练、推理或 GUI 运行测试。

### 数据集状态

仓库**未包含原始数据集**。现有材料未确认其原始来源和再分发条款，而且当前本地副本不完整：

| 项目 | 项目报告记载 | 本地文件核查 |
| --- | ---: | ---: |
| 训练图片 | 4,678 | 4,663 |
| 验证图片 | 1,157 | 1,157 |
| 训练标签文件 | — | 4,678，其中 15 个没有对应训练图片 |
| 验证标签目录 | — | 缺失 |

项目报告记载总计 5,835 张图片，当前副本实际包含 5,820 张。这两组数字来自不同材料，不能据此确认历史训练时具体使用了哪些文件。**复现指标前需要补齐缺失图片与验证标签，不能将缺失标签当作“图中没有目标”。**

数据采用 YOLO 文本标注格式，每行为 `class_id x_center y_center width height`，坐标和尺寸归一化至 0–1。目录结构如下：

```text
shipdata/datasets/
├── images/
│   ├── train/
│   └── valid/
└── labels/
    ├── train/
    └── valid/
```

准备好完整数据和原始初始权重后，可以参考以下与历史设置对应的训练命令。仓库未附带初始化用的 `yolov5s.pt`，需要另行准备正确的文件；重新训练不保证完全复现原指标。

```bash
python train.py --weights yolov5s.pt --cfg shipdata/ship_model.yaml --data shipdata/ship_parameter.yaml --hyp runs/train/exp/hyp.yaml --epochs 40 --batch-size 1 --imgsz 640 --workers 0 --optimizer SGD --seed 0 --name harborvision
python val.py --weights runs/train/exp/weights/best.pt --data shipdata/ship_parameter.yaml --imgsz 640 --batch-size 1
```

