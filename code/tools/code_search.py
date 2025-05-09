from copy import deepcopy
import os
import re
import logging
from turtle import position

import tools.io_utils as utils
from code_analysis import SnippetReader

class CodeSearcher:
    project_path: str
    code_info: dict
    snippet_reader: SnippetReader

    def __init__(self, project_path: str, code_info_path: str):
        self.project_path = project_path
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Loading code info from {code_info_path}")
        self.code_info = utils.load_json(code_info_path)

    # todo: will be replaced by _get_class_info
    def _get_test_classes(self, class_url: str):
        """
        find the test class for the given class
        """
        test_source = f"{self.project_path}/{class_url}".replace("test/", "test-original/")
        content = None
        if os.path.exists(test_source):
            content = utils.load_text(test_source)
        return content

    def _get_class_info(self, class_name: str, istest=False) -> dict:
        if istest:
            return self.code_info["test"].get(class_name, None)
        else:
            return self.code_info["source"].get(class_name, None)

    def _get_method_info(self, class_info: str, method_name: str) -> dict:
        '''
        get the method info in the class info
        '''
        method_info = next(
            (m_info for method, m_infos in class_info["methods"].items()
             if method_name.startswith(method)
             for m_info in m_infos if m_info["signature"].endswith(method_name)),
            None
        )
        return method_info

    def _extract_snippet(self, context:dict):
        full_context = {}
        for key, value in context.items():
            finds = re.findall(r"(<position:\[(.*)\]>)", value, re.DOTALL)
            if len(finds) > 0:
                for find in finds:
                    pivot = find[0]
                    position = find[1].split(", ")
                    file_path = position[0]
                    start_line = int(position[1])
                    end_line = int(position[2])
                    snippet = self.snippet_reader.read_lines(file_path, start_line, end_line)
                    value.replace(pivot, f"{'\n'.join(snippet)}")
                full_context[key] = value
            else:
                full_context[key] = value
        return full_context

    # todo: compress overlong context
    def collect_construct_context(self, class_name, method_name:str, class_url):
        '''
        content in construct context:
        - API documents (optional)
        - Class constructor
        - Parameter in constructor, expecially classes defined in the project        
        - Existing test class (optional)
        '''
        class_info = self._get_class_info(class_name)
        if class_info is None:
            raise ValueError(f"Class `{class_name}` not found in code info")
        method_info = self._get_method_info(class_info, method_name)
        if method_info is None:
            raise ValueError(f"Method `{method_name}` not found in class `{class_name}`")

        self.snippet_reader = SnippetReader(self.project_path)
        source_path = class_info["file"]
        context = {}
        pclass = {}
        # get api document
        if "javadoc" in class_info:
            context[f"api document of class {class_name}"] = class_info["javadoc"]
        # get the constructor info
        constructor_info = []
        for constructor in class_info["constructors"]:
            ptext = []
            for param in constructor["parameters"]:
                ptype = param["type"]
                pname = param["name"]
                pinfo = self._get_class_info(ptype)
                if pinfo is not None:
                    pclass[ptype] = pinfo
                    ptext.append(f"{ptype} {pname} ")
            body_pos = [source_path,constructor["start_line"],constructor["end_line"]]
            constructor_info.append(f"params: {'\n'.join(ptext)}\nbody:\n```java\n<position:{body_pos}>\n```")
        if len(constructor_info) > 0:
            context[f"constructors for class `{class_name}`"] = '\n'.join(constructor_info)
        # parameter in constructor & focus method
        parameter_info = []
        for param in method_info["parameters"]:
            ptype = param["type"]
            pname = param["name"]
            pinfo = self._get_class_info(ptype)
            if pinfo is not None:
                pclass[ptype] = pinfo
        for param, pinfo in pclass.items():
            pcontext = "class `{param}`:\n"
            if "javadoc" in pinfo:
                pcontext += f"api document : {pinfo['javadoc']}\n"
            pcontext += f"constructor:\n```java\n"
            for constructor in pinfo["constructors"]:
                body_pos = [pinfo["file"],constructor["start_line"],constructor["end_line"]]
                pcontext += f"<position:{body_pos}>\n"
            pcontext += f"```"
            parameter_info.append(pcontext)
        if len(parameter_info) > 0:
            context[f"parameters in constructors and focal method"] = '\n'.join(parameter_info)
        # get existing test class
        test_url = class_url.replace("main","test").replace(".java", "Test.java")
        test_class = self._get_test_classes(test_url)
        if test_class is not None:
            context["existing test class"] = f"```java\n{test_class}\n```"
        # more context can be added here
        context = self._extract_snippet(context)
        return context


    # todo: compress overlong context
    def collect_usage_context(self, class_name, method_name:str):
        '''
        content in usage context:
        - External variables (unimplemented) and methods called in the focus method
        - Code context for calling focus methods (unimplemented)
        - Parameter & Return Value in the focus method, expecially classes defined in the project
        - API documents (optional)
        - Code summary (optional) (unimplemented)
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
        depclass = {}
        def update_depclass(class_name, key, value):
            if class_name not in depclass:
                depclass[class_name] = {key:value}
            elif key not in depclass[class_name]:
                depclass[class_name][key] = value
            elif  isinstance(depclass[class_name][key],set):
                depclass[class_name][key].append(value)
            else:
                depclass[class_name].update({key:value})
        
        # api documents
        if "javadoc" in class_info:
            context[f"api document of class {class_name}"] = class_info["javadoc"]
        if "javadoc" in method_info:
            context[f"api document of method {method_name}"] = method_info["javadoc"]
        # parameters in focus method
        ptext = []
        for param in method_info["parameters"]:
            ptype = param["type"]
            pinfo = self._get_class_info(ptype)
            if pinfo is not None:
                update_depclass(ptype, {"APIdoc":pinfo["javadoc"]})
            pass
        # return type in focus method
        return_type:str = method_info["return_type"]
        if return_type!="void" and not return_type.startswith("java"):
            context["return type"] = return_type
        # calling methods in focus method
        for cmethod in method_info["call_methods"]:
            method_sig = cmethod["signature"].split(".")
            class_name = '.'.join(method_sig[:-1])
            method_name = method_sig.split(".")[-1]
            cinfo = self._get_class_info(class_name)
            if cinfo is not None:
                update_depclass(class_name, {"APIdoc":cinfo["javadoc"]})
                minfo = self._get_method_info(cinfo, method_name)
                if minfo is not None:
                    update_depclass(class_name, {"dep_func":minfo["javadoc"]+minfo["signature"]})

            if len(class_name) == 0: continue
            class_name = class_name[0]
            return_type = cmethod["return_type"]
            # any other infomation?
            cmtexts.append(f"method: {method_name}, return: {return_type}")
        if len(cmtexts) > 0: context["calling methods"] = '\n'.join(cmtexts)
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

    def search_method_usage(self, target_method: str) -> list[dict]:
        """
        Search the usage of the specified method name in the Java project and extract the context.
        Args:
            target_method: Method to search for.
        Returns:
            A list containing method usage information. Each element is a dictionary containing file path, line number, and context.
        """
        results = []
        return results


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