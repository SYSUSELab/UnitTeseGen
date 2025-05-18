import re
import json
import logging
from openai import NOT_GIVEN, OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

from settings import LLMSettings as ST

class LLMCaller:
    account_num = 0
    cur_account_num = 0
    accounts = None
    gpt = None
    system_prompt = None
    base_message = []
    
    def __init__(self) -> None:
        self.model = ST.MODEL
        self.accounts = ST.API_ACCOUNTS
        self.account_num = len(ST.API_ACCOUNTS)
        account = self.accounts[self.cur_account_num]
        self.gpt = OpenAI(api_key=account["api_key"],base_url=account["base_url"])
        if self.system_prompt:
            self.base_message.append({"role": "system", "content": self.system_prompt})
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"LLM API initialized, model name: {self.model}.")
        pass

    def change_account(self):
        if self.account_num == 1:
            # self.logger.error("Only one account info, can't change account.")
            return
        self.cur_account_num = (self.cur_account_num+1)%self.account_num
        account = self.accounts[self.cur_account_num]
        self.gpt = OpenAI(api_key=account["api_key"],base_url=account["base_url"])
        self.logger.info(f"Change api_key successfully.")
        return

    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(3))
    def _generation(self, prompt:str, 
                response_format:dict=NOT_GIVEN) -> str:
        messages = self.base_message.copy()
        messages.append({"role": "user", "content": prompt})
        response = self.gpt.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format = response_format,
            # add more parameters
        )
        if response.choices[0].message.content:
            return response.choices[0].message.content 
        else:
            self.change_account()
            raise ValueError("Empty response from API")
        
    def _filter_code(self, output:str) -> str:
        # extract java code from output
        java_pattern = r"```(?:[jJ]ava)?\n+([\s\S]*?)\n```"
        matches = re.findall(java_pattern, output, re.DOTALL)
        # select the longest one in matches
        code = max(matches, key=len) if len(matches)>0 else ""
        return code
    
    # get response surrounded by ```java````
    def get_response_code(self, prompt:str) -> list:
        try:
            response = self._generation(prompt)
            code = self._filter_code(response)
            return [code, response]
        except Exception as e:
            self.logger.error(f"Error occured while calling llm api: {e}")
            return ["",""]

    # split json object from response
    def _handle_json_response(self, response):
        result = re.sub(r'//.*', '', response)
        json_str = result.replace("\'", '\"')
        obj = json.loads(json_str)
        return obj
    
    # get response in json format
    def get_response_json(self, prompt:str) -> list:
        try:
            response_format = { "type": "json_object" }
            response = self._generation(prompt, response_format)
            json_data = self._handle_json_response(response)
            return json_data
        except Exception as e:
            self.logger.error(f"Error occured while calling llm api: {e}")
            return None


# test
if __name__ == '__main__':
    llm = LLMCaller()
    s = """
    """
    matches = llm.handle_output(s)
    print(matches)