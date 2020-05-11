import os
import shutil
import requests
import logging
import hashlib
from enum import Enum

DOWNLOAD_FOLDER = 'tmp'


class FileType(Enum):
    TCG = 'https://db.ygoprodeck.com/api/v7/cardinfo.php'
    DL = 'https://www.duellinksmeta.com/data/cards.json'
    SKILLS = 'https://www.duellinksmeta.com/data/skills.json'


def download(file_type):
    shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)
    os.makedirs(DOWNLOAD_FOLDER)
    file_name = f'{file_type.name}.json'
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    r = requests.get(file_type.value, stream=True)
    if r.ok:
        logging.info(
            f'Downloading {file_type} to {os.path.abspath(file_path)}')
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        return {'path': file_path, 'md5': md5}
    else:  # HTTP status code 4XX/5XX
        logging.error(
            f'Download failed: status code {r.status_code}\n{r.text}')
