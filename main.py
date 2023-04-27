import os
import argparse
import re
import json
import sqlite3  # For prompt history
from sqlite3 import Error
from datetime import datetime

import transformers
import torch

import openai

import prompt_texts

# Static variables for the API
openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")

tokenizer = transformers.GPT2Tokenizer.from_pretrained('gpt2')
tokenizer.pad_token = 0

stop_char = "#*#"


def define_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt GPT using the API.")
    parser.add_argument("-p", "--prompt", type=str, help="The full prompt on the command line.", required=False)
    parser.add_argument("-m", "--model", type=str, help="The model to use.",
                        choices=["text-ada-001", "text-davinci-003", "text-curie-001"],
                        required=False, default="text-davinci-003")
    parser.add_argument("-t", "--temperature", type=float, help="The model temperature.", required=False, default=0.9)
    parser.add_argument("-o", "--tokens", type=int, help="Max tokens for the generated reply.",
                        required=False, default=1000)
    parser.add_argument("-f", "--file", type=str, help="A file containing a prompt.", required=False)
    parser.add_argument("-b", "--background", action='store_true', default=False,
                        help="Use prompt history to supplement the interaction.", required=False)
    return parser


def query_gpt(prompt_text: str, model: str, max_t: int = 1000, temp: float = 0.9) -> dict:
    """Return the gpt response."""
    return openai.Completion.create(
        engine=model,
        prompt=prompt_text,
        temperature=temp,
        max_tokens=max_t,
        #top_p=1.0,
        frequency_penalty=1.2,
        presence_penalty=0.0,
        # stop=stop_char
    )


def build_prompt(prompt_text) -> str:
    """Just now it passes through, will do cleverer stuff in the future."""
    print(f"The prompt text is: {prompt_text}")
    return prompt_text


def manage_response(response: json):
    """Manage responses from GPT"""
    print(response["choices"][0]["text"])
    print("-" * 20)
    print(f'The message ended due to {response["choices"][0]["finish_reason"]}.')


def get_prompt_from_file(file_path: str):   # -> [str, None]:
    """Get the prompt from a file when this option is chosen. If the file doesn't exist, return None."""
    if os.path.isfile(file_path):
        text_file = open(file_path, "r")
        data = text_file.read()
        text_file.close()
        return data
    return None


