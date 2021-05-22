from celery import Celery
from celery.utils.log import get_task_logger
from consts import (glob_boards, RABBITMQ_USER,
                    RABBITMQ_PASSWORD, RABBITMQ_HOST_PORT,
                    RABBITMQ_VHOST)
from WormChan import memeater

# Create the celery app and get the logger
celery = Celery('wormchan_tasks', broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_PORT}/{RABBITMQ_VHOST}')
celery.conf.update(task_track_started=True,
                   worker_concurrency=1,
                   result_backend='mongodb://127.0.0.1:27017/',
                   mongodb_backend_settings={'database': 'mydb',
                                             'taskmeta_collection': 'my_taskmeta_collection'})
celery_log = get_task_logger(__name__)


@celery.task()
def eat_mem_task(boards, username):
    memeater([f"/{board}/" for board in
              boards if board in glob_boards],
             username)
    celery_log.info(f"scrape of boards {boards} started for {username}")
    return {"message": f"{username} scrape of boards {boards} complete"}
