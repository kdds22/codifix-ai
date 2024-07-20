
import os
import json
from pathlib import Path
from google.cloud import bigquery
from datetime import datetime

ignore_files = ['KotlinExtensions.kt', 'CoroutineScheduler.kt', 'DispatchedTask.kt','DispositivoBluetooth.kt','ZebraRFR8500.kt','ContinuationImpl.kt', 'ReaderManager.kt']

def mostrar_erros_por_tipo(path_folder):

    erros_analisados = []
    erros_analisados.append('te5t3')

    try:
        for file_path in Path(path_folder).iterdir():
            # print(f'File Path: {file_path}\n')
            if file_path.is_file() and file_path.suffix == '.json':
                with file_path.open(mode='r', encoding='utf-8') as json_file:
                    file_name = file_path.name.split('.')[0]
                    erros_analisados.append(file_name)
    except:
        print("Except: Não foram analisados nenhuma issue...")
    finally:
        if len(erros_analisados) <= 1:
            print("Não foram analisados nenhuma issue ainda...")
            erros_analisados.append('None')


    # print(f"{','.join(f"'{issue_id}'" for issue_id in erros_analisados)}")
    final_result = []
    client = bigquery.Client()    
    print(client)
    print(os.getcwd())
    query = f"""
        SELECT
            DISTINCT t1.issue_id,
            COUNT(DISTINCT t1.event_id) AS number_of_crashes,
            t1.error_type
        FROM
            `agility-picking.firebase_crashlytics.com_havan_app_abastecimento_ANDROID` AS t1
            LEFT OUTER JOIN `firebase_crashlytics.latest_issues_analyzed` AS t2 ON t1.issue_id = t2.issue_id
        WHERE
            t1.event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            AND t1.error_type = 'FATAL' --OR t1.error_type = 'NON_FATAL'
            AND t2.issue_id IS NULL
            -- issue_id not in erros_analisados
            AND t1.issue_id NOT IN ({','.join(f"'{issue_id}'" for issue_id in erros_analisados)})
        GROUP BY
            t1.issue_id,
            t1.error_type
        ORDER BY
            number_of_crashes DESC
        LIMIT 1;
    """

    query_job = client.query(query)
    results = query_job.result()

    erros_por_tipo = {}

    for row in results:
        detalhes_erro = {
            "issue_id": row.issue_id,
            "number_of_crashes": row.number_of_crashes,
            "error_type": row.error_type,
        }

        main_error_type = row.error_type

        if main_error_type not in erros_por_tipo:
            erros_por_tipo[main_error_type] = []

        erros_por_tipo[main_error_type].append(detalhes_erro)
    
    for tipo_erro in ['NON_FATAL','FATAL']:
        if tipo_erro not in erros_por_tipo:
            continue
        for erro in erros_por_tipo[tipo_erro]:
            final_result.append(buscar_excecoes_por_issue_id(erro['issue_id'], path_folder, erros_analisados=erros_analisados))
        pass
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

if __name__ == "__main__":
    path_folder = 'erros'
    mostrar_erros_por_tipo(path_folder)
    pass
