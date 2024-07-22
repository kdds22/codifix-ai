
from datetime import datetime
from pydantic import BaseModel
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import BaseTool, \
    					 DirectoryReadTool, \
                         FileReadTool

directory_read_tool = DirectoryReadTool(directory='erros')
directory_read_tool_kotlin = DirectoryReadTool(directory='kotlin-files')
file_read_tool = FileReadTool()

from .models import custom_model as cm
from .tools import custom_tool as ct

bigquery_config_tool = ct.ConfigureDynamicEnvTool()
bigquery_research_tool = ct.BigQueryResearchTool()
git_search_tool = ct.GitSearchTool()
webhhok_tool = ct.WebhookTool()

human_input_value = False

now = datetime.now().strftime("%Y-%m-%d")

@CrewBase
class CodifixAiCrew():
	"""CodifixAi crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			allow_delegation=False,
			verbose=True
		)

	@agent
	def git_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['git_analyst'],
			allow_delegation=False,
			verbose=True
		)
  
	@agent
	def software_engineer(self) -> Agent:
		return Agent(
			config=self.agents_config['software_engineer'],
			allow_delegation=False,
			verbose=True
		)
  
	@agent
	def qa_software_engineer(self) -> Agent:
		return Agent(
			config=self.agents_config['qa_software_engineer'],
			allow_delegation=False,
			verbose=True
		)
  
	@agent
	def cf_qa_software_engineer(self) -> Agent:
		return Agent(
			config=self.agents_config['cf_qa_software_engineer'],
			allow_delegation=False,
			verbose=True
		)
  
	############################

	@task
	def config_env_task(self) -> Task:
		return Task(
			config=self.tasks_config['config_env_task'],
			agent=self.researcher(),
   			tools=[bigquery_config_tool],
			human_input=human_input_value
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.researcher(),
   			tools=[directory_read_tool, file_read_tool, bigquery_research_tool],
			output_json=cm.BigQueryError,
			output_file="firebase_error_report.json",
			human_input=human_input_value
		)

	@task
	def git_repo_task(self) -> Task:
		return Task(
			config=self.tasks_config['git_repo_task'],
			agent=self.git_analyst(),
			tools=[git_search_tool],
			human_input=human_input_value
		)
  
	@task
	def git_file_task(self) -> Task:
		return Task(
			config=self.tasks_config['git_file_task'],
			agent=self.git_analyst(),
			tools=[directory_read_tool_kotlin, file_read_tool],
			output_json=cm.GitFileError,
			context=[self.git_repo_task()],
			human_input=human_input_value,
		)

	@task
	def code_task(self) -> Task:
		return Task(
			config=self.tasks_config['code_task'],
			agent=self.software_engineer(),
			output_json=cm.FileSuggest,
			context=[self.research_task(), self.git_file_task()],
			human_input=human_input_value
		)
  
	@task
	def review_task(self) -> Task:
		return Task(
			config=self.tasks_config['review_task'],
			agent=self.qa_software_engineer(),
      		output_json=cm.FileSuggest,
			context=[self.code_task(), self.git_file_task()],
			human_input=human_input_value
		)

	@task
	def evaluate_task(self) -> Task:
		return Task(
			config=self.tasks_config['evaluate_task'],
			agent=self.cf_qa_software_engineer(),
			output_file=f"file_error_solved_{now}.md",
			context=[self.research_task(), self.code_task(), self.review_task()],
			human_input=human_input_value
		)
  
	# @task
	# def microsoft_teams_task(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['microsoft_teams_task'],
	# 		agent=self.notifier(),
	# 		json_model=cm.WebhookModel,
	# 		output_json="microsoft_teams_notification.json",
	# 		tools=[ct.WebhookTool],
	# 		human_input=human_input_value,
	# 	)




	@crew
	def crew(self) -> Crew:
		"""Creates the CodifixAi crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)