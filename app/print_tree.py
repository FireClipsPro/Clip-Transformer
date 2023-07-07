import os

def print_tree(directory, file_output=False, indents=0):
    print('-' * indents + os.path.basename(directory))
    
    for name in os.listdir(directory):
        if str(directory).__contains__('__pycache__') or str(directory).__contains__('.git') or str(directory).__contains__('.idea'):
            continue
        
        path = os.path.join(directory, name)
        
        if path.__contains__('__pycache__') or path.__contains__('.git') or path.__contains__('.idea'):
            continue
        
        if os.path.isfile(path) and path.endswith('.py') and not path.__contains__('__pycache__'):
            print('-' * (indents + 1) + name)
        elif os.path.isdir(path):
            print_tree(path, file_output, indents + 1)

print_tree(os.getcwd())
