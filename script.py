
with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'async function generateFinalReport' in line:
        print(f'Start generateFinalReport: {i}')
    if 'async function buildWordReport' in line:
        print(f'Start buildWordReport: {i}')

