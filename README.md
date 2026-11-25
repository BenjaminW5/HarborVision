# HarborVision · 港湾视界

**Seven-class ship detection with YOLOv5 — from training to a desktop video demo.**

English | [简体中文](README.zh-CN.md)

HarborVision is a personal deep learning project for detecting and classifying ships in images and video. It brings together a customized YOLOv5 configuration, archived training checkpoints, evaluation plots, and a PyQt5 desktop interface. The name combines *harbor* with *computer vision*.

Built on [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5), this repository preserves the project implementation and its recorded results. It does not claim a new detection architecture or a production-ready navigation system.

## Highlights

- **7 vessel categories**, with bounding boxes, class labels, and confidence scores.
- **40-epoch training archive**, including `best.pt`, `last.pt`, CSV metrics, and original plots.
- **Image and video inference** through `detect.py`.
- **PyQt5 video interface** with file/weight selection, confidence and IoU controls, pause/resume, and displayed detection counts. Counts are detections, not unique-vessel tracking.
- **Bilingual documentation** with explicit provenance and reproduction limits.

## Personal contributions and engineering work

**BenjaminW5 independently implemented the ship-detection application and its experiments**, including data preparation and annotation processing, model configuration, training and tuning, evaluation, and the PyQt5 desktop interface. The underlying detection framework is Ultralytics YOLOv5.

| Area | Implementation and repository evidence |
| --- | --- |
| Data preparation | Seven-class mapping, YOLO annotation format, and train/validation paths in `shipdata/ship_parameter.yaml` |
| Model adaptation | Seven-class detection head and depth/width configuration in `shipdata/ship_model.yaml` |
| Training and tuning | 40 epochs with SGD, image size 640, batch size 1, and workers 0; settings and checkpoints retained |
| Evaluation | Precision, recall, both mAP metrics, PR curves, and a confusion matrix |
| Application development | PyQt5 and OpenCV video display, checkpoint selection, threshold controls, and pause/resume functionality |

### Engineering highlights

- **Model-to-application workflow:** connects dataset configuration, training, evaluation, command-line inference, and desktop interaction.
- **Resource-conscious training configuration:** small batches reduce per-batch memory requirements, while single-process loading simplifies data loading. No separate memory or speed comparison was conducted.
- **Traceable experimental evidence:** metrics refer to the original CSV; checkpoints and figures have SHA-256 checksums, with dataset gaps explicitly documented.

### Resume description

> **HarborVision | YOLOv5 Ship Detection and Visualization**  
> Independently prepared data, configured and trained a seven-class ship detector, analyzed evaluation results, and developed a PyQt5/OpenCV video interface with checkpoint selection, confidence/IoU controls, and pause/resume functionality. Completed 40 training epochs, achieving archived validation mAP@0.5 of 71.39%, precision of 77.34%, and recall of 64.17%; packaged model checkpoints, evaluation figures, and bilingual documentation.

## Recorded results

The values below come from the **final row (epoch index 39, the 40th epoch)** of [`runs/train/exp/results.csv`](runs/train/exp/results.csv). They are archived validation metrics, not a newly executed benchmark or independent test-set results.

| Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
| ---: | ---: | ---: | ---: |
| 77.34% | 64.17% | 71.39% | 37.65% |

![Training losses and validation metrics across 40 epochs](runs/train/exp/results.png)

<details>
<summary>Precision–recall curve and confusion matrix</summary>

![Precision–recall curve](runs/train/exp/PR_curve.png)
![Confusion matrix](runs/train/exp/confusion_matrix.png)

</details>

### Archived predictions

![Original validation batch predictions](runs/train/exp/val_batch0_pred.jpg)

This unmodified validation visualization includes a distant ship without a visible prediction and overlapping class predictions on a passenger vessel. It illustrates remaining detection and classification errors as well as the output format; it is not a curated claim of uniformly correct predictions. Additional batches and their ground-truth visualizations are in [`runs/train/exp`](runs/train/exp).

## Classes

IDs must retain the order in [`shipdata/ship_parameter.yaml`](shipdata/ship_parameter.yaml).

