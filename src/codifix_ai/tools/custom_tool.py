import os
from dotenv import load_dotenv
load_dotenv()

import requests
from pydantic import BaseModel
from typing import List

from crewai_tools import BaseTool

from ..models import custom_model as cm
from . import bigquery_script, repo_downloader, extrator_funcao, webhook

class ConfigureDynamicEnvTool(BaseTool):
    name: str ="Dynamic Environment Key Tool"
    description: str = ("Configuring dynamic keys on environment.")
    
    def _run(self, text: str) -> str:
        return bigquery_script.config_environment()

class BigQueryResearchTool(BaseTool):
    name: str ="Google BigQuery Research Tool"
    description: str = ("Getting the error data of bigquery "
         "to identify possible error causes.")
    
    def _run(self, text: str) -> str:
        return bigquery_script.start_bigquery('erros')


class GitSearchTool(BaseTool):
	name: str="Git Helper Tool"
	description: str = ("Getting the project files repository to "
					 "to analyze the reported errors.")
	
	def _run(self, text: str) -> str:
		return repo_downloader.start_repo_downloader("repo_temp",'erros',"kotlin-files")


class WebhookTool(BaseTool):
    name: str ="Webhook Tool"
    description: str = ("Sending a webhook to a specified channel "
         "to notify about the error. And receiving the status code it the end")
    
    def _run(self, text: str) -> str:
        webhook_model = cm.WebhookModel(
            themeColor="#0078D7",
            summary=f"CodiFix - Sugestão: {text}.",
            sections=[
                cm.SectionModel(
                    activityTitle="Mensagem de Erro",
                    activitySubtitle="CodiFix webhook XPTO",
                ),
            ],
        )
        return webhook.send_teams_by_model(webhook_model)
    

