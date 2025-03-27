import os
import argparse

import utils
import settings as ST
from evaluations.coverage_test import test_coverage

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
    dataset_dir = f"{ST.ROOT_PATH}/{ST.DATASET_PATH}"
    report_path = f"{ST.ROOT_PATH}/{ST.REPORT_PATH}"
    dependency_path = f"{ST.ROOT_PATH}/{ST.DEPENDENCY_PATH}"
    if operation == 'coverage':
        test_coverage(dataset_dir, dependency_path, report_path)


if __name__ == "__main__":
    args = get_args()
    # logging.basicConfig(level=args.log_level)
    run(args.operation)
    