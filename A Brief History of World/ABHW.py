import os
from random import *

FIRST_EVENT = 1
LAST_EVENT = 128
MAX_PRECONDITION = 3
EVENT_CARD_NUMBER = (LAST_EVENT - FIRST_EVENT) + 1
FIRST_DESTINY = 1
LAST_DESTINY = 20
DESTINY_CARD_NUMBER = (LAST_DESTINY - FIRST_DESTINY) + 1
MAX_PLAYERS = 6
MIN_PLAYERS = 2
NAMES = ["Meteor", "Jungle", "Seed", "Dukeduck", "HawkY", "Gregory"]
INIT_EVENTS_NUMBER = 6
INIT_EVENTS_DECK = 9
INIT_DESTINY_DRAW = 4
INIT_DESTINY_DISCARD = 1
EVENT_HAND_LIMIT = 12
ACTION_DEVELOP_HISTORY = 0
ACTION_DRAW_DECK = 1
ACTION_DRAW_DISCARD = 2
ACTION_CHANGE_HISTORY = 3
CHANGE_HISTORY_LIMIT = 6
STRATEGY_NORMAL = 0 # normal strategy
STRATEGY_RANDOM = 1 # random play

events = []
destinys = []

def swap(a, i, j):
    temp = a[i]
    a[i] = a[j]
    a[j] = temp

class eventCard:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.condition_ids = [] # an array with max MAX_PRECONDITION elements
        self.start_age = FIRST_EVENT  # = FIRST_EVENT if <= specHistory
        self.end_age = LAST_EVENT  # = LAST_EVENT if >= specHistory
        self.can_be_played = True

    def add_condition(self, condition_id):
        self.condition_ids.append(condition_id)

    def change_start(self, new_start):
        self.start_age = new_start

    def change_end(self, new_end):
        self.end_age = new_end

    def check_play(self, play_status):
        self.can_be_played = play_status

class destinyCard:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.trigger_event = FIRST_EVENT # Trigger Event ID
        self.score_event = []
        self.event_score = []

    def set_trigger(self, trigger_id):
        self.trigger_event = trigger_id

    def add_score_event(self, event_id, score):
        self.score_event.append(event_id)
        self.event_score.append(score)

class player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.hand_events = [] # Current hand like [eventCard[0],...] etc
        self.hand_destinys = [] # [destinyCard[1],...] etc
        self.strategy = STRATEGY_NORMAL
        self.current_score = 0
        self.events_played = [] # Player's played event
        self.destinys_played = []   # Player's played destiny
        self.change_history_count = 0   # Ability used times.

    def record_event_play(self, event_id):
        self.events_played.append(event_id)

    def record_destiny_play(self, destiny_id):
        self.destinys_played.append(destiny_id)

    def sort_hands(self):
        for i in range(len(self.hand_events)):  # Sort Events in time line.
            for j in range(i):
                if self.hand_events[i].id < self.hand_events[j].id:
                    swap(self.hand_events, i, j)

    def add_hand_events(self, draw_events):
        for d_e in draw_events:
            self.hand_events.append(d_e)

    def add_hand_destinys(self, draw_destinys):
        for d_d in draw_destinys:
            self.hand_destinys.append(d_d)

    def discard_hand_events(self, discard_events):
        for d_e in discard_events:
            if d_e not in self.hand_events: # Something wrong
                print("Discard Events Failure!")
            else:
                discard_index = self.hand_events.index(d_e)
                discard_info = self.name + "弃掉了" + str(self.hand_events[discard_index].id) + "号事件卡： " \
                               + self.hand_events[discard_index].name
                self.hand_events.pop(discard_index)
                #print(discard_info)

        self.sort_hands()

    def discard_hand_destinys(self, discard_destinys):
        for d_d in discard_destinys:
            if d_d not in self.hand_destinys: # Something wrong
                print("Discard Destinys Failure!")
            else:
                discard_index = self.hand_destinys.index(d_d)
                discard_info = self.name + "弃掉了归宿卡： " + self.hand_destinys[discard_index].name
                self.hand_destinys.pop(discard_index)
                print(discard_info)

