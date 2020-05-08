import logging
import json
import time
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
from modules import config
from modules.download import download, FileType


client = AsyncIOMotorClient(config.DB_CONNECTION_URL)
db = client.duellinksbot


async def retrieve_md5s():
    result = {}
    for file_type in FileType:
        retrieved = await db.md5.find_one({"name": file_type.name})
        result[file_type.name] = retrieved['md5'] if retrieved and 'md5' in retrieved else None
    return result


async def insert_md5(file_type, md5):
    await db.md5.update_one({"name": file_type.name}, {"$set": {"name": file_type.name, 'md5': md5}}, upsert=True)


async def load_json_file(file_type, file_path):
    with open(file_path, 'r') as data_file:
        data_json = json.load(data_file)

    if file_type is FileType.TCG:
        await db.cards.delete_many({})
        await db.cards.insert_many(data_json['data'])
        await insert_md5(FileType.DL, '')

    elif file_type is FileType.DL:
        requests = []
        for dl_card in data_json:
            card_name = dl_card['name']
            requests.append(UpdateOne({"name": card_name}, {"$set": dl_card}))
        await db.cards.bulk_write(requests)

    elif file_type is FileType.SKILLS:
        await db.cards.delete_many({})
        await db.skills.insert_many(data_json)


async def check_updates():
    stored_md5 = await retrieve_md5s()
    for file_type in FileType:
        logging.info(f'')
        logging.info(f'Checking {file_type.name} updates...')
        start_time = time.time()
        file_download = download(file_type)
        new_md5 = file_download['md5']
        if new_md5 != stored_md5[file_type.name]:
            logging.info(f'New md5 found for {file_type.name}: {new_md5}')
            await load_json_file(file_type, file_download['path'])
            logging.info(f'Loaded new version of {file_type.name}')
            await insert_md5(file_type, new_md5)
        else:
            logging.info(
                f'File {file_type.name} is still at the newest version')
        elapsed_time = int(time.time() - start_time)
        elapsed_minutes = elapsed_time // 60
        elapsed_seconds = elapsed_time % 60
        logging.info(
            f'Update took {elapsed_minutes} minutes and {elapsed_seconds} seconds')
