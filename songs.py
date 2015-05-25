import re
import sys

txt = open(sys.argv[1], "r").read()

for mo in re.finditer("<td> <a (href=.*?)>(.+?)</a>", txt):
    print mo.group(2)
