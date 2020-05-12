# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord import Colour
from modules.config import EMOTES, COLORS


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


def get_card_type(card):
    card_type = card['type']
    race = card['race']
    if card_type == 'Monster':
        monster_type = card['monster_type']
        # race_emote = EMOTES['race'][race]
        return f'{race}/{monster_type}'
    else:
        # type_emote = EMOTES['type'][card_type]
        # subtype_emote = '' if race == 'Normal' else EMOTES['type'][race]
        return f'{card_type}/{race}'


def get_card_desc(card):
    desc = ''

    if 'archetype' in card:
        archetype = card['archetype']
        desc = desc + f'**Archetype**: {archetype} '

    rarity = card['rarity'] if 'rarity' in card else 'Unavailable'
    desc = desc + f'**Rarity**: {rarity}'

    if 'release' in card:
        release = card['release'] if 'release' in card else 'Not released yet'
        desc = desc + f' **Released**: {release}'

    type_text = get_card_type(card)
    desc = desc + f'\n**Type**: {type_text}'

    if card['type'] == 'Monster':
        attribute = card['attribute']
        # attribute_emote = EMOTES['attribute'][attribute]
        desc = desc + f' **Attribute**: {attribute}'

        level = card['level']
        # level_emote = EMOTES['misc']['level']
        attack = card['atk']
        defense = card['def']
        desc = desc + f'\n**Level**: {level} **ATK**: {attack} **DEF**: {defense}'

    how = ', '.join(card['how']) if 'how' in card else 'Unavailable'
    desc = desc + f'\n**How to Obtain**: {how}'

    return desc


def get_card_thumbnail_url(card):
    card_id = card['id']
    return f'https://pics.alphakretin.fail/{card_id}.png'


def get_card_color(card):
    card_type = card['type']
    if card_type == 'Spell' or card['type'] == 'Trap':
        color_string = COLORS[card_type]
    else:
        monster_type = card['monster_type']
        color_string = COLORS[monster_type]
    return int(color_string, 16)


def get_card_text_title(card):
    if card['type'] == 'Monster':
        if card['monster_type'] == 'Normal':
            return 'Lore Text'
        else:
            return 'Monster Effect'
    else:
        return 'Card Effect'


def get_card_embed(card):
    name = card['name']
    desc = get_card_desc(card)
    color = get_card_color(card)
    thumbnail_url = get_card_thumbnail_url(card)
    desc_title = get_card_text_title(card)
    card_text = card['desc']
    card_id = card['id']

    embed = discord.Embed(title=name, description=desc, color=color)
    embed.set_thumbnail(url=thumbnail_url)
    embed.add_field(name=desc_title, value=card_text, inline=False)
    embed.set_footer(text=card_id)
    return embed


def get_embed(result):
    if is_skill(result):
        return get_skill_embed(result)
    else:
        return get_card_embed(result)
