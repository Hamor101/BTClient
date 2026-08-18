codes = ["\033[41m", "\033[42m", "\033[43m", "\033[44m", "\033[45m", "\033[46m", "\033[47m"]

def printDict(d, tabs = 0):
    specialPrintables = {dict : printDict, list: printList}
    for key in d:
        if type(d[key]) in specialPrintables:
            print(f"{tabs * " "}{codes[tabs] + "--"+ "\033[0m "}{key.decode()}: {codes[tabs] + "{" + "\033[0m" if type(d[key])==dict else codes[tabs] + "[" + "\033[0m"}")
            specialPrintables[type(d[key])](d[key], tabs+1)
            print(f"{tabs * " "}{codes[tabs] + "}" + "\033[0m" if type(d[key])==dict else codes[tabs] + "]" + "\033[0m"}")
        else:
            print(f"{tabs * " "}{key.decode()}: {d[key]}")

def printList(l, tabs = 0):
    specialPrintables = {dict : printDict, list: printList}
    for elem in l:
        if type(elem) in specialPrintables:
            specialPrintables[type(elem)](elem, tabs+1)
        else:
            print(f"{tabs * " "} {elem.decode()}", end="\n")