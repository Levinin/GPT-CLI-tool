# Author:   Andy Edmondson
# Date:     20-04-23
#
# Purpose:  Prompt texts for background tasks.
# Content:  get_importance_prompt
#           get_summary_prompt
#           get_conv_plan_prompt    
#           get_background_prompt_section
#           get_question_or_answer_prompt


def get_importance_prompt() -> str:
    """Return a prompt asking GPT to give an importance score to the prompt."""
    return """
    I need you to rate a question on an integer scale of 1 to 10 where 1 is least important and 10 is most important.
    By important I mean that the question is asking something specific about a topic that requires expert specialist knowledge to answer accurately.
    In the future, this will be used to rank the questions. Here are some examples:
    - Example Question 1: What colour is grass? Example Importance 1: 1
    - Example Question 2: How could I modify a model-free algorithm such as A2C so that it incorporates imagination rollout planning in the manner of I2A? Example Importance: 9 
    Given the above, how important is the following?
     
    """


def get_summary_prompt() -> str:
    """Return a prompt asking GPT to summarise the previous conversation"""
    return "Please summarise the following text into a short passage suitable for prompting a large language model: "


def get_conv_plan_prompt() -> str:
    """A prompt to help with conversation planning. The second 1/2 of the final line is necessary to get past eternal clarification questions."""
    return """
    Please ask clarifying questions if you need to. For instance, if I asked what to pack for holiday, you might ask questions such as:
    1. Where are you going on holiday?
    2. How long are you going on holiday for?
    3. What activities do you expect to do on holiday?

    If I reply:
    1. Spain
    2. 3 weeks
    3. Swimming in the sea

    You may then advise me to take clothes for warm weather and swimming, sun-tan lotion and so on.

    Apply this idea to my question, giving a full answer once you have enough information.

    """


def get_background_prompt_section() -> str:
    """A prompt section to go at the start of a prompt providing background for the model."""
    return "The following information is background from previous conversations. " \
           "It is not part of the prompt itself, but take it into account when providing your answer."


def get_question_or_answer_prompt() -> str:
    """A prompt tasking GPT to classify whether it's previous reply was a question or an answer.
    It is hard to do this as part of the conv_plan prompt because it then tries to answer it's own question."""
    return """
    Classification Task:
    Is the following [1] a clarification question or [2] a full answer? Reply with the number [1] if a clarification question or [2] if an answer.

    Text to classify:
    """
