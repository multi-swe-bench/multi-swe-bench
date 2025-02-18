import argparse
import sys
from pathlib import Path


def parse_tokens(tokens: str | list[str] | Path) -> list[str]:
    """
    Try to parse tokens as a list of strings.
    """

    if isinstance(tokens, list):
        return tokens
    elif isinstance(tokens, str):
        return [tokens]
    elif isinstance(tokens, Path):
        if not tokens.exists() or not tokens.is_file():
            raise ValueError(f"Token file {tokens} does not exist or is not a file.")
        with tokens.open("r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    return []


def find_default_token_file() -> Path:
    """
    Try to find a default token file in the current directory.
    """

    possible_files = ["token", "tokens", "token.txt", "tokens.txt"]
    for file_name in possible_files:
        file_path = Path(file_name)
        file_path = Path.cwd() / file_path
        if file_path.exists() and file_path.is_file():
            return file_path
    return None


def get_tokens(tokens) -> list[str]:
    if tokens is None:
        default_token_file = find_default_token_file()
        if default_token_file is None:
            print("Error: No tokens provided and no default token file found.")
            sys.exit(1)
        tokens = default_token_file
    else:
        # If tokens are provided as a list, they might need conversion
        tokens = tokens[0] if len(tokens) == 1 else tokens

    try:
        token_list = parse_tokens(tokens)
        if not token_list:
            raise ValueError("Token list is empty after parsing.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    assert token_list, "No tokens provided."
    return token_list


def optional_int(value):
    if value.lower() == "none" or value.lower() == "null" or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: {value}")
