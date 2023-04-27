# GPT Command Line App

This application will allow you to interact with the OpenAI GPT 3 API from the command line. It is intended to be a simple helper 
for my everyday queries. <br>

The program does a few things:
- It accepts a prompt from the command line or from a specified file.
- It records all prompts and responses to a sqlite3 database.
- It allows you to use this history to supplement the prompt. This feature is inspired by this paper: https://arxiv.org/abs/2304.03442
- It asks GPT for any clarifying questions that will help it give a better answer.


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
8|embedding|BLOB|0||0
```

For API access you will need to do the following once you have a key:<br>

Set `OPENAI_API_KEY` environment variable to your own API key.<br>
Set `OPENAI_ORG` environment variable to your own org ID.

This is best done in your ~/.bashrc file with something like:
> export OPENAI_API_KEY='....'<br>
> export OPENAI_ORG='....'

I also recommend creating an alias such as:
> alias gpt='python path/to/python file'

so you can run it from anywhere very easily. I use it from guake, so it is always available with F12.

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

Output is to the terminal, to redirect to file use normal cli tools, of course the output is always saved to sqlite3 anyway.

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
more helpful over time as the number of prompts on a particular topic increases. Personal usage so far indicates this 
additional context helps since it grounds the responses in my previous questions making them easier to understand.

#### __General Note, this application does submit more than 1 prompt, so it will use more tokens than you expect from the raw prompt text you have entered.__
<br>

## Future
Refine the prompt and the way it tokenizes history, sometimes the similarity scores in particular are not very accurate. It might be better to use topic-based clustering.<br>

