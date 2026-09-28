with open('index.html', 'r', encoding='utf-8') as f:
    for line in f:
        if 'evaluation-type' in line or 'Ronda' in line or 'Seminario' in line or 'Tema' in line or 'MiniCEX' in line:
            if '<option' in line or '<select' in line:
                print(line.strip())
