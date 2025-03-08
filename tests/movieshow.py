# -*- coding: utf-8 -*-
import pytest
import tests

for tracker in tests.config.tracker_config.MULTI_TRACKER:
    tracker_data = tests.TRACKData.load_from_module(tracker)
    assert isinstance(tracker_data.category, dict)


def test_tmdb():

    test_content_movie = r"C:\test_folder"
    content_manager = tests.ContentManager(path=test_content_movie, mode='auto')
    contents = content_manager.process()

    TRACKER_TEST = 'ITT'
    tracker_data = tests.TRACKData.load_from_module(TRACKER_TEST)

    # // Print list
    for item in contents:
        tests.custom_console.bot_warning_log(item.title)

    for content in contents:

        """ DUPLICATE """
        assert isinstance(tests.UserContent.is_duplicate(content=content, tracker_name=TRACKER_TEST),bool)

        """ VIDEO INFO """
        if content.category in [tests.System.MOVIE, tests.System.TV_SHOW]:
            # TMDB
            tests.custom_console.bot_log(f"FileName = {content.file_name}")
            db_online = tests.DbOnline(query=content.guess_title, category=content.category)
            if db:= db_online.media_result:
                assert hasattr(db, 'video_id') and hasattr(db, 'keywords_list') and hasattr(db, 'trailer_key')

            video_info = tests.Video(content.file_name, tmdb_id=db.video_id, trailer_key=db.trailer_key)
            video_info.build_info()
            assert video_info.video_frames
            assert video_info.mediainfo is not None

            if media_info:= tests.MediaFile(content.file_name):
                assert all(value is not None for value in vars(media_info).values())

            # """ TRACKER DATA"""
            tests.custom_console.bot_log(f"name = {content.display_name}")
            tests.custom_console.bot_log(f"tmdb = {db.video_id}")
            tests.custom_console.bot_log(f"keywords = {db.keywords_list}")
            tests.custom_console.bot_log(f"category_id = {content.category}")
            resolution_id = tracker_data.resolution[content.screen_size]\
                if content.screen_size else tracker_data.resolution[content.resolution]
            tests.custom_console.bot_log(f"resolution_id = {resolution_id}")
            # tests.custom_console.bot_log(f"mediainfo = {video_info.mediainfo}")
            tests.custom_console.bot_log(f"description = {video_info.description}")
            tests.custom_console.bot_log(f"sd = {video_info.is_hd}")
            tests.custom_console.bot_log(f"type_id = {tracker_data.filter_type(content.file_name)}")
            tests.custom_console.bot_log(f"season_number = {content.guess_season}")
            tests.custom_console.bot_log(f"episode_number = {content.guess_episode if not content.torrent_pack else 0}")

        """ GAME """
        if content.category == tests.System.GAME:
            igdb = tests.IGDBClient()
            assert isinstance(igdb, tests.IGDBClient)

            login = igdb.connect()
            assert login

            game_data_results = igdb.game(content=content)
            # Skip the upload if there is no valid IGDB
            if not game_data_results:
                continue

            igdb_platform = content.platform_list[0].lower() if content.platform_list else ''
            tests.custom_console.bot_log(f"name = {content.display_name}")
            tests.custom_console.bot_log(f"category_id = {content.category}")
            tests.custom_console.bot_log(f"description = {game_data_results.description if igdb else 'Sorry, there is no valid IGDB'}")
            tests.custom_console.bot_log(f"type_id = {tracker_data.type_id.get(igdb_platform)}")
            tests.custom_console.bot_log(f"igdb id = {game_data_results.id if game_data_results else 1}")


        """ TORRENT INFO """
        if torrent_response:=tests.UserContent.torrent(content=content):
            assert all(value is not None for value in vars(torrent_response).values())

        """ UPLOAD """
        # Tracker Bot
        unit3d_up = tests.UploadBot(content=content, tracker_name=TRACKER_TEST)


        # Send data to the tracker
        if content.category in [tests.System.MOVIE, tests.System.TV_SHOW]:
            tracker_response, tracker_message = unit3d_up.send(show_id=db.video_id, imdb_id = db.imdb_id,
                                                               show_keywords_list=db.keywords_list,
                                                               video_info=video_info)


        if content.category == tests.System.GAME:
            tracker_response, tracker_message = unit3d_up.send_game(igdb=game_data_results, nfo_path=content.game_nfo)


        tests.custom_console.bot_log(f"TRACKER RESPONSE {tracker_response}")
        tests.custom_console.bot_log(f"TRACKER MESSAGE {tracker_message}")

        if not tracker_response:
            tests.custom_console.bot_error_log(f"NO TRACKER RESPONSE {tracker_message}")
            input("Press Enter to continue...")
            continue

        """ TRANSMISSION """
        transmission = tests.TransmissionClient()
        transmission.connect()
        transmission.send_to_client(
            tracker_data_response=tracker_response,
            torrent=torrent_response,
            content=content
        )

        """ QBITTORRENT """
        qbittorrent = tests.QbittorrentClient()
        qbittorrent.connect()
        qbittorrent.send_to_client(
            tracker_data_response=tracker_response,
            torrent=torrent_response,
            content=content
        )
        tests.custom_console.bot_log("Done.")
        tests.custom_console.rule()
        pytest.exit()