| ID | Label | 中文说明 |
| ---: | --- | --- |
| 0 | ore carrier | 矿砂船 |
| 1 | bulk cargo carrier | 散货船 |
| 2 | general cargo ship | 杂货船 |
| 3 | container ship | 集装箱船 |
| 4 | fishing boat | 渔船 |
| 5 | passenger ship | 客船 |
| 6 | gondola | 贡多拉船 |

## Quick start

Clone the repository and install dependencies in a dedicated Python environment:

```bash
git clone https://github.com/BenjaminW5/HarborVision.git
cd HarborVision
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in Windows PowerShell, or `source .venv/bin/activate` on Linux/macOS, then:

```bash
python -m pip install -r requirements.txt
python detect.py --weights runs/train/exp/weights/best.pt --data shipdata/ship_parameter.yaml --source path/to/ships.jpg --imgsz 640 --conf-thres 0.25 --device cpu
```

Replace `path/to/ships.jpg` with your own image, image directory, or video path. A video example:

```bash
python detect.py --weights runs/train/exp/weights/best.pt --source path/to/ships.mp4 --imgsz 640 --conf-thres 0.25
```

Results are written under `runs/detect/exp*`. Add `--save-txt --save-conf` to save detections as text. Use `--device 0` with a compatible CUDA-enabled PyTorch installation to select the first GPU.

**Environment status:** the historical environment was not locked, and the original `requirements.txt` contains minimum versions. The release preserves those requirements; it is not a verified compatibility matrix for current Python/PyTorch releases. The source loads serialized model objects using `torch.load`; environments that default to weights-only loading may need a reviewed compatibility adjustment. Only load trusted checkpoints. No new training, inference, or GUI execution was performed when preparing this archive.

### Desktop interface

```bash
python -m pip install -r requirements-gui.txt
python launch_gui.py
```

Choose a video in the interface; it starts processing after selection. The default checkpoint points to the included trained `best.pt`. The interface also supports selecting a different checkpoint and changing confidence/IoU thresholds. `launch_gui.py` is a packaging helper that sets the working directory and import paths expected by the original UI. The original UI and inference implementation are preserved.

## Training and validation

The archived [`opt.yaml`](runs/train/exp/opt.yaml) records:

| Setting | Value |
| --- | --- |
| Model configuration | `shipdata/ship_model.yaml` |
| Depth / width multipliers | `0.33` / `0.25` |
| Initial checkpoint argument | `yolov5s.pt` |
| Epochs / batch size / image size | `40` / `1` / `640` |
| Optimizer / initial learning rate | SGD / `0.01` |
| Workers / seed | `0` / `0` |

The **custom architecture has width multiplier 0.25**. Although the initial checkpoint argument is named `yolov5s.pt`, that filename does not make the configured network a standard YOLOv5s architecture. Weight transfer depends on compatible tensor shapes.

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

## Repository layout

```text
HarborVision/
├── README.md / README.zh-CN.md
├── detect.py / train.py / val.py / export.py
├── models/                     # YOLOv5 model implementation
├── utils/                      # Data loading, metrics, plotting, etc.
├── shipdata/                   # Seven-class dataset and model configuration
├── show_0/                     # Original PyQt interface and video inference
├── launch_gui.py               # Portable entry point for the archived UI
├── runs/train/exp/             # Formal 40-epoch results and both checkpoints
├── docs/artifact-sha256.json    # Checksums for archived training artifacts
└── docs/upstream/              # Original upstream README files (historical reference)
```

The formal artifacts were copied from the supplied project's separate `训练结果/exp` folder, **not** from the earlier experimental runs under its source tree. Raw datasets, videos, caches, IDE files, unrelated files, and internal project reports are excluded. The original local project is unchanged.

## Attribution and license

HarborVision is a personal project by **BenjaminW5**, covering ship-specific configuration, model training and evaluation, and a desktop demonstration. The core detection framework is by **Ultralytics and the YOLOv5 contributors**. Original source notices and the supplied [GNU AGPL-3.0 license](LICENSE) are retained. The upstream README copies are historical references and may contain links that are relative to their original location.

Model artifacts and result images are preserved from the supplied project archive. Their presence does not establish a separate license for the underlying dataset or third-party media.
