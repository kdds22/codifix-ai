#!/usr/bin/env python
from codifix_ai.crew import CodifixAiCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'GIT_AZURE_TOKEN': "",
        'GIT_AZURE_REPO': "",
        'SQUAD': '',
        
    }
    CodifixAiCrew().crew().kickoff(inputs=inputs)