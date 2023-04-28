# GPT Command-Line App

This application will allow you to interact with the OpenAI GPT 3 API from the command line. It is intended to be a simple helper 
for my everyday queries. <br>

The program does a few things:
- It accepts a prompt from the command line or from a specified file.
- It records all prompts and responses to a sqlite3 database.
- It allows you to use this history to supplement the prompt. This feature is inspired by the paper <a href=https://arxiv.org/abs/2304.03442>Generative Agents: Interactive Simulacra of Human Behavior</a>.
- It asks GPT for any clarifying questions that will help it give a better answer (see examples below). 
This is not perfect because it asks GPT to classify its own responses, but it does work most of the time.


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
| temperature | 0.5              |
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
However, it does sometimes match to previous prompts that have no relation to what 
I'm currently asking which can occasionally lead to confused answers.

#### __General Note, this application does submit more than 1 prompt, so it will use more tokens than you expect from the raw prompt text you have entered.__
<br>

## Example conversations

This first example shows that it can help to disambiguate the topic of the question. 
```terminal

```terminal
$ gpt -p "What is the most important consideration in continual learning?"

The most important consideration in continual learning depends on the context. 
What type of learning are you referring to? Is it academic, professional, or 
personal development? What is the goal of the learning - to acquire knowledge, 
develop skills, or gain experience? Are there any specific topics that need to be 
covered? Do you have a timeline for completing this learning?

--------------------
Please enter any clarifications: I am referring to continual reinforcement learning 
in the contexts of robots which must operate in the real world completing tasks such 
as finding people in distress.

The most important consideration in continual reinforcement learning for robots 
completing tasks such as finding people in distress is the ability to accurately 
perceive and interpret the environment. This includes being able to identify 
potential hazards, navigate around obstacles, and recognize objects of interest. The 
robot must also be able to learn from its experiences, so that it can adapt itself 
to different environments and situations. Additionally, it should be able to make 
decisions based on its understanding of the environment and any external input 
received from sensors or other robots. Finally, the robot must have robust safety 
protocols in place so that it does not cause harm while carrying out its task.
```

I'm not taking decoration advice from a computer (yet), but this example shows 
how it can provide clarification for a vague question and how these shape the final reply.

```terminal
$ gpt -p "How should I redecorate my bedroom?"


To help you answer my question, I need to know more about my bedroom. What is the 
size of the room? Is there any furniture in it already? How much money do I have to 
spend on redecorating? Do I want a particular style or theme for the room, such as 
modern or traditional? 

Based on this information, some suggestions for redecorating your bedroom could 
include: 
- If you have a large budget and want to create an elegant look, consider investing 
in new furniture pieces such as a bed frame with matching side tables and dresser. 
You could also add decorative accents like wall art and area rugs. 
- If your budget is smaller but you still want something special, focus on small 
details that can make a big difference. Paint one wall in an accent color that 
matches your bedding or curtains; replace light fixtures; hang mirrors; add throw 
pillows and blankets for texture; install window treatments; invest in artwork or 
photographs for the walls. 
- If you prefer a traditional style, use classic colors like navy blue and white 
with hints of gold accents throughout. Opt for timeless pieces such as wooden 
dressers with ornate detailing or four poster beds with canopy drapes. Add touches 
of luxury by including velvet cushions and throws along with patterned wallpaper 
borders around windows and doors.

--------------------
Please enter any clarifications: I would like an elegent modern look but I don't 
have a large budget. I have quite a lot of old furniture in the room already.



To help you come up with an elegant modern look for your bedroom, I need to ask a 
few clarifying questions. 
1. What size is the room? 
2. What colors do you prefer? 
3. Do you have any specific ideas in mind regarding the overall look of the room? 
4. Are there any pieces of furniture that are non-negotiable and must stay in the room? 
5. Is there anything else that needs to be taken into consideration such as windows, 
wall space or flooring?

--------------------
Please enter any clarifications: 1. The room is quite large. 2. I like bright colors 
such as yellow and orange. 3. Overall I want a modern style. 4. I have an old arm 
chair that I must keep since it has sentimental value. 5. One end of the room has a 
large window, at the other end is an en-suite.



To answer your question, here are some suggestions for redecorating your bedroom on 
a budget: 
1. Start by painting the walls in a bright, modern color like yellow or orange to 
give the room an updated look. 
2. Look for inexpensive but stylish furniture pieces that will fit with the modern 
style and complement your existing furniture. Consider getting rid of any furniture 
that is too bulky or outdated and replace it with something more modern looking. 
3. Hang some artwork or other wall decorations to add personality and interest to
the room without breaking the bank. You can also try making your own art using 
materials you have around the house such as old frames, magazines, fabric scraps 
etc..  
4. Add accessories such as throw pillows and blankets to bring in some texture and 
color into the room while still keeping it elegant and modern looking at a low cost 
price point. 
5. If possible, rearrange existing furniture so that it looks more organized and 
intentional rather than cluttered; this can help make even older pieces look new 
again!

```

<br>

## Future
Refine the prompts and the way it tokenizes history, sometimes the similarity 
scores in particular are not very accurate. 


