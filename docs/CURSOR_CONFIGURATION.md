# Configuração do Cursor para VS Code

Este documento explica como o Cursor foi configurado para usar as mesmas teclas de atalho e configurações do Visual Studio Code.

## Arquivos de Configuração

### 1. keybindings.json
Localização: `%APPDATA%\Cursor\User\keybindings.json`

Este arquivo contém todas as teclas de atalho do VS Code, incluindo:

#### Navegação Básica
- `Ctrl+P` - Abrir arquivo rapidamente
- `Ctrl+Shift+P` - Paleta de comandos
- `Ctrl+G` - Ir para linha
- `Ctrl+Shift+O` - Ir para símbolo
- `Ctrl+T` - Mostrar todos os símbolos

#### Edição
- `Ctrl+C/V/X` - Copiar/Colar/Recortar
- `Ctrl+Z/Shift+Z` - Desfazer/Refazer
- `Ctrl+D` - Selecionar próxima ocorrência
- `Ctrl+Shift+L` - Selecionar todas as ocorrências
- `Ctrl+U/Shift+U` - Desfazer/Refazer cursor

#### Busca e Substituição
- `Ctrl+F` - Buscar
- `Ctrl+H` - Substituir
- `Ctrl+Shift+F` - Buscar em arquivos
- `Ctrl+Shift+H` - Substituir em arquivos

#### Multi-cursor
- `Alt+Click` - Adicionar cursor
- `Ctrl+Alt+Up/Down` - Adicionar cursor acima/abaixo

#### Seleção
- `Ctrl+A` - Selecionar tudo
- `Ctrl+L` - Expandir seleção de linha

#### Indentação
- `Tab` - Indentar
- `Shift+Tab` - Desindentar
- `Ctrl+]/[` - Indentar/Desindentar linhas

#### Comentários
- `Ctrl+/` - Comentar linha
- `Shift+Alt+A` - Comentar bloco

#### Formatação
- `Shift+Alt+F` - Formatar documento

#### Refatoração
- `F2` - Renomear
- `Ctrl+.` - Ações rápidas
- `Shift+F12` - Ir para referências

#### Navegação de Código
- `F12` - Ir para definição
- `Alt+F12` - Ver definição

#### Debug
- `F5` - Iniciar debug
- `F9` - Alternar breakpoint
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out

#### Terminal
- `Ctrl+`` - Alternar terminal
- `Ctrl+Shift+`` - Novo terminal

#### Arquivos
- `Ctrl+N` - Novo arquivo
- `Ctrl+O` - Abrir arquivo
- `Ctrl+S` - Salvar
- `Ctrl+Shift+S` - Salvar como
- `Ctrl+W` - Fechar editor
- `Ctrl+Shift+T` - Reabrir editor fechado

#### Abas
- `Ctrl+Tab` - Próximo editor
- `Ctrl+Shift+Tab` - Editor anterior
- `Ctrl+1-9` - Ir para aba específica

#### Painéis
- `Ctrl+B` - Alternar barra lateral
- `Ctrl+Shift+E` - Explorer
- `Ctrl+Shift+F` - Search
- `Ctrl+Shift+G` - Source Control
- `Ctrl+Shift+D` - Debug
- `Ctrl+Shift+X` - Extensions

#### Zoom
- `Ctrl+=` - Zoom in
- `Ctrl+-` - Zoom out
- `Ctrl+0` - Reset zoom

#### IntelliSense
- `Ctrl+Space` - Trigger suggestions
- `Ctrl+Shift+Space` - Trigger parameter hints

### 2. settings.json
Localização: `%APPDATA%\Cursor\User\settings.json`

Este arquivo contém as configurações gerais do editor:

#### Editor
- Tamanho da fonte: 14px
- Fonte: Consolas, Courier New, monospace
- Altura da linha: 1.5
- Tamanho da tab: 4 espaços
- Word wrap: ativado
- Minimap: ativado
- Rulers: 80 e 120 caracteres
- Colorização de parênteses: ativada

#### Terminal
- Tamanho da fonte: 14px
- Fonte: Consolas, Courier New, monospace
- Perfil padrão: PowerShell

#### Workbench
- Tema: Default Dark+
- Ícones: vs-seti
- Editor inicial: novo arquivo
- Preview de editores: desativado
- Barra lateral: esquerda
- Painel: baixo

#### Arquivos
- Auto-save: após 1 segundo
- Remover espaços em branco: ativado
- Inserir nova linha final: ativado
- Exclusões de arquivos configuradas

#### Python
- Interpreter padrão: python
- Linting: ativado (pylint, flake8)
- Formatação: black (88 caracteres)
- Format on save: ativado

#### Git
- Ativado
- Auto-fetch: ativado
- Smart commit: ativado

#### Cursor Específico
- Chat ativado
- Modelo padrão: gpt-4
- Auto-save do chat: ativado

#### Configurações por Linguagem
- Python: tab 4, ruler 88
- JavaScript/TypeScript: tab 2, ruler 80
- JSON/HTML/CSS: tab 2
- Markdown: word wrap, ruler 80

## Como Aplicar as Configurações

1. **Reiniciar o Cursor**: Feche e abra o Cursor para aplicar as configurações
2. **Verificar**: Teste algumas teclas de atalho para confirmar que estão funcionando
3. **Personalizar**: Você pode modificar os arquivos conforme necessário

## Personalização

### Adicionar Novas Teclas de Atalho
Edite o arquivo `keybindings.json` e adicione novas entradas:

```json
{
    "key": "ctrl+shift+alt+n",
    "command": "seu.comando.aqui",
    "when": "editorTextFocus"
}
```

### Modificar Configurações
Edite o arquivo `settings.json` para alterar configurações:

```json
{
    "editor.fontSize": 16,
    "workbench.colorTheme": "Light+"
}
```

## Resolução de Problemas

### Teclas de Atalho Não Funcionam
1. Verifique se o arquivo `keybindings.json` está no local correto
2. Reinicie o Cursor
3. Verifique se não há conflitos com outras configurações

### Configurações Não Aplicadas
1. Verifique se o arquivo `settings.json` está no local correto
2. Reinicie o Cursor
3. Verifique a sintaxe JSON

### Localização dos Arquivos
- Windows: `%APPDATA%\Cursor\User\`
- macOS: `~/Library/Application Support/Cursor/User/`
- Linux: `~/.config/Cursor/User/`

## Extensões Recomendadas

Para uma experiência completa do VS Code, considere instalar:

1. **Python**
   - Python (Microsoft)
   - Pylance
   - Python Docstring Generator

2. **Git**
   - GitLens
   - Git History

3. **Produtividade**
   - Auto Rename Tag
   - Bracket Pair Colorizer
   - Path Intellisense
   - Prettier

4. **Temas e Ícones**
   - Material Icon Theme
   - One Dark Pro

## Notas Importantes

- O Cursor é baseado no VS Code, então a maioria das configurações é compatível
- Algumas funcionalidades específicas do Cursor (como o chat AI) podem ter configurações próprias
- As configurações são aplicadas globalmente para todos os projetos
- Você pode criar configurações específicas por workspace criando arquivos `.vscode/settings.json` nos projetos
