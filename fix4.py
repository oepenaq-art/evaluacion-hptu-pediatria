import os

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# I will just write the Python script to replace the newline with literal \n
code = code.replace(" + '\n\n(Nota: ' +", r" + '\n\n(Nota: ' +")
# Same for the other places that might have been broken by """ string in python.
# Actually, the join('\\n') might have become join('\n')
code = code.replace("join('\\\n')", r"join('\n')")
code = code.replace("join('\\\n')", r"join('\n')")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)
