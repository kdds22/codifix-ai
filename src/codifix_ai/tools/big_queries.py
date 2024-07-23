
import os
import json
from pathlib import Path
from google.cloud import bigquery
from datetime import datetime

from dotenv import load_dotenv
load_dotenv() 

ignore_files = ['KotlinExtensions.kt', 'CoroutineScheduler.kt', 'DispatchedTask.kt','DispositivoBluetooth.kt','ZebraRFR8500.kt','ContinuationImpl.kt', 'ReaderManager.kt']

def mostrar_erros_por_tipo(path_folder):

    erros_analisados = []
    erros_analisados.append('te5t3')
    
    eventos_analisados = []
    eventos_analisados.append('12345')

    try:
        for file_path in Path(path_folder).iterdir():
            # print(f'File Path: {file_path}\n')
            if file_path.is_file() and file_path.suffix == '.json' and not file_path.name.startswith('event_id_'):
                with file_path.open(mode='r', encoding='utf-8') as json_file:
                    file_name = file_path.name.split('.')[0]
                    erros_analisados.append(file_name)
            if file_path.is_file() and file_path.name.startswith('event_id_'):
                with file_path.open(mode='r', encoding='utf-8') as json_file:
                    file_name = file_path.name.split('.')[0].split('_')[-1]
                    print(file_name)
                    eventos_analisados.append(file_name)
    except:
        print("\nExcept: Não foram analisados nenhuma issue...")
        print("\nExcept: Não foram analisados nenhum evento...")

    finally:
        if len(erros_analisados) <= 1:
            print("\nNão foram analisados nenhuma issue ainda...")
            erros_analisados.append('None')
        if len(eventos_analisados) <= 1:
            print("\nNão foram analisados nenhum evento ainda...")
            eventos_analisados.append('None')


    # print(f"{','.join(f"'{issue_id}'" for issue_id in erros_analisados)}")
    final_result = []
    client = bigquery.Client()
    query = f"""
        SELECT
            DISTINCT t1.issue_id,
            COUNT(DISTINCT t1.event_id) AS number_of_crashes,
            t1.error_type,
            t4.file,
            t4.symbol,
        FROM
            `agility-picking.firebase_crashlytics.com_havan_app_abastecimento_ANDROID` AS t1
            LEFT OUTER JOIN `firebase_crashlytics.latest_issues_analyzed` AS t2 ON t1.issue_id = t2.issue_id
            LEFT JOIN UNNEST(t1.exceptions) as t3 on t3.blamed = True
            LEFT JOIN UNNEST(t3.frames) as t4 on t4.owner = 'DEVELOPER'
        WHERE
            t1.event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 28 DAY)
            AND t1.error_type = 'FATAL' --OR t1.error_type = 'NON_FATAL'
            AND t2.issue_id IS NULL
            AND t1.issue_id NOT IN ({','.join(f"'{issue_id}'" for issue_id in erros_analisados)})
            AND SPLIT(t4.file, '.')[SAFE_OFFSET(1)] = 'kt' --SOMENTE ARQUIVOS KOTLIN
        GROUP BY
            t1.issue_id,
            t1.error_type,
            t4.file,
            t4.symbol
        ORDER BY
            number_of_crashes DESC
        LIMIT 1;
    """

    # print(query)
    query_job = client.query(query)
    results = query_job.result()

    erros_por_tipo = {}

    for row in results:
        detalhes_erro = {
            "issue_id": row.issue_id,
            "number_of_crashes": row.number_of_crashes,
            "error_type": row.error_type,
            "file": row.file,
            "symbol": row.symbol
        }
        
        # print(detalhes_erro)

        main_error_type = row.error_type

        if main_error_type not in erros_por_tipo:
            erros_por_tipo[main_error_type] = []

        erros_por_tipo[main_error_type].append(detalhes_erro)
    
    for tipo_erro in ['NON_FATAL','FATAL']:
        if tipo_erro not in erros_por_tipo:
            continue
        for erro in erros_por_tipo[tipo_erro]:
            final_result.append(salvar_dados(path_folder,erro))
    if final_result == [{}]:
        return mostrar_erros_por_tipo(path_folder)
    return final_result

def buscar_excecoes_por_issue_id(issue_id: str, path_folder, erros_analisados):
    client = bigquery.Client()
    query = f"""
    SELECT
        blame_frame.file,
        blame_frame.line,
        exceptions
    FROM `agility-picking.firebase_crashlytics.com_havan_app_abastecimento_ANDROID`
    WHERE
        error_type IS NOT NULL 
        AND issue_id = '{issue_id}' 
        
    """
