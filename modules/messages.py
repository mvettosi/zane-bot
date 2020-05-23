import logging
import math
from itertools import groupby

import discord
from discord import Colour

from modules import database, download, config
from modules.config import COLORS

CARD_ANNOTATOR_URL = 'https://dl-card-annotator.paas.drackmord.space'
CARD_BUTTONS = [
    '\U0001f1e6',  # A
    '\U0001f1e7',  # B
    '\U0001f1e8',  # C
    '\U0001f1e9',  # D
    '\U0001f1ea',  # E
    '\U0001f1eb',  # F
    '\U0001f1ec',  # G
    '\U0001f1ed',  # H
    '\U0001f1ee',  # I
    '\U0001f1ef',  # J
    '\U000023ee',  # PREV
    '\U000023ed',  # NEXT
]
CARD_BUTTONS_BY_INDEX = dict((e, i) for (i, e) in enumerate(CARD_BUTTONS))


def is_skill(result):
    return 'exclusive' in result


def get_skill_thumbnail_url(skill):
    char = 'vagabond'
    if skill['exclusive']:
        char = skill['characters'][0]['name'].lower().replace(' ', '-')
    return f'https://www.duellinksmeta.com/img/characters/{char}/portrait.png'


def get_skill_embed(skill):
    name = skill['name']
    char_list = [h['name'] for h in skill['characters']]
    chars = ', '.join(char_list)
    hows_list = [h['how'] + ' from ' + h['name'] if h['how'] == 'Drop' else h['name'] + ' ' + h['how'] for h in
                 skill['characters']]
    hows = ', '.join(hows_list)
    desc = f'''
        **Characters**: {chars}
        **How to Obtain**: {hows}'''
    color = config.BOT_COLOR
    thumbnail_url = get_skill_thumbnail_url(skill)
    skill_text = skill['description']

    embed = discord.Embed(title=name, description=desc, color=color)
    embed.set_thumbnail(url=thumbnail_url)
    embed.add_field(name='Description', value=skill_text)
    return embed


async def get_card_desc(card, status):
    desc = ''
    race = card['race']

    if 'Monster' in card['type']:
        # Attribute
        attribute = card['attribute']
        desc = desc + f'**Attribute**: {attribute}'

        # Level
        if 'level' in card:
            level = card['level']
            if 'XYZ' in card['type']:
                desc = desc + f' **Rank**: {level}'
            else:
                desc = desc + f' **Level**: {level}'
        elif 'linkval' in card:
            linkval = card['linkval']
            desc = desc + f' **Link Val**: {linkval}'

        # Type
        type_text = race
        card_type = card['type'].replace(' Monster', '').replace('Normal', '').strip().replace(' ', '/')
        if card_type:
            type_text = type_text + f'/{card_type}'
        desc = desc + f'\n**Type**: {type_text}'

        # Atk/Def
        attack = card['atk']
        desc = desc + f' **ATK**: {attack}'

        if 'def' in card:
            defense = card['def']
            desc = desc + f' **DEF**: {defense}'
    else:
        # Type
        card_type = card['type'].replace(' Card', '')
        type_text = f'{card_type}/{race}'
        desc = desc + f'\n**Type**: {type_text}'

    # How to obtain
    how = ', '.join(card['how']) if 'how' in card else 'Unavailable'
    desc = desc + f'\n**How to Obtain**: {how}'

    # Release date
    if 'release' in card:
        release = card['release'] if 'release' in card else 'Not released yet'
        desc = desc + f'\n**Released**: {release}'

    return desc


async def get_card_thumbnail_url(card, status):
    result = ''
    if 'annotated_url' in card:
        logging.info('Using cached card image')
        result = card['annotated_url']
    else:
        if 'customURL' in card:
            custom_url = card['customURL']
            result = f'https://www.duellinksmeta.com/{custom_url}'
        elif 'konami_id' in card:
            konami_id = card['konami_id']
            result = f'https://www.konami.com/yugioh/duel_links/en/box/cards/en/{konami_id}.jpg'
        elif 'card_images' in card:
            result = card['card_images'][0]['image_url']

        if result and 'rarity' in card and card['rarity'] != 'N/A':
            logging.info('Retrieving new annotated card image')
            request = {'url': result, 'rarity': card['rarity']}
            if status.startswith('Limited'):
                request['limit'] = status[-1]
            response = await download.json(CARD_ANNOTATOR_URL, download.HttpMethod.POST, request)
            # logging.info(f'Sending request with {request}')
            # async with aiohttp.ClientSession() as cs:
            #     async with cs.post(CARD_ANNOTATOR_URL, json=request) as r:
            #         response = await r.json()
            #         logging.info(f'Received response: {response}')
            if response and 'url' in response and response['url']:
                result = response['url']
                card['annotated_url'] = result
                await database.update_card(card)
        else:
            logging.info('Using non-annotated image')

    return result


def get_card_color(card):
    card_type = card['type']
    color_string = COLORS[card_type]
    return int(color_string, 16)


def get_card_text_title(card):
    if 'Monster' in card['type']:
        if 'Normal' in card['type']:
            return 'Lore Text'
        else:
            return 'Monster Effect'
    else:
        return 'Card Effect'


async def get_card_embed(card):
    name = card['name']
    status = await database.get_forbidden_status(card['name'])
    desc = await get_card_desc(card, status)
    color = get_card_color(card)
    thumbnail_url = await get_card_thumbnail_url(card, status)
    desc_title = get_card_text_title(card)
    card_text = card['desc']

    embed = discord.Embed(title=name, description=desc, color=color)
    embed.set_thumbnail(url=thumbnail_url)
    embed.add_field(name=desc_title, value=card_text, inline=False)

    if 'id' in card:
        card_id = card['id']
        embed.set_footer(text=card_id)
    return embed


async def get_embed(result):
    if is_skill(result):
        return get_skill_embed(result)
    else:
        return await get_card_embed(result)


def get_search_result(results, page, query):
    first_index = page * 10
    last_index = first_index + 10 if first_index + 10 < len(results) else len(results)
    title = f'Results for {query}' if query else 'Search results'
    desc = f'Page `{page + 1}` of `{math.ceil(len(results) / 10)}`, results `{first_index + 1} - {last_index + 1}`'
    color = Colour.light_grey()
    embed = discord.Embed(title=title, description=desc, color=color)
    for index in range(first_index, last_index):
        entry = results[index]
        button = CARD_BUTTONS[index % 10]
        name = entry['name']
        entry_type = 'Skill' if 'exclusive' in entry else 'Card'
        entry_text = f'{button} {name}'
        embed.add_field(name=entry_type, value=entry_text, inline=False)
    return embed


def get_ladder(ladder, page):
    first_index = page * 10
    last_index = first_index + 10 if first_index + 10 < len(ladder) else len(ladder)
    title = ''


def get_tpc(ladder):
    title = 'Top Player Council current candidates'
    result = discord.Embed(title=title, color=config.BOT_COLOR)
    ladder_sorted = sorted(ladder, reverse=True, key=lambda key: key['total_points'])
    rank = 0
    for k, v in groupby(ladder_sorted, key=lambda x: x['total_points']):
        players = list(v)
        rank = rank + 1
        if rank <= 16:
            rank_text = f'Rank {rank}'
            if len(players) > 1:
                rank = rank + len(players) - 1
                rank_text = f'{rank_text}-{rank}'
            rank_desc = '\n'.join(['`' + p['name'] + '` (' + str(p['total_points']) + ' points)' for p in players])
            result.add_field(name=rank_text, value=rank_desc)
        else:
            break
    return result