def read_events():  # exception work may needed
    file = open("/Users/meteor/Documents/Game Design/__Old Works__/A Brief History of World/events.txt")
    for line in file:
        line = line.strip("\n")
        elements = line.split(" ")
        id = int(elements[0])
        # print(id, len(elements))
        name = elements[1]
        event_in_line = eventCard(id, name)
        pre_condition = elements[2]
        if pre_condition != "-1":
            pcs = pre_condition.split(",")
            for pc in pcs:
                event_in_line.add_condition(int(pc))
        event_in_line.change_start(int(elements[3]))
        event_in_line.change_end(int(elements[4]))
        events.append(event_in_line)
    return events

def read_destiny():
    file = open("/Users/meteor/Documents/Game Design/__Old Works__/A Brief History of World/destiny.txt")
    for line in file:
        line = line.strip("\n")
        elements = line.split(" ")
        id = int(elements[0])
        name = elements[1]
        destiny_in_line = destinyCard(id, name)
        trigger_id = int(elements[2])
        destiny_in_line.set_trigger(trigger_id)
        event_score = elements[3: len(elements)]
        for es in event_score:
            event = int(es.split(",")[0])
            score = int(es.split(",")[1])
            destiny_in_line.add_score_event(event, score)
        destinys.append(destiny_in_line)
    return destinys

def drawCard(deck, draw_number): # deck is an array of cards [1,3,...10,...128] while draw_number <= len(deck)
    draw_cards = [] # cards would be drawn
    draw_count = 0
    while (draw_count < draw_number):
        if (len(deck) >= 1):
            draw_index = randint(0, len(deck)-1)
        else:
            break
        draw_card = deck.pop(draw_index)
        draw_cards.append(draw_card)
        draw_count += 1
    return draw_cards, deck

def init_world():   # Choose 6 cards from Event[1...9] to create World's init events.
    e = read_events()   # read all event cards from file.
    init_deck = e[0:INIT_EVENTS_DECK]
    init_draw = drawCard(init_deck, INIT_EVENTS_NUMBER)
    init_events = init_draw[0]
    events_unhappen = init_draw[1]

    for i in range(len(init_events)):   # Sort Init Events in time line.
        for j in range(i):
            if init_events[i].id < init_events[j].id:
                swap(init_events, i, j)

    for i in range(len(events_unhappen)):   # Sort Unused Events in time line.
        for j in range(i):
            if events_unhappen[i].id < events_unhappen[j].id:
                swap(events_unhappen, i, j)

    deck_remain = events_unhappen + e[INIT_EVENTS_DECK:]    # Add back unused events.

    return init_events, deck_remain

def deal_init_hands(players, event_deck):   # Deal 12 cards to each players
    player_number = len(players)
    current_deck = event_deck
    if (player_number * EVENT_HAND_LIMIT <= len(event_deck)): # Each player could have 12 initial events
        for p in players:
            p_events_draw = drawCard(current_deck, EVENT_HAND_LIMIT)
            p_hand_events = p_events_draw[0]
            current_deck = p_events_draw[1]
            p.add_hand_events(p_hand_events)
            p.sort_hands()
    else:
        print ("手牌分发失败！")

    return players, current_deck

def calc_destiny_value(destiny, init_events, hand_events): # Calc a destiny's value, trigger event for 10, score event
    # *2 if in hand, *1 if in init.
    score = 0
    s_e_pair = []
    hand_ids = []
    init_ids = []

    for i_e in init_events:
        init_ids.append(i_e.id)

    for h_e in hand_events:
        hand_ids.append(h_e.id)

    t_e = destiny.trigger_event
    for i in range(len(destiny.score_event)):
        s_e_pair.append([destiny.score_event[i], destiny.event_score[i]])

    if t_e in hand_ids:
        score += (max(destiny.event_score) + 1) * 2 # suppose = 10
    elif t_e in init_ids:
        score += (max(destiny.event_score) + 1)

    for i in range(len(s_e_pair)):
        if s_e_pair[i][0] in hand_ids:
            score += s_e_pair[i][1] * 2
        elif s_e_pair[i][0] in init_ids:
            score += s_e_pair[i][1]

    return score

