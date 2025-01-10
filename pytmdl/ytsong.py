import requests
import os.path
import logging
import itunespy
import pytmdl.utils as utils

from datetime import datetime
from bs4 import BeautifulSoup
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import RegexMatchError
from pytubefix.exceptions import VideoUnavailable
from mutagen.mp4 import MP4, MP4Cover
from rich.console import Console
from rich.table import Table

class YTSong:
    def __init__(
            self,
            url,
            output_dir,
            skip_metadata=False,
            search_max_display=15,
            language="EN",
            country="US",
            lang_dict=None,
            on_progress=on_progress
            ):
        """
        Constructs a `YTSong` object.

        Args:
            url (str): The URL of the song or video.
            output_dir (str, optional): The directory where the downloaded file should be saved. 
                This does not apply to covers and other generated data. 
                Defaults to the current user's home directory if not specified.
            skip_metadata (bool, optional): Specifies whether searching for metadata is enabled. 
                Defaults to `False`.
            search_max_display (int, optional): Maximum number of search results that are displayed when searching for metadata. 
                Defaults to 15.
            language (str, optional): The preferred language for the metadata search. 
                Defaults to "EN" (English).
            country (str, optional): The preferred country for the metadata search. 
                Defaults to "US" (United States).
            lang_dict (dict, optional): A dictionary mapping languages to their codes. 
                If not provided, the dictionary matching the default language will be used.
            on_progress (func): The progress callback function.

        Raises:
            SongUnavailable: If the song/video cannot be found at the given URL
        """
        # Arguments
        self.url = url
        self.output_dir = os.path.expanduser(output_dir) # Needs $HOME to be set
        self.skip_metadata = skip_metadata
        self.search_max_display = search_max_display

        # Initialize core features
        self.__init_logger(utils.log_dir)
        if lang_dict == None:
            self.lang_dict = utils.load_language(language)
        else:
            self.lang_dict = lang_dict

        # Initialize YouTube and check if the provided URL is a video or song
        try:
            self.yt = YouTube(url, on_progress_callback=on_progress)
            self.full_track_name = utils.remove_artifacts(f"{self.yt.author} - {self.yt.title}")
            self.filename = self.full_track_name + ".m4a" # TODO: Don't hardcode the extension
            self.full_path = self.output_dir + "/" + self.filename
        except (RegexMatchError, VideoUnavailable) as e:
            raise SongUnavailable(e)

        if not skip_metadata:
            try:
                # Search without non-alphanumeric characters
                # Sometimes they can break the search and return nothing
                self.track_metadata = itunespy.search(utils.rna(self.full_track_name), country)
            except LookupError:
                self.skip_metadata = True

    def __init_logger(self, log_path):
        """
        Initializes a logger with a specified log path.

        Args:
            log_path (str): The directory where the log file should be stored. 
                If the directory does not exist, it will be created.

        This method performs the following steps:
        1. Creates a directory for logs if it doesn't already exist.
        2. Configures the logging system to write logs to a specified file.
        3. Sets up a logger that uses this configuration.

        The log file name is determined by the `utils.log_filename` constant, and its format includes:
        - Timestamp
        - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - Message

        The logging level is set to `NOTSET`, which means all levels of messages will be captured.
        """
        utils.create_dir(log_path)

        logging.basicConfig(
            filename=log_path / utils.log_filename,
            level=logging.NOTSET,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        self.logger = logging.getLogger(__name__)
    
    def __select_metadata(self):
        """
        Allows the user to select the metadata that is written to the song.
        
        Returns:
            int: user-selected ID.
        """
        table = Table(title=self.lang_dict["metadata_table_name"])
        columns = [
            self.lang_dict["table_id"],
            self.lang_dict["table_artist_name"],
            self.lang_dict["table_track_name"],
            self.lang_dict["table_release_year"],
            self.lang_dict["table_album"],
            self.lang_dict["table_genre"]
            ]
        rows = []

        for i in range(0, self.search_max_display):
            l = []
            try:
                l.append(f"{i}")
                try:
                    l.append(self.track_metadata[i].artist_name) 
                except AttributeError:
                    l.append(self.lang_dict["unknown_artist"]) 

                try:
                    l.append(self.track_metadata[i].track_name)
                except AttributeError:
                    l.append(self.lang_dict["unknown_track"])

                try:
                    l.append(str(datetime.fromisoformat(self.track_metadata[i].release_date).year))
                except AttributeError:
                    l.append(self.lang_dict["unknown_year"])

                try:
                    l.append(self.track_metadata[i].collection_name)
                except AttributeError:
                    l.append(self.lang_dict["unknown_album"])

                try:
                    l.append(self.track_metadata[i].primary_genre_name)
                except AttributeError:
                    l.append(self.lang_dict["unknown_genre"])

            # If search results are under the `self.search_max_display` value
            # delete the last item created by appending the ID and break the loop
            except IndexError:
                l.pop()
                break
            rows.append(l)
        
        for column in columns:
            table.add_column(column)
        
        for row in rows:
            table.add_row(*row, style="bright_green")

        console = Console()
        console.print(table)

        user_input = input(self.lang_dict["select_metadata_prompt"])
        return user_input

    def embed_metadata(self, auto_select_mode):
        """
        Embeds metadata into the audio file based on user selection or automatic selection mode.

        Args:
            auto_select_mode (bool): Specifies if automatic selection should be enabled.
                If set to `True` and search returns any results, it will always select the first
                metadata element (id 0).

        Raises:
            ValueError: If there is an error saving the metadata to the audio file.
        """
        # Disable functionality in case searching returns no results
        # or metadata searching is disabled and the method is called
        if self.skip_metadata == True:
            self.logger.warning("Method embed_metadata was called but metadata searching is disabled.")
            print(self.lang_dict["cannot_embed_metadata"])
            return
        
        # Ask user to select the metadata to be used
        if not auto_select_mode:
            sel = self.__select_metadata()
        else:
            sel = "0"

        # Return if user skipped
        if sel.lower() == "skip":
            print(self.lang_dict["metadata_embedding_skipped"])
            return
        
        # Set metadata selection first item if
        # none is specified or if the input is incorrect. 
        try:
            sel = int(sel)
        except ValueError:
            sel = 0

        # Open the audio file, write metadata to it and save it 
        audio = MP4(self.full_path)
        try:
            audio["\xa9ART"] = self.track_metadata[sel].artist_name
        except AttributeError:
            audio["\xa9ART"] = self.lang_dict["unknown_artist"]
        
        try:
            audio["\xa9nam"] = self.track_metadata[sel].track_name
        except AttributeError:
            audio["\xa9nam"] = self.lang_dict["unknown_track"]
        
        try:
            audio["\xa9day"] = str(datetime.fromisoformat(self.track_metadata[sel].release_date).year)
        except AttributeError:
            audio["\xa9day"] = self.lang_dict["unknown_year"]

        try:
            audio["\xa9alb"] = self.track_metadata[sel].collection_name
        except AttributeError:
            audio["\xa9alb"] = self.lang_dict["unknown_album"]
        
        try:
            audio["\xa9gen"] = self.track_metadata[sel].primary_genre_name
        except AttributeError:
            audio["\xa9gen"] = self.lang_dict["unknown_genre"]

        try:
            audio.save()
            print(self.lang_dict["metadata_embedded"] % self.full_path)
        except Exception as e:
            raise ValueError(f"Error saving metadata: {e}")

    def __get_cover_url(self, youtube_url):
        """
        Scrapes and returns the music cover URL as a string from the given YouTube video/song URL.

        Args:
            youtube_url (str): The YouTube video/song URL.

        Returns:
            str: The cover URL if found; otherwise, an error message indicating that the URL was not found or retrieval failed.

        Raises:
            requests.exceptions.RequestException: If there is a network-related error when making the request.
        """
        response = requests.get(youtube_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_tag = soup.find('meta', attrs={'property': 'og:image'})
            
            if meta_tag:
                return meta_tag['content']
            else:
                return "Cover URL not found."
        else:
            return "Failed to retrieve page."
    
    def embed_cover(self, audio_path, image_path, delete_image):
        """
        Downloads and embeds a cover image into the audio file.

        Args:
            audio_path (str): The path to the audio file where the cover will be embedded.
            image_path (str): The path where the downloaded cover image will be saved temporarily.
            delete_image (bool): Indicates whether the temporary image file should be deleted after embedding.

        Raises:
            requests.exceptions.RequestException: If there is a network-related error when making the request.
        """

        # Download the cover
        response = requests.get(self.__get_cover_url(self.url))
        with open(image_path, "wb") as image:
            image.write(response.content)

        # Embed the cover
        with open(image_path, "rb") as f:
            cover_data = f.read()
        audio = MP4(audio_path)
        audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
        audio.save()

        print(self.lang_dict["cover_embedded"] % self.full_path)
        
        if delete_image:
            os.remove(image_path)

    def download_only(self):
        """
        Downloads only the audio file if it does not already exist.

        Raises:
            pytubefix.exceptions.PytubeFixError: If there is an error with the YouTube stream extraction process.

        Returns:
            None
        """
        if not os.path.isfile(self.full_path):
            print(self.lang_dict["downloading"] % self.full_path)

            ys = self.yt.streams.get_audio_only()
            ys.download(output_path=self.output_dir, filename=self.filename)
        else:
            self.logger.info(f"The download was skipped because a file with the same name already exists: {self.full_path}")

    def download(
            self,
            image_path=".cover.jpg",
            delete_image=True,
            auto_select_mode=False
            ):
        """
        Downloads a song and its cover, embeds the image into the audio file,
        and deletes the downloaded image by default.

        Allows the user to select metadata sources to download and embeds the
        selected metadata into the audio file.

        Args:
            image_path (str, optional): Determines the path where the cover
            image is to be saved. Defaults to `.cover.jpg`.
            delete_image (bool, optional): When set to `True`, it will keep the image file.
            Defaults to `True`.
            auto_select_mode (bool, optional): When set to `True`, it allows the metadata source
            to be automatically selected, therefore bypassing the user selection screen.
            Defaults to `False`.

        Raises:
            requests.exceptions.RequestException: If there is a network-related error when making the request.
            pytubefix.exceptions.PytubeFixError: If there is an error with the YouTube stream extraction process.
        """
        self.download_only()
        self.embed_cover(self.full_path, image_path, delete_image)
        if self.skip_metadata == False:
            self.embed_metadata(auto_select_mode)

class SongUnavailable(Exception):
    def __init__(self, message):
        super().__init__(message)