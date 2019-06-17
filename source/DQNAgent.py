import random
import pickle
import numpy as np
import pandas as pd
from operator import add
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout

class DQNAgent(object):
    '''
    Based on: https://github.com/maurock/snake-ga/blob/master/DQN.py 
    '''

    def __init__(self, attitude='Normal', Regent='Default'):
        '''
        Attitude -> Normal, Peaceful, or Aggressive... defines the rewards 
        '''
        self.attitude = attitude
        self.reward = 0
        self.gamma = 0.9
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = 0.0005
        
        # different models for different decisions
        self.tax_model = self.network(N=4, K=23)
        
        self.epsilon = 0
        self.actual = []
        self.memory = {}
        self.memory['Taxes'] = []
        
    def get_state(self, step, df, action=1, ):
        '''
        In Original, returns an np.asarray of a list it looks like.
        
        How to include the entire state of a 'player'... maybe just neighbor states?
        
        Also, likely depends on the action in question.
        
        step -> which decision I am training.
                Taxes -> setting taxes
                
        df -> a row from a dataframe
        action -> which action it is (1, 2, or 3) for Actions
        '''
        if step == 'Taxes':
            state = [1*(df['Population'] == a) for a in range(9)]   # population 0-8, 9
            if df['Population'] >= 9:  # 9s the limit, 10
                state.append(1)
            else:
                state.append(0)
            if df['Loyalty'] == 'Rebellious':  # 11
                state.append(1)
            else:
                state.append(0)
            if df['Loyalty'] == 'Poor':  #12
                state.append(1)
            else:
                state.append(0)
            if df['Loyalty'] == 'Average':
                state.append(1)
            else:
                state.append(0)
            if df['Loyalty'] == 'High':  #14
                state.append(1)
            else:
                state.append(0)
            if df['Taxation'] == 'None':
                state.append(1)
            else:
                state.append(0)
            if df['Loyalty'] == 'Light':  #16
                state.append(1)
            else:
                state.append(0)
            if df['Loyalty'] == 'Moderate':
                state.append(1)
            else:
                state.append(0)
            if df['Loyalty'] == 'Severe':  #18
                state.append(1)
            else:
                state.append(0)
            if df['Type'] == 'Law':
                state.append(1)
            else:
                state.append(0)
            if df['Cost'] >= 1:  #20
                state.append(1)
            else:
                state.append(0)
            if df['Cost'] >= 2:
                state.append(1)
            else:
                state.append(0)
            if df['Cost'] >= 4:  #22
                state.append(1)
            else:
                state.append(0)
            if df['Cost'] >= 10:  #23
                state.append(1)
            else:
                state.append(0)
            
            if step == 'Action':
                '''
                is_action_1
                is_action_2
                is_action_3
                is_bonus
                i_am_evil
                i_am_good
                i_am_lawful
                i_am_chaotic
                has_provences
                has_temples
                has_law
                has_guild
                has_source
                has_temple_in_friend
                has_temple_in_enemy
                has_law_in_enemy
                has_temple_in_rando
                i_have_contested_holding
                i_have_contested_provence
                i_am_at_war
                i_have_military_units
                i_have_levees
                i_have_mercenaries
                was_victim_of_espionage
                i_have_ley_lines
                number_of_ley_networks
                capital_can_have_road
                highpop_can_have_road
                lowpop_can_have_road
                not_all_provences_connected_by_roads
                space_for_a_holding_nearby_that_i_can_make
                capital_has_castle
                highpop_has_castle
                lowpop_has_castle
                troops_garrisoned_capital
                troops_garrisoned_highpop
                troops_garrisoned_lowpop
                border_provences_no_troops
                border_provences_no_castle
                capital_no_castle
                highpop_no_castle
                lowpop_no_castle
                my_holdings_can_increase_level
                my_waterways_can_have_routes
                my_provences_can_have_routes
                i_have_10_gold_bars
                i_have_20_gold_bars
                i_have_30_gold_bars
                i_have_40_gold_bars
                i_have_50_gold_bars
                i_have_100_gold_bars
                i_have_10_rp
                i_have_20_rp
                i_have_30_rp
                i_have_40_rp
                i_have_50_rp
                i_have_100_rp
                
                no_road_on_border_with_friend
                friend_has_opened_caravans
                friend_has_opened_waterway
                friend_has_more_regency
                friend_has_more_gold
                diplomacy_friend_5_higher
                diplomacy_friend_10_higher
                arranged_trade_route_friend
                friend_max_pop_higher
                friend_alive
                
                no_road_on_border_with_rando
                arranged_trade_route_rando
                rando_has_opened_waterway
                rando_has_opened_caravans
                diplomacy_rando_0
                diplomacy_rando_plus
                rando_has_more_regency
                rando_has_more_gold
                rando_max_pop_higher
                rando_alive
                
                enemy_has_law_holding_in_my_lands
                enemy_has_temple_holding_in_my_lands
                enemy_has_source_holding_in_my_lands
                enemy_has_guild_holding_in_my_lands
                enemy_has_same_type_of_holding_as_me_somewhere_i_have_holding
                enemy_has_contested_holding
                enemy_has_contested_provence
                enemy_has_no_law_holdings_and_rebellious_or_poor_loyalty_in_a_province
                contested_all_enemy_provinces
                all_enemy_castles_0
                diplomacy_enemy_5_lower
                diplomacy_enemy_10_lower
                enemy_has_more_regency
                enemy_has_more_gold
                enemy_troops_in_domain
                enemy_troops_in_friends_domain
                enemy_has_more_troops
                enemy_alive
                
                random_event_monsters
                brigandage
                great_captain_heresy
                
                '''
        return np.asarray(state)
            
    def network(self, weights=None, N=3, K=11):
        '''
        Original had 3 outputs...
        Setting this to N outputs.
        '''
        model = Sequential()
        model.add(Dense(units=120, activation='relu', input_dim=K))
        model.add(Dropout(0.15))
        model.add(Dense(units=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(units=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(units=N, activation='softmax'))
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if weights:
            model.load_weights(weights)
        return model
    
    def remember(self, state, action, reward, next_state, type):
        self.memory[type].append((state, action, reward, next_state))
        
    def replay_new(self, memory, type):
        if len(memory[type]) > 1000:
            minibatch = random.sample(memory[type], 1000)
        else:
            minibatch = memory[type]
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if done == False:    
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            target_f = self.model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)
            
    def train_short_memory(self, state, action, reward, next_state, type, done=False):
        if type == 'Taxes':
            rs = (1,23)
            model = self.tax_model
        target = reward
        if done == False:    
            target = reward + self.gamma * np.amax(model.predict(next_state.reshape(rs))[0])
        target_f = model.predict(state.reshape(rs))
        target_f[0][np.argmax(action)] = target
        model.fit(state.reshape(rs), target_f, epochs=1, verbose=0)
        
    def save(self, filename=None):
        '''
        Save this using Pickle
        '''
        if filename == None:
            filename = 'agents/agent_' + self.attitude[0] + '.pickle'
        
        with open(filename, 'wb') as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)