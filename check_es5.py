import re
try:
    import pyjsparser
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyjsparser'])
    import pyjsparser

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Very aggressive polyfill to make pyjsparser (ES5) happy with ES6
code = re.sub(r'\bconst\b', 'var', code)
code = re.sub(r'\blet\b', 'var', code)
code = re.sub(r'\basync function\b', 'function', code)
code = re.sub(r'\bawait\b', '', code)
code = re.sub(r'=>', '', code) # this will break semantics but might pass syntax
# actually replacing arrow functions is hard with regex, let's just strip '...' spread
code = re.sub(r'\.\.\.', '', code)

# Let's just use node via a portable binary if possible? No.
print("We can't perfectly ES5-ify the code via regex.")
