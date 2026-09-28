import esprima
import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix literal newline in single-quoted string
code = code.replace(" + '\n\n(Nota: '", r" + '\n\n(Nota: '")

# Write back
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

# Check syntax
code = re.sub(r'\?\.', '.', code)
code = re.sub(r'\?\?', '||', code)

try:
    esprima.parseScript(code)
    print('Syntax OK!')
except Exception as e:
    print('Syntax Error:', e)
