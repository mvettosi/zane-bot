import logging

import aiohttp
import discord
from discord import Colour

from modules import database
from modules.config import COLORS

CARD_ANNOTATOR_URL = 'https://dl-card-annotator.paas.drackmord.space'


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
    color = Colour.light_grey()
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
            logging.info(f'Sending request with {request}')
            async with aiohttp.ClientSession() as cs:
                async with cs.post(CARD_ANNOTATOR_URL, json=request) as r:
                    response = await r.json()
                    logging.info(f'Received response: {response}')
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
