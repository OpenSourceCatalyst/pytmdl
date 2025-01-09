from pytmdl.ytsong import YTSong
from pytubefix import Playlist

class YTAlbum:
    def __init__(
            self,
            url,
            output_dir,
            skip_metadata=False,
            search_max_display=15,
            language="EN",
            country="US",
            lang_dict=None
            ):
        """
        Constructs a `YTAlbum` object.

        Args:
            url (str): The URL of the album or playlist.
            output_dir (str): The directory where the downloaded files should be saved (does not include album covers/thumbnails).
            skip_metadata (bool, optional): Specifies whether searching for metadata is enabled. Defaults to `False`.
            search_max_display (int, optional): Maximum number of search results that are displayed when searching for metadata. Defaults to `15`.
            language (str, optional): The language preference for the metadata search. Defaults to "EN".
            country (str, optional): The country preference for the metadata search. Defaults to "US".
            lang_dict (dict, optional): A dictionary containing custom language translations. Defaults to `None`.

        Raises:
            NotAnAlbum: If no album/playlist is detected at the given URL
        """
        self.pl = Playlist(url)
        self.language = language
        self.output_dir = output_dir
        self.skip_metadata = skip_metadata
        self.search_max_display = search_max_display
        self.country = country
        self.lang_dict = lang_dict

        try:
            print(f"Items in album: {self.pl.length}")
        except KeyError as e:
            raise NotAnAlbum(e)
    
    def download_only(self):
        """
        Downloads audio files only if they do not already exist.

        This method iterates through each video URL in the playlist and checks if the corresponding audio file already exists.
        If it does not exist, the method downloads the audio file using the `YTSong` class.

        Raises:
            pytubefix.exceptions.PytubeFixError: If there is an error with the YouTube stream extraction process.
        """
        for url in self.pl.video_urls:
            # Replace URL to the music version to get the square cover
            music_url = url.replace("www", "music")

            ytsong = YTSong(
                music_url,
                self.output_dir + "/" + self.pl.title,
                self.skip_metadata,
                self.search_max_display
                )
            ytsong.download_only()

    def download(
            self,
            delete_image=True,
            auto_select_mode=False
            ):
        """
        Loops through the songs/videos in the playlist and calls `YTSong.download()`
        on each one.

        `YTSong.download()` downloads a song and its cover, embeds the image into the audio file, 
        and deletes the downloaded image by default.
        Then, it allows the user to select metadata sources to download and embeds the selected metadata 
        into the audio file.

        Args:
            delete_image (bool, optional): When set to `False`, it will keep the image file.
            Defaults to `True`.
            auto_select_mode (bool, optional): When set to `True`, it allows the metadata source
            to be automatically selected therefore bypassing the user selection screen.
            Defaults to `False`.
        """
        for url in self.pl.video_urls:
            # Replace URL to the music version to get the square cover image
            music_url = url.replace("www", "music")

            ytsong = YTSong(
                music_url,
                self.language,
                self.output_dir + "/" + self.pl.title,
                self.skip_metadata,
                self.search_max_display,
                self.country,
                self.lang_dict
                )
            
            ytsong.download(
                image_path=ytsong.full_track_name + ".jpg",
                delete_image=delete_image,
                auto_select_mode=auto_select_mode
                )

class NotAnAlbum(Exception):
    def __init__(self, message):
        super().__init__(message)