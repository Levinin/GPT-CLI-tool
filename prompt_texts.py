# Author:   Andy Edmondson
# Date:     20-04-23
#
# Purpose:  Prompt texts for background tasks.
# Content:  get_importance_prompt
#           get_summary_prompt

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
    """A prompt to help with conversation planning."""
    return """
    Please help me with this, if clarifications would help your reply, give me questions in the form 
    {'q1': 'the question', 'q2':'the question'} 
    and I will help you with that.
    """


def get_background_prompt_section() -> str:
    """A prompt section to go at the start of a prompt providing background for the model."""
    return "The following information is background from previous conversations. " \
           "It is not part of the prompt itself, but take it into account when providing your answer."


