import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace document.getElementById('X')?.classList.something
def replacer(match):
    id_str = match.group(1)
    action = match.group(2)
    cls = match.group(3)
    return f"var el_{id_str.replace('-', '_')} = document.getElementById('{id_str}'); if (el_{id_str.replace('-', '_')}) el_{id_str.replace('-', '_')}.classList.{action}('{cls}');"

js = re.sub(r"document\.getElementById\('([^']+)'\)\?\.classList\.(remove|add)\('([^']+)'\);", replacer, js)

# Replace err.error?.message
js = js.replace("err.error?.message", "(err.error && err.error.message)")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Removed all optional chaining from app.js")
