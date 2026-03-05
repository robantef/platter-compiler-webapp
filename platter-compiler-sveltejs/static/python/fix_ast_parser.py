import os

file_path = 'app/semantic_analyzer/ast/ast_parser_program.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# safely flatten node_0 if it happens to be a list
old_str = "result = [node_0] + node_1"
new_str = "result = (node_0 if isinstance(node_0, list) else [node_0]) + node_1"

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Flattening patch applied successfully.")
else:
    print("Could not find the target string to replace.")
