# GPT Command Line App

This application is intended as a very basic tool, really for my own use, that is run from the linux command line. Feel free to use it as you wish.


## Setup

Install the openai package to a python environment with: 
> mamba install openai

Set OPENAI_API_KEY environment variable to your own API key.
Set OPENAI_ORG environment variable to your own org ID.

This is best done in your ~/.bashrc file with something like:
export OPENAI_API_KEY='....'
export OPENAI_ORG='....'

I also recommend creating an alias such as:
> alias gpt='python path/to/python file'

so you can run it from anywhere very easily. 

## Options
To view the help options simply:
> gpt --help

>usage: main.py [-h] [-p PROMPT] [-m {text-ada-001,text-davinci-003,text-curie-001}] [-t TEMPERATURE] [-o TOKENS] [-f FILE]
>
>Prompt GPT using the API.
>
>options:
>  -h, --help            show this help message and exit
>  -p PROMPT, --prompt PROMPT
>                        The full prompt on the command line.
>  -m {text-ada-001,text-davinci-003,text-curie-001}, --model {text-ada-001,text-davinci-003,text-curie-001}
>                        The model to use.
>  -t TEMPERATURE, --temperature TEMPERATURE
>                        The model temperature.
>  -o TOKENS, --tokens TOKENS
>                        Max tokens for the generated reply.
>  -f FILE, --file FILE  A file containing a prompt.

All options except --file and --prompt have defaults, so it is possible to run as follows:
> gpt -f prompt.txt
> gpt -p "Give me 3 activities that are fun for kids birthday parties."

Output is to the terminal, to redirect to file use normal cli tools.

## Defaults

| option | default |
| ### | ### |
| model | text-davinci-003 |
| temperature | 0.9 |
| tokens | 1000 |


## Using
There are two basic modes; immediate prompt and file-based prompt.
For immediate prompts, it will simply take the cli argument and pass it to the API.
For file prompts, it will simple read the file and pass it to the API.

## Future
The plan is to allow the use of background information whereby the user can specify documents which will then 
be read in, automatically summarised by GPT and used as part of the prompt. Currently, this type of thing must
be done by hand using a series of file prompts.

