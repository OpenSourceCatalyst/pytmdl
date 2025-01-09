import argparse

import pytmdl.utils as utils
from pytmdl.ytsong import YTSong, SongUnavailable
from pytmdl.ytalbum import YTAlbum, NotAnAlbum

class PYTMDL:
    """
    Main class for the CLI program.
    
    This class handles argument parsing, validation, and execution of the program.
    """
    def __init__(self):
        """
        Initialize the PYTMDL object with default values.
        
        Sets up the version, language, output directory, and skip metadata flag.
        Loads the language dictionary based on the system's locale or a default language
        if the system's locale is not supported. Default "EN" (English).

        Initializes the argument parser with the application description.
        """
        self.version = 0.1
        self.default_language = "EN"
        self.output_dir = "~"
        self.skip_metadata = False

        try:
            self.lang_dict = utils.load_language(utils.get_language_from_locale())
        except utils.LanguageNotFound:
            self.lang_dict = utils.load_language(self.default_language)
        
        self.parser = argparse.ArgumentParser(
            add_help=False,
            description=self.lang_dict["app_description"]
        )
    
    def parse_arguments(self):
        """
        Parse the command-line arguments.

        Adds several argument options to the parser:
        - url: positional argument for one or more URLs
        - help: flag to display help message
        - version: flag to display version information
        - skip-metadata: flag to skip downloading metadata
        - output: optional argument for specifying the output directory
        - language: optional argument for specifying the language

        Returns:
            parsed arguments object
        """
        self.parser.add_argument("url", nargs="*")
        self.parser.add_argument("-h", "--help", action="store_true")
        self.parser.add_argument("-v", "--version", action="store_true")
        self.parser.add_argument("-s", "--skip-metadata", action="store_true")
        self.parser.add_argument("-o", "--output", nargs=1)
        self.parser.add_argument("-l", "--language")

        return self.parser.parse_args()

    def validate_arguments(self, arguments):
        """
        Validate and process the parsed arguments.

        - If a language is provided, it loads the corresponding language dictionary.
        - If an output directory is provided, it updates the output directory for the program.
        - Sets the skip metadata flag based on user input.
        - Handles help and version flags by printing respective messages and exiting.
        - Iterates through each URL and attempts to download a song or album using YTSong or YTAlbum.

        Args:
            arguments: parsed arguments object
        """
        if arguments.language:
            try:
                # This will load the chosen language. If the language argument is provided,
                # the language will be loaded twice: once when the program begins execution
                # and the second time if the user is choosing a language
                self.lang_dict = utils.load_language(arguments.language)

            # If the provided language does not have a translation, do nothing
            except FileNotFoundError:
                pass
        
        if arguments.output:
            self.output_dir = arguments.output[0]
        
        if arguments.skip_metadata:
            self.skip_metadata = True

        
        if arguments.help:
            print(self.lang_dict["help_message"] % self.lang_dict["app_description"])
        elif arguments.version:
            print(self.lang_dict["version_text"] % str(self.version))

        for url in arguments.url:
            try:
                YTSong(url,
                       output_dir=self.output_dir,
                       skip_metadata=self.skip_metadata,
                       lang_dict=self.lang_dict
                       ).download()
            except SongUnavailable:
                try:
                    YTAlbum(url,
                            output_dir=self.output_dir,
                            skip_metadata=self.skip_metadata,
                            lang_dict=self.lang_dict
                            ).download()
                except NotAnAlbum:
                    print(self.lang_dict["wrong_url"])

if __name__ == "__main__":
    pytmdl = PYTMDL()
    arguments = pytmdl.parse_arguments()
    pytmdl.validate_arguments(arguments)