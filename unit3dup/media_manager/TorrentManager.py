# -*- coding: utf-8 -*-

import argparse

from unit3dup.media_manager.VideoManager import VideoManager
from unit3dup.media_manager.GameManager import GameManager
from unit3dup.media_manager.DocuManager import DocuManager
from unit3dup import config_settings
from unit3dup.media import Media

from common.bittorrent import BittorrentData
from common.constants import my_language
from common.utility import System

from unit3dup.media_manager.common import UserContent
from view import custom_console


class TorrentManager:
    def __init__(self, cli: argparse.Namespace):

        self.preferred_lang = my_language(config_settings.user_preferences.PREFERRED_LANG)
        self.games: list[Media] = []
        self.videos: list[Media] = []
        self.doc: list[Media] = []
        self.cli = cli

    def process(self, contents: list) -> None:
        """
        Send content to each selected tracker with the trackers_name_list.
        trackers_name_list can be a list of tracker names or the current tracker for the upload process

        Args:
            contents: torrent contents
        Returns:
            NOne
        """
        # // Build a GAME list
        self.games = [
            content for content in contents if content.category == System.category_list.get(System.GAME)
        ]

        if self.games:
            if 'no_key' in config_settings.tracker_config.IGDB_CLIENT_ID:
                custom_console.bot_warning_log("Skipping game upload, no IGDB credentials provided")
                self.games = []

        # // Build a VIDEO list
        self.videos = [
            content
            for content in contents
            if content.category in {System.category_list.get(System.MOVIE), System.category_list.get(System.TV_SHOW)}
        ]

        # // Build a Doc list
        self.doc = [
            content for content in contents if content.category == System.category_list.get(System.DOCUMENTARY)
        ]

        if config_settings.user_preferences.DUPLICATE_ON:
            custom_console.bot_log("'[ACTIVE]' Searching for duplicates")

    def run(self, trackers_name_list: list):
        """

        Args:
            trackers_name_list: list of tracker names to update the torrent file ( -cross or -tracker)
        Returns:

        """

        game_process_results: list[BittorrentData] = []
        video_process_results: list[BittorrentData] = []
        docu_process_results: list[BittorrentData] = []

        for selected_tracker in trackers_name_list:
            # Build the torrent file and upload each GAME to the tracker
            if self.games:
                game_manager = GameManager(contents=self.games, cli=self.cli)
                game_process_results = game_manager.process(selected_tracker=selected_tracker,
                                                            tracker_name_list=trackers_name_list)

            # Build the torrent file and upload each VIDEO to the trackers
            if self.videos:
                video_manager = VideoManager(contents=self.videos, cli=self.cli)
                video_process_results = video_manager.process(selected_tracker=selected_tracker,
                                                              tracker_name_list=trackers_name_list)

            # Build the torrent file and upload each DOC to the tracker
            if self.doc:
                docu_manager = DocuManager(contents=self.doc, cli=self.cli)
                docu_process_results = docu_manager.process(selected_tracker=selected_tracker,
                                                            tracker_name_list=trackers_name_list)

            # No seeding
            if self.cli.noseed or self.cli.noup:
                custom_console.bot_warning_log(f"No seeding active. Done.")
                return None


            if game_process_results:
                UserContent.send_to_bittorrent(game_process_results, 'GAME')

            if video_process_results:
                UserContent.send_to_bittorrent(video_process_results, 'VIDEO')

            if docu_process_results:
                UserContent.send_to_bittorrent(docu_process_results, 'DOCUMENTARY')
            custom_console.bot_log(f"Tracker '{selected_tracker}' Done.")
            custom_console.rule()

    custom_console.bot_log(f"Done.")


    def send(self, this_path: str, trackers_name_list: list):
        # Send a torrent file that has already been created for seeding
        # you can update the announce list by adding the -tracker or -cross flags

        # for each selected tracker we send our tracker list ( default or by -tracker,-cross flags)
        for selected_tracker in trackers_name_list:
            if UserContent.torrent_file_exists(path=this_path, selected_tracker=selected_tracker,
                                                               tracker_name_list=trackers_name_list):
                client = UserContent.get_client()
                client.send_file_to_client(torrent_path=this_path)
            else:
                custom_console.bot_warning_log(f"File torrent not found for '{this_path}'"
                                               f" in {config_settings.user_preferences.TORRENT_ARCHIVE_PATH}" )



