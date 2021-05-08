# -*- coding: utf-8 -*-


# start of import list
import asyncio
import requests
import json
from joblib import Parallel, delayed
from minio_utils import client, save_to_minio
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


def download(boardNAME, post, user):
    try:
        tim = str(post['tim'])
        ext = str(post['ext'])
    except KeyError:
        return
    image_url = f'http://i.4cdn.org{boardNAME}{tim}{ext}'
    logger.debug(image_url)
    try:
        if '.jpg' in ext or '.png' in ext:
            if f'{tim+ext}' not in f"{user}_main":
                content_pic = requests.get(image_url).content
                save_to_minio(client, f"{user}_main",
                              f'{tim+ext}', content_pic,
                              len(content_pic))
        else:
            return
    except Exception as ex:
        logger.error(f'content retrieval failed, {ex}')


def get_resources(boardNAME, thread, user):
    try:
        url = f'http://a.4cdn.org/{boardNAME}/thread/{thread}.json'
        response = requests.get(url)
        output = response.content.decode('utf-8')
        if output:
            # Parse for success or failure
            out = json.loads(output)
            Parallel(n_jobs=2, backend="threading")(delayed(download)(boardNAME, post, user)
                               for post in out['posts'])
        logger.debug(f"finished thread {thread} for {boardNAME}")
    except Exception as ex:
        logger.error(f'thread retrieval failed, {ex}')


def memeater(boards, user):
    logger.debug(f"big_memeater intinated for boards {boards}")
    for board in boards:
        try:
            logger.debug(f"memeater intinated for board {board}")
            threads = catalog_list(board)
            logger.debug(f"thread numbers:\n {threads}")
            Parallel(n_jobs=4, backend="threading")(delayed(get_resources)(board, thread, user)
                               for thread in threads)
        except Exception as ex:
            logger.error(f"board {board} scrape returned an error: {ex}")


async def small_memeater(board, user):
    try:
        logger.debug(f"small_memeater intinated for board {board}")
        threads = catalog_list(board[0])
        logger.debug(f"thread numbers:\n {threads}")
        Parallel(n_jobs=4, backend="threading")(delayed(get_resources)(board, thread, user)
                           for thread in threads)
    except Exception as ex:
        logger.error(f"board {board} scrape returned an error: {ex}")

# memeater(["/x/"])
