import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'<div id="step-login" class="step.*?</form>\s*</div>', text, re.DOTALL)
if match:
    # remove non-ascii to avoid printing issues
    out = match.group(0).encode('ascii', 'ignore').decode('ascii')
    print(out)
