# -*- coding: utf-8 -*-

import argparse

from unit3dup.media_manager.VideoManager import VideoManager
from unit3dup.media_manager.GameManager import GameManager
from unit3dup.media_manager.DocuManager import DocuManager
from unit3dup.qbittorrent import QBittorrent
from unit3dup import config

from common.custom_console import custom_console
from common.trackers.trackers import ITTData
from common.constants import my_language
from unit3dup.media_manager.common import UserContent


class TorrentManager:
    def __init__(self, cli: argparse.Namespace, tracker_name=None):  # todo tracker_name
        self.cli = cli

        tracker_data = ITTData.load_from_module()

        self.movie_category = tracker_data.category.get("movie")
        self.serie_category = tracker_data.category.get("tvshow")
        self.docu_category = tracker_data.category.get("edicola")
        self.game_category = tracker_data.category.get("game")
        self.preferred_lang = my_language(config.PREFERRED_LANG)

    def process(self, contents: list) -> None:

        game_process_results: list["QBittorrent"] = []
        video_process_results: list["QBittorrent"] = []
        docu_process_results: list["QBittorrent"] = []
        custom_console.rule()

        # // Build a GAME list
        games = [
            content for content in contents if content.category == self.game_category
        ]

        # // Build a VIDEO list
        videos = [
            content
            for content in contents
            if content.category in {self.movie_category, self.serie_category}
        ]

        # // Build a Doc list
        doc = [
            content for content in contents if content.category == self.docu_category
        ]

        if config.DUPLICATE_ON:
            custom_console.bot_log("'[ACTIVE]' Searching for duplicate")

        # Build the torrent file and upload each GAME to the tracker
        if games:
            game_manager = GameManager(contents=games, cli=self.cli)
            game_process_results = game_manager.process()

        # Build the torrent file and upload each VIDEO to the tracker
        if videos:
            video_manager = VideoManager(contents=videos, cli=self.cli)
            video_process_results = video_manager.process()

        # Build the torrent file and upload each DOC to the tracker
        if doc:
            docu_manager = DocuManager(contents=doc, cli=self.cli)
            docu_process_results = docu_manager.process()


        if game_process_results or video_process_results or docu_process_results:
            custom_console.panel_message("\nSending torrents to the client... Please wait")

        # * QBITTORRENT *
        # Send
        if game_process_results:
            if not self.cli.torrent:
                UserContent.send_to_qbittorrent(game_process_results)

        if video_process_results:
            if not self.cli.torrent:
                UserContent.send_to_qbittorrent(video_process_results)

        if docu_process_results:
            if not self.cli.torrent:
                UserContent.send_to_qbittorrent(docu_process_results)