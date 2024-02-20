# Import necessary modules
import openai
import os
import sys
import time
import json
import re
import ast
from constants import DEFAULT_DIRECTORY, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from utils import clean_dir, write_file, get_file_content, get_file_paths, get_functions, chunk_and_summarize, num_tokens_from_string
from codingagents import clarifying_agent, algorithm_agent, coding_agent, debug_agent, file_code_agent, unit_test_agent
from glob import glob
from openai.embeddings_utils import get_embedding
import pathlib
import pandas as pd
from db import DB, DBs
import numpy as np
import traceback
from dotenv import load_dotenv
# Initialize OpenAI and GitHub API keys
openai.api_key = os.getenv('OPENAI_API_KEY')

tokenLimit = 50000
DEFAULT_MODEL = 'gpt-4-1106-preview'  # Set your default model here

class CodebaseGenerator:
    def __init__(self, prompt, directory):
        self.prompt = prompt
        self.directory = directory

    def clarify_prompt(self):
        while True:
            clarifying_prompt = clarifying_agent()
            clarifying_prompt += (
                '\n\n'
                'Is anything unclear? If yes, only answer in the form:\n'
                '{remainingunclear areas} remaining questions. \n'
                '{Next question}\n'
                'If everything is sufficiently clear, only answer "no".'
            )
            clarifying_questions = self.chat_with_gpt3(clarifying_prompt, self.prompt)
            print(clarifying_questions)
            user_input = input('(answer in text, or "q" to move on)\n')
            self.prompt += user_input
            print()

            if not user_input or user_input.strip().lower() == 'q':
                break
        return json.dumps(self.prompt)

    def parse_response(self, response):
        # Check if design_response is not empty and is a string
        if response and isinstance(response, str):
            try:
                # Attempt to parse the JSON string
                program_design = json.loads(response)
                return program_design
            except json.JSONDecodeError:
                # Handle the case where design_response is not a valid JSON string
                print("Failed to decode JSON. Handling as a string or other format.")
                # Here, you can implement custom logic depending on your needs
                # For example, check if it's a specific string format you can handle
                # Or log the error and return a default object or error message
                return None
        elif isinstance(response, (dict, list)):
            # If design_response is already a dictionary or list, return it directly
            return response
        else:
            # Handle other unexpected data types
            print("Unexpected data type received.")
            return None

    def design_program_structure(self):
        print("Designing program structure based on requirements...")

        systemprompt = f"""Based on the following clarified requirements:

        {self.prompt}


        Provide a JSON structure of the program architecture, including modules, classes, functions, 
        relationships, and dataflow. An example format is provided below:

        {{
            "modules": [],
            "classes": [],
            "functions": [],
            "relationships": [],
            "dataflow": []
        }}

        This description should include:

        - Module names and their responsibilities
        - Class definitions and their methods
        - Functions and their purpose
        - Relationships and interactions between components
        - Data flow within the program
        
        Present the design in a structured JSON format.
        """
        design_response = self.chat_with_gpt3(systemprompt, self.prompt)
        print(f"program design:  {design_response}")
        # Parse the returned JSON string into a Python dictionary.
        program_design = self.parse_response(design_response)
        return program_design
    def generate_file_paths(self, program_structure):
        # Convert program_structure to JSON string if not already in that form
        program_structure_json = json.dumps(program_structure) if isinstance(program_structure, dict) else program_structure
        systemprompt = f"""You are an AI developer who is trying to write a program that will generate code for the user based on their intent.
        Based on the follow program requirements:
        {program_structure_json}
        When given their intent, create a complete, exhaustive list of filepaths that the user would write to make the program.
        An example format is provided below:

                    
        [README.md, main.py, models.py, data.py, utils.py]
        
        The filepaths should only list the paths for the program files and folders, structured in a way that adheres to the design specified in the program architecture. Simply provide the array structure of filepaths, without any additional explanation.
        """
        formatted_prompt = systemprompt.format(program_structure_json=program_structure_json)
        result = self.chat_with_gpt3(formatted_prompt, self.prompt)
        print(f"file path: {result}")
        cleaned_result = result.strip("` \n")
        try:
            filepaths = ast.literal_eval(cleaned_result)
        except (SyntaxError, ValueError):
        # If direct evaluation fails, attempt to manually parse the list using regex
            try:
                # This regex pattern assumes that the list items are properly quoted strings
                # and tries to capture the entire list structure including brackets
                pattern = r'\[\s*(?:\'[^\']*\'\s*,?\s*)*\]'
                match = re.search(pattern, cleaned_result, re.DOTALL)
                if match:
                    list_str = match.group(0)
                    # Evaluate the matched list string
                    return ast.literal_eval(list_str)
                else:
                    # If no match is found, return an empty list or raise an error
                    print("Failed to parse list with regex.")
                    return []
            except (SyntaxError, ValueError) as e:
                # Log any errors encountered during regex parsing
                print(f"Error during regex parsing: {e}")
                return []

        return filepaths

    def generate_shared_dependencies(self, filepaths_string, program_structure):

        # Prepare the prompt for the AI developer based on the program structure and file paths
        systemprompt = f"""As an AI developer, understand the program's architecture and file structure to identify shared dependencies required across the codebase. The program structure and intended file paths are as follows:

        Program Structure: {json.dumps(program_structure, indent=2)}
        File Paths: {filepaths_string}

        Based on the above context, identify shared dependencies across the program such as shared
        variables, common utility functions, data schemas, interfaces or classes that need to be 
        consistent and reusable. Provide your response in a JSON structure with the following format:

        {{
            "shared_variables": [],
            "common_utilities": [],
            "data_schemas": [],
            "interfaces": [],
            "classes": []
        }}

        Focus on extracting names and a brief description of the shared dependencies without extra explanations.
        """
        result = self.chat_with_gpt3(systemprompt, self.prompt)
        print(result)
        return result

    def generate_code_for_each_file(self, filepaths_string, program_structure, shared_dependencies=None):
        print("generating code")
        maincode, unit_tests_code = self.AI_generate_code_and_tests(
            filepaths_string, program_structure, shared_dependencies
        )

        # Write both the main code and unit test files to the directory
        main_file_path = os.path.join(self.directory, filepaths_string)
        unit_test_file_path = os.path.join(self.directory, "test", f"test_{filepaths_string}")

        # Ensure the directory for he tests exists
        os.makedirs(os.path.dirname(unit_test_file_path), exist_ok=True)

        self.write_files_to_directory(main_file_path, maincode)
        self.write_files_to_directory(unit_test_file_path, unit_tests_code)

        print(f"Code and unit tests for {filepaths_string} have been generated.")

    def AI_generate_code_and_tests(self, filepath, program_structure, shared_dependencies=None):
        new_prompt = f"""
        We are building a program in a structured and test-driven manner. Based on the given program
        structure and shared dependencies, your task is to generate the code for the file '{filepath}' as well
        as the corresponding unit tests to validate its correctness.

        Program Structure: {json.dumps(program_structure, indent=2)}
        Shared Dependencies if applicable: {json.dumps(shared_dependencies, indent=2)}
        Intent of the program: {self.prompt}

        For the file '{filepath}', generate the following:
        - The main code that implements the required functionality.
        - A corresponding set of unit tests that verify the correctness of the implementation.

        Please separate the main code and unit tests clearly, and ensure the unit tests are comprehensive
        and cover the expected behavior of the code.

        Begin generating the code and unit tests now using JSON format following the example:
        {{
            "main_code": ["def add(a, b):\\nreturn a + b"],
            "unit_tests": ["def test_add():\\nassert add(1, 2) == 3"]
        
        }}
        """
        
        # Call to AI service with the prompt and return the main code and unit tests.
        # Implement this with the actual machinery to call the generative model or API.
        response = self.chat_with_gpt3(new_prompt, self.prompt)
        
        # Parse the AI's response into main code and unit tests.
        # This could be a simple split in the response, or you might have markers in the
        # response text that indicate where the main code ends and the test code begins.
        # For demonstration purposes, response should be structured as a dict
        # with "main_code" and "unit_tests" fields.
        response_dict = json.loads(response)
        main_code = response_dict['main_code']
        unit_tests_code = response_dict['unit_tests']
        
        return main_code, unit_tests_code
    

    def write_files_to_directory(self, filepath, filecode):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        file_path = os.path.join(self.directory, filepath)
        with open(file_path, "w") as f:
            f.write(filecode)

    def debug_generated_code(self):
        extensions = ['py', 'html', 'js', 'css', 'c', 'rs']
        while True:
            code_files = []
            debug_logs = []
            failure_count = {}  # Keeps track of the number of failures for each function

            for extension in extensions:
                code_files.extend(
                    y for x in os.walk(directory) 
                    for y in glob(os.path.join(x[0], f'*.{extension}'))
                    )
            print("Total number of files:", len(code_files))
            if len(code_files) == 0:
                print("Double check that you have downloaded the repo and set the code_dir variable correctly.")
            all_funcs = []
            unit_tests = []
            for code_file in code_files:
                funcs = list(get_functions(code_file))
                code_tokens_string = json.dumps(code_file)
                code_tokens = num_tokens_from_string(code_tokens_string)
                if code_tokens < tokenLimit:
                    unit_test = unit_test_agent(code_file)
                else:
                    for func in funcs:

                        unit_test_prompt = unit_test_agent()
                        unit_test = self.chat_with_gpt3(unit_test_prompt, func)
                        unit_tests.append(unit_test)
                for func in funcs:
                    all_funcs.append(func)
            all_funcs_string = json.dumps(all_funcs)
            print("Total number of functions:", len(all_funcs))
            df = pd.DataFrame(all_funcs)
            df['code_embedding'] = df['code'].apply(lambda x: get_embedding(x, engine="text-embedding-ada-002")) 
            df['filepath'] = df['filepath'].apply(lambda x: x.replace(directory, ""))
            df.to_csv("functions.csv", index=True)
            df.head()
            debug_code_agent = self.chat_with_gpt3(debug_agent, all_funcs_string)

            if not debug_code_agent or debug_code_agent.strip().lower() == 'no':
                break
            else:
                print(debug_code_agent)


    def chat_with_gpt3(self, systemprompt, prompt):
        response = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": systemprompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9
        )
        return response['choices'][0]['message']['content']



