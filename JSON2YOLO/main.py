import os
import numpy as np

import argparse
from convert_json2yolotxt import convert_coco_json_to_yolo_txt

if __name__== "__main__":
    ap = argparse.ArgumentParser(description='Process some integers.')
    ap.add_argument('--output', default= " ", type=str, required=False,
                        help= 'direction of image folder') #output of file

    ap.add_argument('--json_path', default= "", type=str, required=False,
                        help= 'direction of annotation folder') #json path
    ap.add_argument('--segment', default= False , type= bool, required=False,
                        help= 'direction of annotation folder') #True or False
    ap = ap.parse_args()
    convert_coco_json_to_yolo_txt(ap.output,ap.json_path, use_segments = ap.segment)