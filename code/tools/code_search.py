import os
import utils


class CodeSearcher:
    project_path: str
    code_info: dict

    def __init__(self, project_path: str, code_info_path: str):
        self.project_path = project_path
        self.code_info = utils.load_json(code_info_path)


    def _get_test_classes(self, class_url: str):
        """
        搜索Java项目中指定类的测试类
        """
        test_source = f"{self.project_path}/{class_url}".replace("test/", "test-original/")
        content = None
        if os.path.exists(test_source):
            content = utils.load_text(test_source)
        return content

    def _get_class_info(self, class_name: str) -> dict:
        return self.code_info["source"].get(class_name, None)


    def _get_method_info(self, class_info: str, method_name: str) -> dict:
        '''
        get the method info in the class info
        '''
        method_info = next(
            (m_info for method, m_infos in class_info["methods"].items()
             if method_name.startswith(method)
             for m_info in m_infos if m_info["signature"] == method_name),
            None
        )
        return method_info


    def collect_construct_context(self, class_name, class_url):
        '''
        content in construct context:
        - Class constructor
        - Parameter in constructor, expecially classes defined in the project
        - API documents (optional)
        - Existing test class (optional)
        '''
        class_info = self._get_class_info(class_name)
        if class_info is None:
            raise ValueError(f"Class `{class_name}` not found in code info")
        
        context = {}
        constructor_body = ""
        for constructor in class_info["constructors"]:
            # get the constructor boy
            constructor_body += constructor["body"] + "\n"
        context[f"constructors for class `{class_name}`"] = f"```java\n{constructor_body}\n```"
        test_url = class_url.replace("main","test").replace(".java", "Test.java")
        test_class = self._get_test_classes(test_url)
        if test_class is not None:
            context["existing test class"] = f"```java\n{test_class}\n```"
        if "javadoc" in class_info:
            context["api document"] = class_info["javadoc"]
        # more context can be added here
        return context

    def collect_usage_context(self, class_name, method_name:str):
        '''
        content in usage context:
        - External variables and methods called in the focus method
        - Code context for calling focus methods
        - Parameter & Return Value in the focus method, expecially classes defined in the project
        - API documents (optional)
        - Code summary (optional)
        '''
        # get the class info and method info
        class_info = self._get_class_info(class_name)
        if class_info is None:
            raise ValueError(f"Class `{class_name}` not found in code info")
        method_info = self._get_method_info(class_info, method_name)
        if method_info is None:
            raise ValueError(f"Method `{method_name}` not found in class `{class_name}`")
        # collect the context
        context = {}
        if "javadoc" in class_info:
            context["api document"] = class_info["javadoc"]
        ptext = []
        for param in method_info["parameters"]:
            ptype = param["variable_type"]
            pname = param["variable_name"]
            pinfo = self._get_class_info(ptype)
            if pinfo is not None:
                # todo: add more info for paramater
                ptext.append(f"{ptype} {pname} ") #: {pinfo['javadoc']}")
            else:
                ptext.append(f"{ptype} {pname}")
        if len(ptext) > 0:
            context["parameters"] = '\n'.join(ptext)
        # add more context here
        return context

    # def search_class_usage(self, target_class: str) -> List[Dict]:
    #     """
    #     Search the variable declaration of the specified class in the Java project and extract the context.
    #     Args:
    #         target_class: Class to seach for.
    #     Returns:
    #         A list containing variable declaration information. Each element is a dictionary containing file path, line number, and context.
    #     """
    #     results = []
    #     return results

    # def search_method_usage(self, target_method: str) -> List[Dict]:
    #     """
    #     Search the usage of the specified method name in the Java project and extract the context.
    #     Args:
    #         target_method: Method to search for.
    #     Returns:
    #         A list containing method usage information. Each element is a dictionary containing file path, line number, and context.
    #     """
    #     results = []
    #     return results


if __name__ == "__main__":
    project_path = "../dataset/puts/commons-csv"
    method_name = "nextToken"
    searcher = CodeSearcher(project_path)
    # results = searcher.search_method_usage(method_name)
    class_name = "CSVFormat" #"Lexer"
    # results = searcher.search_class_usage(class_name)
    class_url = "src/main/java/org/apache/commons/csv/CSVFormat.java"
    results = searcher.collect_construct_context(class_name, class_url)
    print(results)