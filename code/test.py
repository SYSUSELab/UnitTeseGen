import re

s = """
src\test\java\com\apple\spark\core\ApplicationSubmissionHelper_getExecutorSpec_Test.java:67: error: cannot find symbol
        request.setVolumes(new ArrayList<>());
                               ^
  symbol:   class ArrayList
  location: class ApplicationSubmissionHelper_getExecutorSpec_Test

"""

# package_pattern = r'package\s+([\w\.]+);'
# package_name = re.findall(package_pattern, s)[0]
# print(package_name)

symbol_pattern = r'symbol:   class (.*)' # check
symbols = re.findall(symbol_pattern, s)
print(symbols)


# li = [1,2,3]
# add = [4,5]

# # for i in add:
# #     li.insert(1,i)
# #     print(li)
# li = li[:1] + add + li[1:]
# print(li)

# for i, v in enumerate(li):
#     print(i, v)