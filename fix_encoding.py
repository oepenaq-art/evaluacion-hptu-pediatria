# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("Ronda Mdica", "Ronda Médica")
text = text.replace("Ronda Mdica (50%)", "Ronda Médica (50%)")
text = text.replace("Ronda Mdica (60%)", "Ronda Médica (60%)")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Encoding fixed in app.js")
