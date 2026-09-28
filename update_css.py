import re

with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Add CSS for MiniCEX buttons
minicex_css = """
.btn-score-1 { background: #d32f2f; color: white; border-color: #b71c1c; }
.btn-score-2 { background: #f44336; color: white; border-color: #d32f2f; }
.btn-score-3 { background: #ff7043; color: white; border-color: #f4511e; }
.btn-score-4 { background: #ffa726; color: white; border-color: #fb8c00; }
.btn-score-5 { background: #ffca28; color: #333; border-color: #ffb300; }
.btn-score-6 { background: #ffee58; color: #333; border-color: #fdd835; }
.btn-score-7 { background: #d4e157; color: #333; border-color: #c0ca33; }
.btn-score-8 { background: #9ccc65; color: #333; border-color: #7cb342; }
.btn-score-9 { background: #66bb6a; color: white; border-color: #43a047; }
"""
if '.btn-score-1' not in css:
    with open('styles.css', 'a', encoding='utf-8') as f:
        f.write("\n" + minicex_css)

print("CSS updated")
