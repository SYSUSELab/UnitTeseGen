import os
import logging
import concurrent.futures
from threading import Lock

import tools.io_utils as io_utils
from tools.llm_api import LLMCaller
from procedure.post_process import check_class_name, insert_test_case


def generate_testclass_framework(file_structure, task_setting, dataset_info: dict):
    prompt_path = file_structure.PROMPT_PATH
    response_path = file_structure.RESPONSE_PATH
    gen_path = file_structure.TESTCLASSS_PATH
    projects = task_setting.PROJECTS
    case_list = task_setting.CASES_LIST
    save_res = task_setting.SAVE_INTER_RESULT
    mworkers = task_setting.MAX_WORKERS
    project_select = True if len(projects)>0 else False
    case_select = True if len(case_list)>0 else False
    logger = logging.getLogger(__name__)
    file_lock = Lock() # ensure thread-safe file writing
    llm_callers = [LLMCaller() for _ in range(mworkers)]

    def process_init_response(llm_caller:LLMCaller, test_info, project_prompt, project_response, gen_folder):
        id = test_info["id"]
        class_name = test_info["test-class"].split('.')[-1]
        test_class_path = f"{gen_folder}/{class_name}.java"
        prompt = io_utils.load_text(f"{project_prompt}/{id}/init_prompt.md")
        code, response = llm_caller.get_response_code(prompt)
        check_class_name(code, class_name)
        with file_lock:
            io_utils.write_text(test_class_path, code)
            if save_res:
                res_path = f"{project_response}/{id}/init_response.md"
                io_utils.write_text(res_path, response)
        return id
    
    for pj_name, pj_info in dataset_info.items():
        if project_select and pj_name not in projects: continue
        logger.info(f"Generating test class framework for project {pj_name}...")
        project_prompt = prompt_path.replace("<project>", pj_name)
        project_response = response_path.replace("<project>", pj_name)
        gen_folder = gen_path.replace("<project>", pj_name)
        if not os.path.exists(gen_folder): os.makedirs(gen_folder)
        logger.debug(f"max workers: {mworkers}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=mworkers) as executor:
            futures = []
            api_count = 0
            for test_info in pj_info["focal-methods"]:
                if case_select and test_info["id"] not in case_list: continue
                future = executor.submit(
                    process_init_response, 
                    llm_callers[api_count],
                    test_info, 
                    project_prompt, 
                    project_response, 
                    gen_folder
                )
                futures.append(future)
                api_count = (api_count+1) % mworkers
            # wait for all tasks complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    id = future.result()
                    logger.info(f"Completed test class framework generation for {id}")
                except Exception as e:
                    logger.error(f"Error processing test framework for {id}: {e}")

    return


def generate_testcase_code(file_structure, task_setting, dataset_info: dict):
    prompt_path = file_structure.PROMPT_PATH
    response_path = file_structure.RESPONSE_PATH
    gen_path = file_structure.TESTCLASSS_PATH
    prompt_list = task_setting.PROMPT_LIST
    projects = task_setting.PROJECTS
    case_list = task_setting.CASES_LIST
    save_res = task_setting.SAVE_INTER_RESULT
    mworkers = task_setting.MAX_WORKERS
    project_select = True if len(projects)>0 else False
    case_select = True if len(case_list)>0 else False
    logger = logging.getLogger(__name__)
    file_lock = Lock()
    llm_callers = [LLMCaller() for _ in range(mworkers)]

    def process_case_response(llm_caller:LLMCaller, test_info, project_prompt, project_response, gen_folder):
        class_name = test_info["test-class"].split('.')[-1]
        id = test_info["id"]
        save_path = f"{gen_folder}/{class_name}.java"
        init_class = io_utils.load_text(save_path)
        for prompt_name in prompt_list:
            prompt = io_utils.load_text(f"{project_prompt}/{id}/{prompt_name}_prompt.md")
            prompt = prompt.replace('<initial_class>', init_class)
            code, response = llm_caller.get_response_code(prompt)
            logger.debug("finish get response")
            init_class = insert_test_case(init_class, code)
            logger.debug("finish insert test case")
            if save_res:
                response_path = f"{project_response}/{id}/{prompt_name}_response.md"
                with file_lock:
                    io_utils.write_text(response_path, response)
        with file_lock:
            io_utils.write_text(save_path, init_class)
        return id

    for pj_name, pj_info in dataset_info.items():
        if project_select and pj_name not in projects: continue
        logger.info(f"Generating test cases for project {pj_name}...")
        project_prompt = prompt_path.replace("<project>", pj_name)
        project_response = response_path.replace("<project>", pj_name)
        gen_folder = gen_path.replace("<project>", pj_name)
        logger.debug(f"max workers: {mworkers}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=mworkers) as executor:
            futures = []
            api_count = 0
            for test_info in pj_info["focal-methods"]:
                if case_select and test_info["id"] not in case_list: continue
                future = executor.submit(
                    process_case_response, 
                    llm_callers[api_count],
                    test_info, 
                    project_prompt, 
                    project_response, 
                    gen_folder
                )
                futures.append(future)
                api_count = (api_count+1) % mworkers
            # wait for all tasks complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    id = future.result()
                    logger.info(f"Completed test case generation for {id}")
                except Exception as e:
                    logger.error(f"Error processing test framework for {id}: {e}")
    return


def merge_testcases(exist_cases:dict, new_cases:dict):
    
    return exist_cases

# format of output cases:
# [
#     {
#         "group": "<function_name>",
#         "cases": [
#             {
#                 "input": [
#                     {
#                         "parameter": "<parameter_name>",
#                         "value": "<parameter_value>",
#                     }
#                 ],
#                 "expected": "<expected_value>",
#                 "description": "<description>"
#             }
#         ],
#     }
# ]
def generate_case_then_code(file_structure, task_setting, dataset_info: dict):
    prompt_path = file_structure.PROMPT_PATH
    response_path = file_structure.RESPONSE_PATH
    gen_path = file_structure.TESTCLASSS_PATH
    prompt_list:list = task_setting.PROMPT_LIST
    projects = task_setting.PROJECTS
    case_list = task_setting.CASES_LIST
    save_res = task_setting.SAVE_INTER_RESULT
    mworkers = task_setting.MAX_WORKERS
    project_select = True if len(projects)>0 else False
    case_select = True if len(case_list)>0 else False
    logger = logging.getLogger(__name__)
    file_lock = Lock()
    llm_callers = [LLMCaller() for _ in range(mworkers)]
    # check prompt list
    for pt in prompt_list:
        if not pt.endswith("4case"): pt += "4case"
    if "gencode" not in prompt_list:
        prompt_list.append("gencode")

    def process_case_response(llm_caller:LLMCaller, test_info, project_prompt, project_response, gen_folder):
        id = test_info["id"]
        response_folder = f"{project_response}/{id}"
        prompt_folder = f"{project_prompt}/{id}"
        # generate test cases in json format
        cases_json = []
        for prompt_name in prompt_list:
            prompt = io_utils.load_text(f"{prompt_folder}/{prompt_name}_prompt.md")
            case_data, response = llm_caller.get_response_json(prompt)
            logger.debug("finish get response")
            cases_json = merge_testcases(cases_json, case_data)
            logger.debug("finish insert test case")
        with file_lock:
            io_utils.write_text(f"{response_folder}/cases.json", cases_json)
        # generate test code based on test cases
        class_name = test_info["test-class"].split('.')[-1]
        save_path = f"{gen_folder}/{class_name}.java"
        init_class = io_utils.load_text(save_path)
        #########
        # prompt = prompt.replace('<initial_class>', init_class)
        # with file_lock:
        #     io_utils.write_text(save_path, init_class)
        return id

    for pj_name, pj_info in dataset_info.items():
        if project_select and pj_name not in projects: continue
        logger.info(f"Generating test cases for project {pj_name}...")
        project_prompt = prompt_path.replace("<project>", pj_name)
        project_response = response_path.replace("<project>", pj_name)
        gen_folder = gen_path.replace("<project>", pj_name)
        logger.debug(f"max workers: {mworkers}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=mworkers) as executor:
            futures = []
            api_count = 0
            for test_info in pj_info["focal-methods"]:
                if case_select and test_info["id"] not in case_list: continue
                future = executor.submit(
                    
                )
                futures.append(future)
                api_count = (api_count+1) % mworkers
            # wait for all tasks complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    id = future.result()
                    logger.info(f"Completed test case generation for {id}")
                except Exception as e:
                    logger.error(f"Error processing test framework for {id}: {e}")
    return