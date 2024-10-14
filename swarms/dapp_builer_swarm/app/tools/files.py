import os


def save_to_file(content: str, file_name: str, file_path: str) -> None:
    """
    Saves the given content to a file at the specified path with the specified file name.

    :param content: The content to be written to the file.
    :param file_name: The name of the file to save the content in.
    :param file_path: The path where the file should be saved.
    """

    # ensure the directory exists
    os.makedirs(file_path, exist_ok=True)

    # construct the full file path
    full_path = os.path.join(file_path, file_name)

    # write the content to the file
    with open(full_path, "w") as file:
        file.write(content)

    print(f"File saved to {full_path}")
