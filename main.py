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


def get_prompt_from_file(file_path: str) -> [str, None]:
    if os.path.isfile(file_path):
        text_file = open(file_path, "r")
        data = text_file.read()
        text_file.close()
        return data
    return None


def get_database_connection() -> sqlite3.Connection:
    conn = None
    try:
        conn = sqlite3.connect(os.getenv("PROMPT_HISTORY_DB"))
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def add_to_database(memory):
    conn = get_database_connection()
    if conn:
        sql = ''' INSERT INTO history(id, prompt, tokens, model, finish, response, importance)
                      VALUES(?,?,?,?,?,?,?) '''
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
                    SELECT id, prompt, response, importance, timestamp FROM history                    
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


def get_most_relevant_history(read_cur, write_cur, new_prompt):
    """Get min's and max's and then loop over the new table and do the calculations to find the
    most relevant items from the history."""

    read_cur.execute("SELECT MIN(timestamp) from calc_scores;")
    oldest = datetime.fromisoformat(read_cur.fetchone()[0])

    read_cur.execute("SELECT MAX(timestamp) from calc_scores;")
    newest = datetime.fromisoformat(read_cur.fetchone()[0])

    read_cur.execute("SELECT * FROM calc_scores;")

    # Get prompt tokens for comparison.
    prompt_enc = tokenizer.encode(new_prompt, add_special_tokens=True, truncation=True, return_tensors="pt",
                                  padding='max_length', max_length=512).float()

    # Each row will be a tuple in the form (id, 'What colour is the sky?', 10, '2023-04-20 16:35:10', None, None, None)
    for row in read_cur:
        row_enc = tokenizer.encode((row[1] + row[2]), add_special_tokens=True, truncation=True, return_tensors="pt",
                                   padding='max_length', max_length=512).float()
        similarity_score = torch.nn.functional.cosine_similarity(prompt_enc, row_enc, dim=-1).item()

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
    read_cur.execute("""
                        SELECT prompt, response
                        FROM calc_scores
                        WHERE similarity > 0.3
                        ORDER BY total DESC
                        LIMIT 3;
                        """)
    return read_cur.fetchall()


def get_background_from_previous(new_prompt) -> str:
    conn = get_database_connection()
    if conn is None:
        print("Database error, using original prompt.")
        return new_prompt

    write_cur = conn.cursor()
    read_cur = conn.cursor()

    create_temp_calc_table(write_cur)
    most_relevant_history = get_most_relevant_history(read_cur, write_cur, new_prompt)

    # print(most_relevant_history)

    updated_prompt = prompt_texts.get_background_prompt_section()

    for item in most_relevant_history:
        summary_prompt = ' '.join((prompt_texts.get_summary_prompt() + item[0] + " " + item[1]).split())
        response = query_gpt(prompt_text=summary_prompt, model="text-curie-001", max_t=300, temp=0.5)
        updated_prompt = updated_prompt + response["choices"][0]["text"]

    read_cur.close()
    write_cur.close()

    return updated_prompt


def send_prompt(new_prompt, args):
    """Send the prompt to GPT.
    Get an importance score for later.
    """
    # Importance requires davinci.
    importance: int
    importance_prompt = prompt_texts.get_importance_prompt() + new_prompt
    importance = get_prompt_importance(query_gpt(importance_prompt, "text-davinci-003", 20, 0.9))

    # Get the background from previous conversations if the user chose that options
    if args.background:
        full_prompt = get_background_from_previous(new_prompt) + "\n\nThe following is the prompt:\n" + new_prompt
    else:
        full_prompt = "The following is the prompt: \n" + new_prompt
    print(" ".join(full_prompt.split()))

    # Now actually send the prompt.
    response = query_gpt(full_prompt, args.model, args.tokens, args.temperature)
    manage_response(response)

    memory = (response["id"], full_prompt, response["usage"]["total_tokens"], args.model,
              response["choices"][0]["finish_reason"], response["choices"][0]["text"], importance)
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
