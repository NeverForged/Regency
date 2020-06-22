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

    def __init__(self,regency):
        '''
        '''
        self.action_choices = 0
        self.action_size = 0
        self.regency = regency
        self.reward = 0
        self.gamma = 0.9
        self.action_size = 51
        self.action_choices = 34
        self.learning_rate = 0.0005
        self.model = self.network(N=self.action_choices, K=self.action_size)
        self.memory = []
        

    def get_state(self):
        '''
        Sets the State-vector for each Faction
        '''
        # make life easier...
        regency = self.regency

        # STATE VECTOR DEFINITIONS
        '''
        0 has_100_gold
        1 has_180_gold
        2 has_400_gold
        3 has_500_gold
        4 has_900_gold
        5 has_1000_gold
        6 has_2500_gold
        7 has_5000_gold
        8 has_15000_gold
        9 has_25000_gold
        10 has_50000_gold
        11 has_500000_gold
        12 trained_athletics
        13 trained_acrobatics
        14 trained_stealth
        15 trained_acrana
        16 trained_investigation
        17 trained_religion
        18 trained_perception
        19 trained_persuasion
        '''
        dct = {}
        for a in list(regency.factions['Name']):
            dct[a] = []
        lst = [100,180,400,500,900,1000,2500,5000,15000,25000,50000,500000]
        for i, row in regency.factions.iterrows():
            for a in lst:
                dct[row['Name']].append(1*(row['Gold']>=a))
            for a in ['Athletics', 'Acrobatics', 'Stealth', 'Arcana', 'Investigation', 'Religion', 'Perception', 'Persuasion']:
                dct[row['Name']].append(1*(row[a]>=1))

        '''
        20 more_gold_than_enemy
        21 higher_level_than_enemy
        22 higher_str_than_enemy
        23 higher_dex_than_enemy
        24 higher_con_than_enemy
        25 higher_int_than_enemy
        26 higher_wis_than_enemy
        27 higher_cha_than_enemy
        28 more_gold_than_ally
        29 higher_level_than_ally
        30 higher_str_than_ally
        31 higher_dex_than_ally
        32 higher_con_than_ally
        33 higher_int_than_ally
        34 higher_wis_than_ally
        35 higher_cha_than_ally
        '''
        A = pd.merge(regency.strongholds,regency.stronghold_types,left_on='Type',right_on='Stronghold',how='left')
        A['Type'] = A['Type_y']
        A = pd.merge(A[['Area','Faction','Type']],regency.geography,on='Area',how='left')
        B = pd.merge(A,A,left_on='Area',right_on='Neighbor',how='left')
        B = B[B['Type_x']==B['Type_y']]
        C = pd.merge(A,A,on='Area',how='left')
        D = pd.concat([B,C],sort=False)
        D = D[['Faction_x','Faction_y']].drop_duplicates()
        D = D[D['Faction_x']!=D['Faction_y']]
        D['Faction'] = D['Faction_x']
        D['Other'] = D['Faction_y']
        E = pd.concat([regency.relationships,D[['Faction','Other']]],sort=False).fillna(0).groupby(['Faction','Other']).sum().reset_index()
        E = pd.merge(E,regency.factions[['Name','Level']],left_on='Other',right_on='Name',how='left').dropna()

        E['Check'] = E['Relationship']*E['Level']
        E['Key'] = E['Other'] + E['Check'].astype(str)
        Ally = pd.merge(E[['Faction','Check']].groupby('Faction').max().reset_index(),E,on=['Faction','Check'],how='left').drop_duplicates('Faction')[['Faction','Other']]
        Enemy = pd.merge(E[['Faction','Check']].groupby('Faction').min().reset_index(),E,on=['Faction','Check'],how='left').drop_duplicates('Faction')[['Faction','Other']]
        Ally = pd.merge(Ally,regency.factions,left_on='Faction',right_on='Name', how='left')
        Ally = pd.merge(Ally,regency.factions,left_on='Other',right_on='Name', how='left')
        Enemy = pd.merge(Enemy,regency.factions,left_on='Faction',right_on='Name', how='left')
        Enemy = pd.merge(Enemy,regency.factions,left_on='Other',right_on='Name', how='left')
        ally = {}
        enemy = {}
        lst = ['Gold', 'Level', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        for i, row in Ally.iterrows():
            ally[row['Faction']] = row['Other']
            for a in lst:
                dct[row['Faction']].append(1*(row[a+'_x']>=row[a+'_y']))
        for i, row in Enemy.iterrows():
            enemy[row['Faction']] = row['Other']
            for a in lst:
                dct[row['Faction']].append(1*(row[a+'_x']>=row[a+'_y']))

        '''
        36 can_upgrade_castle
        37 can_upgrade_temple
        38 can_upfgrade_guild
        39 can_upgrade_monastary
        40 can_upgrade_mystic
        '''
        temp = pd.merge(regency.strongholds,regency.areas[['Area','Population','Magic']],on='Area',how='left')
        temp = pd.merge(temp,regency.stronghold_types[['Stronghold','Type','HP']],left_on='Type',right_on='Stronghold',how='left')
        temp['Type'] = temp['Type_y']
        temp = temp[['Area','Faction','Level','Sieged','Hit Points','HP','Population','Magic','Type','Stronghold']]

        A = temp[temp['Type']=='Mystic'].copy().reset_index(drop=True)
        B = temp[temp['Type']=='Castle'].copy().reset_index(drop=True)
        C = temp[temp['Type']!='Castle'][temp['Type']!='Mystic'].copy().reset_index(drop=True)
        BA = B[B['Stronghold']=='Manor'].copy()
        BA = BA[BA['Level']<1]
        BB = B[B['Stronghold']=='Keep'].copy()
        BB = BB[BB['Level']<2]
        BC = B[B['Stronghold']=='Palace'].copy()
        BC = BC[BC['Level']<3]

        A = A[A['Level']<A['Magic']]
        C = C[C['Level']<C['Population']]

        AA = pd.concat([A,BA,BB,BC,C])
        AA = AA[['Faction','Type']].groupby(['Faction','Type']).sum().reset_index()

        lst = ['Castle','Temple','Guild','Monastery','Mystic']
        for i, row in regency.factions.iterrows():
            check = AA[AA['Faction']==row['Name']]
            for a in lst:
                if check.shape[0]>0:
                    dct[row['Name']].append(1*(check[check['Type']==a].shape[0]>0))
                else:
                    dct[row['Name']].append(0)

        '''
        41 have_road_near_stronghold
        '''
        temp = regency.geography[regency.geography['Road/Port']==1]
        acheck = regency.areas[regency.areas['Waterway']==0].copy()
        temp = pd.merge(temp,acheck[['Area', 'Waterway']],on='Area',how='left').dropna()
        temp = pd.merge(temp,acheck[['Area']],left_on='Neighbor', right_on='Area',how='left').dropna()
        temp['Area'] = temp['Area_x']
        temp = pd.merge(temp, regency.strongholds[['Faction','Area']].groupby(['Faction','Area']).sum().reset_index(),on='Area',how='left')
        temp = temp[['Faction']].drop_duplicates()
        temp

        for i, row in regency.factions.iterrows():
            dct[row['Name']].append(1*(temp[temp['Faction']==row['Name']].shape[0]>0))

        '''
        42 have_smaller_castle_or_temple
        43 have_damaged_stronghold
        44 enemy_is_sieged
        45 enemy_has_damaged_stronghold
        46 enemy_has_castle
        47 ally_is_sieged
        '''
        temp = regency.strongholds.copy()
        lst = ['Manor', 'keep', 'Small Temple']
        lst2=[]
        for a in lst:
            lst2.append(temp[temp['Type']==a].copy())
        temp2 = pd.concat(lst2)



        temp = pd.merge(temp,regency.factions[['Name','Con']],left_on='Faction',right_on='Name',how='left')
        temp = pd.merge(temp,regency.stronghold_types[['Stronghold','HP','Type']],left_on='Type', right_on='Stronghold',how='left')
        temp = temp.dropna()
        temp['Max HP'] = (temp['HP'] + temp['Level']*((temp['Con']-10)/2).astype(int)).astype(int)

        temp_low = temp[temp['Hit Points'].astype(int)<temp['Max HP']]
        temp_high = temp[temp['Hit Points'].astype(int)>temp['Max HP']]

        if temp_high.shape[0] > 0:
            for i, row in temp_high.iterrows():
                regency.edit_stronghold(row['Name_x'],'Hit Points',row['Max HP'])


        targets = regency.factions[['Name']].copy()
        enemies = []
        allies = []
        for i, row in targets.iterrows():
            enemies.append(enemy[row['Name']])
            allies.append(ally[row['Name']])
        targets['Enemy'] = enemies
        targets['Ally'] = allies

        targets['is_ally'] = targets['Name']
        targets['is_enemy'] = targets['Name']

        temp_e = pd.merge(temp, targets[['Enemy','is_enemy']], left_on='Faction', right_on='Enemy', how='left')
        temp_a = pd.merge(temp, targets[['Ally','is_ally']], left_on='Faction', right_on='Ally', how='left')


        for i, row in regency.factions.iterrows():
            dct[row['Name']].append(1*(temp2[temp2['Faction']==row['Name']].shape[0]>0))
            dct[row['Name']].append(1*(temp_low[temp_low['Faction']==row['Name']].shape[0]>0))
            check = temp_e[temp_e['is_enemy']==row['Name']].copy()
            if check.shape[0]>0:
                dct[row['Name']].append(check['Sieged'].values[0])
                dct[row['Name']].append(1*(check[check['Hit Points']<check['Max HP']].shape[0]>0))
            else:
                dct[row['Name']].append(0)
                dct[row['Name']].append(0)
            check = temp_a[temp_a['is_ally']==row['Name']].copy()
            if check.shape[0]>0:
                dct[row['Name']].append(check['Sieged'].values[0])
            else:
                dct[row['Name']].append(0)
        '''
        48 enemy_is_lord
        49 ally_is_lord
        50 enemy_is_vassal
        51 ally_is_vassal
        '''
        temp = pd.merge(regency.vassalage,targets[['Name','Enemy','Ally']],left_on='Faction',right_on='Name',how='left')
        for i, row in regency.factions.iterrows():
            check = temp[temp['Name']==row['Name']]
            dct[row['Name']].append(1*(check[check['Enemy']==check['Lord']].shape[0]>0))
            dct[row['Name']].append(1*(check[check['Enemy']==check['Lord']].shape[0]>0))
        temp = pd.merge(regency.vassalage,targets[['Name','Enemy','Ally']],left_on='Lord',right_on='Name',how='left')
        for i, row in regency.factions.iterrows():
            check = temp[temp['Name']==row['Name']]
            dct[row['Name']].append(1*(check[check['Enemy']==check['Faction']].shape[0]>0))
            dct[row['Name']].append(1*(check[check['Enemy']==check['Faction']].shape[0]>0))


        '''
        Bring it all together....
        '''
        targets['Faction'] = targets['Name']
        turn = targets[['Faction','Enemy','Ally']]
        lst = []
        for i, row in targets.iterrows():
            lst.append(dct[row['Faction']])
        turn['State'] = lst
        return turn
        
        
    def network(self, N, K, weights=None):
        '''
        Original had 3 outputs...
        Setting this to N outputs.
        '''
        model = Sequential()
        model.add(Dense(units=K*10, activation='relu', input_dim=K))
        model.add(Dropout(0.15))
        model.add(Dense(units=K*10, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(units=K*10, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(units=N, activation='softmax'))
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if weights:
            model.load_weights(weights)
        return model
    
    def remember(self, state, action, reward, next_state, type, done=False):
        self.memory[type].append((state, action, reward, next_state, done))
        
    def replay_new(self):
        model = self.model
        memory = self.memory
       
        if len(memory) > 1000:
            minibatch = random.sample(memory, 1000)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if done == False:    
                target = reward + self.gamma * np.amax(model.predict(np.array([next_state]))[0])
            target_f = model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            model.fit(np.array([state]), target_f, epochs=1, verbose=0)
        
    def save(self, filename=None):
        '''
        Save this using Pickle
        '''
        if filename == None:
            filename = 'agents/agent.pickle'
        
        with open(filename, 'wb') as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)