def calc_destiny_progress(destiny, spec_player, current_timeline):    # Calc a destiny card's progress. trigger_card
    # count as 50, while event_score count as score * 5, double if played by spec_player
    progress = 0
    timeline_id = []

    for c_t in current_timeline:
        timeline_id.append(c_t.id)

    if destiny.trigger_event in timeline_id:
        progress += 50

    for d_s in destiny.score_event:
        if d_s in timeline_id:
            if d_s in spec_player.events_played:    # So events_played need to be an integer id array.
                progress += destiny.event_score[destiny.score_event.index(d_s)] * 10
            else:
                progress += destiny.event_score[destiny.score_event.index(d_s)] * 5

    return progress

def calc_event_value(event, spec_player, current_timeline): # Calc a card's value for a player within current situation.
    current_time = current_timeline[len(current_timeline) - 1].id
    value = (LAST_EVENT/4 - abs(event.id - current_time)) / 10    # Alogrithm like change history cost, needs update

    destinys_in_hand = spec_player.hand_destinys

    for d_i_h in destinys_in_hand:
        if event.id == d_i_h.trigger_event:    # trigger event, value += progress
            value += calc_destiny_progress(d_i_h, spec_player, current_timeline)

        elif event.id in d_i_h.score_event:    # score event, value += progress * score
            value += calc_destiny_progress(d_i_h, spec_player, current_timeline) * d_i_h.event_score[d_i_h.score_event.index
            (event.id)]

    return value # To be modifed.

def discard_destiny(spec_player, init_events): # Player choose how to discard 1 destiny according to his hands.
    destiny_on_hand = spec_player.hand_destinys
    events_on_hand = spec_player.hand_events
    destiny_discard = []
    destiny_scores = []

    if len(destiny_on_hand) < INIT_DESTINY_DRAW: # no discard needed.
        return destiny_discard  # return [] if no discard
    else:
        for d_hand in destiny_on_hand:
            d_score = calc_destiny_value(d_hand, init_events, events_on_hand)
            destiny_scores.append(d_score)

    for i in range(INIT_DESTINY_DISCARD):   # maybe more than one time.
        score_min_index = destiny_scores.index(min(destiny_scores))
        destiny_discard.append(destiny_on_hand[score_min_index])
        destiny_scores.pop(score_min_index)

    return destiny_discard

def check_playable(event, current_timeline): # Check whether an event card is playable
    playable = False
    current_event = current_timeline[len(current_timeline) - 1] # Current Event
    timeline_ids = []
    for c_t in current_timeline:
        timeline_ids.append(c_t.id)

    if (event.start_age <= current_event.id <= event.end_age) & (event.id > current_event.id):
        if len(event.condition_ids) == 0:
            playable = True
        else:
            for condition in event.condition_ids:
                if condition in timeline_ids:
                    playable = True

    return playable

def calc_change_history_discard(spec_event, spec_player, current_timeiine): # Return Change HIstory Hand Cost defined by
    # game rules.
    discard_number = 0
    discard_number += spec_player.change_history_count
    lastest_age = current_timeiine[len(current_timeiine) - 1].id
    event_age = spec_event.id

    if check_playable(spec_event, current_timeiine) == True:    # Could be played.
        discard_number += 0
    elif (lastest_age - event_age) % 10 == 0:
        discard_number += int((lastest_age - event_age) / 10)
    else:
        discard_number += int((lastest_age - event_age) / 10) + 1

    return discard_number

def calc_change_history_cost(spec_event, spec_player, current_timeline): # First calc change history hand cost, 1) if more
    # than player's hands, return like MAX_ERROR. 2) If not, Calc cost cards within game rules. 3) Calc event_value, event
    # within high values will be considered cost less.
    expectation_cost = 65535 # Hey buddy, don't ask me why the magic number would be this.

    hand_discard = calc_change_history_discard(spec_event, spec_player, current_timeline)
    hands_event = len(spec_player.hand_events)

    if (hand_discard > hands_event) or (spec_event not in spec_player.hand_events) or (spec_event.id >=
    current_timeline[len(current_timeline) - 1].id):  # case #1
        return expectation_cost
    else:
        event_value = calc_event_value(spec_event, spec_player, current_timeline)
        expectation_cost = hand_discard - event_value / 10
        if expectation_cost <= 0:
            expectation_cost = 1
        return expectation_cost

