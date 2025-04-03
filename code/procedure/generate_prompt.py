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
        self.templates = {}
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
            if tmp_name not in self.case_gen_list: continue
            prompt = self.templates[tmp_name].render(content)
            prompts[tmp_name] = prompt
        return prompts


def generate_init_prompts(dataset_dir, code_info_path, prompt_path:str):
    generator = PromptGenerator('./templates', [])
    dataset_dir = f"{dataset_dir}/dataset_info.json"
    dataset_info = utils.load_json(dataset_dir)
    for pj_name, pj_info in dataset_info.items():
        project_url = pj_info["project-url"]
        project_path = f"{dataset_dir}/{project_url}"
        project_info = f"{code_info_path}/{pj_name}.json"
        searcher = CodeSearcher(project_path, project_info)
        for test_info in pj_info["focused-methods"]:
            id = test_info["id"]
            prompt_dir = f"{prompt_path}/{id}".replace("<project>", pj_name)
            if not os.path.exists(prompt_dir):
                os.makedirs(prompt_dir)
            # get context
            construct_context = searcher.collect_construct_context(test_info["class"], test_info["source-path"])
            contxet_file = f"{prompt_dir}/init_context.json"
            utils.write_json(contxet_file, construct_context)
            # generate prompt
            test_class_name =  test_info["test-class"].split('.')[-1]
            content = {
                "focused_method": test_info["focused-method"],
                "target_class": test_info["class-info"],
                "package_name": test_info["package"],
                "class_name": test_class_name,
                "context_dict": construct_context,
            }
            prompt = generator.generate_singal('init', content)
            # save prompt
            prompt_path = f"{prompt_dir}/init_prompt.txt"
            utils.write_text(prompt_path, prompt)


def generate_test_case_prompts(dataset_dir, code_info_path, prompt_path:str, gen_prompt_list:list):
    generator = PromptGenerator('./templates', gen_prompt_list)
    dataset_dir = f"{dataset_dir}/dataset_info.json"
    ds_info = utils.load_json(dataset_dir)
    
    for pj_name, pj_info in ds_info.items():
        project_url = pj_info["project-url"]
        project_path = f"{dataset_dir}/{project_url}"
        project_info = f"{code_info_path}/{pj_name}.json"
        searcher = CodeSearcher(project_path, project_info)
        for test_info in pj_info["focused-methods"]:
            id = test_info["id"]
            prompt_dir = f"{prompt_path}/{id}".replace("<project>", pj_name)
            # get context
            usage_context =searcher.collect_usage_context(test_info["class"], test_info["method-name"])
            contxet_file = f"{prompt_dir}/usage_context.json"
            utils.write_json(contxet_file, usage_context)
            # generate prompt
            content = {
                "focused_method": test_info["focused-method"],
                "target_class": test_info["class-info"],
                "context_dict": usage_context,
            }
            prompt_list = generator.generate_group(content)
            # save prompt
            for tmp_name, prompt in prompt_list.items():
                prompt_path = f"{prompt_dir}/{tmp_name}_prompt.txt"
                utils.write_text(prompt_path, prompt)
    return