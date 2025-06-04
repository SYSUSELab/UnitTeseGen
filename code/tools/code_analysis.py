import re
import tree_sitter_java as ts_java
from queue import Queue
from tree_sitter import Language, Parser

class ASTParser:
    source_code: str
    parser: Parser
    tree = None
    lines:list
    import_position: int = 0

    def __init__(self):
        self.parser = Parser(Language(ts_java.language()))
        return

    def parse(self, source_code):
        self.lines = source_code.splitlines()
        self._update_code()
        # get import position
        for i, line in enumerate(self.lines):
            if line.strip().startswith('import'):
                self.insert_position = i + 1
        return
    

    def _update_code(self):
        """
        Update the source code and AST with the current lines
        """
        self.source_code = '\n'.join(self.lines)
        byte_code = self.source_code.encode('utf-8')
        self.tree = self.parser.parse(byte_code, encoding='utf8')
        return

    def _traverse_get(self, type):
        node_list = []
        bfs_queue = Queue()
        bfs_queue.put(self.tree.root_node)
        while not bfs_queue.empty():
            node = bfs_queue.get()
            if node.type == type:
                node_list.append(node)
            else:
                for child in node.children:
                    bfs_queue.put(child)
        return node_list


    def _get_functions(self):
        functions = []
        # get method_declaration nodes
        method_list = self._traverse_get('method_declaration')
        for node in method_list:
            # get function body
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            while self.lines[start_line-1].lstrip().startswith('@'):
                start_line -= 1
            function_code = '\n'.join(self.lines[start_line:end_line+1])
            functions.append(function_code)
        return functions
    
    # def _get_imports(self):
    #     return re.findall(r'import .*;', self.source_code, re.MULTILINE)

    # def get_additional_imports(self, existing_imports):
    #     imports = self._get_imports()
    #     additional_imports = []
    #     for imp in imports:
    #         if imp not in existing_imports:
    #             additional_imports.append(imp)
    #     return additional_imports

    def remove_lines(self, remove_lines:list[int]):
        """
        Remove lines from the source code.
        param remove_lines: List of line numbers to be removed.
        """
        remove_lines.sort(reverse=True)
        for line in remove_lines:
            self.lines.pop(line)
        self._update_code()
        return


    def add_imports(self, import_lines:list[str]):
        """
        Add import lines to the source code.
        :param import_lines: List of import lines to be added.
        """
        # Insert the new imports and Update the import position
        self.lines = self.lines[:self.insert_position] + import_lines + self.lines[self.insert_position:]
        self.insert_position += len(import_lines)
        self._update_code()
        return


    def get_test_case_position(self):
        function_nodes = self._traverse_get('method_declaration')
        test_case_positions = [[],[]]
        exclude_annotations = ['@BeforeEach', '@AfterEach', '@BeforeAll', '@AfterAll']
        for node in function_nodes:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            while self.lines[start_line-1].lstrip().startswith('@'):
                start_line -= 1
            func_code = '\n'.join(self.lines[start_line:end_line+1])
            flag = True
            for annotation in exclude_annotations:
                if func_code.find(annotation) > -1:
                    flag = False
            if flag:
                test_case_positions[0].append(start_line)
                test_case_positions[1].append(end_line)
        return test_case_positions


    def get_test_cases(self) -> list:
        test_cases = []
        test_annotations = ['@Test', '@ParameterizedTest', '@RepeatedTest']
        functions = self._get_functions()
        for func in functions:
            flag = False
            for annotation in test_annotations:
                if func.find(annotation) > -1:
                    flag = True
                    break
            if flag:
                test_cases.append(func)
        return test_cases


    def comment_code(self, comment_lines):
        for line in comment_lines:
            self.lines[line] = '// ' + self.lines[line]
        # self._update_code()
        self.source_code = '\n'.join(self.lines)
        return


    def get_code(self):
        return self.source_code


#test
if __name__ == '__main__':
    source_code = '''
    package infostructure;
    import java.io.IOException;
    public class MyClass {
        @Test
        public void test1(int a) {
            // test code
        }

        @Test
        public void test2(Token token) {
            // test code
        }

        public void myMethod() {
            // code
        }
    }
    '''
    # ast = ASTParser()
    # ast.parse(source_code)
    # print(ast.get_test_cases())
    # print(ast.get_additional_imports(set()))