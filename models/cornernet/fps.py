import argparse
import os.path as path
import sys
import json
import os
import shutil
import importlib

CURRENT_DIR = './'
MODEL = 'CornerNet'
MODEL_PATH = path.join(CURRENT_DIR, MODEL)
sys.path.append(path.abspath(MODEL_PATH))
from config import system_configs
from db.datasets import datasets

SPLIT = 'testing'
DB = 'db'
IMAGE_SIZE = 300
IMAGE_NAME_FILE = 'top_600.txt'
TRAINED_MODEL_DIR = 'cornernet/weights/'
TRAINED_MODEL_FN = 'CornerNet_500000.pkl'
TRAINED_MODEL_PATH = path.join(TRAINED_MODEL_DIR, TRAINED_MODEL_FN)
TEST_DEV_ANNOS = 'data/coco/annotations/'
TEST_DEV_ANNOS_FN = 'instances_testdev2017.json'
TEST_DEV_PATH = path.join(CURRENT_DIR, path.join(TEST_DEV_ANNOS, TEST_DEV_ANNOS_FN))

def parse_args():
    parser = argparse.ArgumentParser(description='Measure FPS of CornerNet')

    parser.add_argument('--trained-model', required=False, help='Path to trained state_dict file', 
                        default=TRAINED_MODEL_PATH)
    parser.add_argument('--num-classes', required=False, type=int, help='number of classes', 
                        default=81)
    parser.add_argument('--image-path', required=True, help='path to COCO val2014 images dir')
    parser.add_argument('--image-name-file', required=False, help='path to image name file', 
                        default=IMAGE_NAME_FILE)
    parser.add_argument('--image-size', required=False, type=int)
    parser.add_argument('--num-tests', required=False, type=int, default=10)
    parser.add_argument('--model-config', required=False, default='CornerNet')
    parser.add_argument('--suffix', required=False, default='.json')
    return parser.parse_args()

def read_json_file(path):
    with open(path) as f:
        data = json.load(f)
    
    return data

def make_dirs(dirs):
    list(map(lambda d: os.makedirs(d), 
             list(filter(lambda d: not path.exists(d), dirs))))

def run_model(data, system_configs, result_dir):
    corner_net = NetworkFactory(data)
    corner_net.load_params(system_configs.max_iter)
    test_file = "test.{}".format(data.data)
    testing = importlib.import_module(test_file).testing

    corner_net.cuda()
    corner_net.eval_mode()
    

if __name__ == '__main__':
    args = parse_args()

    #prepare dirs
    make_dirs([path.join(CURRENT_DIR, TEST_DEV_ANNOS)])
    shutil.copy(path.join(CURRENT_DIR, TEST_DEV_ANNOS_FN), TEST_DEV_PATH)

    model_config_path = args.model_config + args.suffix
    config_fp = path.join(MODEL_PATH, path.join(system_configs.config_dir, model_config_path))
    config = read_json_file(path=config_fp)
    config['system']['snapshot_name'] = args.model_config
    system_configs.update_config(config['system'])
    
    test_dataset = datasets[system_configs.dataset](config[DB], system_configs.test_split)

    
    print(test_dataset._cat_ids)
    
