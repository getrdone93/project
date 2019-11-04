import os.path as path
import cv2
import torch
import argparse
import json

IMAGE_NAME_FILE = 'top_600.txt'

def default_args(net_name, trained_model_path, num_classes, image_size, 
                 num_tests=10, image_name_file=IMAGE_NAME_FILE):
    parser = argparse.ArgumentParser(description="Measure FPS of {}".format(net_name))
    parser.add_argument('--trained-model', required=False, help='Path to trained state_dict file', 
                        default=trained_model_path)
    parser.add_argument('--num-classes', required=False, type=int, help='number of classes', 
                        default=num_classes)
    parser.add_argument('--image-path', required=True, help='path to COCO val2014 images dir')
    parser.add_argument('--image-name-file', required=False, help='path to image name file', 
                        default=image_name_file)
    parser.add_argument('--image-size', required=False, type=int, default=image_size)
    parser.add_argument('--num-tests', required=False, type=int, default=num_tests)

    return parser

def read_file(path):
    with open(path) as f:
        data = f.read()

    return data

def process_file_names(data):
    return data.split('\n')[:-1]

def resize_images(size, images):
    return [cv2.resize(i, (size, size)) for i in images]

def prepare_images(images, size):
    return [torch.from_numpy(i).unsqueeze(0)\
            .reshape((1, 3, size, size)).float() for i in images]

def load_images(im_path, names):
    images, nf = [], []
    for n in names:
        p = path.join(im_path, n)
        im = cv2.imread(p)
        if im is None:
            nf.append(p)
        else:
            images.append(im)
    return images, nf

def average_averages(times, ik, tm_func, tm_args):
    totals = {}
    for t in range(1, times + 1):
        print("On test number %d" % (t))
        out_m = tm_func(**tm_args)
        totals = {k: totals[k] + out_m[k] if k in totals else out_m[k]\
                  for k in set(out_m).difference(set(ik))}

    return {k: totals[k] / times for k in totals}

def print_output(args, out_data, model_name):
    print('out_data ' + str(out_data))
    print("\n\nFrames Per Second result for %s, averaged over %d runs:" 
          % (str(model_name), args.num_tests))
    for k, v in out_data.items():
        print("%s = %f" % (str(k).ljust(25), v))
    print("\n\n")

def read_json_file(path):
    with open(path) as f:
        data = json.load(f)
    
    return data

def make_dirs(dirs):
    list(map(lambda d: os.makedirs(d, exist_ok=True), 
             list(filter(lambda d: not path.exists(d), dirs))))
