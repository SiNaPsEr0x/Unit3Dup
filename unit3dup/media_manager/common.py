# -*- coding: utf-8 -*-
import os
from concurrent.futures import ThreadPoolExecutor

from unit3dup.qbittorrent import QBittorrent
from unit3dup.pvtTorrent import Mytorrent
from unit3dup.duplicate import Duplicate
from unit3dup.media import Media
from unit3dup.qbitt import Qbitt

from common.custom_console import custom_console
from common.utility import ManageTitles
from common import config


class UserContent:
    """
    Manage user media Files
    """

    @staticmethod
    def torrent_file_exists(content: Media, class_name: str) -> bool:
        """
        Check if a torrent file for the given content already exists

        Args:
            content (Contents): The content object

        Returns:
            bool: True if the torrent file exists otherwise False
        """

        base_name = os.path.basename(content.torrent_path)

        if config.TORRENT_ARCHIVE:
            this_path = os.path.join(config.TORRENT_ARCHIVE, f"{base_name}.torrent")
        else:
            this_path = f"{content.torrent_path}.torrent"

        if os.path.exists(this_path):
            custom_console.bot_warning_log(
                f"** {class_name} **: Reusing the existing torrent file! {this_path}\n"
            )
            return True
        return False


    @staticmethod
    def is_preferred_language(content: Media) -> bool:
        """
           Compare preferred language with the audio language

           Args:
               content (Contents): The content object media

           Returns:
               return boolean
           """
        preferred_lang = config.PREFERRED_LANG.upper()
        preferred_lang_to_iso = ManageTitles.convert_iso(preferred_lang)

        if not content.audio_languages:
            return True

        if preferred_lang == 'ALL':
            return True

        if preferred_lang_to_iso in content.audio_languages:
            return True

        custom_console.bot_log(f"'{content.file_name}'")
        custom_console.bot_warning_log(
            "[UserContent] ** Your preferred lang is not in your media being uploaded, skipping ! **\n"
        )
        custom_console.rule()
        return False

    @staticmethod
    def torrent(content: Media)-> Mytorrent:
        """
           Create the file torrent

           Args:
               content (Contents): The content object media

           Returns:
               my_torrent object
        """

        my_torrent = Mytorrent(contents=content, meta=content.metainfo)
        my_torrent.hash()
        return my_torrent if my_torrent.write() else None

    @staticmethod
    def is_duplicate(content: Media) -> bool:
        """
           Search for a duplicate. Delta = config.SIZE_TH

           Args:
               content (Contents): The content object media

           Returns:
               my_torrent object
        """

        duplicate = Duplicate(content=content)
        if duplicate.process():
            custom_console.bot_error_log(
                f"\n*** User chose to skip '{content.display_name}' ***\n"
            )
            custom_console.rule()
            return True
        else:
            return False


    @staticmethod
    def send_to_qbittorrent_worker(qbittorrent_file: QBittorrent):
        """
        worker: This function will handle sending a single torrent to qBittorrent

        Args:
            qbittorrent_file (QBittorrent): The object containing the torrent and other necessary info
        """
        try:
            # Check if we have a valid response from the tracker
            if qbittorrent_file.tracker_response:
                qb = Qbitt.connect(
                    tracker_data_response=qbittorrent_file.tracker_response,
                    torrent=qbittorrent_file.torrent_response,
                    contents=qbittorrent_file.content,
                )
                # connection successful
                if qb:
                    qb.send_to_client()
            else:
                # invalid response
                custom_console.bot_log(f"[{qbittorrent_file.content.file_name}] ->"
                                       f" {qbittorrent_file.tracker_message}")
        except Exception as e:
            custom_console.bot_error_log(f"Error sending torrent {qbittorrent_file.content.file_name}: {str(e)}")


    @staticmethod
    def send_to_qbittorrent(qbittorrent_list: list[QBittorrent]) -> None:
        """
        Sends a list of torrents to qBittorrent using threads ( async later...)

        Args:
            qbittorrent_list (list[QBittorrent]): A list of QBittorrent objects to be sent to the client
        """
        with ThreadPoolExecutor(max_workers=20) as executor:
            # Submit the torrents
            futures = [executor.submit(UserContent.send_to_qbittorrent_worker, qb) for qb in qbittorrent_list]
            # Wait for all threads to complete
            for future in futures:
                future.result()

