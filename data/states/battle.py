"""This is the state that handles battles against
monsters"""
import random
import pygame as pg
from .. import tools, battlegui, observer, setup
from .. components import person, attack, attackitems
from .. import constants as c
from ..tools import Timer, empty_background

class Battle(tools.State):
    def __init__(self):
        super(Battle, self).__init__()

        self.name = c.BATTLE

        self.enemy_list = None
        self.player_actions = None
        self.allow_input = None
        self.enemy_pos_list = None
        self.attack_animations = None
        self.player_action_dict = None
        self.enemies_to_attack = None
        self.temp_magic = None
        self.new_gold = None
        self.enemy_group = None
        self.select_action_state_dict = None
        self.enemy_index = None
        self.player_level = None
        self.sword = None
        self.observers = None
        self.arrow = None
        self.info_box = None
        self.run_away = None
        self.background = None
        self.inventory = None
        self.player_health_box = None
        self.action_selected = None
        self.select_box = None
        self.player = None
        self.damage_points = None
        self.experience_points = None

        setup.mixer().set_level_song(self.name, 'high_action')

        self.action_timer = Timer(1500)

    def startup(self):
        """
        Initialize state attributes.
        """

        game_data = setup.game_data()

        self.allow_input = False
        self.inventory = game_data['player inventory']
        self.state = 'transition in'
        print("NEXT PRE", self.next)
        self.next = game_data['last state']
        print("NEXT POST", self.next)
        self.run_away = False

        self.player = self.make_player()
        self.attack_animations = pg.sprite.Group()
        self.sword = attackitems.Sword(self.player)
        self.enemy_group, self.enemy_pos_list, self.enemy_list = (
            self.make_enemies())
        self.experience_points = self.get_experience_points()
        self.new_gold = self.get_new_gold()
        self.background = make_background()
        self.info_box = battlegui.InfoBox(self.experience_points,
                                          self.new_gold)
        self.arrow = battlegui.SelectArrow(self.enemy_pos_list,
                                           self.info_box)
        self.select_box = battlegui.SelectBox()
        self.player_health_box = battlegui.PlayerHealth(self.select_box.rect)

        self.select_action_state_dict = self.make_selection_state_dict()
        self.observers = [observer.Battle(self),
                          observer.MusicChange()]
        self.player.observers.extend(self.observers)
        self.observers.append(observer.SoundEffects())
        self.damage_points = pg.sprite.Group()
        self.player_actions = []
        self.player_action_dict = self.make_player_action_dict()
        self.player_level = game_data['player stats']['Level']
        self.enemies_to_attack = []
        self.action_selected = False
        #self.transition_rect = setup.screen().get_rect()
        #self.transition_alpha = 255
        self.temp_magic = game_data['player stats']['magic']['current']

    def make_player_action_dict(self):
        """
        Make the dict to execute player actions.
        """
        action_dict = {
            c.PLAYER_ATTACK: self.player_attack,
            c.CURE_SPELL: self.cast_cure,
            c.FIRE_SPELL: self.cast_fire_blast,
            c.DRINK_HEALING_POTION: self.drink_healing_potion,
            c.DRINK_ETHER_POTION: self.drink_ether_potion}

        return action_dict

    def get_experience_points(self):
        """
        Calculate experience points based on number of enemies
        and their levels.
        """
        experience_total = sum([random.randint(5, 10)
                                for enemy
                                in self.enemy_list])

        #experience_total = 60

        return experience_total

    def get_new_gold(self):
        """
        Calculate the gold collected at the end of the battle.
        """
        gold = 0

        for enemy in self.enemy_list:
            max_gold = enemy.level * 20
            gold += (random.randint(1, max_gold))

        return gold

    def make_enemies(self):
        """
        Make the enemies for the battle. Return sprite group.
        """
        pos_list = []
        game_data = setup.game_data()

        for column in range(3):
            for row in range(3):
                pos_x = (column * 100) + 100
                pos_y = (row * 100) + 100
                pos_list.append([pos_x, pos_y])

        enemy_group = pg.sprite.Group()

        if game_data['battle type']:
            enemy = person.Enemy('evilwizard', (0, 0),
                                 'battle resting')
            enemy_group.add(enemy)
        else:
            if game_data['start of game']:
                for enemy in range(3):
                    enemy_group.add(person.Enemy('devil', (0, 0),
                                                 'battle resting'))
                game_data['start of game'] = False
            else:
                for enemy in range(random.randint(1, 2)):
                    enemy_group.add(person.Enemy('devil', (0, 0),
                                                 'battle resting'))

        for i, enemy in enumerate(enemy_group):
            enemy.rect.topleft = pos_list[i]
            enemy.image = pg.transform.scale2x(enemy.image)
            enemy.index = i
            enemy.level = make_enemy_level_dict()[self.previous]
            if enemy.name == 'evilwizard':
                enemy.health = 100
            else:
                enemy.health = enemy.level * 4

        enemy_list = [enemy for enemy in enemy_group]

        return enemy_group, pos_list[0:len(enemy_group)], enemy_list

    def make_player(self):
        """
        Make the sprite for the player's character.
        """
        player = person.Player((630, 220), 1)
        player.image = pg.transform.scale2x(player.image)
        return player

    def make_selection_state_dict(self):
        """
        Make a dictionary of states with arrow coordinates as keys.
        """

        # can't just get '.pos_list' from the SelectArrow object because
        # it jumps between menu and enemies; maybe can be synced, maybe
        # should be rewritten with different pos_lists for each context
        from ..battlegui import make_select_action_pos_list

        pos_list = make_select_action_pos_list()
        state_list = [
            self.enter_select_enemy_state, self.enter_select_item_state,
            self.enter_select_magic_state, self.try_to_run_away]
        return dict(zip(pos_list, state_list))

    def update(self):
        """
        Update the battle state.
        """
        self.check_input()
        self.check_timed_events()
        self.check_if_battle_won()
        self.enemy_group.update()
        self.player.update()
        self.attack_animations.update()
        self.info_box.update()
        self.arrow.update()
        self.sword.update()
        self.damage_points.update()
        self.execute_player_actions()

        self.draw_battle()

    def check_input(self):
        """
        Check user input to navigate GUI.
        """

        keys = setup.keys()
        game_data = setup.game_data()

        if not self.allow_input:
            if keys[pg.K_RETURN] == False and keys[pg.K_SPACE] == False:
                self.allow_input = True
            return

        if not keys[pg.K_SPACE]:
            return

        inventory = game_data['player inventory']

        print(self.state)

        if self.state == c.SELECT_ACTION:
            self.notify(c.CLICK2)
            self.select_action_state_dict[self.arrow.rect.topleft]()

        elif self.state == c.SELECT_ENEMY:
            self.notify(c.CLICK2)
            self.player_actions.append(c.PLAYER_ATTACK)
            self.enemies_to_attack.append(self.get_enemy_to_attack())
            self.action_selected = True

        elif self.state == c.SELECT_ITEM:
            selected = self.info_box.item_text_list[self.arrow.index]
            self.notify(c.CLICK2)
            if self.arrow.index == (len(self.arrow.pos_list) - 1):
                self.enter_select_action_state()
            elif selected.startswith('Healing Potion'):
                if 'Healing Potion' in game_data['player inventory']:
                    self.player_actions.append(c.DRINK_HEALING_POTION)
                    self.action_selected = True
            elif selected.startswith('Ether'):
                if 'Ether Potion' in game_data['player inventory']:
                    self.player_actions.append(c.DRINK_ETHER_POTION)
                    self.action_selected = True

        elif self.state == c.SELECT_MAGIC:
            selected = self.info_box.magic_text_list[self.arrow.index]
            self.notify(c.CLICK2)
            if self.arrow.index == (len(self.arrow.pos_list) - 1):
                self.enter_select_action_state()
            elif selected == 'Cure':
                magic_points = inventory['Cure']['magic points']
                if self.temp_magic >= magic_points:
                    self.temp_magic -= magic_points
                    self.player_actions.append(c.CURE_SPELL)
                    self.action_selected = True
            elif selected == 'Fire Blast':
                magic_points = inventory['Fire Blast']['magic points']
                if self.temp_magic >= magic_points:
                    self.temp_magic -= magic_points
                    self.player_actions.append(c.FIRE_SPELL)
                    self.action_selected = True

        self.allow_input = False

    def check_timed_events(self):
        """
        Check if amount of time has passed for timed events.
        """

        game_data = setup.game_data()

        timed_states = [c.PLAYER_DAMAGED,
                        c.ENEMY_DAMAGED,
                        c.ENEMY_DEAD,
                        c.DRINK_HEALING_POTION,
                        c.DRINK_ETHER_POTION]
        long_delay = timed_states[1:]

        if self.state in long_delay:
            if self.action_timer.done(1000):
                if self.state == c.ENEMY_DAMAGED:
                    if self.player_actions:
                        self.player_action_dict[self.player_actions[0]]()
                        self.player_actions.pop(0)
                    else:
                        if len(self.enemy_list):
                            self.enter_enemy_attack_state()
                        else:
                            self.enter_battle_won_state()
                elif (self.state == c.DRINK_HEALING_POTION or
                      self.state == c.CURE_SPELL or
                      self.state == c.DRINK_ETHER_POTION):
                    if self.player_actions:
                        self.player_action_dict[self.player_actions[0]]()
                        self.player_actions.pop(0)
                    else:
                        if len(self.enemy_list):
                            self.enter_enemy_attack_state()
                        else:
                            self.enter_battle_won_state()
                self.action_timer.reset()

        elif self.state == c.FIRE_SPELL or self.state == c.CURE_SPELL:
            if self.action_timer.done():
                if self.player_actions:
                    if not len(self.enemy_list):
                        self.enter_battle_won_state()
                    else:
                        self.player_action_dict[self.player_actions[0]]()
                        self.player_actions.pop(0)
                else:
                    if len(self.enemy_list):
                        self.enter_enemy_attack_state()
                    else:
                        self.enter_battle_won_state()
                self.action_timer.reset()

        elif self.state == c.RUN_AWAY:
            if self.action_timer.done():
                self.end_battle()

        elif self.state == c.BATTLE_WON:
            if self.action_timer.done(1800):
                self.enter_show_gold_state()

        elif self.state == c.SHOW_GOLD:
            if self.action_timer.done(1900):
                self.enter_show_experience_state()

        elif self.state == c.LEVEL_UP:
            if self.action_timer.done(2000):
                if game_data['player stats']['Level'] == 3:
                    self.msg_two_actions()
                else:
                    self.end_battle()

        elif self.state == c.TWO_ACTIONS:
            if self.action_timer.done(2100):
                self.end_battle()

        elif self.state == c.SHOW_EXPERIENCE:
            if self.action_timer.done(2200):
                player_stats = game_data['player stats']
                player_stats['experience to next level'] -= (
                    self.experience_points)
                if player_stats['experience to next level'] <= 0:
                    extra_experience = player_stats[
                        'experience to next level'] * -1
                    player_stats['Level'] += 1
                    player_stats['health']['maximum'] += (
                        int(player_stats['health']['maximum']*.25))
                    player_stats['magic']['maximum'] += (
                        int(player_stats['magic']['maximum']*.20))
                    new_experience = int((player_stats['Level'] * 50) * .75)
                    player_stats['experience to next level'] = (
                        new_experience - extra_experience)
                    self.enter_level_up_state()
                else:
                    self.end_battle()

        elif self.state == c.PLAYER_DAMAGED:
            if self.action_timer.done(600):
                if self.enemy_index == (len(self.enemy_list) - 1):
                    if self.run_away:
                        self.enter_run_away_state()
                    else:
                        self.enter_select_action_state()
                else:
                    self.switch_enemy()
                self.action_timer.reset()

    def check_if_battle_won(self):
        """
        Check if state is SELECT_ACTION and there are no enemies left.
        """
        if self.state == c.SELECT_ACTION:
            if len(self.enemy_group) == 0:
                self.enter_battle_won_state()

    def notify(self, event):
        """
        Notify observer of event.
        """
        for new_observer in self.observers:
            new_observer.on_notify(event)

    def end_battle(self):
        """
        End battle and flip back to previous state.
        """

        game_data = setup.game_data()

        if game_data['battle type'] == 'evilwizard':
            # update music theme for main town here?
            game_data['crown quest'] = True
            game_data['talked to king'] = True
        print("END PRE", game_data['last state'])
        game_data['last state'] = self.name
        print("END POST", game_data['last state'])
        game_data['battle counter'] = random.randint(50, 255)
        game_data['battle type'] = None
        self.state = 'transition out'

    def attack_enemy(self, enemy_damage):
        enemy = self.player.attacked_enemy
        enemy.health -= enemy_damage
        self.set_enemy_indices()

        if enemy:
            enemy.enter_knock_back_state()
            if enemy.health <= 0:
                self.enemy_list.pop(enemy.index)
                enemy.cue_death()
                self.arrow.remove_pos(self.player.attacked_enemy)
            self.enemy_index = 0

    def set_enemy_indices(self):
        for i, enemy in enumerate(self.enemy_list):
            enemy.index = i

    def draw_battle(self):
        """Draw all elements of battle state"""

        surface = setup.screen()

        self.background.draw(surface)
        self.enemy_group.draw(surface)
        self.attack_animations.draw(surface)
        self.sword.draw()
        surface.blit(self.player.image, self.player.rect)
        surface.blit(self.info_box.image, self.info_box.rect)
        surface.blit(self.select_box.image, self.select_box.rect)
        surface.blit(self.arrow.image, self.arrow.rect)
        self.player_health_box.draw()
        self.damage_points.draw(surface)
        self.draw_transition()

    def draw_transition(self):
        """
        Fade in and out of state.
        """
        if self.state == 'transition in':

            self.state = c.SELECT_ACTION

            #transition_image = pg.Surface(self.transition_rect.size)
            #transition_image.fill(c.TRANSITION_COLOR)
            #transition_image.set_alpha(self.transition_alpha)
            #surface.blit(transition_image, self.transition_rect)
            #self.transition_alpha -= c.TRANSITION_SPEED
            #if self.transition_alpha <= 0:
            #    self.state = c.SELECT_ACTION
            #    self.transition_alpha = 0

        elif self.state == 'transition out':
            self.done = True
            #transition_image = pg.Surface(self.transition_rect.size)
            #transition_image.fill(c.TRANSITION_COLOR)
            #transition_image.set_alpha(self.transition_alpha)
            #surface.blit(transition_image, self.transition_rect)
            #self.transition_alpha += c.TRANSITION_SPEED
            #if self.transition_alpha >= 255:
            #    self.done = True

        elif self.state == c.DEATH_FADE:
            self.done = True
            #transition_image = pg.Surface(self.transition_rect.size)
            #transition_image.fill(c.TRANSITION_COLOR)
            #transition_image.set_alpha(self.transition_alpha)
            #surface.blit(transition_image, self.transition_rect)
            #self.transition_alpha += c.DEATH_TRANSITION_SPEED
            #if self.transition_alpha >= 255:
            #    self.done = True
            #    self.next = c.DEATH_SCENE

    def player_damaged(self, damage):

        game_data = setup.game_data()

        game_data['player stats']['health']['current'] -= damage
        if game_data['player stats']['health']['current'] <= 0:
            game_data['player stats']['health']['current'] = 0
            self.state = c.DEATH_FADE

    def player_healed(self, heal, magic_points=0):
        """
        Add health from potion to game data.
        """

        game_data = setup.game_data()

        health = game_data['player stats']['health']

        health['current'] += heal

        if health['current'] > health['maximum']:
            health['current'] = health['maximum']

        if self.state == c.DRINK_HEALING_POTION:
            game_data[
                'player inventory'][
                    'Healing Potion'][
                        'quantity'] -= 1
            if game_data[
                    'player inventory'][
                        'Healing Potion'][
                            'quantity'] == 0:
                del game_data['player inventory']['Healing Potion']

        elif self.state == c.CURE_SPELL:
            game_data['player stats']['magic']['current'] -= magic_points

    def magic_boost(self, magic_points):
        """
        Add magic from ether to game data.
        """

        game_data = setup.game_data()

        magic = game_data['player stats']['magic']
        magic['current'] += magic_points
        self.temp_magic += magic_points
        if magic['current'] > magic['maximum']:
            magic['current'] = magic['maximum']

        game_data['player inventory']['Ether Potion']['quantity'] -= 1
        if not game_data['player inventory']['Ether Potion']['quantity']:
            del game_data['player inventory']['Ether Potion']

    def cast_fire_blast(self):
        """
        Cast fire blast on all enemies.
        """

        game_data = setup.game_data()

        self.notify(c.FIRE)
        self.state = self.info_box.state = c.FIRE_SPELL
        power = self.inventory['Fire Blast']['power']
        magic_points = self.inventory['Fire Blast']['magic points']
        game_data['player stats']['magic']['current'] -= magic_points
        for enemy in self.enemy_list:
            damage = random.randint(power//2, power)
            self.damage_points.add(
                attackitems.HealthPoints(damage, enemy.rect.topright))
            enemy.health -= damage
            posx = enemy.rect.x - 32
            posy = enemy.rect.y - 64
            fire_sprite = attack.Fire(posx, posy)
            self.attack_animations.add(fire_sprite)
            if enemy.health <= 0:
                enemy.kill()
                self.arrow.remove_pos(enemy)
            else:
                enemy.enter_knock_back_state()
        self.enemy_list = [
            enemy for enemy in self.enemy_list if enemy.health > 0]
        self.enemy_index = 0
        self.arrow.index = 0
        self.arrow.state = 'invisible'
        self.action_timer.reset()

    def cast_cure(self):
        """
        Cast cure spell on player.
        """
        self.state = c.CURE_SPELL
        heal_amount = self.inventory['Cure']['power']
        magic_points = self.inventory['Cure']['magic points']
        self.player.healing = True
        self.action_timer.reset()
        self.arrow.state = 'invisible'
        self.enemy_index = 0
        self.damage_points.add(
            attackitems.HealthPoints(
                heal_amount, self.player.rect.topright, False))
        self.player_healed(heal_amount, magic_points)
        self.info_box.state = c.DRINK_HEALING_POTION
        self.notify(c.POWERUP)

    def enter_select_enemy_state(self):
        """
        Transition battle into the select enemy state.
        """
        self.state = self.arrow.state = c.SELECT_ENEMY
        self.arrow.index = 0

    def enter_select_item_state(self):
        """
        Transition battle into the select item state.
        """
        self.state = self.info_box.state = c.SELECT_ITEM
        self.arrow.become_select_item_state()

    def enter_select_magic_state(self):
        """
        Transition battle into the select magic state.
        """
        self.state = self.info_box.state = c.SELECT_MAGIC
        self.arrow.become_select_magic_state()

    def try_to_run_away(self):
        """
        Transition battle into the run away state.
        """
        self.run_away = True
        self.arrow.state = 'invisible'
        self.enemy_index = 0
        self.enter_enemy_attack_state()

    def enter_enemy_attack_state(self):
        """
        Transition battle into the Enemy attack state.
        """
        self.state = self.info_box.state = c.ENEMY_ATTACK
        enemy = self.enemy_list[self.enemy_index]
        enemy.enter_enemy_attack_state()

    def player_attack(self):
        """
        Transition battle into the Player attack state.
        """
        self.state = self.info_box.state = c.PLAYER_ATTACK
        enemy_to_attack = self.enemies_to_attack.pop(0)
        if enemy_to_attack in self.enemy_list:
            self.player.enter_attack_state(enemy_to_attack)
        else:
            if self.enemy_list:
                self.player.enter_attack_state(self.enemy_list[0])
            else:
                self.enter_battle_won_state()
        self.arrow.state = 'invisible'

    def get_enemy_to_attack(self):
        """
        Get enemy for player to attack by arrow position.
        """
        enemy_posx = self.arrow.rect.x + 60
        enemy_posy = self.arrow.rect.y - 20
        enemy_pos = (enemy_posx, enemy_posy)
        enemy_to_attack = None

        for enemy in self.enemy_list:
            if enemy.rect.topleft == enemy_pos:
                enemy_to_attack = enemy

        return enemy_to_attack


    def drink_healing_potion(self):
        """
        Transition battle into the Drink Healing Potion state.
        """
        self.state = self.info_box.state = c.DRINK_HEALING_POTION
        self.player.healing = True
        self.action_timer.reset()
        self.arrow.state = 'invisible'
        self.enemy_index = 0
        self.damage_points.add(
            attackitems.HealthPoints(30,
                                     self.player.rect.topright,
                                     False))
        self.player_healed(30)
        self.notify(c.POWERUP)

    def drink_ether_potion(self):
        """
        Transition battle into the Drink Ether Potion state.
        """
        self.state = self.info_box.state = c.DRINK_ETHER_POTION
        self.player.healing = True
        self.arrow.state = 'invisible'
        self.enemy_index = 0
        self.damage_points.add(
            attackitems.HealthPoints(30,
                                     self.player.rect.topright,
                                     False,
                                     True))
        self.magic_boost(30)
        self.action_timer.reset()
        self.notify(c.POWERUP)

    def enter_select_action_state(self):
        """
        Transition battle into the select action state
        """
        self.state = self.info_box.state = c.SELECT_ACTION
        self.arrow.index = 0
        self.arrow.state = self.state

    def enter_player_damaged_state(self):
        """
        Transition battle into the player damaged state.
        """
        self.state = self.info_box.state = c.PLAYER_DAMAGED
        if self.enemy_index > len(self.enemy_list) - 1:
            self.enemy_index = 0
        enemy = self.enemy_list[self.enemy_index]
        player_damage = enemy.calculate_hit(self.inventory['equipped armor'],
                                            self.inventory)
        self.damage_points.add(
            attackitems.HealthPoints(player_damage,
                                     self.player.rect.topright))
        self.info_box.set_player_damage(player_damage)
        self.action_timer.reset()
        self.player_damaged(player_damage)
        if player_damage:
            sfx_num = random.randint(1, 3)
            self.notify('punch{}'.format(sfx_num))
            self.player.damaged = True
            self.player.enter_knock_back_state()
        else:
            self.notify(c.MISS)

    def enter_enemy_damaged_state(self):
        """
        Transition battle into the enemy damaged state.
        """
        self.state = self.info_box.state = c.ENEMY_DAMAGED
        enemy_damage = self.player.calculate_hit()
        self.damage_points.add(
            attackitems.HealthPoints(enemy_damage,
                                     self.player.attacked_enemy.rect.topright))

        self.info_box.set_enemy_damage(enemy_damage)

        self.arrow.index = 0
        self.attack_enemy(enemy_damage)
        self.action_timer.reset()

    def switch_enemy(self):
        """
        Switch which enemy the player is attacking.
        """
        if self.enemy_index < len(self.enemy_list) - 1:
            self.enemy_index += 1
            self.enter_enemy_attack_state()

    def enter_run_away_state(self):
        """
        Transition battle into the run away state.
        """
        self.state = self.info_box.state = c.RUN_AWAY
        self.arrow.state = 'invisible'
        self.player.state = c.RUN_AWAY
        self.action_timer.reset()
        self.notify(c.RUN_AWAY)

    def enter_battle_won_state(self):
        """
        Transition battle into the battle won state.
        """
        self.notify(c.BATTLE_WON)
        self.state = self.info_box.state = c.BATTLE_WON
        self.player.state = c.VICTORY_DANCE
        self.action_timer.reset()

    def enter_show_gold_state(self):
        """
        Transition battle into the show gold state.
        """
        self.inventory['GOLD']['quantity'] += self.new_gold
        self.state = self.info_box.state = c.SHOW_GOLD
        self.action_timer.reset()

    def enter_show_experience_state(self):
        """
        Transition battle into the show experience state.
        """
        self.state = self.info_box.state = c.SHOW_EXPERIENCE
        self.action_timer.reset()

    def enter_level_up_state(self):
        """
        Transition battle into the LEVEL UP state.
        """
        self.state = self.info_box.state = c.LEVEL_UP
        self.info_box.reset_level_up_message()
        self.action_timer.reset()

    def msg_two_actions(self):
        self.state = self.info_box.state = c.TWO_ACTIONS
        self.action_timer.reset()

    def execute_player_actions(self):
        """
        Execute the player actions.
        """
        if self.player_level < 3:
            if self.player_actions:
                self.player_action_dict[self.player_actions[0]]()
                self.player_actions.pop(0)
        else:
            if len(self.player_actions) == 2:
                self.player_action_dict[self.player_actions[0]]()
                self.player_actions.pop(0)
                self.action_selected = False
            else:
                if self.action_selected:
                    self.enter_select_action_state()
                    self.action_selected = False

def make_enemy_level_dict():
    """
    Hard coded map filler

    Was method of Battle; uses no 'self'

    """

    new_dict = {c.OVERWORLD: 1,
                c.DUNGEON: 2,
                c.DUNGEON2: 2,
                c.DUNGEON3: 2,
                c.DUNGEON4: 2,
                c.DUNGEON5: 4}

    return new_dict

def make_background():
    """
    Make the blue/black background.

    Was method of Battle; uses no 'self'

    """

    background = empty_background()

    background_group = pg.sprite.Group(background)

    return background_group

