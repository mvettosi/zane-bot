import logging
from enum import Enum

import discord
from aiohttp import ContentTypeError
from discord import Embed

from modules import database, download, config
from modules.config import COLORS
from modules.pagination import Paginator

CARD_ANNOTATOR_URL = config.CARD_ANNOTATOR_URL or 'https://dl-card-annotator.paas.drackmord.co.uk'
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
]
CARD_BUTTONS_BY_INDEX = dict((e, i) for (i, e) in enumerate(CARD_BUTTONS))
PREV_BUTTON = '\U000023ee'
NEXT_BUTTON = '\U000023ed'


class SearchResult(object):

    def __init__(self, result: dict) -> None:
        super().__init__()
        self.data = result

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        else:
            result_name = self.get('name', '(name not found)')
            logging.warning(f'Attribute "{key}" missing from search result "{result_name}"!')
            logging.debug(f'Full search results: {self.data}')
            return 'Not Found'

    def __setitem__(self, key, value):
        self.data[key] = value

    def is_skill(self) -> bool:
        return 'exclusive' in self.data

    def get(self, key, default_value=None):
        return self.data[key] if key in self.data else default_value


def get_skill_thumbnail_url(skill: SearchResult) -> str:
    char = 'vagabond'
    if skill['exclusive']:
        try:
            char = skill.get('characters')[0]['name'].lower().replace(' ', '-').replace('(', '').replace(')', '')
        except:
            pass
    return f'https://www.duellinksmeta.com/img/characters/{char}/portrait.png'


def get_skill_embed(skill: SearchResult) -> Embed:
    name = skill['name']
    characters = skill.get('characters', [])
    char_list = [h['name'] for h in characters]
    chars = ', '.join(char_list)
    hows_list = [h['how'] + ' from ' + h['name'] if h['how'] == 'Drop' else h['name'] + ' ' + h['how'] for h in
                 characters]
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


async def get_card_desc(card: SearchResult) -> str:
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
        release = card['release']
        desc = desc + f'\n**Released**: {release}'

    return desc


async def get_card_thumbnail_url(card: SearchResult, status: str) -> str:
    default_img = ''
    specific_img = ''
    result = ''
    if 'annotated_url' in card and await download.check(card['annotated_url']):
        logging.info('Using cached card image')
        result = card['annotated_url']
    else:
        try:
            default_img = card.get('card_images')[0]['image_url']
        except:
            pass

        if 'customURL' in card:
            custom_url = card['customURL']
            specific_img = f'https://www.duellinksmeta.com/{custom_url}'
        elif 'konami_id' in card:
            konami_id = card['konami_id']
            specific_img = f'https://www.konami.com/yugioh/duel_links/images/card/en/{konami_id}.jpg'

        if 'rarity' in card and card['rarity'] != 'N/A':
            logging.info('Retrieving new annotated card image')
            request = {'rarity': card['rarity']}
            if status.startswith('Limited'):
                request['limit'] = status[-1]
            response = None

            # Try to fetch specific image first
            if specific_img and await download.check(specific_img):
                request['url'] = specific_img
                try:
                    response = await download.json(CARD_ANNOTATOR_URL, download.HttpMethod.POST, request)
                except Exception as e:
                    logging.error(f'Could not generate annotated specific image, trying with tcg\n{e}')

            # If specific image failed, try to annotate tcg one
            if not response and default_img and await download.check(default_img):
                request['url'] = default_img
                try:
                    response = await download.json(CARD_ANNOTATOR_URL, download.HttpMethod.POST, request)
                except Exception as e:
                    logging.error(f'Could not generate annotated tcg image either! Using no image...\n{e}')

            # If anything worked, update result and db
            if response and 'url' in response and response['url']:
                result = response['url']
                card['annotated_url'] = result
                await database.update_card(card.data)
        else:
            logging.info('Using non-annotated image')
            result = default_img

    return result


