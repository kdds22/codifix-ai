
import json
import re
from pathlib import Path

# Definir a regex para arquivos Kotlin -> *.kt
default_pattern = re.compile(r'[A-Za-z]+(?:[A-Za-z0-9]+)*\.kt')
ignore_files = ['CoroutineScheduler.kt', 'DispatchedTask.kt','ZebraRFR8500.kt','ContinuationImpl.kt', 'ReaderManager.kt']

def search_pattern_in_stack_trace(json_data, pattern, key_search):
    matches = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == key_search and isinstance(value, str):
                matches.extend(pattern.findall(value))
            elif isinstance(value, list) or isinstance(value, dict):
                matches.extend(search_pattern_in_stack_trace(value, pattern, key_search))
    elif isinstance(json_data, list):
        for item in json_data:
            matches.extend(search_pattern_in_stack_trace(item, pattern, key_search))
    return list(set(matches))

def search_pattern_in_symbol(json_data, pattern, key_search):
    matches = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            for v in value:
                matches.append(v[key_search])
    return list(set(matches))

def get_file_list_error(directory_path: str, log: bool = False):
    print(f'Procurando arquivos nos diretórios... {directory_path}\n')

    list_match_unique = []

    for file_path in directory_path.iterdir():
        if file_path.is_file() and file_path.suffix == '.json':
            with file_path.open(mode='r', encoding='utf-8') as file:
                content = json.load(file)

                matches = search_pattern_in_stack_trace(content, default_pattern, "file")
                unique_matches = list(set(matches))
                print(f'Unique_matches: {unique_matches}\n')

                for match in unique_matches:
                    if (match not in ignore_files):
                        list_match_unique.append(match)


                if (log):
                    print(f"Conteúdo do arquivo {file_path.name}:")
                    print(content)
                    print(f"Arquivios únicos encontrados:")
                    print(list_match_unique)
    
    return list(set(list_match_unique))
    
   

if __name__ == '__main__':
    directory_path = Path('erros')
    print(get_file_list_error(directory_path=directory_path, log=False))
    pass