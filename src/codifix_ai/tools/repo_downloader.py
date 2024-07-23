import os
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from git import Repo
import git
import json
from . import get_stack_trace
import shutil

def search_and_copy_files(repo_dir, filenames, destination_dir):
    # print(f"Arquivos: {filenames}")
    found_files = set()
    for root, dirs, files in os.walk(repo_dir):
        for filename in filenames:
            # print(f"Procurando Arquivo: {filename} entre: {files}")
            if filename in files:
                source_file = os.path.join(root, filename)
                destination_file = os.path.join(destination_dir, filename)
                if filename not in found_files:
                    shutil.copy2(source_file, destination_file)
                    found_files.add(filename)
                    # print(f"Copiado {source_file} para {destination_file}")
    return found_files
    

def repo_downloader(repo_dir, error_folder_directory, destinarion_dir):
    # print('Baixando repositório do Projeto...\n')
    repo_url = f"https://{os.environ.get("GIT_AZURE_TOKEN")}@dev.azure.com/HavanLabs/{os.environ.get("SQUAD")}/_git/{os.environ.get("GIT_AZURE_REPO")}"

    if not os.path.exists(repo_dir) or not os.listdir(repo_dir):
        # print(f"Clonando repositorio de {repo_url} para {repo_dir}...")
        repo = Repo.clone_from(repo_url, repo_dir)
        # print("Repositorio clonado com sucesso.\n")
    else:
        print(f"Repositorio já existe {repo_dir}.\n")

    directory_path = Path(error_folder_directory) #Path('builder-crew/erros')
    list_file_error = get_stack_trace.get_file_list_error(directory_path=directory_path, log=False)

    # destinarion_dir = "builder-crew/kotlin-files"

    os.makedirs(destinarion_dir, exist_ok=True)

    # print('Criando backup dos arquivos...\n')
    final_result = search_and_copy_files(repo_dir=repo_dir, filenames=list_file_error, destination_dir=destinarion_dir)



    # with open('erros_por_tipo_20240611115838.json','r') as json_file:
    #     json_stack_trace = json.load(json_file)['FATAL']['Stack Trace']
    #     print(json_stack_trace)

    # repo = Repo(search_parent_directories=True)
    # original_branch = repo.active_branch
    # branch = repo.create_head("crashlytics-ai-auto-suggest")
    # branch.checkout()
    # repo.git.add('*')
    # repo.git.commit(m="Alteração sugerida pelos Agentes (Necessário validação)")
    # repo.git.push('--set-upstream', 'origin', branch)
    # original_branch.checkout()

    return final_result

def repo_delete(repo_dir):
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
        # print(f"........ Deletado repositorio clonado.\n")
    pass

def start_repo_downloader(repo_dir, error_folder_directory, destinarion_dir):
    # print('\n---------------------\n')
    # print('Procurando arquivos com erros...\n')
    final_result = repo_downloader(repo_dir, error_folder_directory, destinarion_dir)
    repo_delete(repo_dir=repo_dir)
    # print('\n---------------------\n')
    # print('..... Finalizada busca dos arquivos com erros.\n')
    return final_result

if __name__ == "__main__":
    repo_dir = "repo_temp"
    start_repo_downloader(repo_dir=repo_dir)
    pass



# rygcie53lap47drnkbkjc5oeop6v56ejuowerppvy334jazthhwq