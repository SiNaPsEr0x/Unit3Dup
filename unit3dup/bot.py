# -*- coding: utf-8 -*-

import argparse
import os
import time
import shutil

from unit3dup.media_manager.ContentManager import ContentManager
from unit3dup.media_manager.TorrentManager import TorrentManager

from common.external_services.ftpx.core.models.list import FTPDirectory
from common.external_services.Pw.pw_manager import PwManager
from common.external_services.ftpx.core.menu import Menu
from common.external_services.ftpx.client import Client
from common.extractor import Extractor

from view import custom_console

from pathlib import Path


class Bot:
    """
    A Bot class that manages media files, including processing, torrent management,TMDB ,FTP

    Methods:
        run(): Starts the media processing and torrent handling tasks
        watcher(duration: int, watcher_path: str): Monitors a folder for changes and processes files
        ftp(): Connects to a remote FTP server and processes files
    """

    def __init__(self, path: str, cli: argparse.Namespace, trackers_name_list: list, mode="man"):
        """
        Initializes the Bot instance with path, command-line interface object, and mode

        Args:
            path (str): The path to the directory or file to be managed
            cli (argparse.Namespace): The command-line arguments object
            mode (str): The mode of operation, default is 'man'
        """
        self.trackers_name_list = trackers_name_list
        self.content_manager = None
        self.path = path
        self.cli = cli
        self.mode = mode

        # Bot Manager
        self.torrent_manager = TorrentManager(cli=self.cli)

    def run(self) -> bool:
        """
        Start the process of analyzing and processing media files.

        This method retrieves media files, decompresses any `.rar` files if needed,
        and then processes the files using the TorrentManager
        """
        custom_console.panel_message("Analyzing your media files... Please wait")

        # Get a Files list with basic attributes and create a content object for each
        self.content_manager = ContentManager(path=self.path, mode=self.mode, cli=self.cli)
        contents = self.content_manager.process()

        # -u requires a single file
        if not contents:
            custom_console.bot_error_log("There are no Media to process")
            return False

        if not os.path.exists(self.path):
            custom_console.bot_error_log("Path doesn't exist")
            return False

        # we got a handled exception
        if contents is None:
            exit(1)

        # -f requires at least one file
        if not contents:
            custom_console.bot_error_log(f"There are no Files to process. Try using -scan")
            exit(1)

        # Print the list of files being processed
        custom_console.bot_process_table_log(contents)

        # Process the contents (files) with tracker list
        for tracker in self.trackers_name_list:
            self.torrent_manager.process(contents=contents, selected_tracker=tracker,
                                         trackers_name_list=self.trackers_name_list)
        return True

    def watcher(self, duration: int, watcher_path: str,  destination_path: str)-> bool:
        """
        Monitors the watcher path for new files, moves them to the destination folder,
        then uploads them to the tracker

        Args:
            duration (int): The time duration in seconds for the watchdog to wait before checking again
            watcher_path (str): The path to the folder being monitored for new files
            destination_path: The destination path for the new files
        """
        self.path = str(destination_path)
        try:
            # Watchdog loop
            while True:
                start_time = time.perf_counter()
                end_time = start_time + duration

                # Return if the watcher path doesn't exist
                if not os.path.exists(watcher_path):
                    custom_console.bot_error_log("Watcher path does not exist or is not configured\n")
                    return False

                print()
                # Counter
                while time.perf_counter() < end_time:
                    remaining_time = end_time - time.perf_counter()
                    custom_console.bot_counter_log(
                        f"WATCHDOG: {remaining_time:.1f} seconds Ctrl-c to Exit "
                    )
                    time.sleep(0.01)
                print()

                # Skip if there are no files in the watcher folder
                if not os.listdir(watcher_path):
                    custom_console.bot_log("The are no files in the Watcher folder\n")
                    continue

                # Scan the source and move each file to the destination folder
                for root, dirs, files in os.walk(watcher_path):
                    dest_root = Path(root.replace(watcher_path, self.path))
                    dest_root.mkdir(parents=True, exist_ok=True)

                    for file_name in files:
                        src_file = Path(root) / file_name
                        dest_file = dest_root / file_name

                        # Limit the length of file paths printed
                        limiter_src = '...' if len(str(src_file)) > 50 else ''
                        limiter_dest = '...' if len(str(dest_file)) > 50 else ''

                        custom_console.bot_log(
                            f"{str(src_file)[:50]}{limiter_src} -> from 'watch folder' to 'destination folder'"
                            f" -> {str(dest_file)[:50]}{limiter_dest}"
                        )
                        shutil.move(str(src_file), str(dest_file))  # Move file to destination

                    # Remove empty directories
                    if root != watcher_path and not os.listdir(root):
                        try:
                            os.rmdir(root)
                        except OSError as e:
                            custom_console.bot_error_log(e)
                            exit()

                # Start uploading
                print()
                self.run()

        except KeyboardInterrupt:
            custom_console.bot_log("Exiting...")
        return True

    def pw(self)-> bool:
        """
        Interacts with the PW service to search for torrent files

        This method performs a search query and logs the results for torrents with
        a certain number of seeders
        """
        # PW service
        pw_manager = PwManager(cli=self.cli)
        pw_manager.process()
        custom_console.panel_message("Searching... Please wait")
        return True


    def ftp(self):
        """
        Connects to a remote FTP server and interacts with files.

        This method handles FTP connection, navigation, and file download from the remote server
        """
        custom_console.bot_question_log("\nConnecting to the remote FTP...\n")

        # FTP service
        ftp_client = Client()
        custom_console.bot_question_log(f"Connected to {ftp_client.sys_info()}\n\n")

        menu = Menu()

        page = ftp_client.home_page()
        menu.show(table=page)

        while True:
            user_option = ftp_client.user_input()
            page = ftp_client.input_manager(user_option)
            if page == 0:
                ftp_client.quit()
                break
            if not page:
                continue

            # Display selected folder or file
            if isinstance(page, FTPDirectory):
                ftp_directory_name = page.name
                if page.type == "Folder":
                    page = ftp_client.change_path(selected_folder=ftp_directory_name)
                    menu.show(table=page)
                else:
                    ftp_client.select_file(one_file_selected=page)
                continue

            # Show page as table
            menu.show(table=page)

        if ftp_client.download_to_local_path:
            self.path = os.path.dirname(ftp_client.download_to_local_path)
            self.mode = 'folder'
            # Upload -f process
            # Decompress .rar files if the flags are set
            extractor = Extractor(compressed_media__path=self.path)
            result = extractor.unrar()
            if result is False:
                custom_console.bot_error_log("Unrar Exit")
                exit(1)

            self.run()

    def seed_it(self):
        """ Send a file torrent file for seeding"""
        self.torrent_manager.send(self.path, self.trackers_name_list)