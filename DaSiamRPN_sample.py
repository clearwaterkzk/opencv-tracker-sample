import argparse
import copy
import csv
import os
import re
import sys
import time

import cv2


def get_args():
    """引数を取得する"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--device",
        help="camera device or movie file path",
        default="sample_movie/bird_short.mp4",
    )
    parser.add_argument(
        "--outpath",
        help="output video file path",
        default=None,
    )
    parser.add_argument(
        "--resize",
        help="resize parameter",
        type=float,
        default=1.0,
    )

    args = parser.parse_args()

    return args


def isint(s):
    p = "[-+]?\d+"
    return True if re.fullmatch(p, s) else False


def initialize_tracker(window_name, image):
    """Trackerを初期化する"""
    params = cv2.TrackerDaSiamRPN_Params()
    params.model = "model/DaSiamRPN/dasiamrpn_model.onnx"
    params.kernel_r1 = "model/DaSiamRPN/dasiamrpn_kernel_r1.onnx"
    params.kernel_cls1 = "model/DaSiamRPN/dasiamrpn_kernel_cls1.onnx"
    tracker = cv2.TrackerDaSiamRPN_create(params)

    # 追跡対象指定
    while True:
        bbox = cv2.selectROI(window_name, image)

        try:
            tracker.init(image, bbox)
        except Exception as e:
            print(e)
            continue

        return tracker


def main():
    color_list = [
        [255, 0, 0],  # blue
    ]

    # 引数解析 #################################################################
    args = get_args()
    cap_device = args.device
    outpath = args.outpath
    resize = args.resize

    # カメラ準備 ###############################################################
    if isint(cap_device):
        cap_device = int(cap_device)
    cap = cv2.VideoCapture(cap_device)
    width, height = (
        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    )
    width_resized, height_resized = int(width * resize), int(height * resize)
    fps = cap.get(cv2.CAP_PROP_FPS)

    cap_device_message = (
        f"input video : {cap_device}" if cap_device != 0 else "input camera(0)"
    )
    print(cap_device_message)
    if outpath is not None:
        print("outpath : ", outpath)
        print(" fps : ", fps)
        print(" width : ", width)
        print(" height : ", height)
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(outpath, fourcc, fps, (width_resized, height_resized))

        # CSVファイルのパスを動画出力先と同じディレクトリに設定
        output_dir = os.path.dirname(outpath)
        base_name = os.path.splitext(os.path.basename(outpath))[0]
        csv_name = os.path.join(output_dir, f"{base_name}_coordinates.csv")

        csv_file = open(csv_name, mode="w", newline="")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["frame_number", "center_x", "center_y"])

    # Tracker初期化 ############################################################
    window_name = "Tracker Demo"
    cv2.namedWindow(window_name)

    ret, image = cap.read()
    if not ret:
        sys.exit("Can't read first frame")
    tracker = initialize_tracker(window_name, image)

    while cap.isOpened():
        ret, image = cap.read()
        if not ret:
            break
        debug_image = copy.deepcopy(image)

        # 追跡アップデート
        start_time = time.time()
        ok, bbox = tracker.update(image)
        elapsed_time = time.time() - start_time
        if ok:
            # 追跡後のバウンディングボックス描画
            cv2.rectangle(debug_image, bbox, color_list[0], thickness=5)
            x = bbox[0]
            y = bbox[1]
            w = bbox[2]
            h = bbox[3]
            center_x = int(x + w / 2)
            center_y = int(y + h / 2)
        else:
            center_x, center_y = 0, 0
        cv2.circle(debug_image, (center_x, center_y), 10, color_list[0], thickness=3)
        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        # 各アルゴリズム処理時間描画
        cv2.putText(
            debug_image,
            "DaSiamRPN" + " : " + "{:.1f}".format(elapsed_time * 1000) + "ms",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color_list[0],
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(window_name, debug_image)

        if outpath is not None:
            resize_img = cv2.resize(debug_image, (width, height))
            out.write(resize_img)
            csv_writer.writerow([frame_number, center_x, center_y])

        k = cv2.waitKey(1)
        if k == 32:  # SPACE
            # 追跡対象再指定
            tracker = initialize_tracker(window_name, image)
        if k == 27:  # ESC
            break
    cap.release()
    if outpath is not None:
        out.release()
        csv_file.close()


if __name__ == "__main__":
    main()