def get_database_connection() -> sqlite3.Connection:
    """Get a connection to the database. If connection is not possible, return None."""
    conn = None
    try:
        conn = sqlite3.connect(os.getenv("PROMPT_HISTORY_DB"))
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def add_to_database(memory) -> None:
    conn = get_database_connection()
    if conn:
        sql = ''' INSERT INTO history(id, prompt, tokens, model, finish, response, importance, embedding)
                      VALUES(?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, memory)
        conn.commit()
        conn.close()


def get_prompt_importance(response: dict) -> int:
    """Ask GPT to rank the importance of this prompt.
    Assumes the first int in the response is the value.
    This could be wrong, but typically it responds with just a value."""

    text = response["choices"][0]["text"]
    return int(re.search(r'\d+', text).group())


def create_temp_calc_table(write_cur):
    write_cur.execute('''
                    CREATE TEMPORARY TABLE calc_scores AS
                    SELECT id, prompt, response, importance, timestamp, embedding FROM history;                    
                    ''')
                    # WHERE importance > 5;

    write_cur.execute('''
                        ALTER TABLE calc_scores 
                        ADD COLUMN similarity REAL;
                        ''')

    write_cur.execute('''
                    ALTER TABLE calc_scores 
                    ADD COLUMN total REAL;
                    ''')


def get_most_relevant_history(read_cur, write_cur, prompt_enc):
    """Get min's and max's and then loop over the new table and do the calculations to find the
    most relevant items from the history."""

    read_cur.execute("SELECT MIN(timestamp) from calc_scores;")
    oldest = datetime.fromisoformat(read_cur.fetchone()[0])

    read_cur.execute("SELECT MAX(timestamp) from calc_scores;")
    newest = datetime.fromisoformat(read_cur.fetchone()[0])

    read_cur.execute("SELECT * FROM calc_scores;")

    # Each row will be a tuple in the form (id, 'What colour is the sky?', 'blue', 10, '2023-04-20 16:35:10', <embedding>, None, None, None)
    for row in read_cur:
        # Compare the prompt embedding to the history embedding.
        similarity_score = torch.nn.functional.cosine_similarity(prompt_enc, torch.tensor(eval(row[5])), dim=-1).item()
        # print(f"Got a similarity score of {similarity_score}")
        importance_score = (row[3] - 6) / 4
        recency_score = (datetime.fromisoformat(row[4]) - oldest) / (newest - oldest)
        total_score = similarity_score + importance_score + recency_score

        write_cur.execute("""
                                UPDATE calc_scores
                                SET similarity = ?, total = ?                                 
                                WHERE id = ?;
                                """, (total_score, similarity_score, row[0]))

        # print(f"Similarity: {similarity_score}, Importance: {importance_score}, "
        #       f"Recency: {recency_score}, Total: {total_score}.")

    # Now query to get the top past prompts where similarity is also above a threshold.
    # Was using the prompt and return, but this doesn't work so well as just the prompt.
    read_cur.execute("""
                        SELECT prompt
                        FROM calc_scores
                        WHERE similarity > 0.4
                        ORDER BY total DESC
                        LIMIT 3;
                        """)
    return read_cur.fetchall()


def get_background_from_previous(prompt_enc) -> str:
    conn = get_database_connection()
    if conn is None:
        print("Database error, using original prompt.")
        return " "

    write_cur = conn.cursor()
    read_cur = conn.cursor()

    create_temp_calc_table(write_cur)

    most_relevant_history = get_most_relevant_history(read_cur, write_cur, prompt_enc)

    # print(most_relevant_history)

    updated_prompt = "Background: \n"       # prompt_texts.get_background_prompt_section()

    for item in most_relevant_history:
        summary_prompt = ' '.join((prompt_texts.get_summary_prompt() + item[0]).split())
        response = query_gpt(prompt_text=summary_prompt, model="text-curie-001", max_t=300, temp=0.5)
        updated_prompt = updated_prompt + response["choices"][0]["text"]

    read_cur.close()
    write_cur.close()

    return updated_prompt


def ask_gpt_the_question(prompt: str, args) -> str:
    """Clarify the prompt by getting GPT to ask the user for more information.
    The returned full prompt will be the original prompt plus the clarification.
    It will not include the replies from GPT, because this doesn't help with responses from GPT."""

    need_clarification = True
    updated_prompt = prompt
    safety_count = 0
    response_text: str = ""
    response = None

    while need_clarification and safety_count < 4:
        
        safety_count += 1   # Make sure we don't get stuck in a loop of doom.
        
        # Ask GPT if it needs any clarification.
        clarification_prompt = ' '.join((updated_prompt + prompt_texts.get_conv_plan_prompt()).split())
        response = query_gpt(prompt_text=clarification_prompt, 
                             model=args.model, max_t=args.tokens, temp=args.temperature)
        response_text = response["choices"][0]["text"]
        print(f"\n{response_text}\n")
        print("-" * 20)
        print(f'The message ended due to {response["choices"][0]["finish_reason"]}.')
        
        # Check if this is a clarification question.
        class_prompt = ' '.join((prompt_texts.get_question_or_answer_prompt() + "\n" + response_text).split())
        classification_response = query_gpt(class_prompt, model="text-davinci-003", max_t=100, temp=0.9)
        classification_response_text = classification_response["choices"][0]["text"]
        try:
            classification = int(re.search(r'\d+', classification_response_text).group())
        except:
            classification = 2      # If it can't find a number, assume it's not a clarification question.
        
        # print(f"The classification is {classification}.")
        if classification == 1:
            additional_info = input("Please enter any clarifications: ")
            updated_prompt = updated_prompt + "\n" + additional_info
        else:
            need_clarification = False

    return updated_prompt, response

        

def send_prompt(new_prompt, args):
    """Send the prompt to GPT.
    Get an importance score for later.
    """

    # Importance requires davinci.
    importance: int
    importance_prompt = ' '.join((prompt_texts.get_importance_prompt() + new_prompt).split())
    importance = get_prompt_importance(query_gpt(importance_prompt, "text-davinci-003", 20, 0.9))

    # Tokenize the prompt for comparison and storage.
    prompt_enc = tokenizer.encode(new_prompt, add_special_tokens=True, truncation=True, return_tensors="pt",
                                  padding='max_length', max_length=512).float()

    # Get the background from previous conversations if the user chose that option
    background: str = ""
    full_prompt: str = ""
    if args.background:
        background = get_background_from_previous(prompt_enc)
        
    
    full_prompt = "Question: " + new_prompt + "\n\n" + background
    
    # See if GPT wants to clarify the prompt at all, and if so, add the clarification to the prompt background.
    final_prompt, response = ask_gpt_the_question(full_prompt, args)

    # Now actually send the prompt.
    #response = query_gpt(" ".join(full_prompt.split()), args.model, args.tokens, args.temperature)
    # manage_response(response)

    memory = (response["id"], final_prompt, response["usage"]["total_tokens"], args.model,
              response["choices"][0]["finish_reason"], response["choices"][0]["text"], importance, str(prompt_enc.numpy().tolist()))
    add_to_database(memory)


def main():
    parser = define_parser()
    args = parser.parse_args()
    new_prompt = None

    if args.prompt:
        new_prompt = args.prompt

    if args.file:
        new_prompt = get_prompt_from_file(args.file)
        if new_prompt:
            print(f'Contents of "{args.file}" loaded as prompt.')
        else:
            print(f'The file "{args.file}" does not exist, doing nothing.')

    if new_prompt:
        send_prompt(new_prompt, args)


if __name__ == "__main__":
    main()