def filter_filepaths(filepaths):
    filepaths_list = ast.literal_eval(filepaths)
    return [fp.lstrip('/') for fp in filepaths_list]


# Main function
def main(prompt, directory=DEFAULT_DIRECTORY, model=DEFAULT_MODEL, file=None):
    if prompt.endswith(".md"):
        with open(prompt, "r") as f:
            prompt = f.read()

    print("Hello, I am your local AI developer! You said you wanted:")
    print("\033[92m" + prompt + "\033[0m")
    # Get the new repo name from the user
    repo_name = input("Enter the name for the new directory: ")
    directory = os.path.join(directory, repo_name)
    
    prompt_string = json.dumps(prompt)

    # Initiate the codebase generator
    generator = CodebaseGenerator(prompt_string, directory)
    
    # Clarify the prompt
    new_prompt_string = generator.clarify_prompt()
    print(new_prompt_string)
    
    # Design program structure
    program_structure = generator.design_program_structure()
    print("Program structure designed:", program_structure)

    # Generate file paths
    filepaths = generator.generate_file_paths(program_structure)
    print(filepaths)
    
    # Generate shared dependencies
    shared_dependencies = generator.generate_shared_dependencies(filepaths, program_structure)

    # Generate code for each file and write to directory
    for filepath in filepaths:
        filecode = generator.generate_code_for_each_file(filepath, program_structure, shared_dependencies)
        generator.write_files_to_directory(filepath, filecode)

    # Debug generated code
    generator.debug_generated_code()




if __name__ == "__main__":
    if len(sys.argv) < 2:
        if not os.path.exists("prompt.md"):
            print("Please provide a prompt file or a prompt string")
            sys.exit(1)
        else:
            prompt = "prompt.md"

    else:
        prompt = sys.argv[1]

    directory = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DIRECTORY
    file = sys.argv[3] if len(sys.argv) > 3  else None
    main(prompt, directory, file)