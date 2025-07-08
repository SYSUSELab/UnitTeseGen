import re

import tools.io_utils as io_utils

'''
structure of calling graph:
{
    "<class_fqn>": {
        "<method_sig>": ["caller1", "caller2"]
    }
}
'''
def build_calling_graph(file_structure):
    code_info_path = file_structure.CODE_INFO_PATH
    dataset_dir = f"{file_structure.DATASET_PATH}/dataset_info.json"
    dataset_info = io_utils.load_json(dataset_dir)

    def process_signature(osig, return_type=None):
        if return_type:
            method_sig = osig[osig.index(return_type)+len(return_type):]
        else:
            method_sig = osig
        while len(re.findall(r"<[^<>]*>", method_sig, flags=re.DOTALL))>0:
            method_sig = re.sub(r"<[^<>]*>", "", method_sig, flags=re.DOTALL)
        return method_sig

    for pj_name, pj_info in dataset_info.items():
        # pj_path = pj_info["project-url"]
        calling_graph = {}
        code_info = io_utils.load_json(f"{code_info_path}/json/{pj_name}.json")
        source_data = code_info["source"]
        for class_fqn, cinfo in source_data.items():
            class_data = {}
            for _, method_infos in cinfo["methods"].items():
                for minfo in method_infos:
                    return_type = minfo["return_type"].split('.')[-1] + " "
                    method_sig = process_signature(minfo["signature"], return_type)
                    class_data[method_sig] = []
            for minfo in cinfo["constructors"]:
                method_sig = minfo["signature"]
                class_data[method_sig] = []
            calling_graph.update({class_fqn: class_data})

        for class_fqn, cinfo in source_data.items():
            # class_data = calling_graph[class_fqn]
            for _, method_infos in cinfo["methods"].items():
                for minfo in method_infos:
                    method_sig = minfo["signature"]
                    return_type = minfo["return_type"].split('.')[-1] + " "
                    method_sig = method_sig[method_sig.index(return_type)+len(return_type):]
                    for call_info in minfo["call_methods"]:
                        call_split = call_info["signature"].split('.')
                        callee = '.'.join(call_split[:-1])
                        call_sig = process_signature(call_split[-1])
                        if callee in calling_graph and call_sig in calling_graph[callee]:
                            calling_graph[callee][call_sig].append(method_sig)
        graph_path = f"{code_info_path}/codegraph/{pj_name}_callgraph.json"
        io_utils.write_json(graph_path, calling_graph)


class InvokePatternExtractor:
    def __init__(self):
        # self.graph = io_utils.load_json(graph_path)
        # self.patterns = {}
        pass


def extract_invoke_patterns():
    pass