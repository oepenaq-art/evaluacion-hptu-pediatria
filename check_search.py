# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()
import re
match = re.search(r'async function searchEvaluations\(\) \{[\s\S]*?document\.getElementById\(\'report-preview\'\)\.classList\.remove\(\'hidden\'\);\n\}', js)
if match:
    out = match.group(0).encode('ascii', 'ignore').decode('ascii')
    print(out[:500] + "\n...[TRUNCATED]...\n" + out[-1000:])
