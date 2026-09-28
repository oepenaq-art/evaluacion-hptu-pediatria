import os
import re
brain_dir = r'C:\Users\LENOVO\.gemini\antigravity\brain\11705742-ddec-4e19-bc0b-e0e230680f05'

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Make sure all template literals are correctly formed
app_js = re.sub(r'\\\$\{', '${', app_js)

with open(os.path.join(brain_dir, 'codigo_app.md'), 'w', encoding='utf-8') as f:
    f.write('# Archivo app.js\n\n```javascript\n' + app_js + '\n```\n')

with open('index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

with open(os.path.join(brain_dir, 'codigo_index.md'), 'w', encoding='utf-8') as f:
    f.write('# Archivo index.html\n\n```html\n' + index_html + '\n```\n')
print('Artifacts created.')
