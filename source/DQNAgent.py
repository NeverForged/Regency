import random
import pickle
import numpy as np
import pandas as pd
import networkx as nx
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
        
    def get_state(self, step, df):
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
                
        return np.asarray(state) 

        
    def get_action_state(self, Regent, Game):
        '''
        State variable for actions
        '''
        
        # get nearby regents
        temp = Game.Provences[Game.Provences['Regent'] == Regent]['Provence']
        temp = pd.concat([temp, Game.Holdings[Game.Holdings['Regent'] == Regent]['Provence']])
        rtemp = Game.Relationships[Game.Relationships['Other']==Regent].copy()
        rtemp = rtemp[rtemp['Vassalage']>0]
        for reg in list(rtemp['Regent']): # include the list for my vassals
            pd.concat([temp, Game.Provences[Game.Provences['Regent'] == reg]['Provence']])
            pd.concat([temp, Game.Holdings[Game.Holdings['Regent'] == Regent]['Provence']])
        # temp is a regent/provence list for nearby players
        temp = pd.merge(temp, Game.Geography[Game.Geography['Border']==1][['Provence','Neighbor', 'Border']], on='Provence', how='left')
        temp['Provence'] = temp['Neighbor']
        temp1 = pd.merge(temp[['Provence']], Game.Provences[['Provence', 'Regent']].copy(), on='Provence', how='left')
        temp2 = pd.merge(temp[['Provence']], Game.Holdings[['Provence', 'Regent']].copy(), on='Provence', how='left')
        temp = pd.concat([temp1, temp2])
        
        prov_regent_list = temp.copy()

        # start the work
        state = [0 for a in range(99)]
        '''
                is_action_1   
                is_action_2
                is_action_3
                is_bonus   
                court_bare
                court_average
                court_rich
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
        '''
        df = Game.Seasons[Game.Season]['Season'].copy()
        df = df[df['Regent'] == Regent]
        for a in range(3):  # 0,1,2
            if Game.Action == a+1:
                state[a] = 1  # action_1, action_2, or action_3
        if Game.Bonus == 1:  # 3
            state[3] = 1  # bonus_action
        for i, a in enumerate(['Bare', 'Average', 'Rich']):  #4, 5, 6
            if df['Court'].values[0] == a:
                state[i+4] = 1  # court_bare, court_average, court_rich
        for i, a in enumerate([1 if df['Gold Bars'].values[0] > a else 0 for i,a in enumerate([10,20,30,40,50,100])]):
            state[6+i] = a  # gold > 10, 20, 30, 40, 50, 100
        for i, a in enumerate([1 if df['Regency Points'].values[0] > a else 0 for i,a in enumerate([10,20,30,40,50,100])]):
            state[12+i] = a # regency > 10, 20, 30, 40, 50, 100 
            '''
                i_am_dead  7
                i_am_evil
                i_am_good
                i_am_lawful
                i_am_chaotic
            '''
        regent = Game.Regents[Game.Regents['Regent'] == Regent].copy()
        if regent['Alive'].values[0] == False:
            state[18] = 1  # i_am_dead
        if 'E' in list(regent['Alignment'].values[0]):
            state[19] = 1  # i_am_evil
        if 'G' in list(regent['Alignment'].values[0]):
            state[20] = 1  # i_am_good
        if 'L' in list(regent['Alignment'].values[0]):
            state[21] = 1  # i_am_lawful
        if 'C' in list(regent['Alignment'].values[0]):  # 11
            state[22] = 1  # i_am_chaotic
            '''
                i_have_provences  10
                i_have_a_brigand_problem
                i_have_contested_provence
                capital_has_castle
                highpop_has_castle
                lowpop_has_castle
            '''
        my_provences = Game.Provences[Game.Provences['Regent'] == Regent].copy()
        capital = None
        high_pop = None
        low_pop = None
        # 23-33 all imply that the Regent has provences
        if my_provences.shape[0] > 0:
            state[23] == 1  # i_have_provences
            if my_provences[my_provences['Brigands'] == True].shape[0] > 0:
                state[24] = 1  # i_have_brigands
            if my_provences[my_provences['Contested'] == True].shape[0] > 0:
                state[25] = 1  # i_have_contested_provence
            # get three cities to look at
            my_provences['roll'] = np.random.randint(1,100,my_provences.shape[0])
            capital = my_provences[my_provences['Capital']==True].sort_values('Population', ascending=False).iloc[0]['Provence']    
            high_pop = my_provences[my_provences['Capital']==False].sort_values('Population', ascending=False).iloc[0]['Provence']
            low_pop = my_provences[my_provences['Capital']==False].sort_values('Population').iloc[0]['Provence']
            provences_i_care_about = [capital, high_pop, low_pop]
            for i, prov in enumerate(provences_i_care_about):
                if my_provences[my_provences['Provence'] == prov]['Castle'].values[0] == 0:
                    state[26+i] = 1  # capital_no_castle, hih_pop_no_castle, low_pop_no_castle
            '''
                capital_can_have_road
                highpop_can_have_road  30
                lowpop_can_have_road
                my_waterways_can_have_routes
                my_provences_can_have_routes
            '''
            my_geography = pd.merge(my_provences, Game.Geography.copy(), on='Provence', how='left')
            my_geography = my_geography[my_geography['Border']==1]
            for i, prov in enumerate(provences_i_care_about):  
                temp = my_geography[my_geography['Provence']==prov]
                temp = temp[temp['Road'] == 0]
                if temp.shape[0] > 0:
                    state[29+i] = 1  # capital_can_has_road, high_pop_can_has_road, low_pop_can_has_road
            temp = my_geography[['Provence', 'Waterway', 'Population', 'Caravan', 'Shipping']].groupby(['Provence', 'Waterway', 'Population']).sum().reset_index()
            temp['Routes Allowed'] = ((temp['Population']+2)/3).astype(int)
            temp = temp[temp['Routes Allowed']>(temp['Caravan']+temp['Shipping'])].copy()
            if temp.shape[0] > 0:
                state[32] = 1  # provences_can_have_trade_routes
            if temp[temp['Waterway']==True].shape[0] > 0:
                state[33] = 1  # waterways_can_have_trade_routes
        # Need regents now
        # get relationships, assume 0 for non-included
        # get list
        rtemp = Game.Relationships[Game.Relationships['Regent']==Regent].copy()
        rtemp['Regent'] = rtemp['Other']
        rtemp = pd.concat([prov_regent_list, rtemp])
        # update numbers
        rtemp2 = Game.Relationships[Game.Relationships['Regent']==Regent].copy()
        rtemp2['Regent'] = rtemp2['Other']
        relationships = pd.merge(rtemp['Regent'], rtemp2, on='Regent', how='left').fillna(0)

        relationships = relationships[relationships['Regent'] != Regent].copy()
        # randomized roll for choices
        relationships['roll'] = np.random.randint(1,100,relationships.shape[0])

        # enmity -> measure of friendship, negative is actual enmity
        relationships['enmity'] = relationships['Diplomacy'] + 2*relationships['Vassalage'] - 10*relationships['At War'] + relationships['Trade Permission']

        # enemy = worst diplomacy
        relationships = relationships.sort_values(['enmity', 'roll'])
        enemy = relationships.iloc[0]['Regent']
        # friend = best relation
        friend = relationships.sort_values(['enmity', 'roll'], ascending=False).reset_index().iloc[0]['Regent']
        regents = Game.Regents.copy()
        regents = regents[regents['Regent'] != enemy].copy()
        regents = regents[regents['Regent'] != friend].copy()
        regents = pd.merge(regents, Game.Relationships[['Regent','Trade Permission']], on='Regent', how='left')
        regents['roll'] = np.random.randint(1,100,regents.shape[0]) - 50*regents['Trade Permission']  # more likely to try and finish the deal
        rando = regents.sort_values('roll').reset_index().iloc[0]['Regent']
        regents_i_care_about = [enemy, friend, rando]
        
        # Next set if for Holdings
        my_holdings = Game.Holdings[Game.Holdings['Regent']==Regent]
        if my_holdings.shape[0] > 0:
            '''
                i_have_temples
                i_have_law
                i_have_guild
                i_have_source
                i_have_temple_in_friend
                i_have_temple_in_enemy
                i_have_law_in_enemy
                i_have_contested_holding  20
                my_holdings_can_increase_level
            '''
            lst = ['Law', 'Temple', 'Guild', 'Source']
            for i, type in enumerate(lst):
                if my_holdings[my_holdings['Type'] == type].shape[0] > 0:
                    state[34+i] = 1  # i_have_law, i_have_temple, i_have_guild, i_have_source
            temp = Game.Provences[['Regent', 'Provence']].copy()
            temp['Other'] = temp['Regent']
            my_holdings = pd.merge(my_holdings, temp[['Provence','Other']], on='Provence', how='left')
            temp = my_holdings[my_holdings['Type']=='Temple']
            if temp[temp['Other'] == friend].shape[0] > 0:
                state[38] = 1  # i_have_temple_in_friend
            if temp[temp['Other'] == enemy].shape[0] > 0:
                state[39] = 1  # i_have_temple_in_enemy
            temp = my_holdings[my_holdings['Type'] == 'Law']
            if temp[temp['Other'] == enemy].shape[0] > 0:
                state[40] = 1  # i_have_law_in_enemy
            if my_holdings[my_holdings['Contested']==1].shape[0] > 0:
                state[41] = 1  # i_have_contested_holdings
            shared_holdings = pd.merge(my_holdings[['Provence']], Game.Holdings.copy(), on='Provence', how='left')
            temp = pd.merge(shared_holdings, Game.Provences[['Provence', 'Population', 'Magic']].copy(), on='Provence', how='left')
            temp = temp[['Provence', 'Type', 'Level', 'Population', 'Magic']].groupby(['Provence', 'Type']).sum().reset_index()
            temp = pd.merge(my_holdings[['Provence', 'Type']], temp, on=['Provence', 'Type'])
            temp_s = temp[temp['Type'] == 'Source']
            temp = temp[temp['Type'] != 'Source' ]
            if temp[temp['Level'] < temp['Population']].shape[0] > 0 or  temp_s[temp_s['Level'] < temp_s['Magic']].shape[0]:
                state[42] = 1  # my_holdings_can_increase_in_level
        '''   
                i_am_at_war
        '''
        temp = pd.concat([Game.Relationships[Game.Relationships[a] == Regent]  for a in ['Regent', 'Other']])
        if temp[temp['At War']>0].shape[0] > 0:
            state[43] = 1  # i_am_at_war
        '''
                i_have_military_units
                i_have_levees
                i_have_mercenaries
                
 
        '''
        my_troops = Game.Troops[Game.Troops['Regent'] == Regent]
        if my_troops.shape[0] > 0:
            state[44] = 1  # i_have_troops
            if my_troops[my_troops['Type'].str.lower().str.contains('levees')].shape[0] > 0:
                state[45] = 1  # i_have_levees
            if my_troops[my_troops['Type'].str.lower().str.contains('mercenary')].shape[0] > 0:
                state[46] = 1  # i_have_mercenaries
            if my_troops[my_troops['Garrisoned'] > 0].shape[0] > 0:
                state[47] = 1  # i_have_garrisoned_troops
        '''
                i_have_ley_lines
                leynetworks
        '''
        temp = Game.LeyLines[Game.LeyLines['Regent'] == Regent]
        if temp.shape[0] > 0:
            state[48] = 1  # i_have_leylines
            temp['Neighbor'] = temp['Other']
            temp = pd.merge(temp[['Provence','Neighbor']], Game.Geography[['Provence', 'Neighbor', 'Border']], on=['Provence','Neighbor'], how='left')
            G = nx.from_pandas_edgelist(temp, 'Provence', 'Neighbor', ['Border'])
            num = len(list(nx.connected_components(G)))
            if G >= 2:
                state[49] = 1  # i_have_disconnected_ley_lines
        '''
                was_victim_of_espionage
        '''        
        if Game.detect_espionage(Regent).shape[0] > 0:
            state[50] = 1  # i_was_victim_of_espionage
            
            
        '''       
                friend_has_more_regency 
                friend_has_more_gold
                diplomacy_friend_above_0
                diplomacy_friend_5_higher
                arranged_trade_route_friend
                friend_alive
                i_am_friends_vassal
        '''
        
        temp = Game.Regents.copy()
        temp = pd.concat([temp[temp['Regent']==a] for a in regents_i_care_about])
        temp = pd.concat([temp, Game.Regents[Game.Regents['Regent']==Regent]])
        if temp[temp['Regent'] == friend]['Regency Points'].values[0] > temp[temp['Regent'] == Regent]['Regency Points'].values[0]:
            state[51] = 1  # friend_has_more_regency
        if temp[temp['Regent'] == friend]['Gold Bars'].values[0] > temp[temp['Regent'] == Regent]['Gold Bars'].values[0]:
            state[52] = 1  # friend_has_more_gold
        fdip = relationships[relationships['Regent'] == friend]['Diplomacy'].values[0]
        if fdip > 0:
            state[53] = 1  # friend_diplomacy_positive
        if fdip > 5:
            state[54] = 1  # friend_diplomacy_high
        if temp[temp['Regent'] == friend]['Alive'].values[0] == True:
            state[55] = 1  # friend_alive
        if relationships[relationships['Regent'] == friend]['Trade Permission'].values[0] > 0:
            state[56] = 1  # friend_trade_permission
        temp_ = Game.Relationships[Game.Relationships['Regent'] == Regent].copy()
        temp_ = temp_[temp_['Other'] == friend]
        if temp_.shape[0] > 0:
            if temp_['Vassalage'].values[0] > 0:
                state[57] = 1  # i_am_friends_vassal
        if relationships[relationships['Regent'] == friend]['Vassalage'].values[0] > 0:
            state[58] = 1  # friend_is_my_vassal
        '''
                arranged_trade_route_rando
                diplomacy_rando_positive
                
                rando_has_more_regency
                rando_has_more_gold
                rando_max_pop_higher
                rando_alive
        '''
        if temp[temp['Regent'] == rando]['Regency Points'].values[0] > temp[temp['Regent'] == Regent]['Regency Points'].values[0]:
            state[59] = 1  # rando_has_more_regency
        if temp[temp['Regent'] == rando]['Gold Bars'].values[0] > temp[temp['Regent'] == Regent]['Gold Bars'].values[0]:
            state[60] = 1  # rando_has_more_gold
        rand_rel = Game.Relationships[Game.Relationships['Regent'] == Regent]  # rando may not be in realtionships 
        dct = {}
        dct['Other'] = [rando]
        rand_rel = pd.merge(rand_rel, pd.DataFrame(dct), on='Other', how='outer').fillna(0)
        fdip = rand_rel[rand_rel['Other']==rando]['Diplomacy'].values[0]
        if fdip > 0:
            state[61] = 1  # rando_diplomacy_positive
        if fdip > 5:
            state[62] = 1  # rando_diplomacy_high
        if temp[temp['Regent'] == rando]['Alive'].values[0] == True:
            state[63] = 1  # rando_alive
        if rand_rel[rand_rel['Other'] == rando]['Trade Permission'].values[0] > 0:
            state[64] = 1  # rando_trade_permission
        '''
                enemy_has_law_holding_in_my_lands
                enemy_has_temple_holding_in_my_lands
                enemy_has_source_holding_in_my_lands
                enemy_has_guild_holding_in_my_lands  80
                enemy_has_same_type_of_holding_as_me_somewhere_i_have_holding
                enemy_has_contested_holding
                enemy_has_contested_provence
                enemy_has_no_law_holdings_and_rebellious_or_poor_loyalty_in_a_province
                contested_all_enemy_provinces
                all_enemy_castles_0
                enemy_troops_in_domain
                enemy_troops_in_friends_domain
                enemy_has_more_troops
                enemy_alive
        '''
        if temp[temp['Regent'] == enemy]['Regency Points'].values[0] > temp[temp['Regent'] == Regent]['Regency Points'].values[0]:
            state[65] = 1  # enemy_has_more_regency
        if temp[temp['Regent'] == enemy]['Gold Bars'].values[0] > temp[temp['Regent'] == Regent]['Gold Bars'].values[0]:
            state[66] = 1  # enemy_has_more_gold
        fdip = relationships[relationships['Regent'] == enemy]['Diplomacy'].values[0]
        if fdip < 0:
            state[67] = 1  # enemy_diplomacy_negative
        if fdip < -5:
            state[68] = 1  # enemy_diplomacy_really_low
        if temp[temp['Regent'] == enemy]['Alive'].values[0] == True:
            state[69] = 1  # enemy_alive
        temp = Game.Holdings[Game.Holdings['Regent'] == enemy]
        temp['Enemy'] = temp['Regent']
        temp = pd.merge(temp[['Enemy', 'Provence', 'Type']], my_provences, on='Provence', how='left')
        for i, a in enumerate(['Law', 'Temple', 'Guild', 'Source']):
            if temp[temp['Type'] == a].shape[0] > 0:
                state[70+i] = 1  # enemy_has_law_in_my_provence, _temple_, _guild_, _source_
        if pd.merge(Game.Holdings[Game.Holdings['Regent'] == enemy], Game.Holdings[Game.Holdings['Regent'] == Regent], on=['Provence', 'Type'], how='inner').shape[0] > 0:
            state[74] = 1  # enemy_has_same_type_of_holding_as_me_somewhere_i_have_holding
        temp = Game.Holdings[Game.Holdings['Regent'] == enemy]
        if temp[temp['Contested'] == 1].shape[0] > 0:
            state[75] = 1  # enemy_has_contested_holding
        temp = Game.Provences[Game.Provences['Regent'] == enemy]
        if temp[temp['Contested'] == 1].shape[0] > 0:
            state[76] = 1  # enemy_has_contested_provence
        temp = temp[temp['Loyalty'] != 'High']
        temp = temp[temp['Loyalty'] != 'Average']
        if temp.shape[0] > 0:  # we have the requisite loyalty issue
            temp = pd.merge(temp, Game.Holdings[Game.Holdings['Type']=='Law'], on='Provence', how='left')
            if temp.shape[0] > 0:
                state[77] = 1  # enemy_has_no_law_holdings_and_rebellious_or_poor_loyalty_in_a_province
        
        temp = Game.Provences[Game.Provences['Regent'] == enemy]
        check = temp.shape[0]
        if temp[temp['Contested'] == True].shape[0] == check and check > 0:
            state[78] = 1  # all_enemy_provences_contested
        if np.sum(temp['Castle']) == 0:
            state[79] = 1  # enemy_has_no_castles
        etroops = Game.Troops[Game.Troops['Regent'] == enemy].copy()
        if pd.merge(my_provences, etroops, on='Provence', how='left').shape[0] > 0:
            state[80] = 1  # enemy has troops in my domain
        temp = Game.Provences[Game.Provences['Regent'] == friend]
        if pd.merge(temp, etroops, on='Provence', how='left').shape[0] > 0:
            state[81] = 1  # enemy_has_troops_in_friends_domain
        if np.sum(etroops['CR']) > np.sum(my_troops['CR']):
            state[82] = 1  # enemy_has_stronger_army
        '''
                random_event_monsters
                unrest_in_override
                feud_in_override
                matter_of_justie_in_override  99!
                
        '''
        try:
            oride = Game.random_override[Regent]
            if oride == 'Monsters':
                state[83] = 1  # random_event_monsters
            if oride == 'Unrest or Rebellion':
                state[84] = 1  # random_event_unrest
            if oride == 'Feud':
                state[85] = 1  # random_event_feud
            if ordie == 'Matter of Justice':
                state[86] = 1  # random_event_matter_of_justice
        except:
            None
        return np.asarray(state), capital, high_pop, low_pop, friend, enemy, rando
            
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
            
            