#--AND issue_id NOT IN ({','.join(f"'{issue_id}'" for issue_id in erros_analisados)})
    query_job = client.query(query)
    results = query_job.result()

    erros_por_arquivo = {}

    duplicate = []
    stack_trace = ""

    for row in results:
        if(row.file != None):
            if row.exceptions:
                exception_details = row.exceptions[0]  
                stack_trace = "\n".join([
                    f"       at {frame['file']}({frame['symbol']}:{frame['line']})"
                    for frame in exception_details['frames']
                    if frame['owner'] == 'DEVELOPER' and frame['blamed'] == True and frame['file'].split('.')[1] == 'kt'
                ])
            else:
                pass
                stack_trace = "Sem stack trace disponível"
            if stack_trace != "" and stack_trace not in duplicate:
                duplicate.append(stack_trace)

                detalhes_erro = {
                    "title": exception_details['title'],
                    "file": row.file,
                    "line": row.line,
                    "function": stack_trace.split('(')[1].split(':')[0],
                    "Stack Trace": stack_trace,    
                }
                if row.file not in ignore_files:
                    if row.file not in erros_por_arquivo:
                        erros_por_arquivo[row.file] = []

                    if detalhes_erro not in erros_por_arquivo[row.file]:
                        erros_por_arquivo[row.file].append(detalhes_erro)
    if len(erros_por_arquivo) > 0:
        os.makedirs(path_folder, exist_ok=True)
        file_name = f"{path_folder}/{issue_id}.json"
        with open(file_name, 'w') as json_file:
            json.dump(erros_por_arquivo, json_file, indent=4)

    #TODO: salvar erros por stackTrace, e não somente por issue_id
    return erros_por_arquivo

def buscar_blame_frame_por_issue_id(issue_id: str, path_folder, erros_analisados):
    client = bigquery.Client()
    query = f"""
    SELECT
        blame_frame.file,
        blame_frame.line,
        blame_frame.symbol,
        exceptions
    FROM `agility-picking.firebase_crashlytics.com_havan_app_abastecimento_ANDROID`
    WHERE
        error_type IS NOT NULL 
        AND issue_id = '{issue_id}'
        AND blame_frame.owner = "DEVELOPER"
        AND blame_frame.blamed = true
        
    """
    
    # print(query)
    query_job = client.query(query)
    results = query_job.result()

    erros_por_arquivo = {}

    for row in results:
        # print(row.file)
        # print(row.file.split('.'))
        # print(row.file.split('.')[-1])
        if(row.file != None and row.file.split('.')[-1] == 'kt'):
            print('\n\n ----')
            print(row.file)
            
            detalhes_erro = {
                "file": row.file,
                "line": row.line,
                "function": row.symbol
            }
            if row.file not in ignore_files:
                if row.file not in erros_por_arquivo:
                    erros_por_arquivo[row.file] = []

                if detalhes_erro not in erros_por_arquivo[row.file]:
                    erros_por_arquivo[row.file].append(detalhes_erro)
                    
            os.makedirs(path_folder, exist_ok=True)
            file_event_id = f"{path_folder}/event_id_{row.event_id}.json"
            with open(file_event_id, 'w') as json_file:
                json.dump(detalhes_erro, json_file, indent=4)
    if len(erros_por_arquivo) > 0:
        os.makedirs(path_folder, exist_ok=True)
        file_name = f"{path_folder}/{issue_id}.json"
        with open(file_name, 'w') as json_file:
            json.dump(erros_por_arquivo, json_file, indent=4)

    #TODO: salvar erros por stackTrace, e não somente por issue_id
    return erros_por_arquivo

def salvar_dados(path_folder,detalhes_erro):

    erros_por_arquivo = {}
    if detalhes_erro.file not in ignore_files:
        if detalhes_erro.file not in erros_por_arquivo:
            erros_por_arquivo[detalhes_erro.file] = []

        if detalhes_erro not in erros_por_arquivo[detalhes_erro.file]:
            erros_por_arquivo[detalhes_erro.file].append(detalhes_erro)
            
    if len(erros_por_arquivo) > 0:
        os.makedirs(path_folder, exist_ok=True)
        file_name = f"{path_folder}/{detalhes_erro.issue_id}.json"
        with open(file_name, 'w') as json_file:
            json.dump(erros_por_arquivo, json_file, indent=4)
            
    return erros_por_arquivo

if __name__ == "__main__":
    path_folder = 'erros'
    mostrar_erros_por_tipo(path_folder)
    pass
