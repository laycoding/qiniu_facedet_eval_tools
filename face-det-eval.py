# coding:utf-8
#!/usr/bin/env python2
# created by atlab weidong zhang

import os
import sys
import json
import argparse
import random

def save_library_dict(lib_file, task_type):
    lib_dict = {}
    with open(lib_file, 'r') as f:
        for line in f:
            img_info = json.loads(line.strip())
            img_name = img_info['url'].split('/')[-1]
            if task_type == 'classification':
                label = img_info['label'][0]['data'][0]['class']
                lib_dict[img_name] = label
            elif task_type == 'detection' or task_type == 'face':
                data = img_info['label'][0]['data']
                lib_dict[img_name] = data
    return lib_dict
# 计算两个框的iou
# bbox: [[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]]
def cal_iou(bbox_a, bbox_b):
    Reframe = [bbox_a[0][0], bbox_a[0][1], bbox_a[2][0], bbox_a[2][1]]
    GTframe = [bbox_b[0][0], bbox_b[0][1], bbox_b[2][0], bbox_b[2][1]]
    x1 = Reframe[0]
    y1 = Reframe[1]
    width1 = Reframe[2]-Reframe[0]
    height1 = Reframe[3]-Reframe[1]

    x2 = GTframe[0]
    y2 = GTframe[1]
    width2 = GTframe[2]-GTframe[0]
    height2 = GTframe[3]-GTframe[1]

    endx = max(x1+width1, x2+width2)
    startx = min(x1, x2)
    width = width1+width2-(endx-startx)

    endy = max(y1+height1, y2+height2)
    starty = min(y1, y2)
    height = height1+height2-(endy-starty)

    if width <= 0 or height <= 0:
        ratio = 0  # 重叠率为 0
    else:
        Area = width*height  # 两矩形相交面积
        Area1 = width1*height1
        Area2 = width2*height2
        ratio = Area*1./(Area1+Area2-Area)
    return ratio

def get_bestmatch_bbox(sand_data_i, labeled_data):
    if 'roll_cls' not in sand_data_i:
        sand_data_i_class = "face"
    else:
        sand_data_i_class = sand_data_i['roll_cls']
    sand_data_i_bbox = sand_data_i['pts']
    max_iou, max_idx = 0.0, -1
    for i in range(len(labeled_data)):
        if 'roll_cls' not in labeled_data[i]:
            labeled_data_i_class = "face"
        else:
            labeled_data_i_class = labeled_data[i]['roll_cls']
        if not (sand_data_i_class == labeled_data_i_class):
            continue
        labeled_data_i_bbox = labeled_data[i]['pts']
        iou_ratio = cal_iou(labeled_data_i_bbox, sand_data_i_bbox)
        if iou_ratio > max_iou:
            max_iou = iou_ratio
            max_idx = i
    return max_idx, max_iou
def valid_face(pts):
    flag = True
    if pts[1][0] - pts[0][0] < 20:
        flag = False
    if pts[2][1] - pts[0][1] < 20:
        flag = False
    return flag

def fliter(face_data):
    new_face = []
    for face in face_data:
        if valid_face(face['pts']):
            new_face.append(face)
    return new_face


def calculate_det_acc(json_file, lib_dict):
    pass_pkg_lst, reject_pkg_lst = [], []

    filename = json_file
    correct_sand_bbox_num, all_sand_bbox_num = 0.0, 0.0
    correct_labeled_bbox_num, all_labeled_bbox_num = 0.0, 0.0
    with open(filename, 'r') as f:
        f = json.load(f)
        for line in f.keys():
            img_info = f[line]
            img_name = line.strip().split('/')[-1]
            labeled_data = img_info
            #print labeled_data
            labeled_data = fliter(labeled_data)
            if img_name in lib_dict:
                sand_data = lib_dict[img_name]
                all_sand_bbox_num += len(sand_data)
                all_labeled_bbox_num += len(labeled_data)
                if len(labeled_data) == 0 or len(sand_data) == 0:
                    continue
                idx_set = {-1}
                for i in range(len(sand_data)):
                    max_idx, max_iou = get_bestmatch_bbox(sand_data[i], labeled_data)
                    if max_iou >= 0.5 and (max_idx not in idx_set):
                        correct_sand_bbox_num += 1
                        idx_set.add(max_idx)
                idx_set = {-1}
                for i in range(len(labeled_data)):
                    max_idx, max_iou = get_bestmatch_bbox(labeled_data[i], sand_data)
                    if max_iou >= 0.5 and (max_idx not in idx_set):
                        correct_labeled_bbox_num += 1
                        idx_set.add(max_idx)
        if all_sand_bbox_num == 0 or all_labeled_bbox_num == 0:
            recall = 0.0
        else:
            recall = correct_sand_bbox_num / all_sand_bbox_num
        if all_labeled_bbox_num == 0:
            precision = 0.0
        else:
            precision = correct_labeled_bbox_num / all_labeled_bbox_num
        print("Recall is: %.3f, and precision is: %.3f" % (recall, precision))
        print correct_sand_bbox_num, all_sand_bbox_num

    return precision, recall

        
if __name__=='__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='json', type=str, default='fake_result.json', help='respond json file')
    ap.add_argument('--gt', dest='gt', type=str, default='val_gt.json', help='gt json file')

    args = ap.parse_args()

    usage = """
    Usage:
    python face-det-eval.py respond_json gt_json
    """
    
    lib_dict = save_library_dict(args.gt, 'face')
    calculate_det_acc(args.json, lib_dict)
