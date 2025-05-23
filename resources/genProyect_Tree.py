# Version: 0.0.1 | Updated: 2025-03-17 15:06:33 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
"""
Generador de estructura de directorios para documentacion.

Este script genera un arbol de directorios en formato ASCII, ideal para incluir
en la documentacion de proyectos (por ejemplo, en el README.md). Permite excluir
directorios y archivos especificos mediante patrones.

Uso:
    python project_tree.py [--output README.md] [--ignore-dirs .git,venv] [--ignore-files *.pyc,*.tmp]

Ejemplos:
    1. Mostrar arbol en consola:
       python project_tree.py

    2. Guardar en README.md e ignorar archivos .log y .tmp:
       python project_tree.py --output README.md --ignore-files "*.log,*.tmp"

    3. Ignorar directorios especificos:
       python project_tree.py --ignore-dirs ".git,venv,temp"
"""
# Importamos las bibliotecas necesarias
import os
import argparse
import sys

# Agregamos el directorio '/workspace' al PYTHONPATH para que pueda encontrar el módulo 'project_tree'
sys.path.insert(0, '/workspace')

# Importamos el módulo 'project_tree' desde el directorio 'modules'
from modules.project_tree import generate_project_tree

# Definimos la función principal del script
if __name__ == '__main__':
    # Definimos las opciones por defecto para ignorar directorios y archivos
    DEFAULT_IGNORE_DIRS = ['.git', '__pycache__', 'venv', '.pytest_cache']
    DEFAULT_IGNORE_FILES = ['*.pyc', '*.tmp', '*.log']

    # Creamos un parser de argumentos para procesar las opciones del usuario
    parser = argparse.ArgumentParser(description='Genera un árbol de directorios en formato ASCII para documentación.', epilog='Ejemplo: python project_tree.py --output README.md --ignore-dirs .git,venv')

    # Agregamos las opciones para el parser
    parser.add_argument('--output', help='Archivo de salida (ej. README.md)', default=None)
    parser.add_argument('--ignore-dirs', help='Directorios a ignorar (separados por comas)', default=','.join(DEFAULT_IGNORE_DIRS))
    parser.add_argument('--ignore-files', help='Patrones de archivos a ignorar (separados por comas, soporta wildcards)', default=','.join(DEFAULT_IGNORE_FILES))

    # Procesamos las opciones del usuario
    args = parser.parse_args()

    # Convertimos las opciones de ignorar directorios y archivos en listas
    ignore_dirs = [item.strip() for item in args.ignore_dirs.split(',')]
    ignore_files = [item.strip() for item in args.ignore_files.split(',')]

    # Llamamos a la función 'generate_project_tree' para generar el árbol de directorios
    generate_project_tree(start_path=os.getcwd(), ignore_dirs=ignore_dirs, ignore_files=ignore_files, output_file=args.output)