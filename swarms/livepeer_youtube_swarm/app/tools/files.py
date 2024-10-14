import os
import requests

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


def read_from_file(file_path: str) -> str:
    """
    Reads the content from a file at the specified path.

    :param file_path: The path of the file to read.
    :return: The content of the file.
    """
    with open(file_path, "r") as file:
        return file.read()
    
def list_files(file_path: str) -> list[str]:
    """
    Lists the files in the specified directory.

    :param file_path: The path of the directory to list.
    :return: A list of files in the directory.
    """
    return os.listdir(file_path)



def download_from_url(url: str, file_name: str,file_path: str) -> str:

    """
    Saves the given content to a file at the specified path with the specified file name.

    :param url: Url to download the image from.
    :param file_name: Name of the file to save the image to.
    :param file_path: Path to save the image to.
    :return: Path to the saved image.
    """
    response = requests.get(url)
    if response.status_code == 200:
        # Create the full directory path
        os.makedirs(file_path, exist_ok=True)
        
        full_path = os.path.join(file_path, file_name)
        
        # Write the image content to the file
        with open(full_path, "wb") as f:
            f.write(response.content)
        
        return full_path
    else:
        raise Exception(f"Failed to download image: HTTP {response.status_code}")