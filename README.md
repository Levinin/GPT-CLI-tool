# GPT Command Line App

This application is intended as a fairly simple CLI tool that will grow over time. Feel free to use it as you wish.


## Setup

This app uses a few key packages as shown here:
> transformers<br>
> pytorch<br>
> openai<br>

These can all be installed using mamba to keep everything together, but just use your favourite environment manager.<br>

Additionally, it uses sqlite3 to keep a history of past prompts. The name of the database can be anything but should be 
pointed to by an environment variable called `PROMPT_HISTORY_DB`. This should be set up with the following schema:<br>
```
sqlite> PRAGMA table_info(history);
0|id|TEXT|0||1
1|prompt|TEXT|1||0
2|tokens|INT|1||0
3|model|TEXT|1||0
4|finish|TEXT|1||0
5|response|TEXT|1||0
6|importance|INT|1||0
7|timestamp|DATETIME|0|CURRENT_TIMESTAMP|0
```

For API access you will need to do the following once you have a key:<br>

Set OPENAI_API_KEY environment variable to your own API key.<br>
Set OPENAI_ORG environment variable to your own org ID.

This is best done in your ~/.bashrc file with something like:
> export OPENAI_API_KEY='....'<br>
> export OPENAI_ORG='....'

I also recommend creating an alias such as:
> alias gpt='python path/to/python file'

so you can run it from anywhere very easily. 

## Options
To view the help options simply:
> gpt --help
```
usage: main.py [-h] [-p PROMPT] [-m {text-ada-001,text-davinci-003,text-curie-001}] [-t TEMPERATURE] [-o TOKENS] [-f FILE] [-b]

Prompt GPT using the API.

options:
  -h, --help            show this help message and exit
  -p PROMPT, --prompt PROMPT
                        The full prompt on the command line.
  -m {text-ada-001,text-davinci-003,text-curie-001}, --model {text-ada-001,text-davinci-003,text-curie-001}
                        The model to use.
  -t TEMPERATURE, --temperature TEMPERATURE
                        The model temperature.
  -o TOKENS, --tokens TOKENS
                        Max tokens for the generated reply.
  -f FILE, --file FILE  A file containing a prompt.
  -b, --background      Use prompt history to supplement the interaction.
```

All options except --file and --prompt have defaults, so it is possible to run as follows:
> gpt -f prompt.txt<br>
> gpt -p "Give me 3 activities that are fun for kids birthday parties."

Output is to the terminal, to redirect to file use normal cli tools.

## Defaults

| option      | default          |
|-------------|------------------|
| model       | text-davinci-003 |
| temperature | 0.9              |
| tokens      | 1000             |


## Using
There are two basic modes; immediate prompt and file-based prompt.<br>
For immediate prompts, it takes the cli argument and pass it to the API.<br>
For file prompts, it reads the file and passes it to the API.

If the `--background` option is selected, it will scan through the history and select up to 3 items it thinks are 
related to the question being asked. This is still a bit rough, and it isn't always correct. This is not intended to 
compete with the way ChatGPT works, this is intended to allow a longer-term memory over a longer period and will be 
more helpful over time as the number of prompts on a particular topic increases. However, it is quite a lot slower than 
the default behaviour.

#### Note, in this mode it does submit more than 1 prompt, so it will use more tokens than you expect from the raw prompt text you have entered.


## Future
Plan is to add some dialog management by which the language model will ask some basic clarifying questions when it's not sure 
how to answer. 

