from dataclasses import dataclass
from io import StringIO
from typing import Iterator
import pandas as pd
import numpy as np
import yaml
from collections import Counter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Move the following utilies to a configuration file under setupCode
# def parseData(input: str) -> tuple[pd.DataFrame]:
#     '''
#     Parse the input data into a full dataframe and the separated dataframes,
#     Named ALL, A, B, C, D
#     '''
#     df = pd.read_csv(StringIO(input), delim_whitespace=True, header=None)
#     # return A,B,C,D dataframes from the full dataframe
#     return df, df.iloc[0:3, 0:6], df.iloc[0:3, 6:], df.iloc[3:, 0:6], df.iloc[3:, 6:]


# def dataframeToList(df: pd.DataFrame) -> list:
#     '''
#     Convert a dataframe to a list
#     '''
#     # Use a List Comprehension in Python to Flatten Lists of Lists
#     return [item for listItem in df.values.tolist() for item in listItem]


# def dataframeToSet(df: pd.DataFrame) -> set:
#     '''
#     Convert a dataframe to a set
#     '''
#     return set(dataframeToList(df))


# def seriesToList(series: pd.Series) -> list:
#     '''
#     Convert a series to a list
#     '''
#     # Use a List Comprehension in Python to Flatten Lists of Lists
#     return [item for item in series.values.tolist()]


# def seriesToSet(series: pd.Series) -> set:
#     '''
#     Convert a series to a set
#     '''
#     return set(seriesToList(series))


# def stringifyIterator(data: list[int] | set[int]) -> str:
#     '''
#     Stringify the iterable data to a space separated string
#     '''
#     logger.debug(f'data: {data}')
#     return ' '.join(map(lambda item: str(item), data))


# def duplicateSet(data: list) -> set:
#     '''
#     Find the duplicates in a list, return as a set
#     '''
#     counts = Counter(data)
#     result = [item for item in counts if counts[item] > 1]
#     return set(result)


# def occurTimesSet(df: pd.DataFrame, times: int) -> set:
#     '''
#     Find the elements that occur a given number of times in a dataframe, return as a set
#     '''
#     counts = Counter(dataframeToList(df))
#     result = [item for item in counts if counts[item] == times]
#     logger.info(f'counts: {counts}, result: {result}')
#     return set(result)


# def occurEqualGreatTimesSet(df: pd.DataFrame, times: int) -> list:
#     '''
#     Find the elements that occur greater equal then times in a dataframe, return as a set
#     '''
#     counts = Counter(dataframeToList(df))
#     result = [item for item in counts if counts[item] >= times]
#     logger.info(f'counts: {counts}, result: {result}')
#     return set(result)


@dataclass
class CodeBlock:
    '''
    CodeBlock class which holds the name, description and the code.
    '''
    name: str
    description: str
    code: str


def is_expression(expression: str):
    '''Check if the expression is a statement '''
    try:
        compile(expression, "<string>", "eval")
        return True
    except:
        return False


def evaluate(expression):
    """Evaluate an expression."""
    # # Compile the expression
    # code = compile(expression, "<string>", "eval")
    # # Validate allowed names
    # for name in code.co_names:
    #     if name not in ALLOWED_NAMES:
    #         raise NameError(f"The use of '{name}' is not allowed")
    # return eval(code, {"__builtins__": {}}, ALLOWED_NAMES)
    return eval(expression)


def save_configuration(configuration, filename='data-saved.yaml'):
    # write the data to yaml file
    with open(filename, encoding='utf-8', mode='w') as f:
        # yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
        # def string_presenter(dumper, data):
        #     if '\n' in data:
        #         return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
        #     return dumper.org_represent_str(data)
        # yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)
        def string_presenter(dumper, data):
            """Presenter to force yaml.dump to use multi-line string style."""
            if '\n' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        yaml.add_representer(str, string_presenter, Dumper=yaml.SafeDumper)
        yaml.dump(configuration, f, encoding='utf-8', allow_unicode=True, default_flow_style=False,
                  default_style=None, indent=2, width=1024, sort_keys=False, canonical=False)


__version__ = "0.1.0"

PS1 = "shell >>"

WELCOME = f"""
REPL {__version__}, your Python expressions evaluator!
Enter a valid math expression after the prompt "{PS1}".
Type "help" for more information.
Type "clear" to clear.
"""

USAGE = f"""
Usage:
Use the REPL to evaluate an expression.
Type "clear" to clear.
"""


def repl():
    """repl loop: Read and evaluate user's input."""
    print(WELCOME)
    while True:
        # Read user's input
        try:
            expression = input(f"{PS1} ")
        except (KeyboardInterrupt, EOFError):
            raise SystemExit()

        # Handle special commands
        if expression.lower() == "help":
            print(USAGE)
            continue
        if expression.lower() in {"quit", "exit"}:
            raise SystemExit()

        # Evaluate the expression and handle errors
        try:
            result = evaluate(expression)
        except SyntaxError:
            # If the user enters an invalid expression
            print("Invalid input expression syntax")
            continue
        except (NameError, ValueError) as err:
            # If the user tries to use a name that isn't allowed
            # or an invalid value for a given math function
            print(err)
            continue

        # Print the result if no error occurs
        print(f"{result}")


global_symbols = globals()


def calculation(data):
    codeblocks = [CodeBlock(**codeblock)
                  for codeblock in data['OperationCodeBlocks']]
    for codeblock in codeblocks:
        exec(codeblock.code, global_symbols)
        print(f'{codeblock.description}:{globals()[codeblock.name]}')


if __name__ == '__main__':
    # sampleData = '''
    # 01	09	05	02	27	14			11	12	26	13	19	30
    # 05	10	01	09	15	29			26	11	12	30	17	08
    # 04	29	15	10	28	05			11	12	21	17	30	08

    # 27	07	03	20	01	09			21	04	08	11	12	26
    # 27	03	20	13	19	01			28	10	05	11	12	08
    # 03	13	16	19	20	22			15	10	08	28	05	23
    # '''

    # Open the yaml file and load the data
    with open('configuration.yaml', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    # execute the setup code, provide some utilities like parseData
    exec(data['setupCode'])
    # get the sample data
    sampleData = data['sampleData']
    # parse the sample data
    ALL, A, B, C, D = parseData(sampleData)
    calculation(data)
    # execute the repl
    repl()
