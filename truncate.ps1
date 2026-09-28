import json

def replace_functions():
    with open('app.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # We will truncate and append via file write to keep things simple
    # But since it's hard to safely replace just the bottom half without breaking, 
    # we'll use a delimiter or find the line index.
    
    start_idx = -1
    for i, line in enumerate(lines):
        if 'async function generateFinalReport' in line:
            start_idx = i
            break
            
    if start_idx == -1:
        print('Could not find generateFinalReport')
        return
        
    top_half = ''.join(lines[:start_idx])
    
    # We will write out top_half and then write the rest manually
    
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(top_half)
        
    print('Truncated file to generateFinalReport.')
    
replace_functions()