def choose_discard_events():
    pass

def choose_action(spec_player, current_timeline): # Normal Strategy v0.5: 1) Play a card if possible, if there's more than
    # one card can be played, calc their value and play the biggest. 2) If can't play a card. calc change history cost,
    # if cost is acceptable, choose change history. 3) Calc Discard pile, if key card is in, choose draw discard
    # 4) Choose draw 2 cards.
    player_hand_events = spec_player.hand_events
    events_can_be_played = []
    events_value = []
    events_discard_cost = []

    if spec_player.strategy == STRATEGY_NORMAL:
        cost_expecation = len(spec_player.hand_events) / 2
    else:
        cost_expecation = 100   # To be upated.

    for p_h_e in player_hand_events:
        phe_playable = check_playable(p_h_e, current_timeline)
        #events_discard_cost.append(calc_change_history_cost(p_h_e, spec_player, current_timeline))
        if phe_playable == True:
            events_can_be_played.append(p_h_e)

    if len(events_can_be_played) > 0: # there's card can be played.
        for e_c_be in events_can_be_played:
            events_value.append(calc_event_value(e_c_be, spec_player, current_timeline))
        events_play = events_can_be_played[events_value.index(max(events_value))]
        return ACTION_DEVELOP_HISTORY, events_play
    else:
        for p_h_e in player_hand_events:
            current_discard_cost = calc_change_history_cost(p_h_e, spec_player, current_timeline)
            if current_discard_cost <= cost_expecation: # Acceptable.
                events_discard_cost.append([p_h_e, current_discard_cost])
        if len(events_discard_cost) > 0: # Action could be choose
            temp_events_cost = []
            for e_d_c in events_discard_cost:
                temp_events_cost.append(e_d_c[1])
            event_change_history = events_discard_cost[temp_events_cost.index(min(temp_events_cost))][0]  # OMG so ugly
            return ACTION_CHANGE_HISTORY, event_change_history   # Needed update.
        return ACTION_DRAW_DECK, [] # this situation #2 parameter won't work.

def deal_destiny(players): # Simplerify this function to let players randomly draw 4 destiny cards.
    # Players like [player1, ... playern]
    d = read_destiny()
    player_number = len(players)
    if (player_number * INIT_DESTINY_DRAW) <= DESTINY_CARD_NUMBER: # Each players could have 4 cards
        deal_number = INIT_DESTINY_DRAW
    elif (DESTINY_CARD_NUMBER / player_number) >= 1: # Each players could have 1 card at least
        deal_number = int(DESTINY_CARD_NUMBER / player_number)
    else:
        deal_number = 1

    for p in players:
        p_draw = drawCard(d, deal_number)
        p_destiny = p_draw[0]
        d = p_draw[1]
        p.add_hand_destinys(p_destiny)

    return players

def choose_first_player(players): # compare max number of player's events, biggest become first player
    player_mapping = [[], []]
    for p in players:
        p.sort_hands()
        p_max = p.hand_events[len(p.hand_events)-1].id # return max number?
        player_mapping[0].append(p)
        player_mapping[1].append(p_max)

    player_max = max(player_mapping[1])
    first_player_index = player_mapping[1].index(player_max)
    first_player = player_mapping[0][first_player_index]

    new_player = []
    for i in range(len(player_mapping[0])):
        if first_player_index + i >= (len(player_mapping[0])):
            new_player.append(player_mapping[0][first_player_index + i - len(player_mapping[0])])
        else:
            new_player.append(player_mapping[0][first_player_index + i])

    return first_player, new_player

