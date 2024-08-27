import os, sys

start_message = {
    'en': f'_Hello_ `%s`!{os.linesep}_Welcome to_ %s{os.linesep}(`%s`).',
    'pt': f'_Olá_ `%s`!{os.linesep}_Bem vindo ao_ %s{os.linesep}(`%s`).'
}

language_dictionary = {
    'start_message': {
        'en': f'_Hello_ `%s`!{os.linesep}_Welcome to_ %s{os.linesep}(`%s`).',
        'pt': f'_Olá_ `%s`!{os.linesep}_Bem vindo ao_ %s{os.linesep}(`%s`).'    
    },
    'help_message': {
        'en': f"_Commands available for %s:_{os.linesep}",
        'pt': f"_Commandos disponíveis %s:_{os.linesep}"    
    },
    'command_not_implemented': {
        'en': f'_Sorry, the command has not yet been implemented:_ %s{os.linesep}',
        'pt': f"_Desculpe, o comando_ %s _ainda não foi implementado._{os.linesep}"
    }
}

def get_translated_message(language_code: str, message_key: str, default_language = 'en', *args):
    
    if message_key in language_dictionary and language_code in language_dictionary[message_key]:
        
        return language_dictionary[message_key][language_code] % args
    
    else:
        
        if default_language in language_dictionary[message_key]:
            
            return language_dictionary[message_key][default_language] % args
            
    
    return None

if __name__ == '__main__':
    
    print(get_translated_message('en', 'start_message', 'John Doe', 'My Bot', 'MyBot'))
    print(get_translated_message('pt', 'start_message', 'João Silva', 'Meu Bot', 'MeuBot'))
    print(get_translated_message('es', 'start_message', 'Juan Perez', 'Mi Bot', 'MiBot'))
    print(get_translated_message('en', 'help_message', 'John Doe', 'My Bot', 'MyBot'))
    print(get_translated_message('pt', 'help_message', 'João Silva', 'Meu Bot', 'MeuBot'))