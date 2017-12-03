a = "{test test test}{test1 test1 test1}{test2 test2 test2}{test3 test3 test3}"


a = a.replace("}{", "}\n{")
print(a)