

from pydantic import BaseModel, Field
from typing import List

class BigQueryError(BaseModel):
    number_of_crashes: int = Field(..., description="The number of crashes of error reported")
    error_type: str = Field(..., description="The error type reported (FATAL | NON-FATAL)")
    title: str = Field(..., description="The main title of error reported")
    file: str = Field(..., description="The file name of error reported")
    line: int = Field(..., description="The line number that error occoured")
    function: str = Field(..., description="The function name blamed by error reported")
    description: str = Field(..., description="The optional exception message of error reported")
    subtitle: str = Field(..., description="The optional subtitle about the error reported")

class GitFileError(BaseModel):
	full_kotlin_code: str = Field(..., description="The full code of kotlin file thats contains the error reported")

class FileSuggest(BaseModel):
	errorName: str = Field(..., description="The main title of error reported")
	description: str = Field(..., description="The summary of the possible solutions ideas to solve the error reported")
	full_kotlin_code: str = Field(..., description="The full code of kotlin file thats contains the error reported")

class SectionModel(BaseModel):
	activityTitle: str = Field(..., description="The activities title about error reported")
	activitySubtitle: str = Field(..., description="The activities subtitle with summary of the solution implemented to solve error")

class WebhookModel(BaseModel):
	themeColor: str = Field(..., description="The theme color for webhook card message")
	summary: str = Field(..., description="The webhook title about error reported")
	sections: List[SectionModel] = Field(..., description="The activities points about how to error was solved")