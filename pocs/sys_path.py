import sys
import os

# Adicione o caminho da pasta raiz do script ao path do python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# sys.path.append(r"c:\Users\gerso\source\repo\gerson\novo-cnpj\.venv\Lib\site-packages")
from tlgfwk import *

# Verifique o sys.path
print(sys.path)