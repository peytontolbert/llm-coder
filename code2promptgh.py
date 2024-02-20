import os
import openai
import pandas as pd
import numpy as np
import json
from dotenv import load_dotenv
from glob import glob
from constants import DEFAULT_DIRECTORY, DEFAULT_MODEL, DEFAULT_MAX_TOKENS, EXTENSION_TO_SKIP
from openai.embeddings_utils import get_embedding
from utils import get_file_paths, get_file_content, get_function_name, get_until_no_space, num_tokens_from_string, truncate_text_tokens, len_safe_get_embedding, save_embedded_code
from codeagents import code_understanding_agent, code_error_detection_agent, code_testing_agent, code_optimization_agent, code_documentation_agent, code_algorithm_agent, code_design_agent, code_prompt_agent
from gptfunctions import ChatGPTAgent

# Load environmental variables and set global constants
load_dotenv()
tokenLimit = 50000
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
CLONE_DIR = os.getenv('CLONE_DIR', '')

# Ensure API key is available
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set it in your environment variables.")

openai.api_key = OPENAI_API_KEY


class CodeToPromptConverter:
    """
    A class to handle the conversion of code to a format suitable for AI model prompting.
    """

    def __init__(self, token_limit=50000):
        """
        Initialize the converter with a token limit.

        Parameters:
        token_limit (int): The maximum number of tokens to process.
        """
        self.token_limit = token_limit
        pass

    def convert(self, code_files, clone_dir):
        """
        Convert code files into prompts.

        Parameters:
        code_files (list): List of paths to code files.
        clone_dir (str): Directory path where the code resides.

        Returns:
        None
        """
        all_funcs = []
        all_docs = []

        for code_file in code_files:
            docs = list(self.chunk_and_summarize(code_file))
            funcs = list(self.get_functions(code_file))

            # Skip the file if both docs and funcs are empty (indicating an empty or non-processable file)
            if not docs and not funcs:
                print(f"Skipping empty or non-processable file: {code_file}")
                continue

            all_funcs.extend(funcs)
            all_docs.extend(docs)

        if all_docs:
            all_docs_string = json.dumps(all_docs)
            tokens = num_tokens_from_string(all_docs_string)
            save_embedded_code(all_funcs, clone_dir, "functions", "code")
            save_embedded_code(all_docs, clone_dir, "documentations", "doc")
            if tokens < tokenLimit:
                print("tokens < limit with all docs. getting prompt")
                prompt = ChatGPTAgent.chat_with_gpt3(all_docs_string, code_prompt_agent())
                print(f"Prompt: " + prompt)
                self.save_prompts_to_file(prompt, 'prompts.txt')  # Save to a text file
            else:
                algorithms, designs = self.create_algorithms_and_design(all_docs)  
                prompts = self.create_prompts_from_algorithms_and_designs(algorithms, designs)
                prompts_string = json.dumps(prompts)
                prompts_tokens = num_tokens_from_string(prompts_string)     
                if prompts_tokens < tokenLimit:
                    prompt = ChatGPTAgent.chat_with_gpt3(prompts_string, code_prompt_agent())
                    print(prompt)
                    self.save_prompts_to_file(prompt, 'prompts.txt')  # Save to a text file
                else:
                    print("Need to chunk data for prompts") 
                    print(prompts)
                    self.save_prompts_to_file(prompts, 'prompts.txt')  # Save to a text file
            print("Total number of functions:", len(all_funcs))

    def save_prompts_to_file(self, prompts, filename):
        """
        Save the generated prompts to a text file.

        Parameters:
        prompts (str or list): The prompts to be saved.
        filename (str): The name of the file where prompts will be saved.
        """
        with open(filename, 'a') as file:  # 'a' mode appends to the file if it already exists
            if isinstance(prompts, list):
                for prompt in prompts:
                    file.write(prompt + "\n\n")
            else:
                file.write(prompts + "\n\n")

    def chunk_and_summarize(self, code_file):
        code = get_file_content(code_file)
        if code is None:
            return None
        tokens = num_tokens_from_string(code)
        function_list = []
        docs = []
        if tokens < tokenLimit:
            doc_text = ChatGPTAgent.chat_with_gpt3(code, code_documentation_agent())
            docs.append({"doc": doc_text, "code": code, "filepath": code_file})  # dict
            print("tokens < limit. saving full code")
            docs.append({"doc": doc_text, "code": code, "filepath": code_file})  # dict
        else:
            funcs = list(self.get_functions(code))
            for func in funcs:
                potential_tokens = tokens + num_tokens_from_string(func)
                if potential_tokens < tokenLimit:
                    function_list.append(func)
                    tokens = potential_tokens
                else:
                    print("Need to chunk the data but not lose track when doing multiple summaries") 
                    function_list = [func]
                    tokens = num_tokens_from_string(code)
            if function_list:
                doc = ChatGPTAgent.chat_with_gpt3(function_list, code_documentation_agent())
                docs.append(doc)
        return docs
    
    def get_functions(self, filepath):
        """
        Get all functions in a Python file.
        """
        with open(filepath, 'r') as file:
            whole_code = file.read().replace('\r', '\n')
        all_lines = whole_code.split("\n")
        for i, l in enumerate(all_lines):
            if l.startswith("def "):
                code = get_until_no_space(all_lines, i)
                function_name = get_function_name(code)
                yield {"code": code, "function_name": function_name, "filepath": filepath}

    def create_algorithms_and_design(self, all_docs):
        all_docs_string = json.dumps(all_docs)
        tokens = num_tokens_from_string(all_docs_string)
        algorithms = []
        designs = []
        docs_list = []
        if tokens < tokenLimit:
            algorithm = ChatGPTAgent.chat_with_gpt3(all_docs_string, code_algorithm_agent())
            algorithms.append(algorithm)
            design = ChatGPTAgent.chat_with_gpt3(all_docs_string, code_design_agent())
            designs.append(design)
        else:
            for doc in all_docs:
                doc_string = json.dumps(doc)
                potential_tokens = tokens + num_tokens_from_string(doc_string)
                if potential_tokens < tokenLimit:
                    docs_list.append(doc_string)
                    tokens = potential_tokens
                else:
                    doc_list_string = json.dumps(docs_list)
                    algorithm = ChatGPTAgent.chat_with_gpt3(doc_list_string, code_algorithm_agent())
                    algorithms.append(algorithm)    
                    design = ChatGPTAgent.chat_with_gpt3(doc_list_string, code_design_agent())
                    designs.append(design)
                    docs_list = [doc_string]
                    tokens = num_tokens_from_string(all_docs_string)
            if docs_list:
                doc_list_string = json.dumps(docs_list)
                algorithm = ChatGPTAgent.chat_with_gpt3(doc_list_string, code_algorithm_agent())
                algorithms.append(algorithm)
                design = ChatGPTAgent.chat_with_gpt3(doc_list_string, code_design_agent())
                designs.append(design)
        return algorithms, designs

    def create_prompts_from_algorithms_and_designs(self, algorithms, designs):
        prompts = []
        for algorithm, design in zip(algorithms, designs):
            prompt = "Algorithm: " + algorithm + "\nDesign: " + design
            prompts.append(prompt)
        return prompts


def main():
    """
    Main function to execute the code conversion process.
    """
    code_files = [y for x in os.walk(CLONE_DIR) for ext in ('*.py', '*.js', '*.cpp', '*.rs', '*.md', '*.txt', '*.html') for y in glob(os.path.join(x[0], ext))]
    if not code_files:
        print("No code files found in the specified directory.")
        return
    converter = CodeToPromptConverter(tokenLimit)
    converter.convert(code_files, CLONE_DIR)

    


if __name__ == "__main__":
    main()