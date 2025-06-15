import os
import jinja2


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

    def generate_single(self, tmp_name, content) -> str:
        return self.templates[tmp_name].render(content)

    def generate_group(self, content) -> dict:
        prompts = {}
        for tmp_name in self.templates:
            if tmp_name not in self.case_gen_list: continue
            prompt = self.templates[tmp_name].render(content)
            prompts[tmp_name] = prompt
        return prompts