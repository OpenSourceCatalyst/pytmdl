import os
import json
import locale
import pycountry


from pathlib import Path

# Paths
working_dir = Path(__file__).parent.parent
language_dir = working_dir / "translations"
log_dir = working_dir / "logs"
log_filename = "main.log"

# Utility functions
def create_dir(dir_path):
    """
    Creates a directory if it does not already exist.

    Args:
        dir_path (str): The path to the directory that needs to be created.
    """
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass
    except OSError as error:
        print("Error creating directory: %s" % error)
        exit(1)

def rna(text):
    """
    Removes all non-alphanumeric characters from a given string, except spaces.

    Args:
        text (str): The input string.

    Returns:
        str: A string containing only alphanumeric characters and spaces.
    """
    return "".join(c for c in text if c.isalnum() or c.isspace())

def remove_artifacts(filename):
    """
    Removes unwanted artifacts or words from a string.

    Args:
        filename (str): The input string containing potential unwanted artifacts.

    Returns:
        str: The cleaned string with unwanted artifacts removed.
    """
    clean_name = filename
    artifacts = [" - Topic"]
    for artifact in artifacts:
        if artifact in filename:
            clean_name = filename.replace(artifact, "")
    return clean_name

def load_language(language):
    """
    Loads the specified language from the translations folder.

    Args:
        language (str): ISO 3166-1 alpha-2 standard language code.
            This will be used in the interface or song metadata.

    Returns:
        dict: A dictionary containing the language data.
    """
    lang = language.upper()

    with open(f"{language_dir / lang}.json", "r") as f:
        data = json.load(f)

    return data

def get_language_from_locale():
    """
    Returns the language corresponding to the current locale.

    This function retrieves the region from the current locale, determines the appropriate ISO 639-1 alpha-2 
    language code based on the operating system, and then checks a JSON file located at `translations/available.json`
    to find the language associated with that country code. If no match is found, it raises a custom exception.

    Returns:
        str: The language corresponding to the current locale.

    Raises:
        LanguageNotFound: If the current locale does not have a translation.
    """
    region = locale.getlocale()[0].split("_")[1]

    if os.name == "nt":
        alpha_2 = pycountry.countries.get(name=region).alpha_2
    elif os.name == "posix":
        alpha_2 = region.upper()

    with open(language_dir / "available.json", "r") as f:
        language_list = json.load(f)
    
    # Loop through all countries to try to find a match
    for l in language_list:
        for c in l["countries"]:
            if c == alpha_2:
                return l["language"]
    
    raise LanguageNotFound("The current locale does not have a translation. Locale: " + alpha_2)

class LanguageNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)