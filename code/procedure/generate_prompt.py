import os
import jinja2
import utils
from tools.code_search import CodeSearcher
class PromptGenerator:
    env: jinja2.Environment
    templates: dict
    case_gen_list: list

    def __init__(self, template_root, cglist):
        # load templates
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_root)) # any other options?
        template_list = os.listdir(template_root)
        for template in template_list:
            template_name = template.split('_')[0]
            self.templates[template_name] = self.env.get_template(template)
        self.case_gen_list = cglist

    def generate_singal(self, tmp_name, content) -> str:
        return self.templates[tmp_name].render(content)

    def generate_group(self, content) -> dict:
        prompts = {}
        for tmp_name in self.templates:
            if tmp_name in ['init', 'testclass']: continue
            prompt = self.templates[tmp_name].render(content)
            prompts[tmp_name] = prompt
        return prompts


def generate_init_prompts(dataset_dir, prompt_path:str):
    generator = PromptGenerator('./templates')
    dataset_dir = f"{dataset_dir}/dataset_info.json"
    dataset_info = utils.load_json(dataset_dir)
    for pj_name, pj_info in dataset_info.items():
        project_path = f"{dataset_dir}/{pj_info["project-url"]}"
        searcher = CodeSearcher(project_path)
        for test_info in pj_info["fucused-methods"]:
            # # get context
            # test_classes = searcher.get_test_classes(pj_info["test-classes"])
            # class_usage = searcher.search_class_usage(pj_info["test-classes"])
            # method_usage = searcher.search_method_usage(pj_info["test-classes"])
            # generate prompt
            content = {
                "focused_method": test_info["focused-method"],
                "target_class": test_info["class_info"],
                "package_name": test_info["package"],
                "class_name:": test_info["test-class"].split('.')[-1],
                "context_dict":{},
            }
            prompt = generator.generate_singal('init', content)
            # save prompt
            prompt_dir = f"{prompt_path}/{test_info["id"]}".replace("<project>", pj_name)
            if not os.path.exists(prompt_dir):
                os.makedirs(prompt_dir)
            prompt_path = f"{prompt_dir}/init_prompt.txt"
            utils.write_text(prompt_path, prompt)


def generate_test_case_prompts(dataset_dir:str, prompt_path:str, gen_prompt_list:list):
    generator = PromptGenerator('./templates', gen_prompt_list)
    dataset_dir = f"{dataset_dir}/dataset_info.json"
    ds_info = utils.load_json(dataset_dir)
    for pj_name, pj_info in ds_info.items():
        project_path = f"{dataset_dir}/{pj_info["project-url"]}"
        searcher = CodeSearcher(project_path)
        for test_info in pj_info["fucused-methods"]:
            # # get context
            # test_classes = searcher.get_test_classes(test_info["class-url"])
            # class_usage = searcher.search_class_usage(test_info["class-name"])
            # method_usage = searcher.search_method_usage(test_info["method-name"])
            # generate prompt
            content = {
                "focused_method": test_info["focused-method"],
                "target_class": test_info["class_info"],
                "existing_test_class": "<initial_class>",
                "context_dict":{},
            }
            prompt_list = generator.generate_group(content)
            # save prompt
            prompt_dir = f"{prompt_path}/{test_info["id"]}".replace("<project>", pj_name)
            for tmp_name, prompt in prompt_list.items():
                prompt_path = f"{prompt_dir}/{tmp_name}_prompt.txt"
                utils.write_text(prompt_path, prompt)
    return