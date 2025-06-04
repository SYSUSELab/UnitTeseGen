# TODO: remove and add to gitignore

import re

# s = """
# src\test\java\com\apple\spark\core\ApplicationSubmissionHelper_getExecutorSpec_Test.java:67: error: cannot find symbol
#         request.setVolumes(new ArrayList<>());
#                                ^
#   symbol:   class ArrayList
#   location: class ApplicationSubmissionHelper_getExecutorSpec_Test
#   symbol: class ArrayList

# """

# package_pattern = r'package\s+([\w\.]+);'
# package_name = re.findall(package_pattern, s)[0]
# print(package_name)

# symbol_pattern = r'symbol:\s+(class|variable) (.*)' # check
# symbols = re.findall(symbol_pattern, s)
# print(symbols)


# li = [1,2,3]
# add = [4,5]

# # for i in add:
# #     li.insert(1,i)
# #     print(li)
# li = li[:1] + add + li[1:]
# print(li)

# for i, v in enumerate(li):
#     print(i, v)

from tools.code_analysis import ASTParser
code = """
import org.mockito.*;
import static org.mockito.Mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import com.apple.spark.core.Constants;
import com.apple.spark.operator.SparkApplication;
import java.util.HashMap;
import java.util.Map;
import com.apple.spark.operator.SparkApplicationSpec;

@ExtendWith(MockitoExtension.class)
class SubmissionSummary_copyFrom_Test {
@BeforeEach
    void setupBeforeEach() throws IOException {
        // Initialize necessary fields and dependencies here before each test
        String csvData = "header1,header2value1,value2";
        parser = CSVParser.parse(new StringReader(csvData), CSVFormat.DEFAULT);
    }
  @Test
    void testNextRecord() throws IOException {
    
    }
}
"""

ast_parser = ASTParser()
ast_parser.parse(code)
remove_imports = [1,2]
add_imports = ["abc","def"]
# ast_parser.remove_lines(remove_imports)
# ast_parser.add_imports(add_imports)
add_exception = [13,19]
ast_parser.add_exception(add_exception)
print(ast_parser.get_code())