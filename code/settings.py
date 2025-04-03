# File path settings
# TODO: clear private infomation before commit
ROOT_PATH = "Path/to/Unit-Test-Generation/code" # absolute path
DEPENDENCY_PATH = "./dependencies"
DATASET_PATH = "../dataset/projects"
CODE_INFO_PATH = "../dataset/project_index/json"
PROMPT_PATH = "../evaluation/<project>/context+prompts"
TESTCLASSS_PATH = "../evaluation/<project>/test_classes"
REPORT_PATH = "../evaluation/<project>/reports"
# LLM settings
MODEL = ""
API_ACCOUNTS = [
    {   
        "base_url":"",
        "api_key":"xxx",
    }
]
# prompt selection
PROMPT_LIST = ['cov']