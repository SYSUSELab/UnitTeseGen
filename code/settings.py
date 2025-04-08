# File path settings
# TODO: clear private infomation before commit
ROOT_PATH = "D:/Study/myevaluation/UnitTeseGen/code" # absolute path
DEPENDENCY_PATH = "./dependencies"
DATASET_PATH = "../dataset/projects"
CODE_INFO_PATH = "../dataset/project_index/json"
PROMPT_PATH = "../evaluation/<project>/context+prompts"
TESTCLASSS_PATH = "../evaluation/<project>/test_classes"
REPORT_PATH = "../evaluation/<project>/reports"
# LLM settings
MODEL = "deepseek-v3-0324"
API_ACCOUNTS = [
    {   
        "base_url":"https://api.agicto.cn/v1",
        "api_key":"sk-1tvIzrm9vSkSpPYykTi1ODvUIfbNfW7986AkQ5T3SjvtZ8IJ",
    }
]
# prompt selection
PROMPT_LIST = ['cov']