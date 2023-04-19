import os
import argparse
import json

import openai

# Static variables for the API
openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")
# model_list = openai.Model.list()


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
    return parser


def query_gpt(prompt_text: str, model: str, max_t: int = 1000, temp: float = 0.9) -> dict:
    """Return the gpt response."""
    return openai.Completion.create(
        engine=model,
        prompt=prompt_text,
        temperature=temp,
        max_tokens=max_t,
        top_p=1.0,
        frequency_penalty=1.2,
        presence_penalty=0.0,
        # stop="\\n"
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


def main():
    parser = define_parser()
    args = parser.parse_args()
    new_prompt = None

    if args.prompt:
        new_prompt = build_prompt(args.prompt)

    if args.file:
        new_prompt = get_prompt_from_file(args.file)
        if new_prompt:
            print(f'Contents of "{args.file}" loaded as prompt.')
        else:
            print(f'The file "{args.file}" does not exist, doing nothing.')

    if new_prompt:
        response = query_gpt(new_prompt, args.model, args.tokens, args.temperature)
        manage_response(response)


if __name__ == "__main__":
    main()




