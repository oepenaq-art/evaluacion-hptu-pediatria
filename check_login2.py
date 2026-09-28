import re

with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'async function handleLogin\(\).*?catch \(error\) \{[^}]*\}', text, re.DOTALL)
if match:
    out = match.group(0).encode('ascii', 'ignore').decode('ascii')
    print(out)
