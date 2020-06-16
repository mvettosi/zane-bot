import hashlib
import logging
import os
import shutil
from enum import Enum
from json import dumps

import aiohttp

DOWNLOAD_FOLDER = 'tmp'


class HttpMethod(Enum):
    GET = 1
    POST = 2


class FileType(Enum):
    TCG = 'https://db.ygoprodeck.com/api/v7/cardinfo.php'
    DL = 'https://www.duellinksmeta.com/data/cards.json'
    EXCLUSIVE = 'https://www.duellinksmeta.com/data/exclusiveCards.json'
    EXCLUSIVE_IMG = 'https://www.duellinksmeta.com/data/cardImageFilter.json'
    FORBIDDEN = 'https://www.duellinksmeta.com/data/forbiddenList.json'
    SKILLS = 'https://www.duellinksmeta.com/data/skills.json'


async def download(file_type: FileType) -> dict:
    shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)
    os.makedirs(DOWNLOAD_FOLDER)
    file_name = f'{file_type.name}.json'
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    logging.info(f'Downloading {file_type} to {os.path.abspath(file_path)}')
    async with aiohttp.ClientSession() as session:
        async with session.get(file_type.value) as resp:
            if resp.status == 200:
                with open(file_path, 'wb') as fd:
                    while True:
                        chunk = await resp.content.read(1024 * 8)
                        if not chunk:
                            break
                        fd.write(chunk)
                md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                return {'path': file_path, 'md5': md5}
            else:  # HTTP status code 4XX/5XX
                logging.error(f'Download failed: status code {resp.status}\n{resp.text()}')


async def json(url: str, method: HttpMethod, request=None) -> dict:
    logging.info(f'{method.name}ing url: {url}')
    if request:
        logging.debug(f'Request body: {request}')
    async with aiohttp.ClientSession() as cs:
        call = cs.get(url) if method is HttpMethod.GET else cs.post(url, json=request)
        async with call as r:
            response = await r.json()
            logging.debug(f'Received response: {dumps(response)}')
            return response


async def check(url: str) -> bool:
    logging.info(f'Checking url: {url}')
    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.head(url) as r:
                logging.debug(f'Check result: {r.status}')
                return 200 <= r.status < 300
    except:
        return False
