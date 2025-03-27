# File path settings
# TODO: clear private infomatino before commit
ROOT_PATH = "D:/Study/myevaluation/Unit-Test-Generation/demo" # absolute path
DEPENDENCY_PATH = "./dependencies"
DATASET_PATH = "../dataset/puts"
PROMPT_PATH = "../evaluation/<project>/context+prompts"
TESTCLASSS_PATH = "../evaluation/<project>/testclasses"
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