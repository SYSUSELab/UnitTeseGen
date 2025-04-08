import os
import logging
import argparse

import utils
import settings as ST
import procedure.workspace_preparation as WSP
import procedure.generate_prompt as GP
from tools.llm_api import LLMCaller
from tools.code_analysis import ASTParser

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-L','--log_level', type=str, default='info', help='log level: info, debug, warning, error, critical')
    parser.add_argument('-W', '--prepare_workspace', action='store_true', help='prepare workspace: True/False')
    # parser.add_argument('--operation',type=str, default='precision', help='evaluation operation: ?')

    args = parser.parse_args()
    log_level = {
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    args.log_level = log_level[args.log_level]
    return args


def generate_testclass_framework(dataset_dir:str, prompt_path:str, gen_path:str):
    dataset_dir = f"{dataset_dir}/dataset_info.json"
    dataset_info = utils.load_json(dataset_dir)
    llm_caller = LLMCaller()
    for pj_name, pj_info in dataset_info.items():
        # project_path = f"{dataset_dir}/{pj_info["project-url"]}"
        project_prompt = prompt_path.replace("<project>", pj_name) 
        gen_folder = gen_path.replace("<project>", pj_name)
        if not os.path.exists(gen_folder):
            os.makedirs(gen_folder)
        for test_info in pj_info["focused-methods"]:
            id = test_info["id"]
            prompt = utils.load_text(f"{project_prompt}/{id}/init_prompt.md")
            code = llm_caller.get_response(prompt)
            class_name = test_info["test-class"].split('.')[-1]
            save_path = f"{gen_folder}/{class_name}.java"
            utils.write_text(save_path, code)
    return


def insert_test_case(init_class:str, insert_code:str):
    # 去掉 initclass 和 insrtcode 末尾不含字符只有空格和换行符的行
    init_class = init_class.rstrip()
    insert_code = insert_code.lstrip()
    lines = init_class.splitlines()
    insert_ast = ASTParser(insert_code)
    # insert import lines
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('import '):
            last_import_idx = i
    existing_imports = set()
    for line in lines[:last_import_idx+1]:
        if line.strip().startswith('import '):
            existing_imports.add(line.strip())
    additional_imports = insert_ast.get_additional_imports(existing_imports)
    if len(additional_imports) > 0:
        lines = lines[:last_import_idx+1] + additional_imports + lines[last_import_idx+1:]
    # insert test case
    add_test_case = insert_ast.get_test_cases()
    lines = lines[:-1] + add_test_case + [lines[-1]]
    added_class = '\n'.join(lines)
    return added_class


def generate_testcase(dataset_dir:str, prompt_path:str, prompt_list:list, gen_path:str):
    dataset_dir = f"{dataset_dir}/dataset_info.json"
    dataset_info = utils.load_json(dataset_dir)
    llm_caller = LLMCaller()
    for pj_name, pj_info in dataset_info.items():
        project_prompt = prompt_path.replace("<project>", pj_name)
        gen_folder = gen_path.replace("<project>", pj_name)
        for test_info in pj_info["focused-methods"]:
            class_name = test_info["test-class"].split('.')[-1]
            id = test_info["id"]
            save_path = f"{gen_folder}/{class_name}.java"
            init_class = utils.load_text(f"{gen_folder}/{class_name}.java")
            for prompt_name in prompt_list:
                prompt = utils.load_text(f"{project_prompt}/{id}/{prompt_name}_prompt.md")
                prompt = prompt.replace('<initial_class>', init_class)
                code = llm_caller.get_response(prompt)
                init_class = insert_test_case(init_class, code)
            utils.write_text(save_path, code)
    return


def run(args):
    '''
    procedure:
    1. workspace preparation
    2. setup & teerdowm generation
        - ~~ 2.1 context collection: code search / static analysis ~~
        - 2.2 prompt combination
        - 2.3 testclass structure generation
    3. test function generation
        - 4.1 prompt combination
        - 4.2 generate test function
    4. package & save test class
        - 5.1 code repair (?)
    '''
    root_path = ST.ROOT_PATH
    dataset_path = ST.DATASET_PATH
    dataset_abs = f"{root_path}/{dataset_path}"
    code_info_path = ST.CODE_INFO_PATH
    prompt_path = ST.PROMPT_PATH
    prompt_list = ST.PROMPT_LIST
    # 1. prepare workspace
    if args.prepare_workspace:
        # todo: add preprocess
        WSP.prepare_workspace(dataset_abs)
    # 2. setup & teardown generation
    GP.generate_init_prompts(dataset_path, code_info_path, prompt_path)
    GP.generate_test_case_prompts(dataset_path, code_info_path, prompt_path, prompt_list)
    # 3. test function generation
    generate_testclass_framework(dataset_path, prompt_path, ST.TESTCLASSS_PATH)
    generate_testcase(dataset_path, prompt_path, prompt_list, ST.TESTCLASSS_PATH)
    return


if __name__ == '__main__':
    args = get_args()
    logging.basicConfig(level=args.log_level)
    run(args)