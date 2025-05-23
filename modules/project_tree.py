
import os
import argparse
import fnmatch

def generate_project_tree(start_path, ignore_dirs=[], ignore_files=[],
                           output_file=None):
    """
    Description:
         generate_project_tree function.
    Args:
        start_path: The first parameter.
        ignore_dirs: The second parameter.
        ignore_files: The third parameter.
        output_file: The fourth parameter.
    Returns:
        None
    """
    tree = ['```\n']

    def should_ignore(name, is_dir):
        """
        Description:
             should_ignore function.
        Args:
            name: The first parameter.
            is_dir: The second parameter.
        Returns:
            None
        """
        if is_dir:
            return name in ignore_dirs
        else:
            return any((fnmatch.fnmatch(name, pattern) for pattern in ignore_files))

    def build_tree(path, prefix='', is_last=True):
        """
        Description:
             build_tree function.
        Args:
            path: The first parameter.
            prefix: The second parameter.
            is_last: The third parameter.
        Returns:
            None
        """
        name = os.path.basename(path)
        line = f'{prefix}└── {name}' if is_last else f'{prefix}├── {name}'
        if prefix == '':
            tree.append(f'{name}\n')
        else:
            tree.append(f'{line}\n')
        if os.path.isdir(path):
            new_prefix = prefix + ('    ' if is_last else '│   ')
            try:
                items = sorted(os.listdir(path))
                items = [item for item in items if not should_ignore(item, os.path.isdir(os.path.join(path, item)))]
            except PermissionError:
                return
            dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]
            files = [f for f in items if not os.path.isdir(os.path.join(path, f))]
            sorted_items = dirs + files
            for index, item in enumerate(sorted_items):
                is_last_item = index == len(sorted_items) - 1
                build_tree(os.path.join(path, item), new_prefix, is_last_item)
    build_tree(start_path)
    tree.append('```')
    result = ''.join(tree)
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f'## Estructura del proyecto\n\n{result}\n')
        print(f'✓ Arbol generado en {output_file}')
    else:
        print(result)
