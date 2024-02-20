import os
from constants import EXTENSION_TO_SKIP
import tiktoken
from itertools import islice
from openai.embeddings_utils import get_embedding, cosine_similarity
import numpy as np
import pandas as pd
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_not_exception_type
import openai
from gptfunctions import ChatGPTAgent
from codeagents import code_understanding_agent, code_documentation_agent


EMBEDDING_MODEL='text-embedding-ada-002'
EMBEDDING_ENCODING = 'cl100k_base'
EMBEDDING_CTX_LENGTH = 8191

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def walk_directory(directory):
    code_contents = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not any(file.endswith(ext) for ext in EXTENSION_TO_SKIP):
                try:
                    relative_filepath = os.path.relpath(os.path.join(root, file), directory)
                    code_contents[relative_filepath] = read_file(os.path.join(root, file))
                except Exception as e:
                    code_contents[relative_filepath] = f"Error reading file {file}: {str(e)}"
    return code_contents


def clean_dir(directory):
    # Check if the directory exists
    if os.path.exists(directory):
        # If it does, iterate over all files and directories
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                _, extension = os.path.splitext(filename)
                if extension not in EXTENSION_TO_SKIP:
                    os.remove(os.path.join(dirpath, filename))
    else:
        os.makedirs(directory, exist_ok=True)

        
def write_file(filename, filecode, directory):
    # Output the filename in blue color
    print("\033[94m" + filename + "\033[0m")
    print("saving file")
    file_path = os.path.join(directory, filename)
    dir = os.path.dirname(file_path)

    # Check if the filename is actually a directory
    if os.path.isdir(file_path):
        print(f"Error: {filename} is a directory, not a file.")
        return
    try:
        os.makedirs(dir, exist_ok=True)

        # Try to open the file
        try:
            file = open(file_path, "w")
        except OSError as e:
            print(f"Failed to open file {file_path}. Error: {e}")
            return

        # Try to write to the file
        try:
            file.write(filecode)
        except OSError as e:
            print(f"Failed to write to file {file_path}. Error: {e}")
            return
        finally:
            file.close()
    except OSError as e:
        print(f"Failed to create directories {dir}. Error: {e}")

def get_file_paths(clone_dir):
    
    # Walk the directory and get all file paths
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(clone_dir):
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))

    return file_paths

def get_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except UnicodeDecodeError:
        print(f'Skipped file due to ecoding issues: {file_path}')
        return None

def get_function_name(code):
    """
    Extract function name from a line beginning with "def "
    """
    assert code.startswith("def ")
    return code[len("def "): code.index("(")]


def get_until_no_space(all_lines, i) -> str:
    """
    Get all lines until a line outside the function definition is found.
    """
    ret = [all_lines[i]]
    for j in range(i + 1, i + 10000):
        if j < len(all_lines):
            if len(all_lines[j]) == 0 or all_lines[j][0] in [" ", "\t", ")"]:
                ret.append(all_lines[j])
            else:
                break
    return "\n".join(ret)


def get_functions(filepath):
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


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0613")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def truncate_text_tokens(text, encoding_name=EMBEDDING_ENCODING, max_tokens=EMBEDDING_CTX_LENGTH):
    """Truncate a string to have `max_tokens` according to the given encoding."""
    encoding = tiktoken.get_encoding(encoding_name)
    return encoding.encode(text)[:max_tokens]

def batched(iterable, n):
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while (batch := tuple(islice(it, n))):
        yield batch

def chunked_tokens(text, encoding_name, chunk_length):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks_iterator = batched(tokens, chunk_length)
    yield from chunks_iterator

def len_safe_get_embedding(text, model=EMBEDDING_MODEL, max_tokens=EMBEDDING_CTX_LENGTH, encoding_name=EMBEDDING_ENCODING, average=True):
    chunk_embeddings = []
    chunk_lens = []
    for chunk in chunked_tokens(text, encoding_name=encoding_name, chunk_length=max_tokens):
        chunk_embeddings.append(get_embedding(chunk, model=model))
        chunk_lens.append(len(chunk))

    if average:
        chunk_embeddings = np.average(chunk_embeddings, axis=0, weights=chunk_lens)
        chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings)  # normalizes length to 1
        chunk_embeddings = chunk_embeddings.tolist()
    return chunk_embeddings


def save_embedded_code(input, clone_dir, file, type, index=True):
    df = pd.DataFrame(input)
    print(input)
    # Check if 'code' column exists
    if type not in df.columns:
        print(f"Warning: Column '{type}' not found in DataFrame.")
        return

    df[type+'_embedding'] = df[type].apply(lambda x: get_embedding(x, engine="text-embedding-ada-002")) 
    df['filepath'] = df['filepath'].apply(lambda x: x.replace(clone_dir, ""))
    df.to_csv(file+".csv", index=index)
    df.head()
    
def chunk_and_summarize(code_file):
    chunks = 1
    tokenLimit = 2000
    code = get_file_content(code_file)
    if code is None:
        return None
    tokens = num_tokens_from_string(code)
    function_list = []
    summaries = []
    docs = []
    if tokens < tokenLimit:
        summary_text = ChatGPTAgent.chat_with_gpt3(code, code_understanding_agent())
        summaries.append({"summary": summary_text, "code": code, "filepath": code_file})  # dict
        doc_text = ChatGPTAgent.chat_with_gpt3(code, code_documentation_agent())
        print("tokens < limit. saving full code")
        docs.append({"doc": doc_text, "code": code, "filepath": code_file})  # dict
    else:
        funcs = list(get_functions(code))
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
            summary = ChatGPTAgent.chat_with_gpt3(function_list, code_understanding_agent())
            summaries.append(summary)
            doc = ChatGPTAgent.chat_with_gpt3(function_list, code_documentation_agent())
            docs.append(doc)
    return summaries, docs


def run_unit_tests(code_dir):
    os.chdir(code_dir)
    result = subprocess.run(['python'], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)