def init_game(): # Init game, while 1) Setting up player number 2) Setting up Init World 3) Deal Event Cards
    #  4) Deal Destiny Cards 5) Choose Destiny Cards 6) Decide Start Player
    player_number = randint(MIN_PLAYERS, MAX_PLAYERS)
    players = []
    for p_n in range(player_number):
        p = player(p_n, NAMES[p_n])
        players.append(p)

    print("世界初始化中……")   # Init World
    i_w = init_world()
    antique_history = i_w[0]
    history_deck = i_w[1]

    print("世界初始事件：\n")  # Choose Antique History Events
    for aq in antique_history:
        info = str(aq.id) + "号事件: " + aq.name
        print(info)

    print("\n事件卡分发中……") # Deal event cards to players
    events_setup = deal_init_hands(players, history_deck)
    players = events_setup[0]
    history_deck = events_setup[1]

    print("参与玩家及其初始事件卡如下：\n")
    for p in players:
        e_info = str((p.id+1)) + "号玩家：" + p.name + "初始事件卡："
        for p_h_e in p.hand_events:
            e_info += str(p_h_e.id) + "号事件: " + p_h_e.name +" "
        print(e_info)

    print("\n归宿卡分发中……") # Deal Destiny cards to players
    players = deal_destiny(players)
    print("玩家初始归宿卡如下：\n")
    for p in players:
        d_info = str((p.id+1)) + "号玩家：" + p.name + "初始归宿卡："
        for p_hd in p.hand_destinys:
            d_info += " " + str(p_hd.name) +" "
        print(d_info)

    print("\n计算玩家行动顺序中……")  # Choose first player, by max no. of event cards
    queued_players = choose_first_player(players)
    first_player = queued_players[0]
    players = queued_players[1]
    first_player_info = "先手玩家是：" + first_player.name
    sequence_info = "玩家行动顺序： "
    for player_now in players:
        sequence_info += player_now.name + " "
    print(first_player_info)
    print(sequence_info)

    print("\n玩家选择归宿卡中：") # Players discard destiny cards if needed.
    for player_now in players:
        p_discard_destiny = discard_destiny(player_now, antique_history)
        player_now.discard_hand_destinys(p_discard_destiny)

    return players, antique_history, history_deck

def game_play(players, antique_history, history_deck):

    print("\n游戏开始！")
    current_timeline = antique_history
    while (len(history_deck) > 0):  # For test.
        for player_now in players:
            player_action = choose_action(player_now, current_timeline)
            if player_action[0] == ACTION_DEVELOP_HISTORY:
                event_playing = player_action[1]
                play_info = player_now.name + "打出了：" + str(event_playing.id) +"号事件： " + event_playing.name
                print(play_info)
                current_timeline.append(event_playing)
                player_now.record_event_play(event_playing.id)
                player_now.discard_hand_events([event_playing])
                player_new = player_now
                players[players.index(player_now)] = player_new
            elif player_action[0] == ACTION_CHANGE_HISTORY:
                event_change_history = player_action[1]
                play_info = player_now.name + "试图插入：" + str(event_change_history.id) + "号事件： " + event_change_history.name
                print(play_info)
                current_timeline.append(event_change_history)
                player_now.record_event_play(event_change_history.id)
                player_now.change_history_count += 1
                player_now.discard_hand_events([event_change_history])
                # MOre Operations needed.
                events_send_to_others = [] #choose_discard_events(player_now, discard_number, current_timeline)
                while (len(events_send_to_others) > 0): # All events need to be chosen.
                    for other_player in (players - player_now):
                        event_chosen = choose_events(other_player, events_send_to_others)
                        e_c_id = events_send_to_others.index(event_chosen)
                        event_send_to_others = events_send_to_others.pop(e_c_id)
                        other_player.add_hand_events([event_chosen])

                player_new = player_now
                players[players.index(player_now)] = player_new
            else:
                play_info = player_now.name + "表示「呵呵」，然后抓了两张牌……"
                print(play_info)
                player_draw = drawCard(history_deck, 2)
                history_deck = player_draw[1]
                player_add_hand = player_draw[0]
                player_now.add_hand_events(player_add_hand)
                player_new = player_now
                players[players.index(player_now)] = player_new

if __name__ == '__main__':
    new_game = init_game()
    players = new_game[0]
    antique_history = new_game[1]
    history_deck = new_game[2]
    game_play(players, antique_history, history_deck)