def get_card_color(card: SearchResult) -> int:
    card_type = card['type']
    if card_type in COLORS:
        color_string = COLORS[card_type]
        return int(color_string, 16)
    else:
        return config.BOT_COLOR


def get_card_text_title(card: SearchResult) -> str:
    if 'Monster' in card['type']:
        if 'Normal' in card['type']:
            return 'Lore Text'
        else:
            return 'Monster Effect'
    else:
        return 'Card Effect'


def add_desc(card: SearchResult, embed: Embed) -> None:
    card_text = card['desc']
    if '[ Pendulum Effect ]' in card_text:
        desc_lines = card_text.splitlines()
        desc_title = ''
        result_lines = []
        for line in desc_lines:
            if line.startswith('[') and line.endswith(']'):
                if desc_title and result_lines:
                    result_desc = '\n'.join(result_lines)
                    embed.add_field(name=desc_title, value=result_desc, inline=False)
                    result_lines = []
                desc_title = line
            elif not all(c == '-' for c in line):
                result_lines.append(line)
        result_desc = '\n'.join(result_lines)
        embed.add_field(name=desc_title, value=result_desc, inline=False)
    else:
        desc_title = get_card_text_title(card)
        embed.add_field(name=desc_title, value=card_text, inline=False)


async def get_card_embed(card: SearchResult) -> Embed:
    name = card['name']
    desc = await get_card_desc(card)
    color = get_card_color(card)
    status = await database.get_forbidden_status(name)
    thumbnail_url = await get_card_thumbnail_url(card, status)

    embed = discord.Embed(title=name, description=desc, color=color)
    embed.set_thumbnail(url=thumbnail_url)
    add_desc(card, embed)

    if 'id' in card:
        card_id = card['id']
        embed.set_footer(text=card_id)
    return embed


async def get_embed(data: dict) -> Embed:
    result = SearchResult(data)
    if result.is_skill():
        return get_skill_embed(result)
    else:
        return await get_card_embed(result)


def get_search_result(paginator: Paginator, query: str) -> discord.Embed:
    page = paginator.get_page()
    title = f'Results for {query}' if query else 'Search results'
    desc = f'Page `{paginator.current_page + 1}` of `{paginator.pages_number()}`, ' \
           f'results `{page.index_start + 1} - {page.index_end + 1}` '
    embed = discord.Embed(title=title, description=desc, color=config.BOT_COLOR)
    for index, entry in enumerate(page.elements):
        button = CARD_BUTTONS[index]
        name = entry['name']
        entry_type = 'Skill' if 'exclusive' in entry else 'Card'
        entry_text = f'{button} {name}'
        embed.add_field(name=entry_type, value=entry_text, inline=False)
    return embed


class LadderType(Enum):
    TOP_PLAYER = 'Top Player'
    ANYTIME = 'Anytime'


def get_ladder_page(paginator: Paginator, ladder_type: LadderType) -> Embed:
    title = f'Duel Links Meta {ladder_type.value} Ladder (Page {paginator.current_page + 1} of {paginator.pages_number()})'
    result = discord.Embed(title=title, color=config.BOT_COLOR)
    page = paginator.get_page()
    for player_group in page.elements:
        rank_min = player_group['rank_min']
        rank_max = player_group['rank_max']
        rank_text = f'Rank {rank_min}' if rank_min == rank_max else f'Rank {rank_min}-{rank_max}'
        if rank_min <= 16 and ladder_type is LadderType.TOP_PLAYER:
            rank_text += ' (new TPC)'
        rank_system = 'points' if ladder_type is LadderType.TOP_PLAYER else 'wins'
        rank_key = 'total_points' if ladder_type is LadderType.TOP_PLAYER else 'wins'
        rank_desc = '\n'.join([
            '`' + p['name'] + '` (' + str(p[rank_key]) + f' {rank_system})' for p in player_group['players']
        ])
        result.add_field(name=rank_text, value=rank_desc)
    return result
