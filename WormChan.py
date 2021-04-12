# -*- coding: utf-8 -*-


# start of import list
import json
import requests
from joblib import Parallel, delayed
from minio_utils import client, save_to_minio
from consts import (pic_folder, gif_folder,
                    swf_folder, webm_folder,
                    pdf_folder, SATAN_folder)
from loguru import logger
# end of import list

# ------------------------------------------------------------------------------
# Working code below
# ------------------------------------------------------------------------------


def catalog_list(boardNAME):
    url = f'http://a.4cdn.org{boardNAME}catalog.json'
    responce = requests.get(url)
    threads = []
    if responce:
        output = responce.json()
        for page in output:
            for thread in page['threads']:
                try:
                    threads.append(str(thread['no']))
                except KeyError:
                    continue
    return threads


def get_thread(boardNAME, thread):
    url = f'http://a.4cdn.org/{boardNAME}/thread/{thread}.json'
    response = requests.get(url)
    output = response.content.decode('utf-8')
    if output:
        # Parse for success or failure
        out = json.loads(output)
        for post in out['posts']:
            try:
                logger.debug(thread['sub'])
                logger.debug(post['com'])
            except KeyError:
                continue


def get_resources(boardNAME, thread):
    url = f'http://a.4cdn.org/{boardNAME}/thread/{thread}.json'
    response = requests.get(url)
    output = response.content.decode('utf-8')
    if output:
        # Parse for success or failure
        out = json.loads(output)
        for post in out['posts']:
            try:
                tim = str(post['tim'])
                ext = str(post['ext'])
                number = str(post['no'])
            except KeyError:
                continue
            image_url = f'http://i.4cdn.org{boardNAME}{tim}{ext}'
            logger.debug(image_url)
            try:
                if '.jpg' in ext or '.png' in ext:
                    if f'{tim+ext}' not in pic_folder:
                        content_pic = requests.get(image_url).content
                        save_to_minio(client, pic_folder,
                                      f'{tim+ext}', content_pic,
                                      len(content_pic))
                if '.gif' in ext:
                    if f'{tim+ext}' not in gif_folder:
                        content_gif = requests.get(image_url).content
                        save_to_minio(client, gif_folder,
                                      f'{tim+ext}', content_gif,
                                      len(content_gif))
                if '.webm' in ext:
                    if f'{tim+ext}' not in webm_folder:
                        content_webm = requests.get(image_url).content
                        save_to_minio(client, webm_folder,
                                      f'{tim+ext}', content_webm,
                                      len(content_webm))
                if '.swf' in ext:
                    if f'{tim+ext}' not in swf_folder:
                        content_swf = requests.get(image_url).content
                        save_to_minio(client, swf_folder,
                                      f'{tim+ext}', content_swf,
                                      len(content_swf))
                if '.pdf' in ext:
                    if f'{tim+ext}' not in pdf_folder:
                        pdf_content = requests.get(image_url).content
                        save_to_minio(client, pdf_folder,
                                      f'{tim+ext}', pdf_content,
                                      len(pdf_content))
                if '666' in number:
                    if f'{number+ext}' not in SATAN_folder:
                        content_666 = requests.get(image_url).content
                        save_to_minio(client, SATAN_folder,
                                      f'{number+ext}', content_666,
                                      len(content_666))
                else:
                    pass
            except Exception as ex:
                logger.error(f'content retrieval failed, {ex}')


def board_task(board):
    threads = catalog_list(board)
    logger.debug(threads)
    for thread in threads:
        logger.debug(thread)
        try:
            get_resources(board, thread)
        except PermissionError:
            logger.error('access denied')
            pass
        except Exception as ex:
            logger.error(f'unknown exception {ex}')
            pass
    logger.debug(f"{board} taken")


def memeater(boards):
    logger.debug(f"big_memeater intinated for boards {boards}")
    for board in boards:
        try:
            logger.debug(f"small_memeater intinated for board {board}")
            threads = catalog_list(board)
            logger.debug(f"thread numbers:\n {threads}")
            Parallel(n_jobs=6)(delayed(get_resources)(board, thread)
                               for thread in threads)
        except Exception as ex:
            logger.error(f"board {board} scrape returned an error: {ex}")


def small_memeater(board):
    logger.debug(f"small_memeater intinated for board {board}")
    threads = catalog_list(board[0])
    logger.debug(f"thread numbers:\n {threads}")
    Parallel(n_jobs=6)(delayed(get_resources)(board[0], thread)
                       for thread in threads)

# memeater(["/x/"])
