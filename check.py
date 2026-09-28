with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()
print('Has escaped dollars?', r'\${' in text)
