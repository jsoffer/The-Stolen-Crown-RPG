"""

Entry point

"""

from data.states import shop, levels, battle, main_menu, death
from data.states import sc_credits
from . import setup, tools
from . import constants as c

def main():
    """Add states to control here"""
    run_it = tools.Control(setup.ORIGINAL_CAPTION)
    state_dict = {
        c.MAIN_MENU: main_menu.Menu(),
        c.TOWN: levels.LevelState(c.TOWN),
        c.CASTLE: levels.LevelState(c.CASTLE),
        c.HOUSE: levels.LevelState(c.HOUSE),
        c.OVERWORLD: levels.LevelState(c.OVERWORLD, True),
        c.BROTHER_HOUSE: levels.LevelState(c.BROTHER_HOUSE),
        c.INN: shop.Inn(),
        c.ARMOR_SHOP: shop.ArmorShop(),
        c.WEAPON_SHOP: shop.WeaponShop(),
        c.MAGIC_SHOP: shop.MagicShop(),
        c.POTION_SHOP: shop.PotionShop(),
        c.BATTLE: battle.Battle(),
        c.DUNGEON: levels.LevelState(c.DUNGEON, True),
        c.DUNGEON2: levels.LevelState(c.DUNGEON2, True),
        c.DUNGEON3: levels.LevelState(c.DUNGEON3, True),
        c.DUNGEON4: levels.LevelState(c.DUNGEON4, True),
        c.DUNGEON5: levels.LevelState(c.DUNGEON5, True),
        c.INSTRUCTIONS: main_menu.Instructions(),
        c.LOADGAME: main_menu.LoadGame(),
        c.DEATH_SCENE: death.DeathScene(),
        c.CREDITS: sc_credits.Credits()}

    run_it.setup_states(state_dict, c.MAIN_MENU)
    run_it.main()
