# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()
import re
match = re.search(r'async function generateFinalReport\(\) \{[\s\S]*?a\.click\(\);', text)
if not match:
    # Try another name
    match = re.search(r'async function [\w]+\(\) \{[\s\S]*?Packer\.toBlob[\s\S]*?a\.click\(\);', text)
if match:
    out = match.group(0).encode('ascii', 'ignore').decode('ascii')
    print(out[:500] + "\n...[TRUNCATED]...\n" + out[-500:])
