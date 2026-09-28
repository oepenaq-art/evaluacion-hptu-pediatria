
with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
start_idx = next(i for i, line in enumerate(lines) if 'async function generateFinalReport' in line)
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(''.join(lines[:start_idx]))

