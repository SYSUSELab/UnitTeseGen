import re

# s = """
# package com.github.javaparser.ast;

# import static com.github.javaparser.JavaToken.Kind.EOF;
# """

# package_pattern = r'package\s+([\w\.]+);'
# package_name = re.findall(package_pattern, s)[0]
# print(package_name)


li = [1,2,3]
add = [4,5]

# for i in add:
#     li.insert(1,i)
#     print(li)
li = li[:1] + add + li[1:]
print(li)

for i, v in enumerate(li):
    print(i, v)