import logging
import argparse


import tools.io_utils as utils
from evaluations.coverage_test import test_coverage
from settings import FileStructure as FS, TaskSettings as TS

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_level', type=str, default='info', help='log level: info, debug, warning, error, critical')
    # evaluation mode
    parser.add_argument('--operation',type=str, default='precision', help='evaluation operation: coverage')

    args = parser.parse_args()
    # log_level = {
    # 'info': logging.INFO,
    # 'debug': logging.DEBUG,
    # 'warning': logging.WARNING,
    # 'error': logging.ERROR,
    # 'critical': logging.CRITICAL
    # }
    # args.log_level = log_level[args.log_level]
    return args

'''
procedure:
1. run test & generate report
2. extract: pass rate, coverage, .....
'''
def run(operation):
    dataset_path = FS.DATASET_PATH
    dataset_info = utils.load_json(f"{dataset_path}/dataset_info.json")

    if operation == 'coverage':
        test_coverage(FS, TS, dataset_info)


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args.log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    run(args.operation)
    