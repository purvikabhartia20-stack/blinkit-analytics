import ast
pages = [
    'pages/0_Insights.py',
    'pages/1_Dashboard.py',
    'pages/2_Q_and_A.py',
    'pages/3_Architecture.py',
    'pages/4_Upload.py',
    'auto_tag.py',
    'generate_insights.py',
]
all_ok = True
for p in pages:
    try:
        with open(p, encoding='utf-8') as f:
            src = f.read()
        ast.parse(src)
        print(f'  OK: {p}')
    except SyntaxError as e:
        print(f'  SYNTAX ERROR: {p}: {e}')
        all_ok = False
    except Exception as e:
        print(f'  ERROR: {p}: {e}')
        all_ok = False
print('\nAll OK' if all_ok else '\nFix errors above before deploying')
