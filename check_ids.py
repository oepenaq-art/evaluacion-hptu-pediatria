import re

with open('app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

ids_in_app = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", app_text))
ids_in_html = set(re.findall(r"id=['\"]([^'\"]+)['\"]", html_text))

print('IDs in app.js:', len(ids_in_app))
missing = ids_in_app - ids_in_html
print('Missing IDs in index.html:', missing)
