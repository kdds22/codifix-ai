
import json
import os
import ast
from dotenv import load_dotenv
load_dotenv()

from . import big_queries
# import big_queries

def config_environment():    
    access_token = ast.literal_eval(os.environ["BIGQUERY_SERVICE_ACCOUNT"])    
    file_name = "service_account.json"
    with open(file_name, 'w') as json_file:
        json.dump(access_token, json_file, indent=4)
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "service_account.json"
    return f"project_id: {access_token['project_id']}"
    

def start_bigquery(directory_path):
    return big_queries.mostrar_erros_por_tipo(directory_path)


if __name__ == "__main__":
    directory_path = 'erros'
    config_environment()
    result = start_bigquery(directory_path=directory_path)
    print(result)