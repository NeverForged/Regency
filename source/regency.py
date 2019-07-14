import os
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from PIL import Image
from random import randint
import matplotlib.pyplot as plt
from source.DQNAgent import DQNAgent
from keras.utils import to_categorical
from IPython.display import clear_output


class Regency(object):
    '''
    Based on the 5e Conversion of the Regency system from Birthright,
    found here: https://www.gmbinder.com/share/-L4h_QHUKh2NeYhgD96A
    
    DataFrames:
    Provences: [Provence, Domain, Region, Regent, Terrain, Loyalty, Taxation, 
                Population, Magic, Castle, Capital, Position, Waterway]
    Holdings: [Provence, Domain, Regent, Type, Level]
    Regents: [Regent, Full Name, Player, Class, Level, Alignment, Race, 
                Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion, 
                Regency Points, Gold Bars, Regency Bonus, Attitude, Alive]
    Geography: [Provence, Neighbor, Border, Road, Caravan, Shipping, RiverChasm]
    Relationships: [Regent, Other, Diplomacy, Payment, Vassalage, At War, Trade Permission]
    Troops: [Regent, Provence, Type, Cost, CR, Garrisoned, Home]
    Seasons: A dctionary of season-dataframes (to keep track of waht happened)
    Lieutenants: A List of regent lieutenant pairs, with a marker for 'busy'
    LeyLines: [Regent, Provence, Other]
    Projects: ['Regent', 'Project Type', 'Details', 'Gold Bars Left']
    '''
    
    # Initialization
    def __init__(self, train=False, train_short=False, world='Birthright', dwarves=True, elves=True, goblins=True, gnolls=True, halflings=True, jupyter=True, IntDC=5):
        '''
        
        initialization of Regency class.
        Sets the dataframes based on saved-version
        Birthright is Default.
        '''
        self.game_year = 1524
        self.jupyter = jupyter
        self.random_override = {}
        self.IntDC = IntDC
        self.errors = []
        self.failed_actions = pd.DataFrame()
        self.Train = train
        self.Train_Short = train_short

        # Provence Taxation Table
        dct = {}
        dct['Population'] = [a for a in range(11)]
        dct['Light'] = [(-1,0), (-1,1), (0,1), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16)]
        dct['Moderate'] = [(-1,0), (0,2), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16), (4,18)]
        dct['Severe'] =  [(-1,1), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16), (4,18), (4,22)]
        self.provence_taxation = pd.DataFrame(dct)
        
        # troops
        dct = {}
        dct['Unit Type'] = ['Archers', 'Archers', 'Archers'
                            , 'Artillerists'
                            , 'Cavalry'
                            , 'Infantry', 'Infantry', 'Infantry'
                            , 'Elite Infantry'
                            , 'Irregulars', 'Irregulars', 'Irregulars'
                            , 'Knights'
                            , 'Levies'
                            , 'Mercenary Cavalry', 'Mercenary Infantry', 'Mercenary Irregulars', 'Mercenary Archers', 'Mercenary Pikeman'
                            , 'Pikemen', 'Pikemen', 'Pikemen'
                            , 'Scouts', 'Scouts'
                            ]  
        dct['Type'] = ['Human', 'Human', 'Human'
                            , 'Human'
                            , 'Human'
                            , 'Human', 'Human', 'Human'
                            , 'Human'
                            , 'Human', 'Human', 'Human'
                            , 'Human'
                            , 'Human'
                            , 'Mercenary', 'Mercenary', 'Mercenary', 'Mercenary', 'Mercenary'
                            , 'Human', 'Human', 'Human'
                            , 'Human', 'Human'
                            ]  
        dct['Muster Cost'] = [2, 2, 2
                              , 4
                              , 4
                              , 2, 2, 2
                              , 4
                              , 1, 1, 1
                              , 6
                              , 0
                              , 6, 4, 4, 4, 4
                              , 2, 2, 2
                              , 2, 2
                              ]
        dct['Maintenance Cost'] = [1, 1, 1
                                    , 2
                                    , 2
                                    , 1, 1, 1
                                    , 2
                                    , 1, 1, 1
                                    , 2
                                    , 1
                                    , 2, 2, 1, 1, 1
                                    , 1, 1, 1
                                    , 1, 1
                                    ]
        dct['Requirements Holdings'] = ['Law', 'Temple', 'Guild'
                                        , 'Law'
                                        , 'Law'
                                        , 'Law', 'Temple', 'Guild'
                                        , 'Law'
                                        , 'Law', 'Temple', 'Guild'
                                        , 'Law'
                                        , 'Law'
                                        , 'Mercenaries', 'Mercenaries', 'Mercenaries', 'Mercenaries', 'Mercenaries'
                                        , 'Law', 'Temple', 'Guild'
                                        , 'Law', 'Guild'
                                        ]
        dct['Requirements Level'] = [1, 4, 4
                                    , 5
                                    , 3
                                    , 1, 4, 4
                                    , 3
                                    , 1, 3, 3
                                    , 4
                                    , 1
                                    , 0, 0, 0, 0, 0
                                    , 2, 3, 3
                                    , 1, 2
                                    ]
        dct['BCR'] = [1, 1, 1
                        , 1
                        , 3
                        , 1, 1, 1
                        , 2
                        , 0.5, 0.5, 0.5
                        , 4
                        , 0.25
                        , 3, 2, 1, 1, 1
                        , 1, 1, 1
                        , 0.5, 0.5
                        ]
        # Dwarves
        if dwarves == True:
            dct['Unit Type'].append('Dwarf Guards')
            dct['Type'].append('Dwarf')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(4)
            dct['BCR'].append(2)
            dct['Unit Type'].append('Mercenary Dwarf Guards')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(2)
            dct['Unit Type'].append('Dwarf Crossbows')
            dct['Type'].append('Dwarf')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(4)
            dct['BCR'].append(2)
            dct['Unit Type'].append('Mercenary Dwarf Crossbows')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(2)
            dct['Unit Type'].append('Dwarf Engineers')
            dct['Type'].append('Dwarf')
            dct['Muster Cost'].append(5)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(3)
            dct['BCR'].append(1)
            dct['Unit Type'].append('Mercenary Dwarf Engineers')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(5)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(1)
        
        # Elves     
        if elves:
            dct['Unit Type'].append('Elf Archers')
            dct['Type'].append('Elf')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(3)
            dct['BCR'].append(2)
            dct['Unit Type'].append('Mercenary Elf Archers')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(2)
            dct['Unit Type'].append('Elf Cavalry')
            dct['Type'].append('Elf')
            dct['Muster Cost'].append(8)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(4)
            dct['BCR'].append(4)
            dct['Unit Type'].append('Mercenary Elf Cavalry')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(8)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(4)
        
        # Goblins
        if goblins:
            dct['Unit Type'].append('Goblin Archers')
            dct['Type'].append('Goblin')
            dct['Muster Cost'].append(1)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(2)
            dct['BCR'].append(1)
            dct['Unit Type'].append('Mercenary Goblin Archers')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(1)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(1)
            dct['Unit Type'].append('Goblin Infantry')
            dct['Type'].append('Goblin')
            dct['Muster Cost'].append(1)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(2)
            dct['BCR'].append(1)
            dct['Unit Type'].append('Mercenary Goblin Infantry')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(1)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(1)
            dct['Unit Type'].append('Goblin Cavalry')
            dct['Type'].append('Goblin')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(3)
            dct['BCR'].append(1)
            dct['Unit Type'].append('Mercenary Goblin Cavalry')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(4)
            dct['Maintenance Cost'].append(2)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(1)
            
        # Gnolls
        if gnolls:
            dct['Unit Type'].append('Mercenary Gnoll Marauders')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(2)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(3)
            dct['Unit Type'].append('Mercenary Gnoll Infantry')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(3)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(2)
            
        # halflings
        if halflings:
            dct['Unit Type'].append('Halfling Scouts')
            dct['Type'].append('Halfling')
            dct['Muster Cost'].append(2)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Law')
            dct['Requirements Level'].append(1)
            dct['BCR'].append(1)
            dct['Unit Type'].append('Mercenary Halfling Scouts')
            dct['Type'].append('Mercenary')
            dct['Muster Cost'].append(2)
            dct['Maintenance Cost'].append(1)
            dct['Requirements Holdings'].append('Mercenaries')
            dct['Requirements Level'].append(0)
            dct['BCR'].append(1)
        
        # make the table...
        self.troop_units = pd.DataFrame(dct)
        
        # Load the World
        self.load_world(world)

        # Agents...
        self.agent = {}
        try:
            self.agent = pickle.load( open( 'agents/agent.pickle', "rb" ) )
        except:
            self.agent = DQNAgent()
            self.agent.save()
        self.last_action = self.agent.action_choices -1    
    def clear_screen(self):
        '''
        For Jupyter notebook use
        self.clear_screen
        '''
        if self.jupyter:
            clear_output()
        else:
            print()
            print()
            print()
        
    def add_to_override(Regent, Action):
        try:
            self.Seasons[self.Season][self.Action]
        except:
            self.Seasons[self.Season][self.Action] = {}
        try:
            self.Seasons[self.Season][self.Action]['Override']   
        except:
            self.Seasons[self.Season][self.Action]['Override'] = {}
        self.Seasons[self.Season][self.Action]['Override'][Regent] = Action
        
    #  World Loading
    def load_world(self, world):
        '''
        loads world-dictionary
        '''
        
        try:
            dct = pickle.load( open( 'worlds/' + world + '.pickle', "rb" ) )
            lst = ['Provences', 'Holdings', 'Regents', 'Geography', 'Relationships', 'Troops', 'Seasons', 'Lieutenants', 'LeyLines', 'Projects', 'Espionage', 'War']
            self.Provences, self.Holdings, self.Regents, self.Geography, self.Relationships, self.Troops, self.Seasons, self.Lieutenants, self.LeyLines, self.Projects, self.Espionage, self.War = [dct[a] for a in lst]
        except (OSError, IOError) as e:
            self.new_world(world)

    
    # AGENT STUFF
    def make_decision(self, attitude, N, type, state, Regent, over=None):
        '''
        Have the Agent do a thing to make a decision.
        '''
        
        # get Int modifier
        mod = self.Regents[self.Regents['Regent']==Regent]['Int'].values[0]
        # predict action based on the old state
        if type == 'Taxes':
            prediction = self.agent.tax_model.predict(state.reshape((1,25)))
            move =  to_categorical(np.argmax(prediction[0]), num_classes=N)
        else:  # action
            prediction = self.agent.action_model.predict(state.reshape((1,self.agent.action_size)))
            roll = randint(1, 20)
            if over != None and state[94]==0 and state[95]==0:  # override
                move = to_categorical(over[0], num_classes=N)
            elif roll < self.IntDC or roll == 1:   #Fails a dc 5 int check and does something random
                move =  to_categorical(randint(0, N-1), num_classes=N)
                # instead, let's assign an action based on last_action
                # self.last_action += 1
                # elif self.last_action == self.agent.action_choices:
                #    self.last_action = 0
                # move = to_categorical(self.last_action, num_classes=self.agent.action_choices)
            else:
                move =  to_categorical(np.argmax(prediction[0]), num_classes=N)
        return move
        
    # World Building
    def new_world(self, world):
        # Holdings
        cols= ['Provence', 'Regent', 'Type', 'Level', 'Contested']
        self.Holdings = pd.DataFrame(columns=cols)
        
        # Provences
        cols = ['Provence', 'Domain', 'Region', 'Regent', 'Terrain', 'Loyalty', 'Taxation',
                'Population', 'Magic', 'Castle', 'Castle Name','Capital', 'Position', 'Contested'
                , 'Waterway', 'Brigands']
        self.Provences = pd.DataFrame(columns=cols)
        
        # Regents
        cols = ['Regent', 'Full Name', 'Bloodline', 'Culture', 'Player', 'Class', 'Level', 'Alignment', 'Race', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha', 'Insight', 'Deception', 'Persuasion', 'Regency Points', 'Gold Bars', 'Regency Bonus', 'Attitude', 'Alive', 'Divine', 'Arcane']
        self.Regents = pd.DataFrame(columns=cols)
        
        # Geography
        cols = ['Provence', 'Neighbor', 'Border', 'Road', 'Caravan', 'Shipping', 'RiverChasm']
        self.Geography = pd.DataFrame(columns=cols)
        
        # Relationships
        cols = ['Regent', 'Other', 'Diplomacy', 'Payment', 'Vassalage', 'At War', 'Trade Permission']
        self.Relationships = pd.DataFrame(columns=cols)
        
        # Troops
        cols = ['Regent', 'Provence', 'Type', 'Cost', 'CR', 'Garrisoned', 'Home', 'Injury']
        self.Troops = pd.DataFrame(columns=cols)
        
        # Lieutenants
        cols = ['Regent', 'Lieutenant', 'Busy']
        self.Lieutenants = pd.DataFrame(columns=cols)
        
        #Ley Lines
        cols = ['Regent', 'Provence', 'Other']
        self.LeyLines = pd.DataFrame(columns=cols)
        
        # Seasons
        self.Seasons = {}
        
        # Projects
        cols = ['Regent', 'Project Type', 'Details', 'Gold Bars Left']
        self.Projects = pd.DataFrame(columns=cols)
        
        # Espionage
        cols = ['Regent', 'Target', 'Assassination', 'Diplomacy', 'Troop Movements', 'Other']
        self.Espionage = pd.DataFrame(columns=cols)
        
        # War
        self.War = pd.DataFrame(columns=['Year','Location','Event','Notes'])
        # Save it...
        self.save_world(world)
          
    def save_world(self, world):
        '''
        Saves it as a pickled dictionary of DataFrames
        '''
        dct = {}
        dct['Provences'] = self.Provences
        dct['Holdings'] = self.Holdings
        dct['Regents'] = self.Regents
        dct['Geography'] = self.Geography
        dct['Relationships'] = self.Relationships
        dct['Troops'] = self.Troops
        dct['Seasons'] = self.Seasons
        dct['Lieutenants'] = self.Lieutenants
        dct['LeyLines'] = self.LeyLines
        dct['Projects'] = self.Projects
        dct['Espionage'] = self.Espionage
        dct['War'] = self.War
        with open('worlds/' + world + '.pickle', 'wb') as handle:
            pickle.dump(dct, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    def get_my_index(self, df, temp):
        '''
        Index finder-function (function code)
        '''
        df = df.copy()
        if len(temp)>0:
            return temp[0]
        try:
            index = max(df.index.tolist()) + 1
        except:
            print('new')
            index=0
        return index

    def add_holding(self, Provence, Regent, Type='Law', Level=0, Contested=0):
        '''
         Provence: match to provence
         Regent: match to regent
         Type: 'Law', 'Guild', 'Temple', 'Source' 
         Level: 1 to Population (or Magic for source)
         
        '''
        # get the correct df
        df = self.Holdings.copy()
        
        temp = df[df['Provence']==Provence]
        temp = temp[temp['Regent']==Regent]
        temp = temp.index[temp['Type']==Type].tolist()
        index = self.get_my_index(df, temp)
        
        df.loc[index] = [Provence, Regent, Type, Level, Contested]
        df['Level'] = df['Level'].astype(int)
        
        # set the df...
        self.Holdings = df

    def change_holding(self, Provence, Regent, Type, Level=None, Contested=None, new_Regent = None, mult_level=1):
        '''
        '''
        
        index = self.Holdings[self.Holdings['Provence'] == Provence].copy()
        index = index[index['Regent']==Regent].copy()
        index = index.index[index['Type']==Type].tolist()[0]
        
        old = self.Holdings.loc[index]
        
        if new_Regent == None:
            new_Regent = old['Regent']
        if Level == None:
            Level = (old['Level'])*mult_level  # allows dropping to zero
        else:
            Level = old['Level'] + Level
        if Contested == None:
            Contested = old['Contested']
        
        self.Holdings = self.Holdings[['Provence', 'Regent', 'Type', 'Level', 'Contested']]
        self.Holdings.loc[index] = [Provence, new_Regent, Type, Level, Contested]
        
    def remove_holding(self, Provence, Regent, Type):
        '''
        Remove all rows where Regent, Provence, Type are
        equakl to those set.
        '''
        # Holdings
        df = self.Holdings.copy()
        
        temp = df[df['Provence']==Provence] # just the provence in question
        df = df[df['Provence'] != Provence] # all others are safe
        # add back all other regents in that provence
        df = pd.concat(df, temp[temp['Regent'] != Regent], sort=False) 
        # isolate regent
        temp = temp[temp['Regent'] == Regent]
        # add back all other types
        df = pd.concat(df, temp[temp['Regent'] != Type], sort=False)
        
        #done
        self.Holdings = df

    def add_provence(self, Provence, Domain, Region, Regent, x, y
                     , Population=0, Magic=1, Law=None
                     , Capital=False, Terrain='Plains', Loyalty='Average', Taxation='Moderate'
                     , Castle=0, Castle_Name = '', Contested=False, Waterway=False):
        '''
        Provence: pkey, Name
        Domain: Name 
        Regent: Name, foreign key on Regents 
        Terrain: 'Desert', 'Tundra', 'Forest', 'Mountain', 'Glacier', 'Hills', 
                'Plains', 'Farmland', 'Steppes', 'Swamp', 'Marsh' 
        Taxation: 'Light', 'Moderate', or 'Severe'
        Loyalty: 'High', 'Average', 'Poor', or 'Rebellious'
        Population: 0 thru 9
        Magic: 1 thru 9 (lowers when population increases, minimumm 1)
        Castle: 0+ (when they fortify, they get this)
        Capital: True or False if Capital of Domain
        x,y: x and y position
        Troops: String Values of type(subtype), comma seperated
        '''
        # Provences
        df = self.Provences.copy()
        # print(Provence, df[df['Provence'] == Provence].shape[0], x, y)
        if df[df['Provence'] == Provence].shape[0] > 0:
            # Already exists!
            self.change_provence(Provence=Provence, Regent=Regent, Region=Region, Domain=Domain, Terrain=Terrain, Loyalty=Loyalty, Taxation=Taxation, Castle=Castle, Castle_Name=Castle_Name, Capital=Capital, x=x, y=y, Contested=Contested, Waterway=Waterway, Brigands=False)
        else:
            temp = df.index[df['Provence'] == Provence].tolist()
            index = self.get_my_index(df, temp)
                    
            df.loc[df.shape[0]] = [Provence, Domain, Region, Regent, Terrain, Loyalty, Taxation, Population, Magic, Castle, Castle_Name, Capital, np.array([x, y]), Contested, Waterway, False]
            df['Magic'] = df['Magic'].astype(int)
            df['Population'] = df['Population'].astype(int)
            df['Castle'] = df['Castle'].astype(int)
            # df = df.drop_duplicates(subset='Provence', keep="last")
            
            self.Provences = df

    def change_provence(self, Provence, Regent=None, Region=None, Domain=None, Population_Change=0, Terrain=None, Loyalty=None, Taxation=None, Castle=None, Castle_Name=None, Capital=None, x=None, y=None, Contested=None, Waterway=None, Brigands=False):
        '''
        None = not changed
        '''
        
        index = self.Provences.index[self.Provences['Provence'] == Provence].tolist()[0]
        old = self.Provences.loc[index]
        if Regent == None:
            Regent = old['Regent']
        if Domain == None:
            Domain = old['Domain']
        if Region == None:
            Region = old['Region']
        if Terrain == None:
            Terrain = old['Terrain']
        if Contested == None:
            Contested = old['Contested']
        if Waterway == None:
            Waterway = old['Waterway']
        try:
            loy = old['Loyalty'].replace('Rebellious','0').replace('Poor','1').replace('Average','2').replace('High','3')
            new = int(loy) + int(Loyalty)
            if new <= 0:
                Loyalty = 'Rebellious'
            if new == 1:
                Loyalty = 'Poor'
            if new == 2:
                Loyalty = 'Average'
            if new >= 3:
                Loyalty = 'High'
        except:
            if Loyalty == None:
                Loyalty = old['Loyalty']
        if Taxation == None:
            Taxation == old['Taxation']
           
        Population = old['Population'] + Population_Change
        Magic = old['Magic'] - Population_Change
        
        if Magic <= 0:
            Magic = 0
        if Population <= 0:
            Population = 0
        if Castle == None:
            Castle = old['Castle']
        if Castle_Name == None:
            Castle_Name = old['Castle Name']
        if Capital == None:
            Capital = old['Capital']
        if x == None or y == None:
            pos = old['Position']
        else:
            pos = np.array([x, y])
        self.Provences.loc[index] = [Provence, Domain, Region, Regent, Terrain, Loyalty, Taxation,
            Population, Magic, Castle, Castle_Name, Capital, old['Position'], Contested, Waterway, Brigands]
      
    def change_loyalty(self, Provence, Change):
        temp = self.Provences[self.Provences['Provence'] == Provence].copy()
        temp['Loyalty'] = temp['Loyalty'].str.replace('Rebellious','0').replace('Poor','1').replace('Average','2').replace('High','3').astype(int)
        temp['Loyalty'] = temp['Loyalty'] + Change
        N = temp.iloc[0]['Loyalty']
        if N <= 0:
            self.change_provence(Provence, Loyalty='Rebellious')
        elif N == 1:
            self.change_provence(Provence, Loyalty='Poor')
        elif N == 2:
            self.change_provence(Provence, Loyalty='Average')
        else:
            self.change_provence(Provence, Loyalty='High')
            
    def add_lieutenant(self, Regent, Lieutenant, busy=False):
        '''
        Adds a lieutenant
        '''
        df = self.Lieutenants.copy()
        
        temp = df[df['Regent']==Regent]
        temp = temp.index[temp['Lieutenant']==Lieutenant].tolist()
        index = self.get_my_index(df, temp)
        
        df.loc[index] = [Regent, Lieutenant, busy]
        
        # set the df...
        self.Lieutenants = df
        
    def change_lieutenant(self, Regent, Lieutenant, Busy=False):
        temp = self.Lieutenants[self.Lieutenants['Regent']==Regent]
        index = temp.index[temp['Lieutenant'] == Lieutenant].tolist()[0]
        self.Lieutenants.loc[index] = [Regent, Lieutenant, Busy]
        
    def add_regent(self, Regent, Name, Bloodline='', Culture='A', Player=False
                    , Class='Noble', Level=2, Alignment = 'NN', Race='Human'
                   , Str = 0, Dex = 1, Con = 0, Int = 1, Wis = 2, Cha = 3
                   , Insight = 4, Deception = 5, Persuasion = 5
                   , Regency_Points = 0, Gold_Bars = 0, Regency_Bonus = 1
                   , Attitude = 'Normal', Lieutenants=[], Archetype=None
                   , Divine = False, Arcane = False):
        '''
        Archetype: Allows for pre-loaded skill and ability mods based on NPC statblocks
        '''
        # Regents
        df = self.Regents.copy()
        
        temp = df.index[df['Regent'] == Regent].tolist()
        index = self.get_my_index(df, temp)
        if Archetype != None:
            # set the stats based on archetype
            Class, Level, Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion, Divine, Arcane = self.get_archetype(Archetype)

        df.loc[index] = [Regent, Name, Bloodline, Culture, Player, Class, Level, Alignment, Race, 
                               Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion,
                               Regency_Points, Gold_Bars, Regency_Bonus, Attitude, True, Divine, Arcane]
        df = df.drop_duplicates(subset='Regent', keep='last')
        self.Regents = df
        for Lieutenant in Lieutenants:
            self.add_lieutenant(Regent, Lieutenant)

    def change_regent(self, Regent, Name=None, Bloodline=None, Culture=None, Player=False, Class=None, Level=None, reset_level=False, Alignment = None, Race=None, Str = None, Dex = None, Con = None, Int = None, Wis = None, Cha = None, Insight = None, Deception = None, Persuasion = None, Regency_Bonus = None, Alive=None, Regency_Points=None, Gold_Bars=None, Attitude=None, Divine=None, Arcane=None):
        '''
        Make changes to a Regent.
        '''
        
        if str(Gold_Bars) == 'nan' or str(Regency_Points) == 'nan':
            self.errors.append(Regent, self.state, self.action)
            
        
        index = self.Regents.index[self.Regents['Regent'] == Regent].tolist()[0]
        try:
            old = self.Regents.loc[index]
        except:
            print('{} Errored Out...'.format(Regent))
        if old['Regent'] != Regent:
            self.errors.append(('Change regent', old['Regent'], regent))
        if Name == None:
            Name = old['Full Name']
        if Class == None:
            Class = old['Class']
        if Level == None:
            Level = old['Level']
        elif reset_level == False:
            Level = old['Level'] + Level
        if Bloodline == None:
            Bloodline = old['Bloodline']
        if Culture == None:
            Culture = old['Culture']
        if Alignment == None:
            Alignment = old['Alignment']
        if Race == None:
            Race = old['Race']
        if Str == None:
            Str = old['Str']
        if Dex == None:
            Dex = old['Dex']
        if Con == None:
            Con = old['Con']
        if Int == None:
            Int = old['Int']
        if Wis == None:
            Wis = old['Wis']
        if Cha == None:
            Cha = old['Cha']
        if Insight == None:
            Insight = old['Insight']
        if Deception == None:
            Deception = old['Deception']
        if Persuasion == None:
            Persuasion = old['Persuasion']
        if Regency_Bonus == None:
            Regency_Bonus = old['Regency Bonus']
        if Regency_Points == None: # or str(Regency_Points) == 'nan':
            Regency_Points = old['Regency Points']
        if Gold_Bars == None: # or str(Gold_Bars) == 'nan':
            Gold_Bars = old['Gold Bars']
        if Attitude == None:
            Attitude = old['Attitude']
        if Divine == None:
            Divine = old['Divine']
        if Arcane == None:
            Arcane = old['Arcane']     
        if Alive==False:  # remove references
            # Dead regents are removed at end of season, but their legacy dies now.
            self.Holdings = self.Holdings[self.Holdings['Regent'] != Regent]
            self.Relationships = self.Relationships[self.Relationships['Regent'] != Regent]
            self.Relationships = self.Relationships[self.Relationships['Other'] != Regent]
            self.Provences['Regent'] = self.Provences['Regent'].str.replace('Regent','')
        elif Alive == None:
            Alive = old['Alive']
        
        self.Regents.loc[index] = [Regent, Name, Bloodline, Culture, Player, Class, Level, Alignment, Race, 
                           Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion,
                           Regency_Points, Gold_Bars, Regency_Bonus, Attitude, Alive, Divine, Arcane]
        
    
    def kill_regent(self, Regent):
        '''
        Remove the regent from regents, Relationships, and holdings
        clear the regent from provences
        '''
        self.Holdings = self.Holdings[self.Holdings['Regent'] != Regent]  # just gone
        self.Provences['Regent'] = self.Provences['Regent'].str.replace(Regent, '')
        self.Relationships = self.Relationships[self.Relationships['Regent'] != Regent]
        self.Relationships = self.Relationships[self.Relationships['Other'] != Regent]
              
    def get_archetype(self, Archetype):
        '''
        return  Class, Level, Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion, Divine, Arcane
        '''
        if Archetype == 'Noble':
            return 'Noble', 2, 0, 1, 0, 1, 2, 3, 4, 5, 5, False, False
        elif Archetype == 'Archmage':
            return 'Archmage', 18, 0, 2, 1, 5, 2, 3, 5, 3, 3,  False, True
        elif Archetype == 'Assassin':
            return 'Assassin', 12, 0, 3, 2, 1, 0, 0, 1, 3, 0,  False, False
        elif Archetype == 'Bandit' or Archetype == 'Bandit Captain':
            return 'Bandit Captain', 10, 2, 3, 2, 2, 0, 2, 2, 4, 2,  False, False
        elif Archetype == 'Commoner':
            return 'Commoner', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,  False, False
        elif Archetype == 'Druid':
            return 'Druid', 5, 0, 1, 1, 1, 2, 0, 1, 0, 0, True, False
        elif Archetype == 'Knight':
            return 'Knight', 8, 3, 0, 2, 0, 0, 2, 0, 2, 2,  False, False
        elif Archetype == 'Lich':
            return 'Lich', 18, 0, 3, 3, 5, 2, 3, 9, 3, 3,  False, True
        elif Archetype == 'Mage':
            return 'Mage', 9, -1, 2, 0, 3, 1, 0, 3, 0, 0,  False, True
        elif Archetype == 'Hag' or Archetype == 'Green Hag':
            return 'Green Hag', 11, 4, 1, 3, 1, 2, 2, 1, 4, 2,  False, True
        elif Archetype == 'Priest':
            return 'Priest', 5, 0, 0, 1, 1, 3, 1, 1, 1, 3,  True, False
        elif Archetype == 'Cultist' or Archetype == 'Cult Fanatic':
            return 'Cult Fanatic', 6, 0, 2, 1, 0, 1, 2, 1, 4, 4,  True, False
        elif Archetype == 'Acolyte':
            return 'Acolyte', 2, 0, 0, 0, 0, 2, 0, 0, 0, 0,  True, False    
        elif Archetype == 'Berserker':
            return 'Berserker', 9, 3, 1, 3, -1, 0, -1, 0, -1, -1, False, False
        elif Archetype == 'Gladiator':
            return 'Gladiator', 15, 4, 2, 3, 0, 1, 2, 1, 2, 2, False, False
        elif Archetype == 'Scout':
            return 'Scout', 3, 0, 2, 1, 0, 1, 0, 1, 0, 0, False, False
        elif Archetype == 'Spy':
            return 'Spy', 6, 0, 2, 0, 1, 2, 3, 4, 5, 5, False, False
        elif Archetype == 'Thug':
            return 'Thug', 5, 2, 0, 2, 0, 0, 0, 0, 0, 0, False, False
        elif Archetype == 'Bard':
            return 'Bard(Spy)', 6, 0, 2, 0, 1, 2, 3, 4, 5, 5, False, True
        # if none of the above, return Noble stats
        else:
            return 'Noble', 2, 0, 1, 0, 1, 2, 3, 4, 5, 5
        
    def add_geo(self, Provence, Neighbor, Border=0, Road=0, Caravan=0, Shipping=0, RiverChasm=0):
        '''
        Geography Connection
        
        RiverChasm -> this is for bridges, determines cost of getting a road between the two
        '''
        df = self.Geography
        temp = df[df['Provence'] == Provence].copy()
        temp = temp.index[temp['Neighbor']==Neighbor].tolist()

        index = self.get_my_index(df, temp)

        # only add what's being added
        if len(temp) > 0:
            temp_ = df[df['Provence'] == Provence].copy()
            temp_ = temp_[temp_['Neighbor']==Neighbor]
            Border= Border + temp_['Border'].values[0]
            Road = Road + temp_['Road'].values[0]
            Caravan = Caravan + temp_['Road'].values[0]
            Shipping = Shipping + temp_['Shipping'].values[0]
            RiverChasm = RiverChasm + temp_['Shipping'].values[0]
        # bi-directional

        df.loc[index] = [Provence, Neighbor, Border, Road, Caravan, Shipping, RiverChasm]
        temp = df[df['Provence'] == Neighbor].copy()
        temp = temp.index[temp['Neighbor']==Provence].tolist()
        index = self.get_my_index(df, temp)

        df.loc[index] = [Neighbor, Provence, Border, Road, Caravan, Shipping, RiverChasm]
        
        # fix to zeroes and ones...
        for col in ['Border', 'Road', 'Caravan', 'Shipping']:
            df[col] = (1*(df[col]>=1)).astype(int)

        self.Geography = df 
        
    def change_geography(self, Provence, Neighbor, Border=None, Road=None, Caravan=None, Shipping=None, RiverChasm=None, repeat=True):
        temp = self.Geography[self.Geography['Provence']==Provence]
        index = temp.index[temp['Neighbor'] == Neighbor].tolist()[0]
        old = self.Geography.loc[index]
        if Border == None:
            Border = old['Border']
        if Road == None:
            Road = old['Road']
        if Caravan == None:
            Caravan = old['Caravan']
        if Shipping == None:
            Shipping = old['Shipping']
        if RiverChasm == None:
            RiverChasm = old['RiverChasm']
            
        self.Geography.loc[index] = [Neighbor, Provence, Border, Road, Caravan, Shipping, RiverChasm]
        
        if repeat == True:
            self.change_geography(Provence=Neighbor, Neighbor=Provence, Border=Border, Road=Road, Caravan=Caravan, Shipping=Shipping, RiverChasm=RiverChasm, repeat=False)
        
    def add_relationship(self, Regent, Other, Diplomacy=0, Payment=0, Vassalage=0, At_War=0, Trade_Permission=0):
        '''
        Regent -> Whose Relationships
        Other -> To whom
        Diplomacy -> how much Regent Likes Other
        Payment -> How much Regent jas agreed to pay Other every season
        Vassalage -> How many of Regent's Regency Points are paid to Other as their Liege Lord
        '''
        cols = ['Regent', 'Other', 'Diplomacy', 'Payment', 'Vassalage']
        
        df = self.Relationships.copy()
       
        temp = df[df['Regent']==Regent]
        temp = temp.index[temp['Other']==Other]
        
         # only add what's being added
        if len(temp) > 0:
            temp_ = df[df['Regent'] == Regent].copy()
            temp_ = temp_[temp_['Other']==Other]
            Diplomacy = Diplomacy + temp_['Diplomacy'].values[0]
            Payment = Payment + temp_['Payment'].values[0]
            Vassalage = Vassalage + temp_['Vassalage'].values[0]
        
        index = self.get_my_index(df, temp)
        df.loc[index] = [Regent, Other, Diplomacy, Payment, Vassalage, At_War, Trade_Permission]
        self.Relationships = df
        
    def add_troops(self, Regent, Provence, Type, Home='', Garrisoned=0):
        '''
        This is fired after a decision to buy a troop is made
        OR for setting up troops in the begining
        '''

        temp = self.troop_units[self.troop_units['Unit Type'] == Type]

        self.Troops = self.Troops.append(pd.DataFrame([[Regent, Provence, Type, temp['Maintenance Cost'].values[0], temp['BCR'].values[0], Garrisoned, Home, 0]]
                                                      , columns=['Regent', 'Provence', 'Type', 'Cost', 'CR', 'Garrisoned', 'Home', 'Injury']), ignore_index=True)
        
    def disband_troops(self, Regent, Provence, Type, Killed=False, Real=True):
        '''
        '''
        # disband the troop
        temp = self.Troops[self.Troops['Regent'] == Regent].copy()
        temp = temp[temp['Provence'] == Provence].copy()
        temp = temp.index[temp['Type'] == Type].tolist()
        if len(temp) > 0:
            # start disbanding
            if 'Mercenary' in Type.split() and Real == True:
                # oh no, potential Brigands!
                success, _ = self.make_roll(Regent, 10, 'Persuasion', adj=False, dis=False, player_gbid=None)
                if success == False:
                    self.change_provence(Provence, Brigands=True)
            if 'Levies' in Type.split() and Killed == False and Real == True:  # disbanded, so go back to their stuff.
                self.change_provence(self.Troops.loc[temp[0]]['Home'], Population_Change=1)
            self.Troops.drop(temp[0], inplace=True)
  
    def injure_troop(self, index, penalty):
        old = self.Troops.loc[index] 
    
    # The Season
    # 1. RANDOM EVENTS 
    def random_events(self, style='Birthright', Threshold=50, Regions=None):
        '''
        At the beginning of the season, the Game Master checks for 
        events that take place in each domain. A Game Master 
        may either randomly determine the event (or lack thereof), 
        or they may have a specific set of events that unravels 
        depending on the outcomes of previous seasons or the plot 
        they wish to present.
        
        override = a diction of Regent Keys and assigned random events
        style = 'Birthright' or 'Neverforged' [Replace Blood Challenge with Plague]
        Threshold: Likliehood that an NPC gets an event
        Regions = a list of regions to restrict to
        '''
        override = self.random_override
        if Threshold < 1:  # flaot to int
            Threshold = int(100*Threshold)
        temp = self.Regents[['Regent', 'Player']].copy()
        
        # filter to Regions
        if Regions != None:
            filter = pd.concat([self.Provences[self.Provences['Region']==Region].cpopy() for Region in Regions], sort=False)[['Regent', 'Provence']].copy()
            filter_ = pd.merge(filter, self.Holdings.copy(), on='Provence', how='left')[['Regent', 'Provence']].copy()
            filter = pd.concat([filter, filter_], sort=False)[['Regent', 'Player']].copy()
            temp = pd.merge(filter, temp, on='Regent', how='left')
            
        # seperate players from npcs
        npcs = temp[temp['Player']==False].copy()
        players = temp[temp['Player']==True].copy()

        npcs['Random Event'] = np.random.randint(1,100,npcs.shape[0])
        npcs
        npcs_y = npcs[npcs['Random Event']<Threshold].copy()
        npcs_n = npcs[npcs['Random Event']>=Threshold].copy()

        temp = pd.concat([players, npcs_y[['Regent', 'Player']]], sort=False)
        npcs_n['Random Event'] = 'No Event'

        # roll 2d10
        temp['Random Event'] = np.random.randint(1,10,temp.shape[0])+np.random.randint(1,10,temp.shape[0])
        temp['Random Event'] = temp['Random Event'].astype(str)
        # consult chart
        temp['Random Event'] = temp['Random Event'].str.replace('20', 'Magical Event')  
        temp['Random Event'] = temp['Random Event'].str.replace('19', 'Great Captain or Heresey') 
        temp['Random Event'] = temp['Random Event'].str.replace('18', 'Matter of Justice')
        temp['Random Event'] = temp['Random Event'].str.replace('17', 'Unrest or Rebellion')
        temp['Random Event'] = temp['Random Event'].str.replace('16', 'Intrigue')
        temp['Random Event'] = temp['Random Event'].str.replace('15', 'Trade Matter')
        temp['Random Event'] = temp['Random Event'].str.replace('14', 'Monsters')
        temp['Random Event'] = temp['Random Event'].str.replace('13', 'Brigandage')
        temp['Random Event'] = temp['Random Event'].str.replace('12', 'No Event').replace('11', 'No Event').replace('10', 'No Event').replace('9', 'No Event')
        temp['Random Event'] = temp['Random Event'].str.replace('8', 'Corruption/Crime')
        temp['Random Event'] = temp['Random Event'].str.replace('7', 'Diplomatic Matter')
        temp['Random Event'] = temp['Random Event'].str.replace('6', 'Natural Event')
        temp['Random Event'] = temp['Random Event'].str.replace('5', 'Feud')
        temp['Random Event'] = temp['Random Event'].str.replace('4', 'Festival')
        temp['Random Event'] = temp['Random Event'].str.replace('3', 'Assassination')
        if style == 'Birthright':
            temp['Random Event'] = temp['Random Event'].str.replace('2', 'Blood Challenge')
        else:
            temp['Random Event'] = temp['Random Event'].str.replace('2', 'Plague')
            
        temp = pd.concat([temp, npcs_n], sort=False)

        for reg in self.random_override.keys():  # Override is Override
            index = temp.index[temp['Regent'] == reg].tolist()[0]
            player = temp[temp['Regent'] == reg]['Player'].values[0]
            temp.loc[index] = [reg, player, self.random_override[reg]]
        self.random_override = {}
        try:
            # new season!
            self.Season = max(self.Seasons.keys())+1
            self.Action = 1
        except:
            self.Season = 0
            self.Action = 1
        
        self.Seasons[self.Season] = {}
        self.Seasons[self.Season]['Season'] = temp
        
        # Let's deal with them...
        for event in list(set(temp['Random Event'])):
            # grab the events that are the same...
            df_temp = temp[temp['Random Event'] == event]
            # run the code for it.
            if event == 'Assassination':
                self.random_event_assassination(df_temp)
            elif event == 'Blood Challenge':
                self.random_event_blood_challenge(df_temp)
            elif event == 'Brigandage' or event == 'Monsters':
                self.random_event_brigandage_or_monsters(df_temp)
            elif event == 'Crime/Corruption':
                self.random_event_corruption(df_temp)
            elif event == 'Diplomatic Matter':
                self.random_event_diplomatic_mission(df_temp)
            elif event == 'Festival':
                self.random_event_festival(df_temp)    
            elif event == 'Feud':
                self.random_event_feud(df_temp)    
            elif event == 'Great Captain or Heresy':
                selfrandom_event_great_captain_or_heresy(df_temp)
            elif event == 'Intrigue':
                self.random_event_intrigue(df_temp)
            elif event == 'Magical Event':
                self.random_event_magical_event(df_temp)    
            elif event == 'Matter of Justice':
                self.random_event_matter_of_justice(df_temp)
            elif event == 'Natural Event':
                self.random_event_natural_event(df_temp)
            elif event == 'Trade Dispute':
                self.random_event_trade_dispute(df_temp)
            elif event == 'Unrest or Rebellion':
                self.random_event_trade_dispute(df_temp) 
                
    def random_event_assassination(self, df):
        '''
        An enemy of the regent, whether it be one they have feuded with before or one that has an otherwise 
        hidden grievance with the scion, sends agents to extinguish their life. Typically, this is played out
        as an encounter with an assassin, or group of assassins, as determined by the Game Master. These 
        events typically lead to further intrigue -- assuming the regent survives -- as the organizer(s) of 
        the attempt are sought.
        
        -Determine Who Sent the Assassin
        -Assign them assassination action?
        '''
        df_copy = df.copy()        
        df = pd.merge(df, self.Relationships.copy(), on='Regent', how='left').fillna(0)
        
        # neighbors by provence
        ptemp = pd.concat([self.Provences[self.Provences['Regent']==reg][['Regent', 'Provence']].copy() for reg in set(df['Regent'])], sort=False)
        ptemp['Other'] = ptemp['Regent']
        ptemp['Neighbor'] = ptemp['Provence']
        rand_temp = pd.merge(self.Geography.copy(),ptemp[['Regent', 'Provence']],on='Provence',how='left')
        rand_temp = pd.merge(rand_temp,ptemp[['Other', 'Neighbor']], on='Neighbor', how='left' )
        df2 = pd.merge(df_copy, rand_temp[['Regent','Other']], on='Regent', how='left').fillna(0)
        df2 = df2[df2['Other'] != 0].copy()
        df2 = df2[df2['Other'] != df2['Regent']].copy()
        df = pd.concat([df,df2], sort=False).fillna(0).groupby(['Regent', 'Other']).max().reset_index()


        # holding of same type in same place or nearby place
        temph = self.Holdings.copy()
        
        temph['Other'] = temph['Regent']
        temph = pd.merge(temph[['Regent', 'Provence', 'Type']], temph[['Other', 'Provence', 'Type']], on='Provence')
        temph['Rivals'] = 1*(temph['Type_x'] == temph['Type_y'])
        temph = temph[temph['Regent'] != temph['Other']]

        # nearby
        temph_ = self.Holdings.copy()
        temph_ = pd.merge(temph_,self.Geography[['Provence', 'Neighbor', 'Border']].copy(),on='Provence', how='left')
        temph_ = temph_[temph_['Border']==1].copy()
        temph__ = self.Holdings.copy()
        temph__['Neighbor'] = temph__['Provence']
        temph__['Other'] = temph__['Regent']
        temph_ = pd.merge(temph_, temph__[['Neighbor', 'Other', 'Type']], on='Neighbor', how='left')
        temph_['Rivals'] = temph_['Type_x'] == temph_['Type_y']
        temph_ = temph_[temph_['Regent'] != temph_['Other']]
        temph = pd.concat([temph, temph_[temph.keys()]], sort=False).fillna(0)


        df = pd.concat([df,temph[['Regent', 'Other','Rivals']]], sort=False).fillna(0).groupby(['Regent', 'Other']).max().reset_index()


        df = df[df['Other'] != 0].copy()
        rand_temp =  self.Regents[['Regent', 'Alignment']].copy()
        rand_temp['Other'] = rand_temp['Regent']
        df = pd.merge(df, rand_temp[['Other', 'Alignment']], on='Other', how='left').fillna(0)

        # alignment
        # 10 for Evil, -10 for Good, 5 for chaotic, -5 for Lawful
        df['Alignment'] = df['Alignment'].str.replace('LG','-15').replace('LN','-5').replace('LE','5')
        df['Alignment'] = df['Alignment'].str.replace('NG','-10').replace('NN','0').replace('N','0').replace('NE','10') 
        df['Alignment'] = df['Alignment'].str.replace('CG','-5').replace('CN','5').replace('CE','15')
        df = df.fillna(0)
        df['Likliehood'] = -1*df['Diplomacy'] + 5*df['At War'] - 10*df['Vassalage'] + df['Payment'] + df['Alignment'].astype(int)+3*df['Rivals']
        
        # must have a guild holding...
        temp = self.Holdings[self.Holdings['Type']=='Guild'].copy()
        temp['Other'] = temp['Regent']
        df = pd.merge(temp[['Other']], df, on='Other', how='left')

        
        df2 = df[['Regent', 'Likliehood']].groupby('Regent').max().reset_index()
        df = pd.merge(df2, df, on=['Regent', 'Likliehood'], how='left')
        try:
            self.Seasons[self.Season][self.Action]
        except:
            self.Seasons[self.Season][self.Action] = {}
        try:
            self.Seasons[self.Season][self.Action]['Override']   
        except:
            self.Seasons[self.Season][self.Action]['Override'] = {}
        for regent in set(df_copy['Regent']):
            df1 = df[df['Regent']==regent].copy()
            if df1.shape[0]>0:
                self.Seasons[self.Season][self.Action]['Override'][df1.iloc[0]['Other']] = (10, 'enemy',regent)

    def random_event_blood_challenge(self, df):
        '''
        A blooded champion or an awnsheghlien comes looking for the regent and issues them a challenge, in 
        the form of a duel, insult, or announcement of impending invasion. The ultimate goal of this agent is
        to conquer the regent and usurp their bloodline by force
  
        - Determine if the regent survives; if so, add 1 to ther Regency_Bonus.  If not, well, that happened.
        
        Survival Chance?  Level check, dc 15 (plus regency)
        '''
        df = pd.merge(df, self.Regents[['Regent', 'Level', 'Regency Points', 'Regency Bonus']].copy(), on='Regent', how='left')

        # seperate players & npcs
        dfp = df[df['Player']==True]
        dfn = df[df['Player']==False]

        # determine if player survives...
        for i, row in dfp.iterrows():
            ans = 0
            while ns.lower()[0] != 'y' or ans.lower()[0] != 'n':
                self.clear_screen()
                print('     --- BLOOD CHALLENGE ---')
                ans = input('Did {} survive their Blood Challenge? (y/n)')
                if ans.lower()[0] == 'y':
                    self.change_regent(row['Regent'],Regency_Bonus = row['Regency Bonus'] + 1)
                elif ans.lower()[0] == 'n':
                    self.change_regent(row['Regent'],Alive=False)
                    
        # get bonus for npcs... life or death, so
        dfn1 = dfn[dfn['Regency Points']>=10].copy()
        dfn2 = dfn[dfn['Regency Points']<10].copy()
        dfn1['Bonus'] = 10
        dfn2['Bonus'] = dfn2['Regency Points']
        dfn = pd.concat([dfn1, dfn2], sort=False)

        dfn['Check'] =  np.random.randint(1,20,dfn.shape[0]) + dfn['Level'] + dfn['Bonus']
        dfn1 = dfn[dfn['Check']>=15].copy()
        dfn2 = dfn[dfn['Check']<15].copy()
        for i, row in dfn1.iterrows():
            self.change_regent(row['Regent'],Regency_Bonus = row['Regency Bonus'] + 1, Regency_Points=row['Regency Points']-row['Bonus'])
        for i, row in dfn2.iterrows():
            self.change_regent(row['Regent'], Alive=False,  Regency_Points=row['Regency Points']-row['Bonus'])
        
    def random_event_brigandage_or_monsters(self, df):
        '''
        A group of bandits, a single monster such as a griffon or wyvern, or a similar threat manifests 
        itself somewhere in the regent’s domain. If left to fester without being tended to, the targeted 
        provinces decline in loyalty by one grade for each season the threat is allowed to remain unchallenged.

        To deal with this event, the regent may dispatch a lieutenant for the season to raise local 
        adventurers to deal with the threat (losing their provided bonus action) or issue a Decree to that 
        effect. If the danger is particularly severe, the regent may find themselves forced to raise a levy 
        or dispatch units of troops to deal with the threat.   

        - Monster -> Lieutenant [Lietenant is marked busy the entire season]
        - Brigandage -> Troops need to be moved to the provence
        - Ignore if Regent does not have a provence.
        
        brigandage
        '''
        # Start with Brigands
        dfb = df[df['Random Event']=='Brigandage']
        # see if there are provences...
        dfb = pd.merge(dfb, self.Provences[self.Provences['Brigands']==False][['Provence', 'Regent']].copy(), on='Regent', how='inner')
        dfb['Roll'] = np.random.randint(1,100,dfb.shape[0])
        df1 = dfb[['Regent','Roll']].groupby('Regent').max().reset_index()
        dfb = pd.merge(df1, dfb, on=['Regent','Roll'], how='left')

        # add brigands...
        for i, row in dfb.iterrows():
            self.change_provence(row['Provence'], Brigands=True)
        
        # Monsters!
        dfm = df[df['Random Event']=='Monsters']
        # see if there are provences...
        dfm = pd.merge(dfm, self.Provences[['Provence', 'Regent']].copy(), on='Regent', how='inner')

        dfmn = dfm[dfm['Player'] == False].copy()
        dfmp = dfm[dfm['Player'] == True].copy()
        for reg in set(dfmn['Regent']):
            temp = self.Lieutenants[self.Lieutenants['Regent'] == reg]
            lst = list(temp['Lieutenant'])
            if len(lst) > 0:
                self.change_lieutenant(reg, lst[0], Busy=True)
        for reg in set(dfmp['Regent']):
            ans = 0
            while ans != 1:
                self.clear_screen()
                print('           --- Monsters ---')
                print('How will {} deal with Monsters in their realm?'.format(self.Regents[self.Regents['Regent']==reg]['Full Name']))
                print()
                print('[1] Adventure - Deal with it personally')
                lieu = False
                if self.Lieutenants[self.Lieutenants['Regent']==reg].shape[0] > 0:
                    print('[2] Send Lieutenant')
                    lieu = True
                ans = input('Type a Valid Number')
                if ans == '1':
                    self.add_to_override(Regent, ('Adventure'))
                elif ans == 2 and self.Lieutenants[self.Lieutenants['Regent']==reg].shape[0] > 0:
                    ans = 1
                    self.change_lieutenant(reg, lst[0], Busy=True)
                    
    def random_event_corruption(self, df):
        '''
        An agent of the regent’s court, a high-ranking priest, or a devious guildmaster are publicly accused 
        of corruption. A particularly influential regent may be able to safely ignore this accusation, but 
        for a fresh, inexperienced ruler this may be a stain they must scrub out immediately.
        
        The Game Master determines whether or not the accusations are true, and the regent’s response 
        determines the outcome. This may take the form of ordering and funding an investigation, which costs
        1d4 GB each season it continues, or calling all parties to court to deal with the matter personally
        (which requires that the regent expended funds on court costs this season).
        
        NPCs lose 1d4 GB
        '''
        df = pd.merge(df, self.Regents[['Regent', 'Gold Bars']], on='Regent', how='left')
        df['Roll'] = np.random.randint(1,4,df.shape[0])

        df1 = df[df['Gold Bars'] >= df['Roll']]
        df2 = df[df['Gold Bars'] < df['Roll']]
        df1['Cost'] = df1['Roll']
        df2['Cost'] = df2['Gold Bars']

        df = pd.concat([df1, df2], sort=False)
        for i, row in df.iterrows():
            self.change_regent(row['Regent'], Gold_Bars = row['Gold Bars'] - row['Cost'])
        
    def random_event_diplomatic_mission(self, df):
        '''
        The agents of a foreign ruler arrive in the regent’s domain and expect hospitality and the attentions 
        of the regent for at least part of the season. If the regent does not have court costs for this 
        season, the mission leaves and the realm’s reputation with that foreign regime declines.

        If the diplomats remain, they may ask a favor of the regent or offer some manner of mutual agreement, 
        as determined by the Game Master. Typically, this involves a trade route request (which may require 
        the regent build roads) or similar mutually-beneficial arrangement.
        
        Pick a random NPC regent as a target.  
        
        assign diplomatic_mission
        '''
        df = df.copy()
        temp = pd.merge(self.Regents[['Regent']].copy(), df, on='Regent', how='outer').fillna(0)
        temp = temp[temp['Random Event'] == 0].copy()
        temp = pd.merge(self.Provences.copy(), temp, on='Regent', how='left')
        lst = list(set(temp['Regent']))
        num = len(lst)

        df['Other'] = np.random.randint(0, num-1, df.shape[0]).astype(str)
        for i in range(num-1,-1,-1):
            df['Other'] = df['Other'].str.replace(str(i),lst[i])

        df['Type'] = np.random.randint(1,3,df.shape[0]) + 32

        df['who'] = df['Type'].astype(str).str.replace('33','friend').replace('34','rando').replace('35','rando')
                
        try:
            self.Seasons[self.Season][self.Action]
        except:
            self.Seasons[self.Season][self.Action] = {}
        try:
            self.Seasons[self.Season][self.Action]['Override']   
        except:
            self.Seasons[self.Season][self.Action]['Override'] = {}
        for regent in set(df['Regent']):
            df1 = df[df['Regent']==regent].copy()
            self.Seasons[self.Season][self.Action]['Override'][df1.iloc[0]['Other']] = (df1.iloc[0]['Type'],df1.iloc[0]['who'], regent)
        
    def random_event_festival(self, df):
        '''
        A local festival springs up in one of the regent’s provinces, its exact nature determined by the Game 
        Master. Possibilities include a religious holiday or a festival celebrating a local hero. These kinds 
        of events can net the regent great goodwill from the people if time and resources are expended to 
        support it, or better yet, attend in person.

        The regent can ignore this event safely, or expend 1d4 GB to send gifts and support to the festival. 
        Loyalty in the province increases by one grade if this is done.
        
        
        Ask Players if they want to spend money on gifts.
        
        NPCs spend it if they have 10+ GB.
        
        If spent, random provence increases in Loyalty by 1.
        '''
        # roll 1d4
        df = pd.merge(df, self.Regents[['Regent', 'Gold Bars']], on='Regent', how='left')
        # df = df[df['Gold Bars']>10]
        df['Cost'] = np.random.randint(1,4,df.shape[0])
        # get provences
        temp = pd.merge(df['Regent'], self.Provences[['Provence', 'Regent', 'Loyalty']].copy(), on='Regent', how='left').fillna('High')
        temp = temp[temp['Loyalty']!='High'].copy()  # pointless
        # where it would help
        temp['Loyalty'] = temp['Loyalty'].str.replace('Rebellious','1').replace('Poor','2').replace('Average',3).astype(int)
        # merges
        temp = pd.merge(temp[['Regent', 'Loyalty']].groupby('Regent').min().reset_index(), temp, on=['Regent', 'Loyalty'], how='left')
        # change loyalty to the new value
        df = pd.merge(temp, df, on='Regent', how='left')
        df['Loyalty'] = df['Loyalty'].astype(str).str.replace('1', 'Poor').replace('2', 'Average').replace('3','High')
        # update the gold and loyalty
        lst = []
        for i, row in df.iterrows():
            if row['Regent'] not in lst:
                if row['Player'] == False:
                    if row['Gold Bars'] > 10:
                        self.change_regent(row['Regent'], Gold_Bars = row['Gold Bars'] - row['Cost'])
                        self.change_provence(row['Provence'], Loyalty=row['Loyalty'])
                        lst.append(row['Regent'])
                else:  # Players get a choice
                    ans = 'hi'
                    while ans.lower()[0] != 'y' and ans.lower()[0] != 'n':
                        self.clear_screen()
                        print('{}: There is a festival in {}; would you like to provide gifts for {} gold bars [you have {} Gold Bars]?'.format(self.Regents[self.Regents['Regent']==row['Regent']]['Full Name'], row['Province'], row['Cost'], row['Gold Bars'] ))
                        ans = imput('[y/n]')
                        if ans == 'y':
                            self.change_regent(row['Regent'], Gold_Bars = row['Gold Bars'] - row['Cost'])
                            self.change_provence(row['Provence'], Loyalty=row['Loyalty'])
                            lst.append(row['Regent'])
                    
    def random_event_feud(self, df):
        '''
        Two influential forces collide in the regent’s domain. Possibilities include religious leaders, local 
        heroes, brawling adventurers, or even foreign agents on holiday. Ignoring this event has consequences
        in the form of damages to the realm that cost 1d6 GB to fix, and may also cause loyalty to degrade.

        Addressing the problem can be trickier. Even if one side is grievously out of line, siding with one 
        party or the other causes strain between the regent that the party that is ruled against. This party 
        may become a future thorn in their side.
        
        for NPCs, just -1d6 GB and drop loyalty in a provence by 1 if chosen provence is Average or High.
        (same for PCs...)
        '''
        df = pd.merge(df, self.Regents[['Regent', 'Gold Bars']], on='Regent', how='left')
        df['Cost'] = np.random.randint(1,6,df.shape[0])

        # not allowed to go negative
        df1 = df[df['Cost']<df['Gold Bars']]
        df2 = df[df['Cost']>=df['Gold Bars']]
        df2['Cost'] = df2['Gold Bars']
        df = pd.concat([df1, df2], sort=False)

        temp = pd.merge(df['Regent'], self.Provences[['Provence', 'Regent', 'Loyalty']].copy(), on='Regent', how='left').fillna('Rebellious')
        temp = temp[temp['Loyalty']!='Rebellious'].copy()  # pointless
        temp['Loyalty'] = temp['Loyalty'].str.replace('Poor','1').replace('Average','2').replace('High',3).astype(int)
        temp = pd.merge(temp[['Regent', 'Loyalty']].groupby('Regent').min().reset_index(),temp,on=['Regent', 'Loyalty'], how='left')


        df = pd.merge(temp, df, on='Regent', how='left')
        df = df[df['Provence']!='High'].copy()


        df['Loyalty'] = df['Loyalty'].astype(str).str.replace('1', 'Poor').replace('2', 'Poor').replace('3','Average')
        lst = []
        for i, row in df.iterrows():
            if row['Regent'] not in lst:
                if row['Player'] == False:
                    self.change_regent(row['Regent'], Gold_Bars = row['Gold Bars'] - row['Cost'])
                    self.change_provence(row['Provence'], Loyalty=row['Loyalty'])
                    lst.append(row['Regent'])
                else:
                    ans = '0'
                    while ans.lower()[0] != '1' and ans.lower()[0] != '2':
                        self.clear_screen()
                        print('{}, there is a Feud in {}, would you like to try and deal with it, or just pay {} for the damages?'.format(self.Regents[self.Regents['Regent']==row['Regent']]['Full Name'], row['Province'], row['Cost']))
                        ans = input('[1] for Adventure to deal with it, [2] to pay for damages.')
                        if ans == '1':
                            self.add_to_override('Regent', ('Adventure'))
                            lst.append(row['Regent'])
                        elif ans == '2':
                            self.change_regent(row['Regent'], Gold_Bars = row['Gold Bars'] - row['Cost'])
                            self.change_provence(row['Provence'], Loyalty=row['Loyalty'])
                            lst.append(row['Regent'])
                        
    def random_event_great_captain_or_heresy(self, df):
        '''
        A mighty individual rises to prominence in the regent’s domain. The Game Master determines the traits 
        and goals of the individual in question; they may be a potential ally or lieutenant, or a demagogue 
        attempting to rally the people against the regent. In the case of the former, this may lead to an 
        Unrest event on the following season.
        
        INFO great_captain_heresy
        
        If the Liuetenent event is played, all is well.  if not, Unrest added to Override.
        '''
        # add unrest to random_override
        for i, row in df.iterrows():
            self.random_override[row['Regent']] = 'Unrest or Rebellion'
        
    def random_event_intrigue(self, df):
        '''
        What’s a good story of lords and ladies without some court intrigue? Gossip, rumor-mongering, or even
        a death by poison may be the impetus for this event, where the regent and their court become 
        embroiled in the affair. Poorly handled, this event can cause degradations in loyalty and reputation.
        
        The regent must determine a course of action when this event arises, even if it is a simple Decree. 
        If left unaddressed, this event has a high chance of turning into a Feud or Matter of Justice on the 
        next season.
        
        if no decree action, then Feud or Matter of Justice next season (for npcs)
        '''
        df = df.copy()
        # add Mater of Jutice or Feud to Override
        df['Roll'] = np.random.randint(1,3,df.shape[0])
        for i, row in df.iterrows():
            if row['Roll'] == 1:
                self.random_override[row['Regent']] = 'Matter of Justice'
            else:
                self.random_override[row['Regent']] = 'Feud'
        
    def random_event_magical_event(self, df):
        '''
        A supernatural event takes place somewhere in the regent’s domain. The exact nature of this event 
        varies depending on the events of the campaign and the Game Master’s whim, but some possible random 
        outcomes are as follows. Roll 1d6 and consult the list below.
        
        for NPCs, all Liutenants busy.
        
        1 - Bizarre Weather (+2)
        A supernatural storm, bizarre heat wave, or summer snow washes over a province in the regent’s 
        domain. The source of the event might be the result of a wizard conducting experiments in secret with
        grave consequences, or the stirring of an elemental spirit long imprisoned. Loyalty and holding 
        income is at risk until the situation is resolved.

        2 - Mebhaighl Surge (+3)
        Sources and ley lines run amok. Through the assault of a distant mage-regent or the presence of a 
        magic-devouring entity, Source holdings become tainted and ley lines sputter and atrophy in a random 
        province until the source of the event can be dislodged.

        3 - Shadow Incursion (+3)
        The Shadow World’s touch grows strong in a place within one of the regent’s provinces. A graveyard, 
        battlefield, or blighted temple all make good centers for the event. The incursion is strong enough 
        to allow creatures from the Shadow World to invade by night, ravaging surrounding villages and 
        causing loyalty in the province to steadily decay until the problem is dealt with.

        4 - Starfall (+2)
        A celestial object impacts somewhere within a random province the regent controls. Loyalty in that 
        province immediately decays by one grade as fear and superstition run wild in the land. The object 
        may be a simple meteorite of precious metals and iron (+1d6 GB) or a gruesome monster long banished 
        in the heavens. Either way, the situation must be handled quickly before the populace’s fear gets the
        better of them.

        5 - Supernatural Army (+4)
        A previously unknown force emerges somewhere within the regent’s domain. A 1d3 units of monsters 
        (typically of the fiend or undead type) are summoned or tear their way through a rift into Cerilia 
        and begin to occupy the province, slaughtering its people on each domain turn until nothing remains 
        but death and ruin. The force always moves together, and each season it remains without being 
        completely destroyed allows another unit of the same type to manifest at the beginning of the 
        following season.

        6 - Dragon Awakens (+5)
        One of Cerilia’s few remaining dragons awakens in a province, tearing the earth apart in the throes 
        its fitful slumber. The dragon begins devastating the local terrain until it can be slain or 
        convinced to go elsewhere. Be warned: Cerilia’s dragons are creatures of raw, elemental power and all 
        are of ancient strength. They care nothing for the politics of humans, elves, or dwarves and will 
        devour all indiscriminately in their elemental urges.
        '''
         # Stole code from Monsters!
        dfm = df.copy()
        # see if there are provences...
        dfm = pd.merge(dfm, self.Provences[['Provence', 'Regent']].copy(), on='Regent', how='inner')

        dfmn = dfm[dfm['Player'] == False].copy()
        dfmp = dfm[dfm['Player'] == True].copy()
        for reg in set(dfmn['Regent']):
            temp = self.Lieutenants[self.Lieutenants['Regent'] == reg]
            lst = list(temp['Lieutenant'])
            for a in lst > 0:
                self.change_lieutenant(reg, a, Busy=True)
        for reg in set(dfmp['Regent']):
            ans = 0
            while ans != 1:
                self.clear_screen()
                print('           --- Magical Event ---')
                print('How will {} deal with a Magical Event in their realm?'.format(self.Regents[self.Regents['Regent']==reg]['Full Name']))
                print()
                print('[1] Adventure - Deal with it personally')
                lieu = False
                if self.Lieutenants[self.Lieutenants['Regent']==reg].shape[0] > 0:
                    print('[2] Send Lieutenants')
                    lieu = True
                ans = input('Type a Valid Number')
                if ans == '1':
                    self.add_to_override(Regent, ('Adventure'))
                elif ans == 2 and self.Lieutenants[self.Lieutenants['Regent']==reg].shape[0] > 0:
                    temp = self.Lieutenants[self.Lieutenants['Regent'] == reg]
                    lst = list(temp['Lieutenant'])
                    for a in lst > 0:
                        self.change_lieutenant(reg, a, Busy=True)
                        
    def random_event_matter_of_justice(self, df):
        '''
        The regent is personally called upon to adjudicate a legal matter, typically between greater powers
        in their domain or even other regents who require an impartial voice of equal standing. The encounter
        should be played out, and the regent must expend 1d4 GB to fund the proceedings in their realm. 
        Successfully mediating the dispute causes the regent’s reputation with one or both parties to 
        increase, depending on the ruling.

        The regent may decline to preside over the affair if they wish with no ill effects, but a regent that
        repeatedly does this whenever this event arises may suffer the consequences of their insular nature.
        
        NPCs lose 1d4 Gold Bars (so do PCs, this is an rp opertunity for pcs)
        '''
         # roll 1d4
        df = pd.merge(df, self.Regents[['Regent', 'Gold Bars']], on='Regent', how='left')
        # df = df[df['Gold Bars']>10]
        df['Cost'] = np.random.randint(1,4,df.shape[0])
        
        # shouldn't cause them to go into negatives
        df1 = df[df['Cost']> df['Gold Bars']]
        df2 = df[df['Cost']<=df['Gold Bars']]
        df1['Cost'] = df1['Gold Bars']
        df = pd.concat([df1, df2], sort=False)
       
        lst = []
        for i, row in df.iterrows():
            if row['Regent'] not in lst:    
                self.change_regent(row['Regent'], Gold_Bars = row['Gold Bars'] - row['Cost'])
                lst.append(row['Regent'])
                   
    def random_event_natural_event(self, df):
        '''
        An earthquake, flood, landslide, or other natural disaster strikes somewhere in the regent’s domain. The regent may ignore the event and lose one level of loyalty in the affected province. If the regent
        expends 1d4 GB or dispatches a lieutenant to deal with the aftermath, this loss can be prevented.
        
        NPCs make 1 lieutenant busy or lose 1d4 Gold Bars
        '''
        # see if there are provences...
        df = pd.merge(df, self.Provences[['Provence', 'Regent', 'Loyalty']].copy(), on='Regent', how='inner')
        df = pd.merge(df, self.Regents[['Regent', 'Gold Bars', 'Attitude']].copy(), on='Regent', how='left')
        # in case they cheap out
        df['Loyalty'] = df['Loyalty'].str.replace('Poor','Rebellious').replace('Average', 'Poor').replace('High','Average')
        df['Roll'] = np.random.randint(1, 1000, df.shape[0])
        df = pd.merge(df[['Regent', 'Roll']].groupby('Regent').max().reset_index(), df, on=['Regent', 'Roll'])
        df['Cost'] = np.random.randint(1, 4, df.shape[0])
        dfn = df[df['Player'] == False].copy()
        dfp = df[df['Player'] == True].copy()
        
        for i, row in dfn.iterrows():
            temp = list(self.Lieutenants[self.Lieutenants['Regent'] == row['Regent']]['Lieutenant'].copy())
            if len(temp) > 0:
                self.change_lieutenant(row['Regent'], temp[0], Busy=True)
            elif row['Cost'] >= row['Gold Bars'] and row['Attitude'] != 'Aggressive':
                self.change_regent(row['Regent'],Gold_Bars = row['Gold Bars'] - row['Cost'])
            else:
                self.change_provence(row['Provence'], Loyalty=row['Loyalty'])
        for i, row in dfp.iterrows():
            temp = list(self.Lieutenants[self.Lieutenants['Regent'] == row['Regent']]['Lieutenant'].copy())
            ans = 0
            while ans == 0:
                self.clear_screen()
                print('   --- Natural Disaster ---  ')
                print('A Natural disaster has struck in {}.  How will {} respond?'.format(row['Provence'], self.Regents[self.Regents['Regent']==row['Regent']]['Full Name']))
                print()
                print('[1] Ignore it and let {} fall to {} loyalty.'.format(row['Provence'], row['Loyalty']))
                if row['Cost'] <= row['Gold Bars']:
                    print('[2] Pay {} Gold Bars in relief aid.'.format(row['Cost']))
                if len(temp) > 0:
                    print('[3] Send a Lieutenant to deal with the disaster.')
                ans = input()
                if ans == '1':
                    self.change_provence(row['Provence'], Loyalty=row['Loyalty'])
                elif ans == '2' and row['Cost'] <= row['Gold Bars']:
                    self.change_regent(reg,Gold_Bars = row['Gold Bars'] - row['Cost'])
                elif ans == '3' and len(temp) > 0:
                    self.change_lieutenant(reg, lst[0], Busy=True)
                else:
                    ans = 0
                    
    def random_event_trade_dispute(self, df):
        '''
        A trade route or guild holding that the regent owns or connects to falls under dispute, and does not 
        generate GB this season. If the regent has no trade routes or guild holdings, this instead counts as 
        no event. As long as the regent ignores this event, the effect persists.  

        The regent will need to engage in a Diplomacy or Grant action in order to mediate the dispute and 
        return the holding or route to functioning order.
        
        disrupt a trade route or contest a holding until Grant or Diplomacy is done.
        (gonna get rid of the trade route to make life easier)
        '''
        df2 = df.copy()
        # get guilds
        df1 = pd.merge(df, self.Holdings[self.Holdings['Type']=='Guild'][['Regent', 'Provence', 'Type']], on='Regent', how='left').fillna(0)
        df1 = df1[df1['Provence'] != 0].copy()
        # get trade routes
        df2 = pd.merge(df2, self.Provences[['Regent', 'Provence']].copy(), on='Regent', how='left')
        df2 = pd.merge(df2, pd.concat([self.Geography[self.Geography['Caravan']==1].copy(),self.Geography[self.Geography['Shipping']==1].copy()], sort=False), on='Provence', how='left')               
         
        df = pd.concat([df1, df2], sort=False).fillna(0)
        df['roll'] = np.random.randint(1,100,df.shape[0])
        df = df.sort_values('roll')
        lst = []
        for i, row in df.iterrows():
            if row['Regent'] not in lst:
                if row['Type'] == 'Law':
                    self.change_holding(row['Regent'], row['Provence'], Contested = 1)
                    lst.append(row['Regent'])
                if row['Caravan'] == 1:
                    self.change_geography(row['Provence'], row['Neighbor'], Caravan=0)
                if row['Shipping'] == 1:
                    self.change_geography(row['Provence'], row['Neighbor'], Shipping=0)
        
    def random_event_unrest(self, df):
        '''
        Grave unrest takes hold in a random province within the regent’s domain. The cause may be a rebel 
        leader, the antagonism of a distant ruler inciting rebellion, or other event as the Game Master 
        determines. The province immediately drops in loyalty by two grades. If this results in the province 
        becoming rebellious, the province immediately raises as many levies as possible, which are hostile to
        the regent.

        These units will rampage across the regent’s domain until quelled by force or negotiation. The 
        loyalty effects endure until the regent finds another way to return the province to its previous 
        state of affairs.
        
        New regent Created, gains population in levies in the target's domain if rebellious hit....all levies have that
        provence set to home.
        '''
        df = pd.merge(df, self.Provences[['Regent', 'Provence', 'Loyalty', 'Population']].copy(), on='Regent')
        df['Roll'] = np.random.randint(1, 1000, df.shape[0])
        df = df.sort_values('Roll')

        lst = []
        for i, row in df.iterrows():
            if row['Regent'] not in lst:
                lst.append(row['Regent'])
                if row['Loyalty'] == 'High':
                    self.change_provence(row['Provence'], Loyalty='Poor')
                elif row['Loyalty'] == 'Average':
                    self.change_provence(row['Provence'], Loyalty='Rebellious')
                else:
                    check = self.Regents[self.Regents['Regent'] == Regent+'_rebel'].copy()
                    if check.shape[0] == 0:
                        self.add_regent(Regent+'_rebel', Name=row['Provence']+ ' Rebellion!', Archetype='Commoner')
                    enemy = Regent+'_rebel'
                    self.add_relationship(enemy, Regent, Diplomacy = -3, At_War=1)
                    self.change_provence(row['Provence'], Loyalty='Rebellious', Population_Change=-1*row['Population'])
                    for a in range(row['Population']):
                        self.add_troops(enemy, row['Provence'], 'Levies', home_provence=row['Provence'])
        
    # 2. DOMAIN INITIATIVE  
    def domain_initiative(self):
        '''
        This step is only necessary when there are domains in 
        conflict, or when the order of events is extremely critical. 
        When only players are involved (and they are not in conflict 
        for whatever reason), they may take their domain actions in 
        any order they choose before moving to the next domain 
        action round (but all players must take their domain action 
        before moving to the next round).

        Domain initiative is rolled making a Bloodline ability check 
        (that is, rolling a d20 and adding one's Bloodline modifier). 
        Once the action rounds begin, regents take turns based on 
        this initiative order, as though they were engaging in combat 
        (for in many cases, they are indeed doing just that).
        
        Bloodline Modifier = Regency Bonus, for non-Birthright Worlds
        '''
        
        temp = self.Regents[['Regent', 'Regency Bonus']].copy()
        temp['Initiative'] =  np.random.randint(1,20,temp.shape[0]) + temp['Regency Bonus']
        
        Season = pd.merge(self.Seasons[self.Season]['Season'], temp[['Regent', 'Initiative']], on='Regent', how='left')
        self.Seasons[self.Season]['Season'] = Season.sort_values('Initiative', ascending=False)
    
    # 3. COLLECT REGENCY POINTS
    def collect_regency_points(self):
        '''
        As outlined previously, a regent collects Regency Points 
        equivalent to their Domain Power (sum of all levels of all 
        holdings and provinces) plus their Bloodline score modifier.
        '''
        # collect keys
        regents = self.Regents.copy()
        keys = list(regents.copy().keys())

        # Provinces
        df = self.Provences.copy()
        df = df[df['Contested'] == False]  # no rp from contested holding
        df['Regency Points Add'] = df['Population']
        df = df[['Regent', 'Regency Points Add']]

        # holdings
        temp = self.Holdings.copy()
        temp = temp[temp['Contested'] == 0]  # no rp from contested holding
        temp['Regency Points Add'] = temp['Level']
        df = pd.concat([df, temp[['Regent','Regency Points Add']]], sort=False)
       
        # tribute from Vassalage
        temp = self.Relationships[['Other', 'Vassalage']].copy()
        temp['Regent'] = temp['Other']
        temp['Regency Points Add'] = temp['Vassalage']
        df = pd.concat([df, temp[['Regent','Regency Points Add']]], sort=False)  # add to the liege
        temp = self.Relationships[['Regent', 'Vassalage']].copy()
        temp['Regency Points Add'] = -1*temp['Vassalage']
        df = pd.concat([df, temp[['Regent','Regency Points Add']]], sort=False)  # take from the others
        
        # calculation
        df = df.groupby('Regent').sum().reset_index()  # this should be it
        temp = pd.merge(self.Regents.copy(),df,on='Regent', how='left').fillna(0)
        temp['Regency Points'] = temp['Regency Points'].astype(int) + temp['Regency Points Add'].astype(int)
        self.Seasons[self.Season]['Season'] = pd.merge(self.Seasons[self.Season]['Season'], temp[['Regent','Regency Points']], on='Regent', how='left').fillna(0)
        self.Regents = temp[keys]
        
    # 4. TAXATION, COLLECTION, AND TRADE
    # STILL NEED OCCUPIED FORCES THING
    def collect_gold_bars(self):
        '''
        At this phase of the season, each regent declares taxation and 
        collects income in the form of Gold Bars. This process can be 
        heavy on the rolls, so for groups who wish to expedite this 
        process, there are flat values that may be used instead.
        '''
        cols = self.Regents.copy().keys()
        
        # 4.1 & 4.2 Taxation From Provences
        df = pd.DataFrame(columns=['Regent', 'Revenue', 'Provence'])
        
        # set taxtation
        temp = self.Regents[self.Regents['Player']==True]
        law = self.Holdings.copy()
        law = law[law['Contested'] == 0]  # no gb from contested holdings
        law = law[law['Type']=='Law'].copy()
        
        for i, row in temp.iterrows():
            check = 0
            while check == 0:
                self.clear_screen()
                print('Taxation Settings for {}'.format(row['Full Name']))
                print('-'*33)
                temp_ = self.Provences[self.Provences['Regent']==row['Regent']][['Provence','Population', 'Loyalty', 'Taxation']]
                temp_ = pd.merge(temp_, law[law['Regent']==row['Regent']][['Provence', 'Type']].copy(), on='Provence', how='left').fillna('')
                p = input('Type a Provence name, or "DONE" if done:  ')
                if p.lower() == 'done':
                    check = 1
                else:
                    if p in list(temp_['Provence']):
                        tax = input('Change Taxation to: [0]None, [1]Light, [2]Moderate, [3]Severe:  ') 
                        
                        if int(tax) == 0:
                            self.change_provence(Provence=p, Taxation='None', Loyalty='1')
                        elif int(tax) == 1:
                            self.change_provence(Provence=p, Taxation='Light')
                        elif int(tax) == 2:
                            if p in list(temp_[temp_['Type']=='Law']['Provence']):
                                self.change_provence(Provence=p, Taxation='Moderate')
                            else:
                                self.change_provence(Provence=p, Taxation='Moderate', Loyalty='-1')
                        elif int(tax) == 3:
                            input('severe')
                            self.change_provence(Provence=p, Taxation='Severe', Loyalty='-1')
        
        # Agents need to pick now...
        temp = self.Regents[self.Regents['Player']==False].copy()
        costs = self.maintenance_costs(Update=False)
        provences_owned = self.Provences[self.Provences['Contested']==False][['Regent', 'Provence']].copy().groupby('Regent').count().reset_index()
        costs = pd.merge(costs, provences_owned, on='Regent', how='left').fillna(1)
        costs['Cost'] = (costs['Cost']/costs['Provence']).replace('','0').astype(int).fillna(0)
        temp = pd.merge(temp, costs, on='Regent', how='left').fillna(0)
        save_states = pd.DataFrame(columns=['Regent', 'Provence', 'state', 'action'])
        for i, row in temp.iterrows():
            temp_ = self.Provences[self.Provences['Regent']==row['Regent']][['Provence','Population', 'Loyalty', 'Taxation']]
            temp_ = pd.merge(temp_, law[law['Regent']==row['Regent']][['Provence', 'Type']].copy(), on='Provence', how='left').fillna('')
            # pick for each... this can likely be more efficient
            temp_['Cost'] = row['Cost']
            for j, row_ in temp_.iterrows():
                state = self.agent.get_tax_state(self, row_, row['Regent'])
                tax = self.make_decision(row['Attitude'], 4, 'Taxes', state, row['Regent'])
                p = row_['Provence']
                if tax[0] == 1:
                    self.change_provence(Provence=p, Taxation='None', Loyalty='1')
                elif tax[1] == 1:
                    self.change_provence(Provence=p, Taxation='Light')
                elif tax[2] == 1:
                    if p in list(temp_[temp_['Type']=='Law']['Provence']):
                        self.change_provence(Provence=p, Taxation='Moderate')
                    else:
                        self.change_provence(Provence=p, Taxation='Moderate', Loyalty='-1')
                elif tax[3] == 1:
                    self.change_provence(Provence=p, Taxation='Severe', Loyalty='-1')
                save_states.loc[save_states.shape[0]] = [row['Regent'], row_['Provence'], state, tax]       
        # collect taxes
        for p in range(11):
            temp = self.Provences[self.Provences['Population'] == p].copy()
            temp = temp[temp['Contested']==False]  # no gb from contested holdings
            if temp.shape[0] > 0:
                for t in ['Light', 'Moderate', 'Severe']:
                    temp_ = temp[temp['Taxation'] == t].copy()
                    if temp_.shape[0] > 0:
                        a,b = self.provence_taxation[self.provence_taxation['Population'] == p][t].values[0]
                        temp_['Revenue'] = np.random.randint(a,b,temp_.shape[0])
                        df = pd.concat((df, temp_[['Regent', 'Revenue', 'Provence']].copy()), sort=False)
                        # print(df.shape[0])
        # make reward vector
        temp = self.Provences.copy()
        temp = pd.merge(temp, costs[['Regent', 'Cost']], on='Regent', how='left')
        temp = pd.merge(temp, self.Holdings[self.Holdings['Type'] == 'Law'][['Provence', 'Type', 'Regent']], on=['Provence', 'Regent'], how='left').fillna('')
        temp['Relative'] = temp['Loyalty'].str.replace('Rebellious','4').replace('Poor','3').replace('Average','2').replace('High','1').astype(int)
        temp['Cost'] = temp['Cost'].astype(str).str.replace('','0').fillna('0').astype(float).astype(int)
        temp['Tax Effect'] = temp['Relative']*(-1)*((temp['Taxation']=='Severe') + (temp['Type'] != 'Law')*(temp['Taxation']=='Moderate')) + temp['Relative']*(temp['Taxation']=='None') + (-10)*(temp['Loyalty']=='Rebellious') - temp['Cost']
        temp = temp[['Tax Effect', 'Provence']]
        reward = pd.merge(df, temp, on='Provence', how='left')  # skips players
        reward = pd.merge(reward, self.Regents[self.Regents['Player']==False][['Regent', 'Attitude']].copy(), on='Regent', how='left')
        reward = reward.dropna()
        # Aggro Regents don't care if the people are unhappy as much as peaceful Regents
        reward['tm'] = reward['Attitude']
        reward['rm'] = reward['Attitude']
        for Attitude in list(set(self.Regents['Attitude'].copy())):
            if Attitude != 'Peaceful' and Attitude != 'Aggressive':  # the rest care evenly
                reward['tm'] = reward['tm'].str.replace(Attitude,'1')
                reward['rm'] = reward['rm'].str.replace(Attitude,'1')
            elif Attitude == 'Peaceful':  # Peaceful care more
                reward['tm'] = reward['tm'].str.replace(Attitude,'2')
                reward['rm'] = reward['rm'].str.replace(Attitude,'1')
            elif Attitude == 'Aggressive':  # Aggressive care less
                reward['tm'] = reward['tm'].str.replace(Attitude,'1')
                reward['rm'] = reward['rm'].str.replace(Attitude,'2')
        reward['Reward'] = reward['Revenue']*reward['rm'].astype(int) + reward['Tax Effect']*reward['tm'].astype(int)
        # update memory
        save_states = pd.merge(save_states, reward[['Provence', 'Reward']], on='Provence', how='left').fillna(0)
        lst = []
        for i, row in save_states.iterrows():
            # hate having to iterrow, but here we are
            Attitude = self.Regents[self.Regents['Regent'] == row['Regent']]['Attitude'].values[0]
            temp = self.Provences.copy()
            temp = pd.merge(temp, costs[['Regent','Cost']], on='Regent', how='left').fillna(0)
            temp = temp[temp['Regent'] == row['Regent']].copy()
            temp = temp[temp['Provence'] == row['Provence']].copy()
            temp = pd.merge(temp, law[law['Regent']==row['Regent']][['Provence', 'Type']].copy(), on='Provence', how='left').fillna('')
            new_state = self.agent.get_tax_state(self, list(temp.iterrows())[0][1], row['Regent'])
            self.agent.remember(row['state'], row['action'], row['Reward'], new_state, 'Taxes')
            self.agent.train_short_memory(row['state'], row['action'], row['Reward'], new_state, 'Taxes')
        # after reward given
        df = df[df['Revenue']>0].copy()
        
        # 4.3 Taxation From Guild and Temple Holdings
        lst = [(0,1), (1,2), (1,3), (2,4), (2,5), (2,6)]
        for h in ['Guild', 'Temple']:
            temp = self.Holdings[self.Holdings['Type'] == h].copy()
            temp = temp[temp['Contested']==0].copy()  # no gb from contested holdings
            for i in range(6):
                temp_ = temp[temp['Level']==i].copy()
                if temp_.shape[0] > 0:
                    temp_['Revenue'] = np.random.randint(lst[i][0],lst[i][1],temp_.shape[0])
                    df = pd.concat([df, temp_[['Regent', 'Revenue']].copy()], sort=False)
            temp_ = temp[temp['Level']>=6].copy()
            if temp_.shape[0] > 0:
                temp_['Revenue'] = np.random.randint(4,10,temp_.shape[0])
                df = pd.concat([df, temp_[['Regent', 'Revenue']].copy()], sort=False)
        
        # 4.4 Claims from Law Holdings
        temp = pd.merge(self.Holdings[self.Holdings['Contested']==0].copy(),self.Provences.copy(), on='Provence')
        temp = temp[temp['Type']=='Law'].copy()
        temp = temp[temp['Regent_x'] != temp['Regent_y']].copy()
        temp['Level'] = (temp['Level']/2).astype(int)
        temp = temp[temp['Level']>0]
        temp['Revenue'] = temp['Level']
        temp['Regent'] = temp['Regent_x']
        # give to the poor
        df = pd.concat([df, temp[['Regent', 'Revenue']].copy()], sort=False)
        # ... take from the rich
        temp['Regent'] = temp['Regent_y']
        temp['Revenue'] = temp['Level']*-1
        df = pd.concat([df, temp[['Regent', 'Revenue']].copy()], sort=False)
        
        # 4.5 Trade Routes - Caravans
        temp = self.Provences[['Provence', 'Regent', 'Population']].copy()
        df_ = pd.concat([self.Geography[self.Geography['Caravan']==1].copy(), self.Geography[self.Geography['Shipping']==1].copy()], sort=False)
        temp['A'] = temp['Population']
        temp['B'] = temp['Population']
        df_ = pd.merge(df_, temp[['Provence', 'A']], on='Provence', how='left')
        df_ = pd.merge(df_, temp[['Provence', 'B']], right_on='Provence', left_on='Neighbor', how='left').fillna(1)
        df_['Provence'] = df_['Provence_x']
        df_['Revenue'] = ((df_['A']+df_['B']+2*df_['Shipping'])/2).astype(int)
        df_ = pd.merge(df_, self.Provences.copy(), on='Provence', how='left')
        df = pd.concat([df, df_[['Regent', 'Revenue']]], sort=False)
        
        # 4.6 Tribute (the greatest code in the world)
        temp = self.Relationships[self.Relationships['Payment']>0].copy()
        temp['Revenue'] = temp['Payment']*-1
        df = pd.concat([df, temp[['Regent', 'Revenue']]], sort=False)

        temp['Regent'] = temp['Other']
        temp['Revenue'] = temp['Payment']
        df = pd.concat([df, temp[['Regent', 'Revenue']]], sort=False)
        
        # 4.7 occupation and Pillaging
        # CODE NEEDED HERE

        # figure it all out
        df = df.groupby('Regent').sum().reset_index()
        temp_Regents =  pd.merge(self.Regents.copy(), df, on='Regent', how='left')
        temp_Regents['Gold Bars'] = temp_Regents['Gold Bars'].fillna(0).astype(int) + temp_Regents['Revenue'].fillna(0).astype(int)
        
        # Results!
        temp_Regents['Revenue'] = temp_Regents['Revenue'].fillna(0).astype(int)
        self.Seasons[self.Season]['Season'] = pd.merge(self.Seasons[self.Season]['Season'], temp_Regents[['Regent','Gold Bars', 'Revenue']], on='Regent', how='left').fillna(0)
        self.Regents = temp_Regents[cols]
        
        if self.Train == True:
            self.agent.replay_new('Taxes')
    
    # 5. MAINTENANCE COSTS
    def maintenance_costs(self, Update=False):
        '''
        A domain does not support itself. Gold is required to keep the 
        wheels of politics greased and ensure the people have enough 
        infrastructure to support their nation. The cost of owning and 
        operating holdings, feeding armies, and paying for court 
        expenses adds up quickly.
        '''
        cols = self.Regents.copy().keys()
        
        # 5.1 Domain Expenses - 1 per 5 holdings, up to nearest gb
        temp = self.Provences.copy()
        temp['Domain'] = 1
        df = temp[['Regent','Domain']]
        temp = temp[temp['Castle']>0]
        df = pd.concat([df,temp[['Regent','Domain']]], sort=False)
        temp = self.Holdings[self.Holdings['Type'] != 'Source'].copy()
        temp['Domain'] = 1
        df = pd.concat([df,temp[['Regent','Domain']]], sort=False)
        df = df[['Regent','Domain']].groupby('Regent').sum().reset_index().fillna(0)
        df['Cost'] = ((df['Domain']+4)/5).astype(int)
        df = df[['Regent','Cost']]
        
        # 5.2 Pay Armies
        temp = self.Troops[['Regent', 'Cost']].copy()  # this would be easy,        but we have to disband if we can't pay
        if Update:
            temp_ = temp.groupby('Regent').sum().reset_index()
            check = pd.merge(self.Regents[['Regent', 'Gold Bars', 'Player']].copy(), df.copy(), on='Regent')
            check['Gold Bars'] = check['Gold Bars'] - check['Cost']
            temp_ = pd.merge(temp_, check[['Regent', 'Gold Bars', 'Player']], on='Regent', how='left').fillna(0)
            
            disband = temp_[temp_['Cost'] > temp_['Gold Bars']]
            for i, row in disband.iterrows():
                cost = row['Cost']
                gb = row ['Gold Bars']
                _temp = self.Troops.copy()
                _temp = _temp[_temp['Regent'] == row['Regent']]
                if row['Player']==False:
                    if cost > gb and self.Troops[self.Troops['Regent']==row['Regent']].shape[0] > 0:
                        _temp = self.Troops[self.Troops['Regent'] == row['Regent']].copy()
                        _temp = _temp.sort_values('CR')  # want to dump levies first to get them back to work
                        for j, _row in _temp.iterrows():
                            if cost > gb and _temp.shape[0]>0:
                                self.disband_troops(_row['Regent'], _row['Provence'], _row['Type'])
                                cost = cost - _row['Cost']  # make sure only the single troop cost
                else:
                    while cost > gb:
                        dbnd = -1
                        while dbnd not in list(_temp.index):
                            self.clear_screen()
                            print(_temp)
                            print()
                            print('{} cannot afford their troops!  They Have {} Gold Bars and a Maintenance Cost of {}.'.format(row['Regent'], gb, cost))
                            dbnd = int(input('Pick a Unit to Disband (Type Index Number)'))
                        print('okay...')    
                        if _temp.loc[dbnd]['Type'].find('Mercenary') >= 0:
                            # oh no, brigands!
                            print('Replace with a disband mercenary thing')
                        cost = cost - int(_temp.loc[dbnd]['Cost'])  # make sure only the single troop cost
                        # disband the troop
                        self.Troops.drop(dbnd, inplace=True, axis=0)
                        _temp.drop(dbnd, inplace=True, axis=0)
            # now the easy step
            temp = self.Troops[['Regent', 'Cost']].copy()
        df = pd.concat([df, temp[['Regent','Cost']]], sort=False)
        df = df[['Regent','Cost']]    
        
        # 5.3 Lieutenants
        temp = self.Lieutenants.copy()
        temp_ = temp.copy()
        temp_['Cost'] = 1
        temp_ = temp_[['Regent','Cost']].groupby('Regent').sum().reset_index()
        check = pd.merge(self.Regents[['Regent', 'Gold Bars']].copy(), df.copy(), on='Regent')
        check['Gold Bars'] = check['Gold Bars'] - check['Cost']
        temp_ = pd.merge(temp_, check[['Regent', 'Gold Bars']], on='Regent', how='left').fillna(0)
        
        disband = temp_[temp_['Cost'] > temp_['Gold Bars']]
        for i, row in disband.iterrows():
            cost = row['Cost']
            gb = row ['Gold Bars']
            _temp = self.Lieutenants.copy()
            _temp = _temp[_temp['Regent'] == row['Regent']]
            if Update:
                while cost > gb and self.Lieutenants[self.Lieutenants['Regent']==row['Regent']].shape[0] > 0:
                    for j, _row in _temp.iterrows():
                        cost = cost - 1
                        # disband the troop
                        self.Lieutenants.drop(j, inplace=True)
        # now the money
        temp = self.Lieutenants.copy()
        temp['Cost'] = 1
        df = pd.concat([df, temp[['Regent','Cost']]], sort=False)
        df = df[['Regent','Cost']].groupby('Regent').sum().reset_index()  # calculate here
        
        # 5.4 Court Expenses - what can we afford
        temp_4 = self.Regents[self.Regents['Player'] == True][['Regent', 'Gold Bars']].copy()
        temp = self.Regents[self.Regents['Player'] == False][['Regent', 'Gold Bars']].copy()
        temp = pd.merge(temp, df, on='Regent', how='left').fillna(0)
        temp['Check'] = temp['Gold Bars'] - temp['Cost']
        temp['Court'] = 'Dormant'
        temp_0 = temp[temp['Check'] <= 5].copy()
        temp_ = temp[temp['Check'] > 5].copy()
        temp_3 = temp_[temp_['Check'] >= 30].copy()
        temp_ = temp_[temp_['Check'] < 30].copy()
        temp_2 = temp_[temp_['Check'] >= 15].copy()
        temp_1 = temp_[temp_['Check'] < 15].copy()
        temp_0['Court'] = 'Dormant'  # no cost
        
        temp_1['Court'] = 'Bare'    # 2 bars
        temp_1['Cost'] = temp_1['Cost'] + 2
        temp_2['Court'] = 'Average'  # 5 bars
        temp_2['Cost'] = temp_2['Cost'] + 5
        temp_3['Court'] = 'Rich'  # 8 bars
        temp_3['Cost'] = temp_3['Cost'] + 8
        
        # ask the player what they want to do
        temp_4 = pd.merge(temp_4, df, on='Regent', how='left').fillna(0)
        temp_4['Check'] = temp_4['Gold Bars'] - temp_4['Cost']
        temp_4['Court'] = 'Dormant'
        for i, row in temp_4.iterrows():
            check = 0
            while check == 0:
                self.clear_screen()
                print('-- Court Expenses --')
                print(temp_4[temp_4['Regent']==row['Regent']][['Regent','Gold Bars','Cost']])
                print()
                most_can_spend = row['Gold Bars'] - row['Cost']
                
                print('[0] Dormant')
                print('For zero Gold Bars, your court is dormant and only the mice rule the castle guest halls. This option saves money, but you are incapable of performing the Decree or Diplomacy actions on any of your action rounds this season.')
                if most_can_spend >= 2:
                    print()
                    print('[2] - Bare')
                    print('For two Gold Bars, your court is at the bare minimum to function. Your Decree and Diplomacy actions are at disadvantage for the domain action check; no one likes a stingy regent, especially expectant ambassadors.')
                if most_can_spend >= 5:
                    print()
                    print('[5] - Average')
                    print('For five Gold Bars, your court is of average standing and comfort. Your Decree and Diplomacy actions are at neither advantage nor disadvantage.')
                if most_can_spend >= 8:
                    print()
                    print('[8] Rich')
                    print('[8] For eight Gold Bars, your court is the talk of the realm. Fine wines, imported cuisine, mummers and bards -- you have it all, and the pomp is sure to impress the dignitaries. Your Decree and Diplomacy actions are made with advantage on the domain action check.')
                print()
                q = 'How much does {} want to spend on their court?'.format(row['Regent'])
                ex = input(q)
                if int(ex) in [0, 2, 5, 8] and int(ex) <= most_can_spend:
                    temp_4.at[i, 'Cost'] =  row['Cost'] + int(ex)
                    if ex == '2':
                        temp_4.at[i, 'Court'] =  'Bare'  # 'Bare'
                    elif ex == '5':
                        temp_4.at[i, 'Court'] =  'Average'  # 'Average'
                    elif ex == '8':
                        temp_4.at[i, 'Court'] = 'Rich'  # 'Rich'
                    print(temp_4[temp_4['Regent']==row['Regent']][['Regent','Gold Bars','Cost']])
                    check = 1   
        df = pd.concat([temp_0, temp_1, temp_2, temp_3, temp_4], sort=False)
        
        if Update == True:
            # add to the thing
            temp = pd.merge(self.Seasons[self.Season]['Season'], df[['Regent','Cost','Court']], on='Regent', how='left').fillna(0)
            temp['Cost'] = temp['Cost'].astype(int)
            self.Seasons[self.Season]['Season'] = temp
            
            # lets clear the gold bars
            temp['Gold Bars'] = temp['Gold Bars'] - temp['Cost']
            temp = pd.merge(self.Regents[[col for col in cols if col != 'Gold Bars']], temp[['Regent', 'Gold Bars']], on='Regent', how='left')
            
            
            self.Regents = temp[cols]
        else:  # Return for the gold thing
            return df[['Regent', 'Cost']]
        
    # 6, 7, and 8 TAKING DOMAIN ACTIONS
    def take_domain_actions(self):
        '''
        During each season, the regent takes a total of three domain 
        actions. Each of these represents roughly a month of time 
        in-world, thus there are twelve domain actions that can be 
        taken in the course of a game year.

        While most domain actions are fairly straightforward, there 
        does exist the concept of the bonus action during a season. 
        Bonus actions can be taken in addition to regular domain actions, 
        but the player is limited to a single bonus action per action 
        round, as with bonus actions during combat rounds.
        
        So, 1 Action and 1 Bonus Action, if applicable.
        
        1 Bonus Action per Lieutenant.
        
        '''
        self.Action=1
        self.Seasons[self.Season]['Actions'] = {}
        
        while self.Action < 4:
            # Make A DataFrame
            cols = ['Regent', 'Actor', 'Action Type', 'Action', 'Decision', 'Target Regent', 'Provence', 'Target Provence', 'Target Holding', 'Success?', 'Base Reward', 'State', 'Invalid', 'Message']
            self.Seasons[self.Season]['Actions'][self.Action] = pd.DataFrame(columns=cols)
            for I in reversed(list(set(self.Seasons[self.Season]['Season']['Initiative']))):
                # grab the regents that are acting this round
                # self.clear_screen()
                print('Season {} - Action {} - Initiative {:2d}'.format(self.Season, self.Action, I), end='\r')
                df = self.Seasons[self.Season]['Season'][self.Seasons[self.Season]['Season']['Initiative'] == I].copy()
                for i, row in df.iterrows():  # each regent
                    Regent = row['Regent']
                    # bonus first
                    self.Bonus = 1
                    actors = list(self.Lieutenants[self.Lieutenants['Regent'] == Regent]['Lieutenant'])
                    actors.append(self.Regents[self.Regents['Regent'] == Regent]['Full Name'].values[0])
                    for actor in actors:
                        if row['Player'] == True:
                            print('Player...')
                        else:  # NPC!
                            type = 'Bonus'
                            invalid = True
                            if invalid == True:
                                state, capital, high_pop, low_pop, friend, enemy, rando, enemy_capital = self.agent.get_action_state(row['Regent'], self)  # allow player actions to inform Agent
                                decision = self.make_decision('', self.agent.action_choices, 'Action', state, row['Regent'])
                                # translate into action...
                                index = self.Seasons[self.Season]['Actions'][self.Action].shape[0]
                                Regent, Actor, Action_Type, action, Decision, Target_Regent, Provence, Target_Provence, Target_Holding, Success, reward, State, invalid, Message = self.take_action(decision, Regent, actor, type, state, capital, high_pop, low_pop, friend, enemy, rando, enemy_capital)
                                # update memory if invalid
                                if invalid == True:
                                    next_state = state
                                    self.agent.remember(state, decision, reward, next_state, 'Action', invalid)
                                    self.failed_actions.append(pd.DataFrame([[Regent,action,Success]], columns=['Regent','Action','Success?']))
                                    # and train it... to prevent future mistakes
                                    self.agent.train_short_memory(state, action, reward, next_state, 'Action', invalid)
                                else:  # update action vector
                                    self.Seasons[self.Season]['Actions'][self.Action].loc[index] = [Regent, Actor, Action_Type, action, Decision, Target_Regent, Provence, Target_Provence, Target_Holding, Success, reward, State, invalid, Message]
                    self.Bonus = 0
                    # time for the actual action...
                    

                    if row['Player'] == True:
                        print('Player...')
                    else:  # NPC!
                        try:
                            over = self.Seasons[self.Season][self.Action]['Override'][Regent]
                        except:
                            over = None
                        state, capital, high_pop, low_pop, friend, enemy, rando, enemy_capital = self.agent.get_action_state(row['Regent'], self, over)  # allow player actions to inform Agent
                        invalid = True
                        tries = 0
                        while invalid == True:
                            Type = 'Action'
                            if tries == 0:
                                decision = self.make_decision('', self.agent.action_choices, 'Action', state, row['Regent'], over)
                            else:
                                decision = self.make_decision('', self.agent.action_choices, 'Action', state, row['Regent'],None)
                           
                            # translate into action...
                            index = self.Seasons[self.Season]['Actions'][self.Action].shape[0]
                            Regent, Actor, Action_Type, action, Decision, Target_Regent, Provence, Target_Provence, Target_Holding, Success, reward, State, invalid, Message = self.take_action(decision, Regent, actor, Type, state, capital, high_pop, low_pop, friend, enemy, rando, enemy_capital)
                            # update memory if invalid
                            tries += 1
                            if invalid == True:
                                next_state = state
                            else:  # update action vector
                                self.Seasons[self.Season]['Actions'][self.Action].loc[index] = [Regent, Actor, Action_Type, action, Decision, Target_Regent, Provence, Target_Provence, Target_Holding, Success, reward, State, invalid, Message]
                                if over != None and tries == 0:
                                    del self.Seasons[self.Season][self.Action]['Override'][Regent]
                                next_state = self.agent.get_action_state(row['Regent'], self, None)[0]
                            # and train it...
                            if self.Train == True or self.Train_Short == True:
                                self.agent.remember(state, decision, reward, next_state, 'Action', invalid)
                                self.agent.train_short_memory(state, action, reward, next_state, 'Action', invalid)
            # update memories and train, unless action = 3 (wait for begining of next round to add in gold and regency
            if self.Train==True:
                self.agent.replay_new('Action')
            # last bit in function while loop
            self.Action = self.Action+1
           
    def take_action(self, decision, Regent, actor, Type, state, capital, high_pop, low_pop, friend, enemy, rando, enemy_capital):
        '''
        
        ['Regent', 'Actor', 'Action Type', 'Action', 'Target Regent', 'Provence', 'Target Provence', 'Target Holding', 'Success?', 'Base Reward', 'State', invalid, message]
        '''
        invalid = False
        self.action = decision
        self.state = state
        # decision[0] == 1
        if decision[0] == 1:  # build_road 
            # need provences
            temp = pd.merge(self.Provences[['Provence']][self.Provences['Regent'] == Regent], self.Geography, on='Provence', how='left')
            temp = temp[temp['Border'] == 1]
            temp = temp[temp['Road'] == 0]
            temp['Roll'] = np.random.randint(1,100,temp.shape[0]) + 10*temp['RiverChasm']
            temp = temp.sort_values('Roll')
            success, reward = False, 0
            # this can only be done if you have a provence
            if state[23] == 1 and state[94] == 1:
                
                success, reward, message = self.bonus_action_build(Regent, temp.iloc[0]['Provence'], temp.iloc[0]['Neighbor'])
                return [Regent, actor, Type, 'build_road', decision, '', temp.iloc[0]['Provence'], temp.iloc[0]['Neighbor'], '', success, reward, state, invalid, message]
            else:
                invalid = True
                return [Regent, actor, Type, 'build_road', decision, '', '', '', '', success, -100, state, invalid, '']
        # decision[1] == 1
        elif decision[1] == 1:  #decree_general
            if state[94]==1 or state[4] + state[5] + state[6] == 0:  # Dormant Court, not a valid action
                invalid = True
                return [Regent, actor, Type, 'decree_general', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                
                court = 'Average'
                if state[4] == 1:
                    court = 'Bare'
                elif state[6] == 1:
                    court = 'Rich'
                success, reward, message = self.bonus_action_decree(Regent, actor, 'General')
                message = message.replace('!Regent', actor)
                return [Regent, actor, Type, 'decree_general', decision, '', '', '', '', success, reward, state, invalid, message]
        # decision[2] == 1
        elif decision[2] == 1:  #decree_assest_seizure  
            if state[4] + state[5] + state[6] == 0 or state[94] == 1:  # Dormant Court, not a valid action
                invalid = True
                return [Regent, actor, Type, 'decree_asset_seizure', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                court = 'Average'
                if state[4] == 1:
                    court = 'Bare'
                elif state[6] == 1:
                    court = 'Rich'
                success, reward, message = self.bonus_action_decree(Regent, actor, 'Asset Seizure')
                message = message.replace('!Regent', actor)
                return [Regent, actor, Type, 'decree_asset_seizure', decision, '', '', '', '', success, reward, state, invalid, message]
        # decision[3] == 1
        elif decision[3] == 1:  #disband_army
            if state[44] == 0:
                invalid = True
                return [Regent, actor, Type, 'disband_army', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                try:
                    temp = self.Troops[self.Troops['Regent'] == Regent].copy()
                    temp['target'] = temp['CR'] - temp['Cost']
                    temp = temp.sort_values('target')
                    row = temp.iloc[0]
                    self.bonus_action_disband(Regent, [row['Type']], [row['Provence']])
                    reward = 0
                    if state[87] == 1:  #Aggressive
                        reward = -3
                    return [Regent, actor, Type, 'disband_army', decision, '', row['Provence'], '', '', True, reward, state, invalid, '{} disbanded a unit of {} stationed in {}'.format(actor, row['Type'], row['Provence'])]
                except:
                    print(Regent, self.Troops[self.Troops['Regent'] == Regent].copy())
                    return [Regent, actor, Type, 'disband_army', decision, '', '', '', '', False, -10, state, True, '']
        # decision[4] == 1
        elif decision[4] == 1:  #disband_levees
            if state[44] == 0 or state[45] == 0:
                invalid = True
                return [Regent, actor, Type, 'disband_levees', decision, '', '', '', '', False, -10, state, invalid, '']   
            else:
                
                temp = self.Troops[self.Troops['Regent'] == Regent].copy()
                temp = temp[temp['Type'].str.lower().str.contains('levees')]
                units = []
                provences = []
                reward = int(len(units)/3)
                if state[87] == 1:  #Aggressive
                    reward = reward -3
                for i, row in temp.iterrows():
                    units.append(row['Type'])
                    provences.append(row['Provence'])
                self.bonus_action_disband(Regent, [row['Type']], [row['Provence']])
                return [Regent, actor, Type, 'disband_levees', decision, '', row['Provence'], '', '', True, reward, state, invalid, '{} disbanded all levees'.format(actor)]
        # decision[5] == 1
        elif decision[5] == 1:  #disband_mercenaries
            if state[44] == 0 or state[46] == 0:
                invalid = True
                return [Regent, actor, Type, 'disband_mercenaries', decision, '', '', '', '', False, -10, state, invalid, '']  
            else:
                temp = self.Troops[self.Troops['Regent'] == Regent].copy()
                temp = temp[temp['Type'].str.lower().str.contains('mercenary')]
                units = []
                provences = []
                reward = int(len(units)/3)
                if state[87] == 1:  #Aggressive
                    reward = reward -3
                for i, row in temp.iterrows():
                    units.append(row['Type'])
                    provences.append(row['Provence'])
                    self.bonus_action_disband(Regent, [row['Type']], [row['Provence']])
                return [Regent, actor, Type, 'disband_mercenaries', decision, '', ', '.join(provences), '', '', True, reward, state, invalid, '{} disbanded all mercenaries'.format(actor)]
        # decision[6] == 1
        elif decision[6] == 1:  #agitate_for_friend
            if state[35] == 0 and state[4] == 1 or state[34]+state[35]+state[36]+state[37] == 0 or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'agitate', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                
                temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
                limit = min(self.Regents[self.Regents['Regent']==Regent][['Regency Points', 'Gold Bars']].values[0])
                if state[4] == 1:  # bonus action, temple only
                    temp = temp[temp['Type'] == 'Temple'].copy()
                    limit = 1
                temp = pd.merge(temp, self.Provences[self.Provences['Regent'] == friend].copy(), on='Provence', how='left')
                targets = []
                for i, row in temp.iterrows():
                    if i < limit:
                        targets.append(row['Provence'])
                success, reward, message = self.domain_action_agitate(Regent, friend, False, targets)
                
                if state[92] == 0 and state[90] == 1:  # xenophobic penalty
                    reward = reward - 5
                return [Regent, actor, Type, 'agitiate_for_friend', decision, friend, '', ', '.join(targets), '', success, reward, state, invalid, message]
        # decision[7] == 1:
        elif decision[7] == 1:  #agitate_against_enemy
            if state[35] == 0 and state[4] == 1 or state[34]+state[35]+state[36]+state[37] == 0 or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'agitate', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                
                temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
                limit = min(self.Regents[self.Regents['Regent']==Regent][['Regency Points', 'Gold Bars']].values[0])
                if state[4] == 1:  # bonus action, temple only
                    temp = temp[temp['Type'] == 'Temple'].copy()
                    limit = 1
                temp = pd.merge(temp, self.Provences[self.Provences['Regent'] == friend].copy(), on='Provence', how='left')
                targets = []
                for i, row in temp.iterrows():
                    if i < limit:
                        targets.append(row['Provence'])
                success, reward, message = self.domain_action_agitate(Regent, enemy, True, targets)
                if state[89] == 1 or  (state[92] == 1 and state[90] == 1):  # Agressive bonus/Xenophobic bonus
                    reward = 2*reward
                if state[92] == 0 and state[90] == 1:  # xenophobic penalty
                    reward = reward - 5
                return [Regent, actor, Type, 'agitiate_for_friend', decision, friend, '', ', '.join(targets), '', success, reward, state, invalid, message]
        # decision[8] == 1:
        elif decision[8] == 1:  #agitate_for_rando
            if state[35] == 0 and state[3] == 1 or state[34]+state[35]+state[36]+state[37] == 0 or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'agitate', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                
                temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
                limit = min(self.Regents[self.Regents['Regent']==Regent][['Regency Points', 'Gold Bars']].values[0])
                if state[4] == 1:  # bonus action, temple only
                    temp = temp[temp['Type'] == 'Temple'].copy()
                    limit = 1
                temp = pd.merge(temp, self.Provences[self.Provences['Regent'] == friend].copy(), on='Provence', how='left')
                targets = []
                for i, row in temp.iterrows():
                    if i < limit:
                        targets.append(row['Provence'])
                success, reward, message = self.domain_action_agitate(Regent, rando, False, targets)
                if state[92] == 0 and state[90] == 1:  # xenophobic penalty
                    reward = reward - 5
                return [Regent, actor, Type, 'agitiate_for_friend', decision, friend, '', ', '.join(targets), '', success, reward, state, invalid, message] 
        # decision[9] == 1
        elif decision[9] == 1:  #agitate_against_rando
            if state[35] == 0 and state[3] == 1 or state[34]+state[35]+state[36]+state[37] == 0 or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'agitate', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                
                temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
                limit = min(self.Regents[self.Regents['Regent']==Regent][['Regency Points', 'Gold Bars']].values[0])
                if state[4] == 1:  # bonus action, temple only
                    temp = temp[temp['Type'] == 'Temple'].copy()
                    limit = 1
                temp = pd.merge(temp, self.Provences[self.Provences['Regent'] == friend].copy(), on='Provence', how='left')
                targets = []
                for i, row in temp.iterrows():
                    if i < limit:
                        targets.append(row['Provence'])
                success, reward, message = self.domain_action_agitate(Regent, rando, True, targets)
                if state[89] == 1 or  (state[92] == 1 and state[90] == 1):  # Agressive bonus/Xenophobic bonus
                    reward = 2*reward
                if state[92] == 0 and state[90] == 1:  # xenophobic penalty
                    reward = reward - 5
                return [Regent, actor, Type, 'agitiate_for_friend', decision, friend, '', ', '.join(targets), '', success, reward, state, invalid, message]
        # decision[10] == 1:
        elif decision[10] == 1:  #espionage_assassination
            if (state[3] == 1 and state[36] == 0) or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'espionage_assassination', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                # get enemy provences
                temp = self.Provences[self.Provences['Regent'] == enemy].copy()
                # if bonus action, must have a Guild in that provence
                if state[3] == 1:
                    check = self.Holdings[self.Holdings['Regent']==Regent]
                    temp = pd.merge(check[check['Type']=='Guild'][['Provence']], temp, on='Provence', how='left')
                if temp.shape[0] == 0:  # no valid targets
                    invalid = True
                    return [Regent, actor, Type, 'espionage_assassination', decision, '', '', '', '', False, -10, state, True, '']
                if temp[temp['Capital']==True].shape[0] == 0:
                    temp = temp.sort_values('Population', ascending=False)
                    Provence = temp.iloc[0]['Provence']  # hardest one to hit
                else:
                    Provence = temp[temp['Capital']==True]['Provence'].values[0]
                success, reward, message = self.domain_action_espionage(Regent, enemy, Provence, 'Assassination')
                return [Regent, actor, Type, 'espionage_assassination', decision, enemy, '', Provence, '', success, reward, state, False, message]
        # decision[11] == 1:
        elif decision[11] == 1:  # espionage_discover_troop_movements
            if (state[3] == 1 and state[36] == 0) or state[94] == 1:
                invalid = True
                return [Regent, actor, Type, 'espionage_discover_troop_movements', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                # get enemy provences
                temp = self.Provences[self.Provences['Regent'] == enemy].copy()
                # if bonus action, must have a Guild in that provence
                if state[3] == 1:
                    check = self.Holdings[self.Holdings['Regent']==Regent]
                    temp = pd.merge(check[check['Type']=='Guild'][['Provence']], temp, on='Provence', how='left')
                if temp.shape[0] == 0:  # no valid targets
                    invalid = True
                    return [Regent, actor, Type, 'espionage_discover_troop_movements', decision, '', '', '', '', False, -10, state, invalid, '']
                if temp[temp['Capital']==True].shape[0] == 0:
                    temp = temp.sort_values('Population', ascending=False)
                    Provence = temp.iloc[0]['Provence']  # hardest one to hit
                else:
                    Provence = temp[temp['Capital']==True]['Provence'].values[0]
                success, reward, message = self.domain_action_espionage(Regent, enemy, Provence, 'Troops')
                return [Regent, actor, Type, 'espionage_discover_troop_movements', decision, enemy, '', Provence, '', success, reward, state, invalid, message]     
        # decision[12] == 1:
        elif decision[12] == 1:  # espionage_diplomatic_details
            if (state[3] == 1 and state[36] == 0) or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'espionage_diplomatic_details', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                # get enemy provences
                temp = self.Provences[self.Provences['Regent'] == enemy].copy()
                # if bonus action, must have a Guild in that provence
                if state[3] == 1:
                    check = self.Holdings[self.Holdings['Regent']==Regent]
                    temp = pd.merge(check[check['Type']=='Guild'][['Provence']], temp, on='Provence', how='left')
                if temp.shape[0] == 0:  # no valid targets
                    invalid = True
                    return [Regent, actor, Type, 'espionage_diplomatic_details', decision, '', '', '', '', False, -10, state, invalid, '']
                if temp[temp['Capital']==True].shape[0] == 0:
                    temp = temp.sort_values('Population', ascending=False)
                    Provence = temp.iloc[0]['Provence']  # hardest one to hit
                else:
                    Provence = temp[temp['Capital']==True]['Provence'].values[0]
                success, reward, message = self.domain_action_espionage(Regent, enemy, Provence, 'Trade')
                return [Regent, actor, Type, 'espionage_diplomatic_details', decision, enemy, '', Provence, '', success, reward, state, invalid, message]
        # decision[13] == 1: 
        elif decision[13] == 1:  #espionage_intrigue
            if (state[3] == 1 and state[36] == 0) or state[94] == 1:
                invalid = True
                return [Regent, actor, Type, 'espionage_intrigue', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                # get enemy provences
                temp = self.Provences[self.Provences['Regent'] == enemy].copy()
                # if bonus action, must have a Guild in that provence
                if state[3] == 1:
                    check = self.Holdings[self.Holdings['Regent']==Regent]
                    temp = pd.merge(check[check['Type']=='Guild'][['Provence']], temp, on='Provence', how='left')
                if temp.shape[0] == 0:  # no valid targets
                    invalid = True
                    return [Regent, actor, Type, 'espionage_intrigue', decision, '', '', '', '', False, -10, state, invalid, '']
                if temp[temp['Capital']==True].shape[0] == 0:
                    temp = temp.sort_values('Population', ascending=False)
                    Provence = temp.iloc[0]['Provence']  # hardest one to hit
                else:
                    Provence = temp[temp['Capital']==True]['Provence'].values[0]
                success, reward, message = self.domain_action_espionage(Regent, enemy, Provence, 'Intrigue')
                return [Regent, actor, Type, 'espionage_intrigue', decision, enemy, '', Provence, '', success, reward, state, invalid, message]
        # decision[14] == 1: 
        elif decision[14] == 1:  #espionage_corruption
            if (state[3] == 1 and state[36] == 0) or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'espionage_corruption', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                # get enemy provences
                temp = self.Provences[self.Provences['Regent'] == enemy].copy()
                # if bonus action, must have a Guild in that provence
                if state[3] == 1:
                    check = self.Holdings[self.Holdings['Regent']==Regent]
                    temp = pd.merge(check[check['Type']=='Guild'][['Provence']], temp, on='Provence', how='left')
                if temp.shape[0] == 0:  # no valid targets
                    invalid = True
                    return [Regent, actor, Type, 'espionage_corruption', decision, '', '', '', '', False, -10, state, invalid, '']
                if temp[temp['Capital']==True].shape[0] == 0:
                    temp = temp.sort_values('Population', ascending=False)
                    Provence = temp.iloc[0]['Provence']  # hardest one to hit
                else:
                    Provence = temp[temp['Capital']==True]['Provence'].values[0]
                success, reward, message = self.domain_action_espionage(Regent, enemy, Provence, 'Corruption')
                return [Regent, actor, Type, 'espionage_corruption', decision, enemy, '', Provence, '', success, reward, state, invalid, message]
        # decision[15] == 1: 
        elif decision[15] == 1:  #espionage_heresy
            if (state[3] == 1 and state[36] == 0) or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'espionage_heresy', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                # get enemy provences
                temp = self.Provences[self.Provences['Regent'] == enemy].copy()
                # if bonus action, must have a Guild in that provence
                if state[3] == 1:
                    check = self.Holdings[self.Holdings['Regent']==Regent]
                    temp = pd.merge(check[check['Type']=='Guild'][['Provence']], temp, on='Provence', how='left')
                if temp.shape[0] == 0:  # no valid targets
                    invalid = True
                    return [Regent, actor, Type, 'espionage_heresy', decision, '', '', '', '', False, -10, state, invalid, '']
                if temp[temp['Capital']==True].shape[0] == 0:
                    temp = temp.sort_values('Population', ascending=False)
                    Provence = temp.iloc[0]['Provence']  # hardest one to hit
                else:
                    Provence = temp[temp['Capital']==True]['Provence'].values[0]
                success, reward, message = self.domain_action_espionage(Regent, enemy, Provence, 'Heresy')
                return [Regent, actor, Type, 'espionage_heresy', decision, enemy, '', Provence, '', success, reward, state, invalid, message]
        # decision[16] == 1: 
        elif decision[16] == 1:  #espionage_trace_espionage
            if (state[3] == 1 and state[36] == 0) or state[94]==1:
                invalid = True
                return [Regent, actor, Type, 'espionage_trace_espionage', decision, '', '', '', '', False, -10, state, invalid, '']
            else:
                # get enemy provences
                temp = self.Provences[self.Provences['Regent'] == enemy].copy()
                # if bonus action, must have a Guild in that provence
                if state[3] == 1:
                    check = self.Holdings[self.Holdings['Regent']==Regent]
                    temp = pd.merge(check[check['Type']=='Guild'][['Provence']], temp, on='Provence', how='left')
                if temp.shape[0] == 0 or state[50] == 0:  # no valid targets
                    invalid = True
                    return [Regent, actor, Type, 'espionage_trace_espionage', decision, '', '', '', '', False, -10, state, invalid, '']
                if temp[temp['Capital']==True].shape[0] == 0:
                    temp = temp.sort_values('Population', ascending=False)
                    Provence = temp.iloc[0]['Provence']  # hardest one to hit
                else:
                    Provence = temp[temp['Capital']==True]['Provence'].values[0]
                success, reward, message = self.domain_action_espionage(Regent, enemy, Provence, 'Investigate')
                return [Regent, actor, Type, 'espionage_trace_espionage', decision, enemy, '', Provence, '', success, reward, state, invalid, message]
        # decision[17] == 1: 
        elif decision[17] == 1:  #bonus_action_grant_rando
            if state[94] == 1:
                return [Regent, actor, Type, 'grant', decision, rando, '', '', '',  False, -10, state, True, '']
            else:  # we have the money to do this
                success, reward, message = self.bonus_action_grant(Regent, rando, 1)
                return [Regent, actor, Type, 'grant', decision, rando, '', '', '', success, reward, state, False, message]
        # decision[18] == 1:
        elif decision[18] == 1:  #bonus_action_grant_friend
            if state[94]==1:
                return [Regent, actor, Type, 'grant', decision, friend, '', '', '',  False, -10, state, True, '']
            else:  # we have the money to do this
                success, reward, message = self.bonus_action_grant(Regent, friend, 1)
                return [Regent, actor, Type, 'grant', decision, friend, '', '', '', success, reward, state, False, message]
        # decision[19] == 1: 
        elif decision[19] == 1:  #bonus_action_lieutenant
            if state[94]==1:
                return [Regent, actor, Type, 'lieutenant', decision, '', '', '', '',  False, -10, state, True, '']
            else:  # we have the money to do this
                success, reward, message = self.bonus_action_lieutenant(Regent)
                if state[84] == 1 and success == True:
                    del self.random_override[Regent]
                return [Regent, actor, Type, 'Lieutenant', decision, '', '', '', '',  success, reward, state, False, message]
        # decision[20] == 1:
        elif decision[20] == 1:  #move_troops_defend_provence
            temp = pd.merge(self.Provences[self.Provences['Regent']==Regent][['Regent', 'Provence']].copy(), self.Troops.copy(), on='Provence', how='left').fillna(0)
            temp = temp[temp['Type'] != 0]
            temp = temp[temp['Regent_x'] != temp['Regent_y']]
            if state[44] == 0 or temp.shape[0] == 0 or state[94]==1:  # no defense needed/able to be done
                return [Regent, actor, Type, 'move_troops_defend_provence', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                temp = temp[['Provence', 'CR']].groupby('Provence').sum().reset_index()
                temp['roll'] = np.random.randint(1, 100,temp.shape[0])+temp['CR']
                temp = temp.sort_values('roll', ascending=False)
                Target = temp.iloc[0]['Provence']
                Target_CR = temp.iloc[0]['CR']
                temp = self.Troops[self.Troops['Regent']=='Regent'].copy()
                temp = temp[temp['Provence'] != Target]
                temp = temp[temp['Garrisoned']==0]
                if temp.shape[0] == 0:
                    return [Regent, actor, Type, 'move_troops_defend_provence', decision, friend, '', '', '',  False, -10, state, True, '']
                else:
                    temp['roll'] = np.random.randint(1, 100,temp.shape[0])+temp['CR']
                    temp = temp.sort_values('roll', ascending=False)
                    troops = []
                    provences = []
                    i = 0
                    cr = 0
                    for i, row in temp.iterrows():
                        if row['CR'] + cr < Target_CR and i < temp.shape[0]:
                            troops.append(row['Unit'])
                            provences.append(row['Provence'])
                            i += 1
                            cr = cr + row['CR']
                    success, reward, message = self.bonus_action_move_troops(Regent, troops, provences, Target)
                    reward = Target_CR
                    return [Regent, Actor, Type, 'move_troops_defend_provence', '', '', Target, '', success, reward, state, invalid, message]
        # decision[21] == 1:
        elif decision[21] == 1:  #move_troops_defend_friend
            temp = pd.merge(self.Provences[self.Provences['Regent']==friend][['Regent', 'Provence']].copy(), self.Troops.copy(), on='Provence', how='left').fillna(0)
            temp = temp[temp['Type'] != 0]
            temp = temp[temp['Regent_x'] != temp['Regent_y']]
            if state[44] == 0 or temp.shape[0] == 0 or state[94]==1:  # no defense needed/able to be done
                return [Regent, actor, Type, 'move_troops_defend_friend', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                temp = temp[['Provence', 'CR']].groupby('Provence').sum().reset_index()
                temp['roll'] = np.random.randint(1, 100,temp.shape[0])+temp['CR']
                temp = temp.sort_values('roll', ascending=False)
                Target = temp.iloc[0]['Provence']
                Target_CR = int(2*temp.iloc[0]['CR']/3)
                temp = self.Troops[self.Troops['Regent']=='Regent'].copy()
                temp = temp[temp['Provence'] != Target]
                temp = temp[temp['Garrisoned']==0]
                if temp.shape[0] == 0:
                    return [Regent, actor, Type, 'move_troops_defend_friend', decision, friend, '', '', '',  False, -10, state, True, '']
                else:
                    temp['roll'] = np.random.randint(1, 100,temp.shape[0])+temp['CR']
                    temp = temp.sort_values('roll', ascending=False)
                    troops = []
                    provences = []
                    i = 0
                    cr = 0
                    for i, row in temp.iterrows():
                        if row['CR'] + cr < Target_CR and i < temp.shape[0]:
                            troops.append(row['Unit'])
                            provences.append(row['Provence'])
                            i += 1
                            cr = cr + row['CR']
                    success, reward, message = self.bonus_action_move_troops(Regent, troops, provences, Target)
                    reward = Target_CR
                    return [Regent, Actor, Type, 'move_troops_defend_provence', '', '', Target, '', success, reward, state, invalid, message]
        # decision[22] == 1:
        elif decision[22] == 1:  #move_troops_into_enemy_territory
            if state[43] == 0 or state[44]==0 or state[94]==1:  # not at war, or don't have troops
                return [Regent, actor, Type, 'move_troops_into_enemy_terrirtory', decision, enemy, '', '', '',  False, -10, state, True, '']
            else:
                # how badly do I hate this guy
                temp = self.Relationships[self.Relationships['Regent']==Regent]
                temp = temp[temp['Other']==enemy]
                try:
                    animosity = -1*temp['Diplomacy'].values[0]
                except:
                    animosity = 0
                if animosity <= 0:
                    animosity = 1
                # which should I attack?
                found = 0
                Target_Provence = ''
                s_dist = 9000
                temp = self.Provences[self.Provences['Regent']==enemy].copy()
                if temp.shape[0] == 0:
                    return [Regent, actor, Type, 'move_troops_into_enemy_terrirtory', decision, enemy, '', '', '',  False, -10, state, True, '']
                else:
                    temp['roll'] = np.random.randint(1, 100, temp.shape[0])
                    temp = temp.sort_values('roll')
                    for i, row in self.Provences[self.Provences['Regent']==enemy].copy().iterrows():
                        try:
                            new_dist = get_travel_cost(Regent, self.Troops[self.Troops['Regent']==Regent].iloc[0]['Provence'].values[0], row['Provence'], 'test')
                        except:
                            new_dist = 9000
                        if new_dist < s_dist*0.75:  # some randomness
                            s_dist = new_dist
                            found = 1
                            Target_Provence = row['Provence']
                    if found == 0:
                        return [Regent, actor, Type, 'move_troops_into_enemy_terrirtory', decision, enemy, '', '', '',  False, -1, state, True, '']
                    else:
                        temp = self.Troops[self.Troops['Regent']==Regent].copy()
                        troops = []
                        provences = []
                        for i, row in temp.iterrows():
                            if len(troops) <= animosity:
                                troops.append(row['Type'])
                                provences.append(row['Provence'])
                        success, reward, message = self.bonus_action_move_troops(Regent, troops, provences, Target_Provence)
                        reward = animosity + 5*state[87]
                        return [Regent, Actor, Type, 'move_troops_into_enemy_terrirtory', '', '', Target, '', success, reward, state, invalid, message]
        # decision[23] == 1:
        elif decision[23] == 1:  # muster_army
            # what can I muster
            race = self.Regents[self.Regents['Regent']==Regent]['Race'].values[0]
            temp = pd.merge(self.Holdings[self.Holdings['Regent']==Regent].copy()
                            , self.troop_units[self.troop_units['Type'] == race].copy()
                            , left_on='Type', right_on='Requirements Holdings'
                            , how='left').fillna(0)
            temp = temp[temp['Requirements Level']<=temp['Level']]
            temp = temp[temp['Unit Type'] != 0]
            temp = temp[temp['Unit Type'] != 'Levies']
            # can I afford it
            gold = self.Regents[self.Regents['Regent'] == Regent]['Gold Bars'].values[0]
            temp = temp[temp['Muster Cost'] <= gold]
            if temp.shape[0] < 1:
                return [Regent, actor, Type, 'muster_army', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                temp['roll'] = np.random.randint(1,100,temp.shape[0])
                temp = temp.sort_values('roll')
                success, reward, message = self.bonus_action_muster_armies(Regent, temp.iloc[0]['Unit Type'], temp.iloc[0]['Provence'], 1)
                reward = reward + 5*state[87] + state[43]
                return [Regent, actor, Type, 'muster_army', decision, '',  temp.iloc[0]['Provence'], '', '',  success, reward, state, False, '']
        # decision[24] == 1:
        elif decision[24] == 1:  # muster_levies
            temp = pd.merge(self.Holdings[self.Holdings['Regent']==Regent].copy()
                , self.troop_units[self.troop_units['Unit Type'] == 'Levies'].copy()
                , left_on='Type', right_on='Requirements Holdings'
                , how='left').fillna(0)
            temp = temp[temp['Requirements Level']<=temp['Level']]
            temp = temp[temp['Unit Type'] != 0]
            temp_ = pd.merge(temp[['Regent', 'Provence']], self.Provences[['Provence', 'Regent', 'Population']], on=['Provence', 'Regent'], how='left')
            temp_ = temp_[temp_['Population'] > 0]
            temp = pd.merge(temp_[['Provence']], temp, on='Provence', how='left')
            if temp.shape[0] < 1:
                return [Regent, actor, Type, 'muster_levies', decision, '', '', '', '',  False, -10, state, True, '']  
            else:
                temp = pd.merge(temp, self.Troops[self.Troops['Regent'] != Regent][['Provence', 'CR']].groupby('Provence').sum().reset_index(), on='Provence', how='left').fillna(0)
                temp = temp.sort_values('CR', ascending=False)  # raise levies in attacked provences if possible
                success, reward, message = self.bonus_action_muster_armies(Regent, 'Levies', temp.iloc[0]['Provence'], temp.iloc[0]['Level'])
                reward = reward + temp.iloc[0]['Level']*state[43]
                return [Regent, actor, Type, 'muster_levies', decision, '',  temp.iloc[0]['Provence'], '', '',  success, reward, state, False, '']
        # decision[25] == 1:
        elif decision[25] == 1:  # muster_mercenaries
            temp = pd.concat([self.Provences[self.Provences['Regent']==Regent][['Provence']]
                              , self.Holdings[self.Holdings['Regent']==Regent][['Provence']]], sort=False)
            mercs = self.troop_units[self.troop_units['Unit Type'].str.contains('Mercenary')]
            gold = self.Regents[self.Regents['Regent'] == Regent]['Gold Bars'].values[0]
            mercs = mercs[mercs['Muster Cost'] <= gold]
            if temp.shape[0] < 1 or mercs.shape[0] < 1:
                return [Regent, actor, Type, 'muster_mercenaries', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                temp = pd.merge(temp, self.Troops[self.Troops['Regent'] != Regent][['Provence', 'CR']].groupby('Provence').sum().reset_index(), on='Provence', how='left').fillna(0)
                temp['roll'] = np.random.randint(1,100,temp.shape[0])
                temp = temp.sort_values(['CR', 'roll'], ascending=False)
                race = self.Regents[self.Regents['Regent']==Regent]['Race'].values[0]
                mercs['roll'] = np.random.randint(1,20,mercs.shape[0]) + mercs['BCR'] + 5*mercs['Unit Type'].str.contains(race) - mercs['Muster Cost']
                mercs = mercs.sort_values('roll', ascending=False)
                success, reward, message = self.bonus_action_muster_armies(Regent, mercs.iloc[0]['Unit Type'], temp.iloc[0]['Provence'], 1)
                reward = -5 + 5*state[87] + 10*state[43]
                return [Regent, actor, Type, 'muster_mercenaries', decision, '',  temp.iloc[0]['Provence'], '', '',  success, reward, state, False, '']
        # Domain Only
        # decision[26] == 1:
        elif decision[26] == 1:  # contest_holding
            temp = pd.concat([self.Holdings[self.Holdings['Regent']==Regent]
                  , self.Provences[self.Provences['Regent']==Regent][['Regent', 'Provence']]], sort=False).fillna(0)
            temp = pd.merge(temp, self.Holdings[self.Holdings['Regent']==enemy], on='Provence')
            if state[3] == 1 or temp.shape[0] == 0 or state[95]==1:
                return [Regent, actor, Type, 'contest_holding', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                temp['roll'] = 10*(temp['Type_x']==temp['Type_y']) +5*temp['Level_y'] + np.random.randint(1,20,temp.shape[0]) - 20*temp['Contested_y']
                temp = temp.sort_values('roll', ascending=False) 
                success, reward, message = self.domain_action_contest(Regent, enemy, temp.iloc[0]['Provence'], temp.iloc[0]['Type_y'])
                reward = reward + state[87]*3
                if success:
                    reward = reward + 2*(temp.iloc[0]['Type_x']==temp.iloc[0]['Type_y']) + temp.iloc[0]['Level_y']
                return [Regent, actor, Type, 'contest_holding', decision, enemy, temp.iloc[0]['Provence'], '', temp.iloc[0]['Type_y'],  success, reward, state, False, message]
        # decision[27] == 1:
        elif decision[27] == 1:  # contest_provence
            if state[3] == 1 or state[77] == 0 or state[95] == 1:
                return [Regent, actor, Type, 'contest_provence', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                temp = self.Provences[self.Provences['Regent'] == enemy]
                temp = temp[temp['Loyalty'] != 'High']
                temp = temp[temp['Loyalty'] != 'Average']
                temp_ =  self.Holdings[self.Holdings['Type']=='Law']
                temp_ = temp_[temp_['Regent'] == enemy]
                temp_ = temp_[temp_['Contested'] == 0]
                temp = pd.merge(temp, temp_, on='Provence', how='left').fillna(0)
                temp = temp[temp['Level']==0]
                temp['roll'] = np.random.randint(1,100,temp.shape[0])
                temp = temp.sort_values('roll')
                success, reward, message = self.domain_action_contest(Regent, enemy, temp.iloc[0]['Provence'], 'Provence')
                reward = reward + state[87]*3
                return [Regent, actor, Type, 'contest_provence', decision, enemy, temp.iloc[0]['Provence'], '', '',  success, reward, state, False, message]
        # decision[28] == 1:
        elif decision[28] == 1 or decision[29] == 1 or decision[30] == 1 or decision[31]==1:  #create_law_holding, _guild_, _temple_, _source_
            if decision[28] == 1:
                Type = 'Law'
                N = 34
            elif decision[29] == 1:
                Type = 'Guild'
                N = 36
            elif decision[30] == 1: 
                Type = 'Temple'
                N = 35
            else:   
                Type = 'Source'
                N = 37
            
            temp = pd.concat([self.Provences[self.Provences['Regent']==Regent][['Provence']].copy()
                          ,self.Holdings[self.Holdings['Regent']==Regent][['Provence']].copy()], sort=False).drop_duplicates()
            # all neighboring provences to regent
            temp = pd.merge(temp, self.Geography.copy(), on='Provence', how='left').drop_duplicates()
            temp = temp[temp['Border']==1]
            temp['Provence'] = temp['Neighbor']

            temp_ = pd.merge(temp[['Provence']], self.Holdings[self.Holdings['Type'] == Type].copy(), on='Provence', how='left')
            dct = {}
            dct['Provence'] = []
            for p in set(temp_['Provence']):
                temp__ = temp_[temp_['Regent']==Regent]
                if temp__[temp__['Provence']==p].shape[0]==0:
                    dct['Provence'].append(p)
            temp_check = pd.DataFrame(dct)
            # Validity
            if state[3] == 1 or temp_check.shape[0] == 0 or state[94]==1 or (state[30]==1 and state[99]==0) or (state[31]==1 and state[100]==0):
                return [Regent, actor, Type, 'create_' + Type.lower() + '_holding', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                temp_check = pd.merge(temp_check, self.Provences[['Provence', 'Population', 'Regent']].copy(), on='Provence', how='left')
                temp_check = pd.merge(temp_check, self.Relationships[self.Relationships['Regent'] ==Regent][['Other', 'Diplomacy']], left_on='Regent', right_on='Other', how='left').fillna(0)

                temp_check['Where'] = temp_check['Population'] - temp_check['Diplomacy']*decision[28]
                temp_check = pd.merge(temp_check[['Provence', 'Where', 'Population']], self.Holdings[self.Holdings['Type']==Type].copy(), on='Provence', how='left')
                temp_check = pd.merge(temp_check, self.Relationships[self.Relationships['Regent'] ==Regent][['Other', 'Diplomacy']], left_on='Regent', right_on='Other', how='left').fillna(0)

                temp_check['Where'] = temp_check['Where'] - temp_check['Diplomacy']
                temp_check = temp_check.sort_values('Where', ascending=False)
                # More likely to set up shop in rival area
                success, reward, message = self.domain_action_create_holding(Regent, temp_check.iloc[0]['Provence'], Type)
                reward = reward + temp_check.iloc[0]['Where'] -10 + 15*state[N]
                return [Regent, actor, Type, 'create_holding', decision, enemy, temp_check.iloc[0]['Provence'], '', Type,  success, reward, state, False, message]                
        # decision[32] == 1:
        elif decision[32] == 1:  # declare_war
            if state[3] == 0:
                return [Regent, actor, Type, 'declare_war', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_declare_war(Regent, enemy)
                temp = self.Relationships[self.Relationships['Regent']==Regent]
                temp = temp[temp['Other']==enemy]
                if temp.shape[0] > 0:
                    reward = reward - temp.iloc[0]['Diplomacy']
                reward = reward + 5*state[87] - 5*state[89] + 5*state[80] -5*(1-state[23])
                return [Regent, actor, Type, 'declare_war', decision, enemy, '', '', '',  success, reward, state, False, message]
        # decision[33] == 1:
        elif decision[33] == 1: #diplomacy_form_alliance
            if state[3] == 1 or state[94]==1 or state[95]==1 or state[58]==1:
                return [Regent, actor, Type, 'diplomacy_form_alliance', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_diplomacy(Regent, friend, Type='form_alliance')
                reward = reward - state[87]*(1-state[65]*state[66])*5 - state[92]*state[90]*10  # aggressive only offers to superior friends, xeno needs same race 
                return [Regent, actor, Type, 'diplomacy_form_alliance', decision, friend, '', '', '',  success, reward, state, False, message]
        # decision[34] == 1:
        elif decision[34] == 1: #diplomacy_trade_agreement
            if state[3]==1 or state[94]==1 or state[95]==1 or state[64]==1:
                return [Regent, actor, Type, 'diplomacy_trade_agreement', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_diplomacy(Regent, rando, Type='trade_agreement')
                return [Regent, actor, Type, 'diplomacy_trade_agreement', decision, rando, '', '', '',  success, reward, state, False, message]
        # decision[35] == 1:
        elif decision[35] == 1: #diplomacy_troop_permission
            if state[3]==1 or state[94]==1 or state[95]==1 or state[58]==1 or state[2] == 1:  # pointless on third turn
                return [Regent, actor, Type, 'diplomacy_troop_permission', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_diplomacy(Regent, friend, Type='troop_permission')
                return [Regent, actor, Type, 'diplomacy_troop_permission', decision, friend, '', '', '',  success, reward, state, False, message]
        # decision[36] == 1:
        elif decision[36] == 1: #diplomacy_force_tribute
            if state[3]==1 or state[94]==1 or state[95]==1:  
                return [Regent, actor, Type, 'diplomacy_force_tribute', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_diplomacy(Regent, enemy, Type='force_tribute')
                return [Regent, actor, Type, 'diplomacy_force_tribute', decision, enemy, '', '', '',  success, reward, state, False, message]
        # decision[37] == 1:
        elif decision[37] == 1: #diplomacy_respond_to_brigandage
            if state[3]==1 or state[94]==1 or state[95]==1:  
                return [Regent, actor, Type, 'diplomacy_respond_to_brigandage', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_diplomacy(Regent, None, Type='deal_with_brigands')
                reward = reward + state[24]*10
                return [Regent, actor, Type, 'diplomacy_respond_to_brigandage', decision, '', '', '', '',  success, reward, state, False, message]
        # decision[38] == 1:
        elif decision[38] == 1: #diplomacy_respond_to_unrest
            if state[3]==1 or state[94]==1 or state[95]==1 or state[84]==0:  
                return [Regent, actor, Type, 'diplomacy_respond_to_unrest', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_diplomacy(Regent, Regent+'_rebel', Type='handle_unrest')
                reward = reward + state[24]*10
                return [Regent, actor, Type, 'diplomacy_respond_to_unrest', decision, '', '', '', '',  success, reward, state, False, message]
        # decision[39] == 1:
        elif decision[39] == 1: #forge_ley_lines
            if state[3]==1 or state[94]==1 or state[95]==1 or state[37]==0 or state[100]==0:  
                return [Regent, actor, Type, 'forge_ley_lines', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                try:
                    temp = self.Holdings[self.Holdings['Regent']==Regent].copy()
                    temp = temp[temp['Type']=='Source']
                    temp['Other'] = temp['Provence']
                    temp = pd.merge(temp[['Provence', 'Type','Level']], temp[['Other', 'Type']], on='Type', how='outer')
                    temp = temp[temp['Provence'] != temp['Other']]
                    temp = pd.merge(temp, self.LeyLines, on=['Provence', 'Other'], how='left').fillna(0)
                    temp = temp[temp['Regent']==0]
                    temp['Roll'] = np.random.randint(1,10,temp.shape[0])+temp['Level']
                    temp=temp.sort_values('Roll', ascending=False)
                    if temp.shape[0] == 0:
                        success, reward, message = self.domain_action_forge_ley_line(Regent, temp.iloc[0]['Provence'], temp.iloc[0]['Other'])
                    else:
                        return [Regent, actor, Type, 'forge_ley_lines', decision, '', temp.iloc[0]['Provence'], temp.iloc[0]['Other'], '',  False, 0, state, True, '']
                    return [Regent, actor, Type, 'forge_ley_lines', decision, '', temp.iloc[0]['Provence'], temp.iloc[0]['Other'], '',  success, reward, state, False, message]
                except:
                    dct = {}
                    dct['temp'] = temp
                    dct['decision'] = decision
                    dct['state'] = state
                    dct['Regent'] = Regent
                    self.errors.append(dct)
                    return [Regent, actor, Type, 'forge_ley_lines', decision, '', '', '', '',  False, 0, state, True, '']
        # decision[40] == 1:
        elif decision[40] == 1: # adventuring
            if state[3]==1:
                return [Regent, actor, Type, 'adventuring', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_adventure(Regent)
                reward = reward + state[94]*10  # good idea if broke
                return [Regent, actor, Type, 'adventuring', decision, '', '', '', '',  success, reward, state, False, message]
        # decision[41] == 1:
        elif decision[41] == 1:  # fortify_capital
            if state[3]==1 or state[94] == 1 or state[95] == 1 or state[23]==0:
                return [Regent, actor, Type, 'fortify_capital', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                level = (1-state[26])*np.random.randint(0,2,1)[0] + 1
                success, reward, message = self.domain_action_fortify(self, Regent, capital, level)
                reward = reward + 7*(1-state[26])
                return [Regent, actor, Type, 'fortify_capital', decision, '', capital, '', '',  success, reward, state, False, message]
        # decision[42] == 1:
        elif decision[42] == 1:  # fortify_high_pop
            if state[3]==1 or state[94] == 1 or state[95] == 1 or state[23]==0:
                return [Regent, actor, Type, 'fortify_high_pop', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                level = (1-state[27])*np.random.randint(0,2,1)[0] + 1
                success, reward, message = self.domain_action_fortify(self, Regent, high_pop, level)
                reward = reward + 5*(1-state[27])
                return [Regent, actor, Type, 'fortify_high_pop', decision, '', high_pop, '', '',  success, reward, state, False, message]
        # decision[43] == 1:
        elif decision[43] == 1:  # fortify_low_pop
            if state[3]==1 or state[94] == 1 or state[95] == 1 or state[23]==0:
                return [Regent, actor, Type, 'fortify_low_pop', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                level = (1-state[28])*np.random.randint(0,2,1)[0] + 1
                success, reward, message = self.domain_action_fortify(self, Regent, capital, level)
                reward = reward + 2*(1-state[28])
                return [Regent, actor, Type, 'fortify_low_pop', decision, '', low_pop, '', '',  success, reward, state, False, message]        
        # investure_invest_friend
        elif decision[44] == 1: 
            if state[3]==1 or state[95]==1:
                return [Regent, actor, Type, 'investure_invest_friend', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_investiture(Regent, Target=friend, Invest=True)
                reward = reward - 20 + 15*state[18] + 10*state[58] + 5*state[57]  # bad idea, unless giving away a legacy
                return [Regent, actor, Type, 'investure_invest_friend', decision, friend, '', '', '',  success, reward, state, False, message]
        # investure_divest_enemy
        elif decision[45] == 1: 
            if state[3]==1 or state[95]==1:
                return [Regent, actor, Type, 'investure_divest_enemy', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_investiture(Regent, Target=enemy, Divest=True)
                reward = reward + state[87]*5
                return [Regent, actor, Type, 'investure_divest_enemy', decision, friend, '', '', '',  success, reward, state, False, message]
        # investiture_become_vassal_friend
        elif decision[46] == 1: 
            if state[3]==1 or state[95]==1 or state[57]==1 or state[58]==1 or state[97]==0:
                return [Regent, actor, Type, 'investiture_become_vassal_friend', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_investiture(Regent, Target=friend, Vassal=True)
                reward = reward + state[51]*5 + state[52]*5
                return [Regent, actor, Type, 'investiture_become_vassal_friend', decision, friend, '', '', '',  success, reward, state, False, message]
        # investiture_claim_provence
        elif decision[47] == 1: 
            if state[3]==1 or state[95]==1 or state[96]==0:
                return [Regent, actor, Type, 'investure_claim_provence', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                Provence = pd.merge(self.Troops[self.Troops['Regent']=='Regent'], self.Provences[self.Provences['Regent']==''], on='Provence',how='inner')['Provence'].values[0]
                success, reward, message = self.domain_action_investiture(Regent, Provence, Claim=True)
                return [Regent, actor, Type, 'investure_iclaim_provence', decision, '', Provence, '', '',  success, reward, state, False, message]
        # rule_holdings
        elif decision[48] == 1: 
            if state[3]==1 or state[95]==1 or state[94]==1 or state[42]==0:
                return [Regent, actor, Type, 'rule_holdings', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_rule(Regent, Holdings=True)
                return [Regent, actor, Type, 'rule_holdings', decision, '', '', '', '',  success, reward, state, False, message]
        # rule_capital
        elif decision[49] == 1: 
            if state[3]==1 or state[95]==1 or state[94]==1 or state[23]==0:
                return [Regent, actor, Type, 'rule_holdings', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_rule(Regent, Holdings=false, Provence=capital)
                return [Regent, actor, Type, 'rule_capital', decision, '', capital, '', '',  success, reward, state, False, message]
        # rule_high_pop
        elif decision[50] == 1: 
            if state[3]==1 or state[95]==1 or state[94]==1 or state[23]==0:
                return [Regent, actor, Type, 'rule_high_pop', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_rule(Regent, Holdings=false, Provence=high_pop)
                return [Regent, actor, Type, 'rule_high_pop', decision, '', high_pop, '', '',  success, reward, state, False, message]
        # rule_low_pop
        elif decision[51] == 1: 
            if state[3]==1 or state[95]==1 or state[94]==1 or state[23]==0:
                return [Regent, actor, Type, 'rule_low_pop', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.domain_action_rule(Regent, Holdings=false, Provence=low_pop)
                return [Regent, actor, Type, 'rule_low_pop', decision, '', low_pop, '', '',  success, reward, state, False, message]
        # establish_trade_route_friend
        elif decision[52] == 1: 
            if state[3]==1 or state[95]==1 or state[94]==1 or state[56]==0 or state[23]==0:
                return [Regent, actor, Type, 'establish_trade_route_friend', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                # where from?
                try:
                    temp = pd.merge(self.Provences[self.Provences['Regent']==Regent][['Provence']], self.Geography, on='Provence', how='left')
                    temp['routes'] = temp['Shipping'] + temp['Caravan']
                    temp = temp[['Provence', 'routes']].groupby('Provence').sum().reset_index()
                    temp = pd.merge(temp, self.Provences[['Provence', 'Population']], on='Provence', how='left')
                    temp['allowed'] = ((temp['Population'] + 2)/3).asType(int)
                    temp['allowed'] = temp['allowed'].asType(str).str.replace('0','1').replace('4','3').replace('5','3')
                    temp['allowed']  = temp['allowed'].asType(int)
                    temp = temp[temp['routes'] < temp['allowed']]
                    temp = temp.sort_values('Population', ascending=False)
                    Base = temp.iloc[0]['Provence']
                    temp = pd.merge(self.Provences[self.Provences['Regent']==friend][['Provence']], self.Geography, on='Provence', how='left')
                    temp['routes'] = temp['Shipping'] + temp['Caravan']
                    temp = temp[['Provence', 'routes']].groupby('Provence').sum().reset_index()
                    temp = pd.merge(temp, self.Provences[['Provence', 'Population']], on='Provence', how='left')
                    temp['allowed'] = ((temp['Population'] + 2)/3).asType(int)
                    temp['allowed'] = temp['allowed'].asType(str).str.replace('0','1').replace('4','3').replace('5','3')
                    temp['allowed']  = temp['allowed'].asType(int)
                    temp = temp[temp['routes'] < temp['allowed']]
                    temp = temp.sort_values('Population', ascending=False)
                    Target = temp.iloc[0]['Provence']
                    success, reward, message = self.domain_action_trade_routes(Regent,Base,Target)
                    return [Regent, actor, Type, ' establish_trade_route_friend', decision, friend, Base, Target, '',  success, reward, state, False, message]
                    reward = reward
                except:
                    dct = {}
                    dct['temp']= temp
                    dct['state'] = state
                    dct['decision']=decision
                    dct['Regent'] = Regent
                    self.errors.append(dct)
                    return [Regent, actor, Type, ' establish_trade_route_friend', decision, friend, '', '', '',  False, 0, state, True, ''] 
        # establish_trade_route_rando
        elif decision[53] == 1: 
            if state[3]==1 or state[95]==1 or state[94]==1 or state[64]==0 or state[23]==0:
                return [Regent, actor, Type, 'establish_trade_route_friend', decision, rando, '', '', '',  False, -10, state, True, '']
            else:
                # where from?
                temp = pd.merge(self.Provences[self.Provences['Regent']==Regent][['Provence']], self.Geography, on='Provence', how='left')
                temp['routes'] = temp['Shipping'] + temp['Caravan']
                temp = temp[['Provence', 'routes']].groupby('Provence').sum().reset_index()
                temp = pd.merge(temp, self.Provences[['Provence', 'Population']], on='Provence', how='left')
                temp['allowed'] = ((temp['Population'] + 2)/3).asType(int)
                temp['allowed'] = temp['allowed'].asType(str).str.replace('0','1').replace('4','3').replace('5','3')
                temp['allowed']  = temp['allowed'].asType(int)
                temp = temp[temp['routes'] < temp['allowed']]
                temp = temp.sort_values('Population', ascending=False)
                if temp.shape[0] > 0:
                    Base = temp.iloc[0]['Provence']
                    temp = pd.merge(self.Provences[self.Provences['Regent']==rando][['Provence']], self.Geography, on='Provence', how='left')
                    temp['routes'] = temp['Shipping'] + temp['Caravan']
                    temp = temp[['Provence', 'routes']].groupby('Provence').sum().reset_index()
                    temp = pd.merge(temp, self.Provences[['Provence', 'Population']], on='Provence', how='left')
                    temp['allowed'] = ((temp['Population'] + 2)/3).asType(int)
                    temp['allowed'] = temp['allowed'].asType(str).str.replace('0','1').replace('4','3').replace('5','3')
                    temp['allowed']  = temp['allowed'].asType(int)
                    temp = temp[temp['routes'] < temp['allowed']]
                    temp = temp.sort_values('Population', ascending=False)
                    Target = temp.iloc[0]['Provence']
                    success, reward, message = self.domain_action_trade_routes(Regent,Base,Target)
                else:
                    success, reward, message = False, 0, 'No provences?'
                return [Regent, actor, Type, ' establish_trade_route_friend', decision, friend, Base, Target, '',  success, reward, state, False, message]
        # Realm Magic - Alchemy
        elif decision[54] == 1: 
            if state[3]==1 or state[37]==0 or state[95]==1:
                return [Regent, actor, Type, 'realm_magic_alchemy_self', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                Amount = 1+state[12]+state[13]+state[14]+state[15]+state[16]+5*state[17]
                success, reward, message = self.relam_magic_alchemy(Regent, Regent, Amount)
                reward = reward + 10*state[94]
                return [Regent, actor, Type, 'realm_magic_alchemy', decision, '', '', '', '',  success, reward, state, False, message]
        # Realm Magic - Alchemy Friend
        elif decision[55] == 1: 
            if state[3]==1 or state[37]==0 or state[95]==1:
                return [Regent, actor, Type, 'realm_magic_alchemy_friend', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                Amount = []
                Amount.append(1+state[12]+state[13]+state[14]+state[15]+state[16]+5*state[17])
                check = self.Relationships[self.Relationships['Regent']==Regent]
                try:
                    check = check[check['Other']==friend]['Diplomacy'].values[0]
                    Amount.append(check)
                except:
                    Amount.append(2)
                success, reward, message = self.relam_magic_alchemy(Regent, friend, min(Amount))
                reward = reward + 5*state[52]
                return [Regent, actor, Type, 'realm_magic_alchemy', decision, '', '', '', '',  success, reward, state, False, message]
        # realm_magic_bless_land
        elif decision[56] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[98]==0:
                return [Regent, actor, Type, 'realm_magic_bless_land', decision, friend, '', '', '',  False, -10, state, True, '']
            else:
                # get Targets
                temp = self.Holdings[self.Holdings['Regent']==Regent]
                temp = temp[temp['Type']=='Temple']
                temp['Roll'] = np.random.randint(1,6,temp.shape[0]) + temp['Level']
                temp = temp.sort_values('Roll', ascending=False)
                Target = list(set(temp['Provence']))
                if len(Target) > 4:
                    Target = Target[:4]
                success, reward, message = self.realm_magic_bless_land(Regent, Target)
                return [Regent, actor, Type, 'realm_magic_bless_land', decision, '', '', ', '.join(Target), '',  success, reward, state, False, message]
        # realm_magic_blight
        elif decision[57] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[98]==0:
                return [Regent, actor, Type, 'realm_magic_blight', decision, enemy, '', '', '',  False, -10, state, True, '']
            else:
                # get Targets
                temp = pd.concat([self.Provences[self.Provences['Regent']==enemy][['Provence']]
                                  , self.Holdings[self.Holdings['Regent']==enemy][['Provence', 'Level']]], sort=False).fillna(5)
                Target = list(set(temp['Provence']))
                if len(Target) > 4:
                    Target = Target[:4]
                success, reward, message = self.realm_magic_blight(Regent, Target)
                return [Regent, actor, Type, 'realm_magic_blight', decision, enemy, '', ', '.join(Target), '',  success, reward, state, False, message]
        # realm_magic_death_plague
        elif decision[58] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[19]==0:
                return [Regent, actor, Type, 'realm_magic_death_plague', decision, enemy, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_death_plague(Regent, enemy)
                return [Regent, actor, Type, 'realm_magic_death_plague', decision, enemy, '', '', '',  success, reward, state, False, message]
        # realm_magic_demagogue_friend
        elif decision[59] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1:
                return [Regent, actor, Type, 'realm_magic_demagogue_friend', decision, enemy, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_demagogue(Regent, friend, Increase=True)
                return [Regent, actor, Type, 'realm_magic_demagogue_friend', decision, friend, '', '', '',  success, reward, state, False, message]
         # realm_magic_demagogue_enemy
        elif decision[60] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1:
                return [Regent, actor, Type, 'realm_magic_demagogue_enemy', decision, enemy, '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_demagogue(Regent, enemy, Increase=False)
                return [Regent, actor, Type, 'realm_magic_demagogue_enemy', decision, enemy, '', '', '',  success, reward, state, False, message]
        # realm_magic_legion_of_the_dead_enemy
        elif decision[61] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1:
                return [Regent, actor, Type, 'realm_magic_legion_of_the_dead', decision, enemy, '', '', '',  False, -10, state, True, '']
            else:
                temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
                temp = temp[temp['Type']=='Source'][['Type', 'Level', 'Provence']]
                temp = temp[temp['Level']>=3]
                temp = pd.concat([temp[['Provence']], self.LeyLines[self.LeyLines['Regent']==Regent][['Provence']]])
                temp_ = self.Troops[self.Troops['Regent'] == enemy]
                temp_ = temp_[['Provence', 'CR']].groupby('Provence').sum().reset_index()
                temp = pd.merge(temp, temp_, on='Provence', how='left').fillna(0)
                temp = temp.sort_values('CR', ascending='False')
                if temp.shape[0] == 0:
                    return [Regent, actor, Type, 'realm_magic_legion_of_the_dead', decision, enemy, '', '', '',  False, -10, state, True, '']
                else:
                    success, reward, message = self.realm_magic_legion_of_the_dead(Regent, temp.iloc[0]['Provence'])
                    reward = reward + 5*state[80] + 5*state[81]
                    return [Regent, actor, Type, 'realm_magic_legion_of_the_dead', decision, enemy, temp.iloc[0]['Provence'], '', '',  success, reward, state, False, message]
        # realm_magic_legion_of_the_dead_capital
        elif decision[62] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1:
                return [Regent, actor, Type, 'realm_magic_legion_of_the_dead', decision, enemy, '', '', '',  False, -10, state, True, '']
            else:
                temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
                temp = temp[temp['Type']=='Source'][['Type', 'Level', 'Provence']]
                temp = temp[temp['Level']>=3]
                temp = pd.concat([temp[['Provence']], self.LeyLines[self.LeyLines['Regent']==Regent][['Provence']]])
                temp = temp[temp['Provence'] == capital]
                if temp.shape[0] == 0:
                    return [Regent, actor, Type, 'realm_magic_legion_of_the_dead', decision, '', capital, '', '',  False, -10, state, True, '']
                else:
                    success, reward, message = self.realm_magic_legion_of_the_dead(Regent, temp.iloc[0]['Provence'])
                    reward = reward
                    return [Regent, actor, Type, 'realm_magic_legion_of_the_dead', decision, '', temp.iloc[0]['Provence'], '', '',  success, reward, state, False, message]
        # realm_magic_mass_destruction
        elif decision[63] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[12]==0:
                return [Regent, actor, Type, 'realm_magic_mass_destruction', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_mass_destruction(Regent, enemy_capital)
                return [Regent, actor, Type, 'realm_magic_mass_destruction', decision, '', enemy_capital, '', '',  success, reward, state, False, message]
        # realm_magic_raze
        elif decision[64] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[79]==1 or state[12]==0:
                return [Regent, actor, Type, 'realm_magic_raze', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_raze(Regent, enemy)
                return [Regent, actor, Type, 'realm_magic_raze', decision, enemy, '', '', '',  success, reward, state, False, message]
        # realm_magic_stronghold_capital
        elif decision[65] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[79]==1 or state[12]==0 or state[6]==0 or state[23]==0:
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_stronghold(Regent, capital)
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', capital, '', '',  success, reward, state, False, message]
        # realm_magic_stronghold_high_pop
        elif decision[66] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[79]==1 or state[12]==0 or state[6]==0 or state[23]==0:
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_stronghold(Regent, high_pop)
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', high_pop, '', '',  success, reward, state, False, message] 
        # realm_magic_stronghold_low_pop
        elif decision[67] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[79]==1 or state[12]==0 or state[6]==0 or state[23]==0:
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_stronghold(Regent, low_pop)
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', low_pop, '', '',  success, reward, state, False, message]
        # realm_magic_stronghold_capital_perm
        elif decision[68] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[79]==1 or state[13]==0 or state[6]==0 or state[23]==0:
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_stronghold(Regent, capital, True)
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', capital, '', '',  success, reward, state, False, message]
        # realm_magic_stronghold_high_pop_perm
        elif decision[69] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[79]==1 or state[13]==0 or state[6]==0 or state[23]==0:
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_stronghold(Regent, high_pop, True)
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', high_pop, '', '',  success, reward, state, False, message] 
        # realm_magic_stronghold_low_pop_perm
        elif decision[70] == 1: 
            if state[3]==1 or state[35]==0 or state[94]==1 or state[95]==1 or state[79]==1 or state[13]==0 or state[6]==0 or state[23]==0:
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', '', '', '',  False, -10, state, True, '']
            else:
                success, reward, message = self.realm_magic_stronghold(Regent, low_pop, True)
                return [Regent, actor, Type, 'realm_magic_stronghold', decision, '', low_pop, '', '',  success, reward, state, False, message]  
        # Nothing Doin'
        else:
            return [Regent, actor, Type, 'None/Error', decision, '', '', '', '', False, 0, state, False, 'Error: No Action Returned']
    
    # Bonus Actions First
    def bonus_action_build(self, Regent, Provence, Road=None, player_gbid=None):
        '''
        
        
        Base Cost: Varies
        Base Success: DC 5

        For any the construction of any structure that is not a fortification 
        or holding, the Build action is the go-to for any regent. Many domain
        events will request that the regent provide the resources for the 
        creation of a guildhall, civic center, statue, or anything else the 
        people might need or desire.

        The self Master sets the Gold Bar cost of a particular construction
        project, which typically ranges from 1 GB for a small chapel to 30
        for a massive palace.

        Build is also useful for the construction of bridges and roads. Roads 
        enable troops and the populace to get about the province more easily,
        while bridges are used to cross rivers and chasms. A bridge can cost 
        anywhere from 2 to 5 GB (1d4+1). A road costs a single gold bar for a
        plains province; a forest, tundra, or desert costs two; a hilly 
        province or swamp costs four; and mountains cost eight. Typically,
        the construction of a “road” really means any number of paths 
        throughout the province.

        The more remote and rural a province, the more expensive a 
        construction project; this represents the cost to secure and move the 
        building materials to the site. If the target province for the 
        building project is rated as 0 or 1, the cost is doubled. If the 
        target province is 3 or 4, the cost is increased by 50%.

        A building project is never instantaneous. Each season, the progress 
        on a structure advances by 3 GB (or 1d6) of its cost. The project is
        considered complete when the full cost of the Build is accounted for
        in this way.

        Critical Success: The building project gets an excellent head start 
        and immediately completes 2d6 of its total building cost.

       
        Road = Target Provence
        
        Terrain (add both together)
        'Desert', 'Tundra', 'Forest', 'Steppes' 2
        'Mountain', 8
        'Glacier', 8
        'Hills', 'Swamp', 'Marsh' 4
        'Plains', Farmland' 1
        
        if bridge needed: + 1d4+1
        
        (multiply by population of higher population provence)
        Population < 2: 1
        Population 3,4: 3/4
        Population > 4: 1/2
        
        (add code to allow for timed project completion)
        
        INFO NEEDED:
        CAPITAL HAS ROADS TO ALL BORDERING PROVENCES IN DOMAIN
        not all provences connected by roads
        UNROADED PROVENCE BETWEEN SELF AND FRIEND
        HAVE PROVENCES
        
        build_road
        '''
        message = ''
        temp = pd.concat([self.Provences[self.Provences['Provence']==Provence], self.Provences[self.Provences['Provence']==Road]], sort=False)
        temp = pd.merge(temp, self.Geography[self.Geography['Neighbor']==Road], on='Provence', how='left').fillna(0)
        temp['Terrain'] = temp['Terrain'].str.replace('Desert', '2').replace('Tundra', '2').replace('Forest','2').replace('Steppes','2')
        temp['Terrain'] = temp['Terrain'].str.replace('Plains', '1').replace('Farmland','1')
        temp['Terrain'] = temp['Terrain'].str.replace('Hills','4').replace('Swamp','4').replace('Marsh','4')
        temp['Terrain'] = temp['Terrain'].str.replace('Mountains', '8').replace('Glacier','8').replace('Mountain','8')

        cost = np.sum(temp['Terrain'].asType(int))
        temp['bridge'] = temp['RiverChasm']*np.random.randint(2,5,temp.shape[0])
        cost = cost + np.sum(temp['bridge'])*2

        if np.max(temp['Population']) <= 2:
            cost = cost*1
        elif np.max(temp['Population']) >= 3 and np.max(temp['Population']) <= 4:
            cost = cost*3/4
        else:
            cost = cost/2
        cost = int(cost)

        # not always opposed
        target = temp[temp['Provence']==Road]['Regent'].values[0]
        if target != Regent:
            dc = self.set_difficulty(5, Regent, target)
        else:
            dc = 5

        if cost > self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:  # can't afford it
            success = False
            crit =  False
        else:
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - cost)
            success, crit = self.make_roll(Regent, dc, 'Persuasion', 'build_road', Player_gbid=player_gbid)
        if success:
            progress = cost
            if crit:
                progress = cost - (np.random.randint(1,6,1) + np.random.randint(1,6,1))  # 2d6 rolls dif than 2-12
            # make sure it doesn't already exist
            df = self.Projects[self.Projects['Project Type']=='Road'].copy()
            df[df['Details'] == '({}, {})'.format(Provence, Road)]
            if df.shape[0] > 0:
                progress = df.iloc[0]['Gold Bars Left'] - np.random.randint(1,6,1)
                self.Projects.loc[df.index.tolist()[0]] = [Regent, 'Road', '({}, {})'.format(Provence, Road), progress]
            else:
                try:
                    self.Projects.loc[max(self.Projects.index.tolist())+1] = [Regent, 'Road', '({}, {})'.format(Provence, Road), progress]
                except:
                    self.Projects.loc[0] = [Regent, 'Road', '({}, {})'.format(Provence, Road), progress]
            message = '{} built a road between {} and {}'.format(Regent, Provence, Road)
        else:
            message = '{} failed to build a road between {} and {}.'.format(Regent, Provence, Road)
        # reward
        reward = 5*success - 5*(1-success)
        if self.Regents[self.Regents['Regent']==Regent]['Attitude'].values[0] == 'Xenophobic':
            if self.Regents[self.Regents['Regent']==Regent]['Race'].values[0] != self.Regents[self.Regents['Regent']==target]['Race'].values[0]:
                reward = -10  #why build a road to let THEM in?
        return success, reward, message
        
    def bonus_action_decree(self, Regent, decType='Asset Seizure', court='Average', player_gbid=None):
        '''
        Type: Bonus
        Base Cost: 1 GB
        Base Success: DC 10

        A Decree encompasses a number of policies and processes that are not otherwise encompassed by other domain actions. While the list provided below is not the limit of what a Decree can do, any action that can be referred to as a Decree must fulfill the following criteria:

        The decree cannot affect another regent’s holdings or provinces.
        The decree cannot change the loyalty or level of any province or holding.
        Decrees cannot affect armies or assets in any way.
        Some examples of common Decrees are as follows. self Masters and players are encouraged to use Decree whenever no other action is suitable, but care must be taken not to go overboard with what a Decree can accomplish.

        A tax or asset seizure is enacted, generating 1d6 Gold Bars for your - treasury.
        A roustabout or rumormonger is arrested.
        A festival is declared throughout your domain.
        A bounty is offered for local monsters, which may draw adventurers to your territory.
        A minor act of legislation is passed regarding changes to the law, acceptable behaviors, or cultural integration.
        A minor event is dealt with by placating the petitioning party through offerings and compensation.
        Furthermore, the condition of the regent’s court may cause this check to be made at advantage or disadvantage, or not at all. See the section on Court Expenses for more details.
        
        
        decree_general
        decree_asset_seizure
        '''
        cost = 1
        dc = 10
        skill = 'Persuasion'
        adj = False
        dis = False
        if court == 'Bare':
            dis = True
        elif court == 'Rich':
            adj = True
        if cost > self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:  # can't afford it
            success = False
            crit =  False
        else:
            success, crit = self.make_roll(Regent, dc, skill, adj, dis)
        if success:
            if decType != 'Asset Seizure':
                # regular decree
                lst = ['!Regent had A roustabout or rumormonger arrested.'
                        , "A festival is declared throughout !Regent's domain."
                        , '!Regent offered a bounty for local monsters, which may draw adventurers to their territory.'
                        , '!Regent passed a minor act of legislation regarding changes to the law, acceptable behaviors, or cultural integration.'
                        , '!Regent dealt with a minor even by placating the petitioning party through offerings and compensation.']
                message = lst[int(np.random.randint(1,5,1))]
                reward = 0
                try:
                    if self.random_override[Regent] == 'Matter of Justice':
                        del self.random_override[Regent]
                        reward = 5
                except:
                    reward = 0
            else:
                roll = np.random.randint(1,6,1)
                message = '!Regent applies a tax or asset seizure, and gains {} gold bars.'.format(roll)
                cost = cost - roll
            reward = 3
        else:
            message = '!Regent tried to make a decree, but failed.'
            reward = 0
        self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - cost)
        return success, reward, message
            
    def bonus_action_disband(self, Regent, units, Provence):
        '''
        Type: Bonus

        Base Cost: None

        Base Success: DC 10 (or Automatic)

        This action is used to break up units under the regent’s command. Any
        number of units can be affected by this action, and if the units are of 
        regular troops, the success is automatic. The spending of a bonus 
        action represents the discharge papers, paying final expenses, and 
        ensuring no soldier makes off with military equipment.
   
        If the targeted unit is a mercenary unit, a domain action check must be
        rolled for each unit. On a success, nothing untoward happens. If the 
        check fails, the mercenary units become units of brigands within the 
        provinces where they were disbanded.
        
        The regent can also use this action to dismantle any holdings or assets
        that they no longer wish to maintain. The effect is immediate, and the
        holding/asset will no longer generate RP or GB for the regent starting 
        on the next season.
        
        INFO NEEDED
        has_military_units
        has_levees
        has_mercenaries
        
        
        disband_army
        disband_levees
        disband_mercenaries
        '''
        df = self.Troops[self.Troops['Regent'] == Regent].copy()
        for i, unit in enumerate(units):
            self.disband_troops(Regent, Provence[i], unit, Killed=False)
    
    def bonus_action_finances(self, regent, number=1):
        '''
        Type: Bonus

        Base Cost: None

        Base Success: Automatic

        Through this action, it is possible for regents to turn Gold Bars from 
        their treasury into liquid assets to purchase personal equipment or pay
        ransoms without using official channels. This action may be performed 
        only once per season, and the number of Gold Bars that can be converted
        is equal to the sum total of all Guild holding levels the regent 
        controls, plus their Bloodline modifier. Each Gold Bar converted 
        becomes 2000 gold pieces of currency in the regent’s possession.
        

        Thus, if Erin Velescarpe (Bloodline score 15) controls four guild 
        holdings of levels 1, 2, 2, and 4, she can convert up to 11 Gold Bars 
        into coins. Regents must be careful not to bankrupt their kingdoms 
        using this action.
        
        (not for agents)
        '''
        
        
    # Bonus & Domain
    def domain_action_agitate(self, Regent, Target, Conflict, Provences=None, bid=None):
        '''
        Base Cost: 1 RP, 1 GB
        Base Success: DC 10

        You may attempt to build sentiment or foster conflict within a targeted province (or multiple 
        provinces). To do this, you must control a holding within the target province. You must pay the listed 
        cost for each province you are affecting, and all of those provinces must be part of the same domain.
        You may Agitate in your own provinces in order to improve your standing within your own territory.

        If the regent who owns the targeted provinces is in support of your actions, you make your domain 
        action check at advantage. If they are opposed, your base success DC increases by the level of the 
        highest Law holding they possess in that province. You must make the domain action check for each 
        targeted province, making this a potentially expensive course of action if you are in conflict with 
        the regent of the lands you are affecting.

        Any targeted province affected by your Agitate attempt increases or decreases its loyalty by one 
        grade, at your discretion.

        Bonus Action: Agitate may be performed as a bonus action if you control a temple holding in the
        targeted province. If you are targeting multiple provinces, this cannot be done as a bonus action.

        Critical Success: The loyalty of the affected province is increased or decreased by two grades instead 
        of one.
        
        Target is a regent.  if a bonus action, will be a randomly determined provence
        in their domain (or Provences if Player)
        
        if conflict==True:
            DC increases by highest Law holding involved
            
        if conflict==False:
            Advantage on the roll.
            
        nat 20: +2 or -2.
        
        INFO NEEDED 
        Temple Holding in Friend/Liege Provence, 
        Temple Holding in Enemy Provence
        Has Temple Holding (can't do without)
        
        agitate_conflict_true
        agitate_conflict_false
        '''
        cost = len(Provences)
        dc = 10
        # spend the money and regency
        
        # set the dc
        adj = (Conflict == False)
        dc = self.set_difficulty(dc, Regent, Target, hostile=Conflict)
        # roll 'em
        success, crit = self.make_roll(Regent, dc, 'Persuasion', adj=False, dis=False, player_gbid=bid)
        add = -1*Conflict + 1-Conflict
        dip = add
        if cost > self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:
            success = False
        else:
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - cost, Regency_Points = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0] - cost)
        if crit:
            add = 2*add
        if success:
            # make the changes
            temp = {}
            temp['Provence'] = Provences
            temp = pd.DataFrame(temp)
            temp = pd.merge(temp, self.Provences.copy(), on='Provence', how='left')
            temp['Loyalty'] = temp['Loyalty'].str.replace('Rebellious','0').replace('Poor','1').replace('Average','2').replace('High','3').astype(int) + add 
            temp['Loyalty'] = temp['Loyalty'].astype(str).str.replace('-2', 'Rebellious').replace('-1', 'Rebellious').replace('0', 'Rebellious').replace('1', 'Poor').replace('2', 'Average').replace('3', 'High').replace('4', 'High').replace('5', 'High')
            for i, row in temp.iterrows():
                self.change_provence(row['Provence'], Loyalty=row['Loyalty'])
            
            if dip == -1:
                message = '{} agitated the people against {} in the following provences: {}'.format(Regent, Target, ', '.join(Provences))
            else:
                message = '{} used their influence to rally the people behind {} in the following provences: {}'.format(Regent, Target, ', '.join(Provences))
            # change diplomacy (Target cares)
            self.add_relationship(Target, Regent, Diplomacy=dip)
            temp = self.Relationships[self.Relationships['Regent']==Regent].copy()
            if temp[temp['Other']==Target]['Diplomacy'].shape[0] > 0:
                reward = dip*temp[temp['Other']==Target]['Diplomacy'].values[0]
            else:
                reward = 0
            attitude = self.Regents[self.Regents['Regent']==Regent]['Attitude']
        else:
            message = '{} failed to change peoples minds about {} in {}'.format(Regent, Target, ', '.join(Provences))
            # change diplomacy (Target cares)
            self.add_relationship(Target, Regent, Diplomacy=dip)
            reward = 0
        return success, reward, message
        
    def domain_action_espionage(self, Regent, Target, Provence, Type, prbid=0, pgbid=0):
        '''
        Type: Action (or Bonus)

        Base Cost: 1 GB
        Base Success: DC 15

        At the heart of being a regent is having a good spy network. The 
        Espionage action covers all manner of skulduggery and legerdemain on 
        behalf of your domain. The regent must declare the intent of the 
        Espionage action before making their domain action check. Espionage can:

        Uncover the details of diplomatic agreements between one domain and its 
        allies, even ones otherwise kept secret (using the province rating of 
        the capital).
        
        Determine troop movements and strength in foreign provinces.
        
        Create an assassination, intrigue, corruption, or heresy event in a 
        target domain (using the province rating of the capital).
        
        Trace another Espionage action performed against you.
        
        Move individuals or transportable assets in secret from one location to another.
        
        Rescue hostages in a foreign province.

        For hostile Espionage actions, the target DC is modified by the level of the 
        province in which Espionage is being performed, as well as the levels of any 
        Law holdings within those provinces. For example, Erin Velescarpe wishes to 
        send agents to investigate rumors of Baron Gavin Tael forming a secret alliance 
        with the Gorgon to expand his own holdings. Her base DC of 15 is increased by 
        the level of the Baron’s capital province (6) and the Law holding in his 
        capital province (4). This increases her DC to 25 -- Erin will be spending a 
        great deal of gold financing this endeavor.

        If the roll fails by 10 or more, then the regent’s spy is caught and 
        imprisoned. They may attempt to rescue the agent with additional 
        Espionage attempts, and the self Master should secretly determine if 
        the agent is successfully interrogated.

        Espionage is dangerous, difficult, and requires a massive investment of 
        Gold Bars to have a solid chance at success. However, the reward for 
        successful Espionage are rich and the destabilization it can create 
        rivals that of invading troops.

        Bonus Action: If you control a Guild holding in the target province, 
        you may enact Espionage as a bonus action when targeting that province.
        
        Critical Success: The regent may select one other effect of Espionage 
        to take place concurrently and at no extra cost.
        
        INFO NEEDED
        was_victim_of_espionage
        
        espionage_diplomatic_details
        espionage_discover_troop_movements
        espionage_assassination
        espionage_intrigue
        espionage_corruption
        espionage_heresy
        espionage_trace_espionage
        
        '''
        # assassination flag for roll
        assassination = False
        if Type == 'Assassination':
            assassination = True
        cost = 1
        dc = 15
        lst = [Regent, Target, '', '', '', '']
        # adjust dc based on provence targeted
        victim = self.Regents[self.Regents['Regent'] == Target]['Full Name'].values[0]

        if Type != 'Investigate' and Type != 'Trade':
            # For hostile Espionage actions, the target DC is modified by the level of the province in which Espionage is being performed, 
            dc = dc + self.Provences[self.Provences['Provence'] == Provence]['Population'].values[0]
            # as well as the levels of any Law holdings within those provinces.
            temp = self.Holdings[self.Holdings['Provence'] == Provence].copy()
            dc = dc + np.sum(temp[temp['Type']=='Law']['Level'])
            
        # now, opposition
        dc = self.set_difficulty(dc, Regent, Target, hostile=True, assassination=assassination, player_rbid=prbid)
        if Type == 'Investigate':
            success, crit = self.make_roll(Regent, dc, 'Insight', player_gbid=pgbid)
        else:
            success, crit = self.make_roll(Regent, dc, 'Deception', player_gbid=pgbid)
        # capital check
        Capital = self.Provences[self.Provences['Provence'] == Provence]['Capital'].values[0]
        if cost > self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:
            success = False
        else:
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - cost, Regency_Points = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0] - cost)
        # Results...
        if Type == 'Assassination':
            lst[2] = self.Season
            # this one is serious
            if Capital == False and crit == False:
                success = False  # bonus action to kill cannot succeed unless a crit if not in capital
            reward = 0
            message = "An attempt was made on {}'s life!".format(victim)
            if success == True:
                self.change_regent(Target, Alive=False)
                message = "{} was assassinated!".format(victim)
                temp = self.Relationships.copy()
                temp = temp[temp['Regent']==Regent].copy()
                try:
                    reward = 5 + -1*temp[temp['Other']==Target]['Diplomacy'].values[0]
                except:
                    reward = 5
            if self.Regents[self.Regents['Regent']==Regent]['Attitude'].values[0] == 'Aggressive':
                reward = 2*reward
            if 'E' in list(self.Regents[self.Regents['Regent']==Regent]['Alignment'].values[0]):
                reward = int(reward*1.5)
            if 'G' in list(self.Regents[self.Regents['Regent']==Regent]['Alignment'].values[0]):
                reward = reward - 5
            if self.Regents[self.Regents['Regent']==Regent]['Attitude'].values[0] == 'Peaceful':
                reward = reward - 3
        elif Type == 'Troops':
            lst[4] = self.Season
            reward = 0
            temp = self.Troops[self.Troops['Regent']==Target].copy()
            if temp[temp['Provence'] == Provence].shape[0] == 0:
                success = False  # no troops there.
            if success:
                temp = self.Relationships.copy()
                temp = temp[temp['Regent']==Regent].copy()
                try:
                    reward = 5 + -1*temp[temp['Other']==Target]['Diplomacy'].values[0]
                except:
                    reward = 5
                if self.Regents[self.Regents['Regent']==Regent]['Attitude'].values[0] == 'Aggressive':
                    reward = 2*reward
            message = "Spied on {}'s troops!".format(victim)
        elif Type == 'Trade':
            lst[3] = self.Season
            reward = 0
            temp = self.Geography[self.Geography['Provence']==Provence].copy()
            if pd.concat([temp[temp['Caravan']==1].copy(), temp[temp['Shipping']==1].copy()], sort=False).shape[0] == 0:
                success = False
            if success:
                temp = self.Relationships.copy()
                temp = temp[temp['Regent']==Regent].copy()
                try:
                    reward = 5 + -1*temp[temp['Other']==Target]['Diplomacy'].values[0]
                except:
                    reward = 5
            message = "Spied on {}'s Trade Routes!".format(victim)
        elif Type == 'Investigate':
            reward = 0
            temp = self.Geography[self.Geography['Provence']==Provence].copy()
            message = "Failed to find evidence that {} used espionage on them.".format(victim)
            temp = self.Espionage[self.Espionage['Regent']==Target].copy()
            temp = temp[temp['Target']==Regent].copy()
            found = 0
            if temp.shape[0] == 0:
                success = False  # no espionage from target
            else:  # change diplomacy to show what they did and how it impacts relations
                temp['roll'] = np.random.randint(1,100,temp.shape[0])
                temp = temp.sort_values('roll')
                found = np.sum(pd.concat([temp[temp[a]==self.Season][a] for a in ['Assassination', 'Assassination', 'Diplomacy', 'Troop Movements', 'Other']]))
                if crit and temp.shape[0] >= 2:
                    found = np.sum(pd.concat([temp[temp[a]==self.Season-1][a] for a in ['Assassination', 'Assassination', 'Diplomacy', 'Troop Movements', 'Other']]))
                self.add_relationship(Target, Regent, Diplomacy=-1*found)
            if success:
                temp = self.Relationships.copy()
                temp = temp[temp['Regent']==Regent].copy()
                try:
                    reward = 5 + -1*temp[temp['Other']==Target]['Diplomacy'].values[0]
                except:
                    reward = 5
                message = "Determined if {} used espionage on them.".format(victim)
            
        else:
            lst[5] = 1
            reward = 0
            if success:
                temp = self.Relationships.copy()
                temp = temp[temp['Regent']==Regent].copy()
                try:
                    reward = 5 + -1*temp[temp['Other']==Target]['Diplomacy'].values[0]
                except:
                    reward = 5
                self.random_override[Target] = Type
                if self.Regents[self.Regents['Regent']==Regent]['Attitude'].values[0] == 'Aggressive':
                    reward = 2*reward
            message = "Caused {} in {}'s court!".format(Type, victim)
        # update espionage thing ['Regent', 'Target', 'Assassination', 'Diplomacy', 'Troop Movements', 'Other']
        if success == True:
            self.Espionage = self.Espionage.append(pd.DataFrame([lst], columns=['Regent', 'Target', 'Assassination', 'Diplomacy', 'Troop Movements', 'Other']), sort=True)
        return success, reward, message
        
    def bonus_action_grant(self, Regent, Target, Amount):
        '''
        Grant
        Type: Bonus
        Base Cost: Special
        Base Success: DC 10 (Automatic, see below)

        This domain action is used by regents who wish to reward helpful 
        servants with titles or gifts of wealth. Typically, this is used when 
        resolving a domain event that requires the appointing or appeasement of
        a government official. It can also be used to give another regent money 
        from your treasury in the form of Gold Bars.

        Unlike other domain actions, the domain action check is made not to see 
        if the action succeeds, but whether anyone is potentially angered by 
        the Grant (especially in the case of giving out wealth). Every Gold Bar 
        that exchanges hands in this way increases the DC by 1. Should anyone 
        be offended by the use of a Grant, it will force a corruption, 
        intrigue, or unrest event on the next season.
        
        bonus_action_grant
        '''
        cost = Amount
        dc = 9 + Amount
        reward = 0 - cost
        success, crit = self.make_roll(Regent, dc, 'Persuasion')
        if cost > self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:
            success = False
        else:
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - cost)
            self.change_regent(Target, Gold_Bars = self.Regents[self.Regents['Regent']==Target]['Gold Bars'].values[0] - cost)
        if success == False:
            roll = np.random.randint(1,20,1)
            if roll <= 8:
                self.random_override[Regent] = 'Corruption'
            elif roll <= 16:
                self.random_override[Regent] = 'Intrigue'
            else:
                self.random_override[Regent] = 'Unrest'
        else:
            if crit == True:
                self.add_relationship(Regent, Target, Diplomacy=1)
                reward = reward + 5
        
        message = '{} granted {} {} Gold Bars'.format(self.Regents[self.Regents['Regent']==Regent]['Full Name'], self.Regents[self.Regents['Regent']==Target]['Full Name'], cost)
        return success, 0, message
        
    def bonus_action_lieutenant(self, Regent):
        '''
        Type: Bonus
        Base Cost: 1 GB
        Base Success: Automatic

        The regent raises a retainer or henchman NPC to the status of a
        lieutenant. A lieutenant can be another player character if that player 
        character is not themselves a regent. Anyone can be a lieutenant, 
        whether they possess a bloodline or not. The lieutenant typically 
        possesses character levels and may undertake missions in the regent’s 
        stead. NPC lieutenants require upkeep, and are paid on the Maintenance
        Costs phase of the season.
        
        Lieutenants are extremely useful in that they provide the regent with a 
        single additional bonus action that may be used at any point in the 
        action phases of the season, provided the lieutenant is within the 
        boundaries of the regent’s domain at the time. Once this bonus action is
        used, it cannot be used again on any subsequent turn in the round. The
        regent cannot benefit from having multiple lieutenants in this regard,
        but many regents keep additional lieutenants around in case one becomes
        occupied.

        Some random events may require the use of a lieutenant to adjudicate 
        outcomes, thus consuming the lieutenant’s attention for the season. This 
        forfeits any bonus action they would have otherwise granted, unless the
        regent has another lieutenant handy.

        For example, Erin Velescarpe raises up her brother, Eist, as a 
        lieutenant. While he is not a regent, he acts in her stead where she
        cannot. She uses him several times to perform Decrees while she tends to
        more pressing matters.

        Eventually, an event arises within Erin’s domain requiring the personal 
        attention of the regent. Instead, Erin dispatches Eist to settle the
        matter, and does not gain his bonus action this season.
        
        bonus_action_lieutenant
        '''
        cost = 1
        success = True
        message = "Could not afford to hire a lieutenant"
        if cost > self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:
            success = False
        else:
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - cost)
            name = 'Lieutenent Insert Name Later'
            self.add_lieutenant(Regent, name, True)
            message =  '{} hired {} as a Lieutenant'.format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], name)
        return success, 5, message
        
    def bonus_action_move_troops(self, Regent, Troops, Provence, Target):
        '''
        Type: Bonus
        Base Cost: 1 GB
        Base Success: Automatic

        Using this domain action, the regent orders any number of loyal troops
        to another location within their own domain. Financing the movement of 
        the troops costs 1 GB for every 10 units or provinces; for example, 1 GB
        can move a unit across 10 provinces, or 10 units across 1 province, or 
        any combination that can be mathematically derived. The troops are not 
        available for use while moving, and the movement completes at the end of 
        the action round, whereupon they become available for battles waging in 
        that province.

        If the regent’s domain is invaded during use of the Move Troops action,
        they can abort any movement that is in progress to come to the defense 
        of an invaded province, but forfeit any GB spent.
        
        INFO NEEDED
        enemy_troops_in_domain
        enemy_troops_in_friends_domain
        at_war
        
        move_troops_defend_provence
        move_troops_defend_friend
        move_troops_into_enemy_territory
        move_troops_to_provence
        '''
        gold = self.Regents[self.Regents['Regent'] == Regent]['Gold Bars'].values[0]
        cost = 0
        points = 9
        for i, unit in enumerate(Troops):
            cost = int(points/10)
            if cost <= gold:
                points = points + get_travel_cost(Regent, provneces[i], Target, unit)
                if int(points/10) <= gold:
                    # do this!
                    temp = self.Troops[self.Troops['Regent']==Regent].copy()
                    temp = temp[temp['Unit'] == unit]
                    temp = temp[temp['Provence'] == Provence]
                    temp = temp[temp['Garrisoned'] == 0]
                    move = 0
                    for i, row in temp.iterrows():
                        if move == 0:
                            move = 1  # only move the 1...
                            self.Troops.loc[i] = [row['Regent'], Target, row['Type'], row['Cost'], row['Garrisoned'], row['Home']]
        self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - int(points/10))
        return True, 0, '{} moved {} to {}'.format(self.Regents[self.Regents['Regent'] == Regent]['Full Name'].values[0], Troop, Target)
        
    def bonus_action_muster_armies(self, Regent, Type, Provence, N=1):
        '''
        Type: Bonus
        Base Cost: Special
        Base Success: Automatic

        The regent calls up his provinces to war, or raises troops in any
        province where they maintain a holding. This can take the form of 
        raising peasant levies, drawing up trained soldiers, or hiring 
        mercenaries. They must pay the GB cost of any unit, as listed in its 
        entry. A province can raise a number of military units equal to its 
        level in a single season. If the troops are being raised in a province 
        you do not control, the owning regent can automatically deny you this 
        action.

        Units cannot be used in the same action round in which they are 
        mustered, unless those units are mercenaries (which can be used 
        immediately, but mercenaries come with their own risks).

        If the Type of unit a regent musters is a Levy, it comes with an 
        additional cost. The province level is temporarily reduced by 1 each 
        time Levies are mustered from that province (see the section on Armies 
        for more details). The rating is restored when the unit is disbanded,
        but if those units are ever destroyed in combat, the province level is
        permanently reduced. Levies cost nothing to muster, but are dangerous to
        use for this reason.  [reduce it, add back when disbanded]
        
        INFO NEEDED
        more_troops_than_enemy
        enemy_troops_in_domain
        at_war
        
        
        muster_army
        muster_levies
        muster_mercenaries
        '''
        Home = ''
        Garrisoned = 1
        # make sure they can muster the troop...
        temp = self.troop_units[self.troop_units['Unit Type']==Type]
        if 'Mercenary' not in Type or 'Levies' not in Type:
            temp = temp[temp['Type'] == self.Regents[self.Regents['Regent']==Regent]['Race'].values[0]]
        temp = pd.merge(temp[['Requirements Holdings', 'Requirements Level']], self.Holdings[self.Holdings['Regent']==Regent].copy()
                        , left_on='Requirements Holdings', right_on='Type')
        temp = temp[temp['Requirements Level'] <= temp['Level']]

        if temp[temp['Provence']==Provence].shape[0] == 0 and temp.shape[0]>0:
            temp['Roll'] = np.random.randint(1,100,temp.shape[0])
            temp = temp.sort_values('Roll')
            Provence = temp.iloc[0]['Provence']
        if 'Levies' in Type:
            temp = pd.merge(temp, self.Provences[self.Provences['Population']>0], on='Provence', how='left').fillna(0)
            temp = temp[temp['Population'] > 0]
        # Go
        if temp.shape[0]==0:
            success = True
            if Type == 'Levies':
                Home = Provence
                check = self.Provences[self.Provences['Provence']==Provence]['Population'].values[0]
                # prevent non-provence holder from raising levies - commented out.
                if check == 0: # and self.Provences[self.Provences['Provence']==Provence]['Regent'] != Regent:
                    success = False
                if N > check:
                    N = check
                self.change_provence(Home, Population_Change=-1*N)
            elif Type == 'Mercenaries':
                Garrisoned = 0
            cost = self.troop_units[self.troop_units['Unit Type'] == Type]['Muster Cost'].values[0]
            if success == True:
                for i in range(N):
                    if cost <= self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:
                        self.add_troops(Regent, Provence, Type, Home=Home)
                        self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]-cost)
            return success, 0, 'Mustered {}s'.format(Type)
        else:
            success = False
            return success, 0, 'Cannot Muster {} in {}'.format(Type, Provence)
        
    # Domain Only
    def domain_action_adventure(self, Regent):
        '''
        Cost: None
        Success: Auto
        
        The call to adventure affects even an established regent from time to time. It’s a major
        responsibility that one sets aside to wander the countryside in an effort to gain fame and
        fortune, or to handle certain situations personally. Choosing to adventure uses up a 
        domain action for the round. Any adventure that takes longer than approximately four weeks
        risks consuming an additional domain action on the next round.
        
        INFO NEEDED NONE
        For NPCs, this is a way to generate some GB for Free, potentially,
        '''
        
        temp = self.Regents[self.Regents['Regent']==Regent].copy()
        message = '{} went adventuring.'.format(temp.iloc[0]['Full Name'])
        reward = 0
        if temp.iloc[0]['Player'] == False:
            check = int(temp.iloc[0]['Level']/3)+2
            temp['Reward'] = np.random.randint(0,check,temp.shape[0])  # 0-4
            self.change_regent(Regent, Gold_Bars = temp['Gold Bars'].values[0]+temp['Reward'].values[0])
            reward = temp['Reward'].values[0]
        return True, reward, message
                   
    def domain_action_contest(self, Regent, Target, Provence, Type, gbid=None):
        '''
        Cost: 1 RP
        success: DC 10
        By contesting a holding or province, a regent attempts to tie it up in claims over its ownership,
        argue over its legitimacy, or otherwise undermine its functions. You must control a holding in the
        same province as the targeted holding in order to Contest.

        To contest a holding, the regent states their intent to do so over a single holding or any number of
        holdings within a given domain. They must pay the cost for each holding contested. A contested holding
        increases the base success DC by its level (thus a level 4 Law holding has a DC of 14 to contest), and
        a domain action check must be made for each targeted holding.

        A successful Contest means the holding is in conflict, and generates no RP or GB for its owner on 
        their next season. This manner of contesting lasts until one of the following conditions is met:

        The owning regent succeeds at a Rule action targeting the holding(s) in particular.
        The attacking regent relents of their own free will on their next domain action (this does not cost an
        action).
        The attacker loses control of all of their holdings in the targeted province, or loses control of the 
        province (if contesting in their own lands).
        A second successful Contest by any regent causes its owner to lose all control of it, and the holding
        becomes free of the control of any regent until brought to heel.

        To Contest a province, the province may not possess any Law holdings higher than level 0 that are not
        under your control, and must be at rebellious or poor loyalty. The province’s level increases the DC
        to Contest (thus a level 4 province has a DC of 14 to contest). Success indicates the province will no
        longer generated RP or GB for its owner, and is ripe to be divested (see Investiture below).

        Armies that occupy a province unchallenged automatically Contest the province in favor of their
        regent, and no roll must be made.

        Critical Success: You recuperate the RP spent on this action.
        
        INFO NEEDED:
        enemy_has_(Type)_holding in my lands
        enemy_has_same_Type_of_holding_as_me_somewhere_i_have_holding
        i have contested holding
        i have contested provence
        enemy_has_contested_holding
        enemy_has_contested_provence
        enemy_has_no_law_holdings_and_rebellious_or_poor_loyalty_in_a_province
        
        
        contest_holding
        contest_provence
        '''
        cost = 1
        dc = 10
        if Type == 'Provence':  # The province’s level increases the DC to Contest
            dc = dc + self.Provences[self.Provences['Provence']==Provence]['Population'].values[0]
        # roll it up
        dc = self.set_difficulty(dc, Regent, Target, hostile=True)
        success, crit = self.make_roll(Regent, dc, 'Persuasion', player_gbid=gbid)
        if crit == False:
            self.change_regent(Regent, Regency_Points = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0] - 1)
        reward = 0
        if success:
            # resent the attempt
            self.add_relationship(Target, Regent, Diplomacy=-1)
            # reward!
            temp = self.Relationships[self.Relationships['Regent'] == Regent].copy()
            temp = temp[temp['Other'] == Target]
            if temp.shape[0] > 0:
                reward = int(-1.25*temp['Diplomacy'].values[0])
        if Type != 'Provence':
            message = 'Failed to contest a {} Holding in {}'.format(Type, Provence)
            if success:
                self.change_holding(Provence, Target, Type, Contested=1)
                message = 'Contested a {} Holding in {}'.format(Type, Provence)
        else:
            # make sure it's valid...
            temp = self.Holdings[self.Holdings['Regent'] != Regent].copy()
            temp = temp[temp['Type'] == 'Law']
            temp = temp[temp['Provence'] == Provence]
            temp = temp[temp['Contested']==0]
            law_level = np.sum(temp['Level'])
            loyalty = self.Provences[self.Provences['Provence']==Provence]['Loyalty'].values[0]
            
            if loyalty != 'High' and loyalty != 'Average' and law_level <= 0:
                # valid!
                self.change_provence(Provence, Contested=True)
                reward = 2*reward
                message = 'Contested {}'.format(Provence)
            else:
                success = False
                reward = -10
            if success == False:
                message = 'Failed to contested {}'.format(Provence)
            None
            
        return success, reward, message
          
    def domain_action_create_holding(self, Regent, Provence, Type, gbid=None):
        '''
        Base: 1 GB
        success: 10 (+ population) (Persuasion)
        
        INFO NEEDED:
        space for a holding nearby where I don't have a holding of that Type and it's a Type I can make
        
        Type: Action

        Base Cost: 1 GB

        Base Success: DC 10

        When a regent wishes to establish a foothold in a given province, they may create a holding of the 
        desired Type. If this holding is created in another regent’s province and the regent wishes to contest 
        your efforts, the level of the province increases the DC of your domain action check (thus, attempting 
        to create a holding in a level 6 province makes the DC 16). They may spend RP to further increase the 
         difficulty.

        Success on the domain action check creates a holding of the desired Type at level 0. You may Rule this
        holding on further domain actions to increase its level as normal.

        Create Province: If a regent wishes and the self Master approves, they may use this action to instead 
        create a new province in any unclaimed territory. The self Master determines the dimensions of this 
        new province and assigns it a Source rating based on the terrain Type that is present. If the new 
        province is not adjacent to any existing provinces, the cost to attempt the action is increased to 3 
        GB. This represents financing any exploratory expeditions or prospectors. If successful, a new 
        province is created at level 0 and may be Ruled as normal.

        Critical Success: The new holding or province is instead created at level 1.

        create_holding
        '''
        dc = 10
        # check if it's easy
        temp = self.Provences[self.Provences['Provence']==Provence].copy()
        temp = pd.merge(temp, self.Relationships[self.Relationships['Other']==Regent].copy(), on='Regent', how='left').fillna(0)
        temp = pd.merge(temp, self.Holdings[self.Holdings['Type']==Type].copy(), on='Provence', how='left')
        hostile = False
        if temp.shape[0] > 0:
            if temp.iloc[0]['Diplomacy'] <= 0:
                dc = dc + temp.iloc[0]['Population']
                if temp.iloc[0]['Diplomacy'] < -1:
                    hostile = True
            dc = self.set_difficulty(dc, Regent, temp.iloc[0]['Regent_x'], hostile=hostile)
        success, crit = self.make_roll(Regent, dc, 'Persuasion')
        
        message = 'Failed to start a {} Holding in {}'.format(Type, Provence)
        if (Type == 'Temple' and self.Regents[self.Regents['Regent']==Regent]['Divine'].values[0]==False) or (Type == 'Source' and self.Regents[self.Regents['Regent']==Regent]['Arcane'].values[0]==False):
            success=False
        if success == True and 1 <= self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]:
            message = 'Established a {} Holding in {}'.format(Type, Provence)
            level = 0
            if crit == True:
                level = 1
            # make the holding
            self.add_holding(Provence, Regent, Type, level)
            # Pay!
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - 1)
        else:
            success = False
        return success, 0, message
        
    def domain_action_declare_war(self, Regent, Target):
        '''
        WA- (headline continued on page 3)
        
        Type: Action
        Base Cost: None

        Base Success: Automatic

        A regent must use the Declare War action before moving troops through provinces that do not belong to 
        them, unless permission is obtained by use of the Diplomacy action. The regent can begin making war
        moves and conducting battles against enemy troops in provinces where they clash.

        If enemy troops are in your province, you do not need to Declare War; you may move your troops on the 
        respective phase of the season within your own territory. The target of a declaration of war must use 
        this action on their turn in order to counterattack into enemy territory; this is not merely the 
        public declaration, but also preparing the logistics of entering enemy territory.


        INFO NEEDED:
        at_war (someone declared war on me)
        
        
        declare_war
        '''
        self.add_relationship(Regent, Target, At_War = 1)
        return True, -2, '{} Declared War on {}!'.format(self.Regents[self.Regents['Regent']==Regent]['Full Name'], self.Regents[self.Regents['Regent']==Target]['Full Name'])
    
    def domain_action_diplomacy(self, Regent, Target, Type='form_alliance'):
        '''
        Type: Domain

        Base Cost: 1 RP, 1 GB

        Base Success: DC 10+ (or Automatic)

        Neighboring regents can generally be assumed to remain in correspondence with one another throughout the course of a season. The Diplomacy action has a much wider impact, and is typically a court affair with dignitaries, soirees, and document signings. Typically, this action is taken in relation to NPC regents or random events; if a player character regent is the target of the Diplomacy action, they can determine whether it is automatically successful (but the expense of GB and action must be made in order to gain the effects).

        The DC of the domain action check depends on the specific action being taken. Diplomacy checks are typically simple affairs, but care must be taken with the proposals and the mood and standing of a regent. If a deal is outright insulting, the self Master can rule the action has no chance of success.

        Furthermore, the condition of the regent’s court may cause this check to be made at advantage or disadvantage, or not at all. See the section on Court Expenses for more details.

        Regents on the sidelines who wish to influence the proceedings one way or another may spend GB and RP as usual, affecting the DC and roll bonus accordingly. This represents their dignitaries at the diplomatic function, currying favor and giving advice.

        A Diplomacy action can encompass one of the following effects, each of which has its own DC.

        DC 10: Form an alliance with another domain with whom you are already friendly.
        DC 10: Create a trade agreement between two domains. This allows the Trade Route action to be taken.
        DC 15: Allow troops to move through the targeted domain without the need to Declare War.
        DC 15: Force a targeted regent to provide tribute or concessions.
        DC 15: Respond to a domain event such as brigandage, unrest, or feuds, causing its effects to subside.
        As it pertains to forcing tribute, a regent typically offers no more than a quarter of what they collect each turn in Gold bars; unless threatened with overwhelming force, a regent will never capitulate to more than that.

        Critical Success: The RP and GB costs for this action are immediately recouped.
        
        
        INFO NEEDED
        arranged_trade_route
        
        
        diplomacy_form_alliance
        diplomacy_trade_agreement
        diplomacy_allow_troop_movement
        diplomacy_force_tribute
        
        diplomacy_respond_to_brigandage
        diplomacy_respond_to_unrest
        '''
        dc = 10
        reward = 0
        reg_name = self.Regents[self.Regents['Regent']==Regent]['Full Name']
        tar_name = self.Regents[self.Regents['Regent']==Target]['Full Name']
        hostile = False
        change_dc = True
        # get diplomacy levels
        Diplomacy = [0,0]
        temp = self.Relationships[self.Relationships['Regent']==Regent]
        temp = temp[temp['Other']==Target]
        try:
            Diplomacy[0] = temp.iloc[0]['Diplomacy']
        except:
            Diplomacy[0] = 0
        temp = self.Relationships[self.Relationships['Regent']==Target]
        temp = temp[temp['Other']==Regent]
        try:
            Diplomacy[1] = temp.iloc[0]['Diplomacy']
        except:
            Diplomacy[1] = 0
        # set things...
        if Type == 'form_alliance':
            message_s = '{} formed an alliance with {}'.format(reg_name, tar_name)
            message_f = '{} failed to form an alliance with {}'.format(reg_name, tar_name)
        if Type == 'trade_agreement':
            message_s = '{} formed a trade agreement with {}'.format(reg_name, tar_name)
            message_f = '{} failed to form a trade agreement with {}'.format(reg_name, tar_name)
        if Type == 'troop_permission':
            dc = 15
            hostile = True
            message_s = '{} will allows troops from {} to travel in their domain'.format(tar_name, reg_name)
            message_f = "{} failed to get permission to move troops through {}'s domain".format(reg_name, tar_name)
        if Type == 'force_tribute':
            dc = 15
            hostile = True
            message_s = '{} has demanded tribute from {}, and they agreed to pay it.'.format(reg_name, tar_name)
            message_f = "{} failed to demanded tribute from {}".format(reg_name, tar_name)
        if Type == 'deal_with_brigands':
            dc = 15
            change_dc=False
            message_s = '{} has negotiated with Brigands.'.format(reg_name)
            message_f = "{} failed tonegotiate with Brigands".format(reg_name)
        if Type == 'handle_unrest':
            dc = 15
            change_dc=False
            message_s = '{} has negotiated with the {}.'.format(reg_name, tar_name)
            message_f = "{} failed tonegotiate with the {}".format(reg_name, tar_name)
            
        # make check
        if change_dc == True:
            dc = self.set_difficulty(dc, Regent, Target, hostile=hostile)
        success, crit = self.make_roll(Regent, dc, 'Persuasion')
        message = message_f
        
        if crit == False:  # recoup costs on a crit
            self.change_regent(Regent, Regency_Points = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]-1)
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]-1)
        if success == True:  # yay!
            message = message_s
            if Type == 'form_alliance':  # Alliance Worked.       
                self.add_relationship(Regent, Target, Diplomacy=2)
                self.add_relationship(Target, Regent, Diplomacy=2)
            if Type == 'trade_agreement':  # Trade Agrrement!
                self.add_relationship(Regent, Target, Diplomacy=1, Trade_Permission=1)
                self.add_relationship(Target, Regent, Diplomacy=1, Trade_Permission=1)
                reward = 5
            if Type == 'troop_permission':  # troop_permission.
                self.add_relationship(Regent, Target, Vassalage=1)
                self.Projects.append(pd.DataFrame([[Regent, 'Troop Permissions', Target, 0]], columns=self.Projects.keys()), ignore_index=True)
            if Type == 'force_tribute':  # force_tribute
                check = self.Relationships[self.Relationships['Regent'] == Regent]
                check = check[check['Other']==Target]
                if 0-Diplomacy[0]>=1:
                    payment = 0-Diplomacy[0] - check['Payment'].values[0]
                else:
                    payment = 1
                self.add_relationship(Target, Regent, Payment=payment, Diplomacy=-1)
                if check.shape[0]>0:
                    if check['At War'].values[0] >= 1:
                        self.add_relationship(Regent, Target, At_War = -1*check['At War'].values[0])  # end hostilities, for now
                    if check['Payment'].values[0] >= 1:
                        self.add_relationship(Regent, Target, Payment = -1*check['Payment'].values[0])  # end payments in other direction
                    reward = reward - check['Diplomacy'].values[0]
            if Type == 'deal_with_brigands':
                temp = self.Provences[self.Provences['Regent']==Regent]
                temp = temp[temp['Brigands']==True]
                if temp.shape[0]==0:
                    success = False
                    message = "{} tried to deal with Brigands that didn't exist.".format(reg_name)
                else:
                    self.change_provence(temp.iloc[0]['Provence'], Brigands=False)
            if Type == 'handle_unrest':
                # undo the unrest...
                provences = self.Provence[self.Provence['Regent'] == Target]['Provence']
                # return the provences
                for p in list(provences):
                    self.change_provence(p, Loyalty='Poor')
                # disband any and all troops
                troops = self.Troops[self.Troops['Regent']==Target]
                for i, row in troops.iterrows():
                    self.disband_troops(Target, row['Provence'], row['Type'], Killed=False)
                self.kill_regent(Target)
                self.Regents = self.Regents[self.Regents != Target]
                reward = 5
        return success, reward, message

    def domain_action_forge_ley_line(self, Regent, Provence, Target):
        '''
        Forge Ley Line
        Type: Action

        Base Cost: 1 RP, 1 GB (see below)

        Base Success: DC 5

        When casting realm magic, arcane spellcasters require the use of a 
        Source. However, they may find themselves in provinces where the Source 
        is weak, and thus at a disadvantage when choosing from among their 
        arsenal. By creating ley lines, the spellcaster can substitute the 
        Source rating of one province with that of another.

        Ley lines are a potentially hefty expenditure, requiring 1 Regency
        Point and 1 Gold Bar for each province between the “home” Source and 
        the destination of the ley line. Always use the shortest distance to 
        determine the number of provinces crossed, geographical features 
        notwithstanding.

        Spellcasters can also expand on ley lines by creating “networks” 
        stemming from the home Source province. Consider existing ley lines 
        when calculating the cost of new ones; the spellcaster need only pay 
        for extension of a ley line rather than recalculating from the home 
        Source, if it is cost-effective.

        Any contiguous ley line the spellcasting regent owns costs 1 Regency 
        Point during the final step of the season. Multiple ley lines that are 
        not connected each cost RP.

        Should the source from which a ley line originates fall to level 0 for 
        any reason, such ley lines immediately disappear and must be reforged.
        

        For example, a spellcasting regent, Calimor the Magnificent, wishes to
        create a ley line connecting his Source holdings in the province of 
        Sorelies (Source rating 4) to a weaker location in Alaroine (Source 
        rating 0) so that he can cast useful realm magic while stationed in 
        there. The distance between provinces is only two along the shortest
        route (south through Hildon, and then to Alaroine), so the cost to 
        build the ley line is 2 RP and 2 GB.

        Calimor later decides to extend the ley line into enemy territory in 
        the province of Ghiere, in Baron Gavin Tael’s domain of Ghoere. He pays 
        only an additional 2 RP and 2 GB to push the ley line two more 
        provinces south, but must still succeed at his domain action check to 
        complete the forging. Now with a strong home Source at his command, 
        Calimor can lead soldiers there and cast devastating realm magic 
        against the warmongering Baron on his own turf.
        
        INFO NEEDED
        lay_lines_from_highest_source
        number_of_ley_networks
        
        
        forge_ley_line
        '''
        # make a network for the calculation
        G = nx.Graph()
        G.add_nodes_from(list(self.Provences['Provence']))
        Gl = G.copy()

        G.add_edges_from([(row['Provence'], row['Neighbor']) for i, row in self.Geography.iterrows()])
        Gl.add_edges_from([(row['Provence'], row['Other']) for i, row in self.LeyLines[self.LeyLines['Regent']==Regent].iterrows()])

        provences = [Provence] + [a[1] for a in Gl.edges(Provence)]
        targets = [Target] + [a[1] for a in Gl.edges(Target)]

        shortest = 9000
        pair = (Provence, Target)
        for p in provences:
            for t in targets:
                a = nx.shortest_path_length(G, p, t, 'Border')
                if a < shortest:
                    shortest = a
                    pair = (p,t)
        cost = shortest
        dc = 5*shortest
        temp = self.Regents[self.regents['Regent']==Regent]
        message = '{} failed to make a ley line from {} to {}'.format(temp.iloc[0]['Full Name'], Provence, Target)
        if temp.iloc[0]['Gold Bars'] < cost or temp.iloc[0]['Regency Points'] < cost:
            success = False
        else:
            self.change_regent(Regent, Regency_Points = temp.iloc[0]['Regency Points'] - cost, Gold_Bars = temp.iloc[0]['Gold Bars'] - cost)
            temp_ = self.Holdings[self.Holdings['Type']=='Source'].copy()
            temp_ = pd.concat([temp_[temp_['Provence']==pair[0]], temp_[temp_['Provence']==pair[1]]], sort=False)
            temp_ = pd.merge(temp_, self.Relationships[self.Relationships['Other']==Regent], on='Regent', how='left').fillna(0)
            temp_ = temp_.sort_values('Diplomacy')
            enemy = temp_.iloc[0]['Regent']
            if enemy != Regent:
                dc = self.set_difficulty(dc, Regent, enemy)
            success, crit = self.make_roll(Regent, dc, 'Regency Bonus')  # classic for reasons  
        if success == True:
            message = '{} forged ley lines from {} to {}'.format(temp.iloc[0]['Full Name'], Provence, Target)
            lst = nx.shortest_path(G, pair[0], pair[1], 'Border')
            for a in range(len(lst)-1):  # make all the paths
                self.LeyLines = self.LeyLines.append(pd.DataFrame([[Regent, lst[a], lst[a+1]]], columns=self.LeyLines.keys()), ignore_index=True)
                self.LeyLines = self.LeyLines.append(pd.DataFrame([[Regent, lst[a+1], lst[a]]], columns=self.LeyLines.keys()), ignore_index=True)
        return success, cost, message
        
    def domain_action_fortify(self, Regent, Provence, level, name=None):
        '''
        Type: Action

        Base Cost: 1 RP, Variable GB

        Base Success: DC 5

        Through use of the Fortify action, regents construct Castle assets to
        protect their provinces (or expand upon existing Castles). A province 
        can only hold a single Castle asset for purposes of this action, though
        you may well have numerous smaller keeps and palaces in the area that 
        do not necessarily contribute to defense in any meaningful way. You can 
        only construct Castles in provinces you own, and Castles require a 
        massive investment of gold to bring to completion.

        To create a new Castle, a regent chooses the target province to begin 
        construction. Castles, like provinces and holdings, have levels which 
        dictate how impregnable they are and how well they defend holdings in 
        their sphere of influence. Castles are unique in that they may be of 
        higher level than the province in which they lie, but if the Castle’s 
        target level exceeds the province level, costs quickly begin to multiply.
        
        The base cost of a Castle is 6 GB per level. If the Castle is greater 
        level than the province, each level beyond the province level costs 9 
        GB. For example, if Erin Velescarpe wants to build a level 6 Castle in 
        a level 4 province on the border with Ghoere to deter any of the 
        neighboring Baron’s aggression, she must pay 42 Gold Bars.

        Castles are expensive, and can take years to build to completion. Once 
        the desired level of the Castle is chosen and the initial cost is paid, 
        progress continues automatically at a rate of 3 (or 1d6) GB each season 
        and the regent does not need to continue to use this action unless they 
        are adding features or upgrading the Castle level.

        A standard Castle has the benefit of completely halting the advance of 
        enemy troops through your provinces. Any enemy units that move into a 
        province occupied by a Castle cannot move out of the province any 
        direction save the way they came, until the Castle is neutralized or 
        destroyed (see Conquest and Occupation section). Furthermore, holdings 
        you own in provinces with a Castle are protected from total destruction 
        using Pillage, as outlined in that action.

        You may also garrison a number of units in the Castle equal to its 
        level. Garrisoned units cost half of their maintenance each season, but 
        are slow to bring back to muster in an emergency.
        
        INFO NEEDED
        capital_has_castle
        highpop_has_castle
        lowpop_has_castle
        troops_garrisoned_capital
        troops_garrisoned_high
        troops_garrisoned_low
        '''
        # gather info
        temp = self.Regents[self.Regents['Regent']==Regent].copy()
        # name the castle
        t1 = pd.read_csv('csv/castle_pre.csv')
        t2 = pd.read_csv('csv/castle_post.csv')
        temp['N'] = np.random.randint(0,t1.shape[0]-1,temp.shape[0])
        temp['X'] = np.random.randint(0,t2.shape[0]-1,temp.shape[0])
        temp = pd.merge(temp, t1, on='N', how='left')
        temp = pd.merge(temp, t2, on='X', how='left')
        temp['New Castle Name'] = temp['Name']+temp['End']
        temp['New Castle Name'] = temp['New Castle Name'].str.replace('_', ' ')
        temp['New Castle Name'] = temp['New Castle Name'].str.title()
        temp['New Castle Name'] = temp['New Castle Name'].str.replace("'S","'s")
        temp = pd.merge(temp, self.Provences[self.Provences['Provence'] == Provence].copy(), on='Regent', how='left').fillna(-1)
        message = 'Failed to Build a Castle'
        if temp.shape[0] > 0:
            self.change_regent(Regent, Regency_Points= temp.iloc[0]['Regency Points']-1)
        success = False
        reward = 0
        if temp.shape[0]>0:
            if temp.iloc[0]['Population']>=0:  # valid action
                success, crit = self.make_roll(Regent, 5, 'Persuasion')
                if success == True:
                    if temp.iloc[0]['Castle Name'] == '':
                        if name == None:
                            temp['Castle Name'] = temp['New Castle Name']
                        else:
                            temp['Castle Name'] = name
                    # already started?
                    previous = temp.iloc[0]['Castle']  # old value
                    # current construction projects
                    for a in self.Projects[self.Projects['Regent'] == Regent].values:
                        if a[2][0] == Provence:
                            previous = previous + a[2][1]
                    end_level = level + previous
                    cost = level*6
                    if end_level > temp.iloc[0]['Population']:
                        additional = (end_level - temp.iloc[0]['Population'])
                        if additional > level:
                            additional = level
                        cost = cost + 3*additional
                    if cost <= temp.iloc[0]['Gold Bars']:
                        # make the castle
                        success = True
                        reward = 5+level
                        message = '{} started construction on {}, a level {} castle in {}'.format(temp.iloc[0]['Full Name'],temp.iloc[0]['Castle Name'], level, Provence)
                        # charge 'em
                        self.change_regent(Regent, Gold_Bars = temp.iloc[0]['Gold Bars'] - cost)
                        if crit == True:  # 2d6 off of the cost as per the rules
                            cost = cost - np.random.randint(1,6,1)[0] - np.random.randint(1,6,1)[0]
                        self.Projects = self.Projects.append(pd.DataFrame([[Regent, 'Castle', (Provence, level), cost]], columns=self.Projects.keys()), ignore_index=True)
                        self.change_provence(Provence, Castle_Name = temp.iloc[0]['Castle Name'])
        return success, reward, message
       
    def domain_action_investiture(self, Regent, Target, Invest=False, Divest=False, Vassal=False, Claim=False):
        '''
        Type: Action
        Base Cost: Varies
        Base Success: Varies

        To enact Investiture, a priest capable of casting the realm spell of 
        the same name must be present for the ceremony. This ceremony is 
        critical for passing rightful ownership of holdings and provinces to 
        new rulers, and without it, a regent cannot draw Regency Points or Gold 
        Bars from either asset Type.

        To invest provinces and holdings, the asset in question must either be 
        willingly given to the investing regent; otherwise, it must be 
        conquered or contested by that regent, and there must not be an enemy 
        Castle present that is not neutralized. The regent must pay Regency 
        Points equal to the combined levels of all holdings, provinces, and 
        castles being invested through the course of this domain action. If the 
        former owner is an unwilling participant, the investing regent must 
        succeed at a domain action check with a DC of 10 + the defending 
        regent’s Bloodline modifier. The defending regent may also spend RP 
        normally to make this more of a challenge for the would-be usurper. 
        This process is known as divesting a regent.

        Investiture is also used to formalize vassalage. Upon using Investiture
        for this purpose, both regents contribute RP equal to the vassal’s 
        Bloodline modifier. From this point on, the vassal contributes that 
        value to their new lord every season, and no longer gains RP from their 
        Bloodline modifier.

        Finally, a blooded individual may be the target of Investiture, either 
        willingly or unwillingly (though they must be present). This strips the
        blooded individual of all derivation, Bloodline ability score, and 
        blood abilities. If the recipient is not a blooded individual, they 
        gain a Bloodline score of 11 and the derivation of the divested scion,
        unless that scion’s Bloodline score was less than 11 (in which case,
        the new value is equal to the scion’s previous value; for this reason,
        Tainted bloodlines are almost never invested in this way). If the 
        recipient of the investiture is already blooded, their Bloodline score
        permanently increases by 1, to a maximum value of 20.
        
        INFO NEEDED
        at_war
        contested_all_enemy_provinces
        neutralized_all_enemy_castles
        friend_has_more_regency
        friend_has_more_gold
        diplomacy_friend_5_higher
        
        investiture_invest_friend
        investiture_divest_enemy
        investiture_become_vassal_friend
        investiture_take_bloodline_enemy
        investiture_take_provence
        '''
        
        if Invest == True:
            # cost
            Provences = self.Provences[self.Provences['Regent']==Regent].copy()
            Holdings = self.Holdings[self.Holdings['Regent']==Regent].copy()
            cost = 0
            if Provences.shape[0] > 0:
                cost = cost + np.sum(Provences['Population']) + np.sum(Provences['Castle'])
            if Holdings.shape[0] > 0:
                cost = cost + np.sum(Holdings['Level'])
            # check if they have the points...
            if self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0] >= cost:
                self.Provences['Regent'] = self.Provences['Regent'].str.replace(Regent, Target)
                # careful with holdings..
                for i, a in enumerate(['Law', 'Guild', 'Temple', 'Source']):
                    Holdings1 = self.Holdings[self.Holdings['Type'] != a]
                    Holdings2 = self.Holdings[self.Holdings['Type'] == a]
                    if i <=1 or (i==2 and self.Regents[self.Regents['Regent']==Target]['Divine'].values[0]==True) or (i==3 and self.Regents[self.Regents['Regent']==Target]['Arcane'].values[0]==True):
                       Holdings2['Regent'] = Holdings2['Regent'].str.replace(Regent, Target)
                    self.Holdings = pd.concat([Holdings1[['Provence', 'Regent', 'Type', 'Level', 'Contested']], Holdings2[['Provence', 'Regent', 'Type', 'Level', 'Contested']]], sort=False)
                self.Troops['Regent'] = self.Troops['Regent'].str.replace(Regent, Target)
                self.Projects['Regent'] = self.Projects['Regent'].str.replace(Regent, Target)
                self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0]
                self.change_regent(Regent, Regency_Points= self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]-cost)
                return True, 0, '{} invested {} with all their Regency'.format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
                
            else:
                return False, 0, '{} failed to invest {} with all their Regency'.format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
        elif Divest == True:
            # only contested holdings & provences
            Provences = self.Provences[self.Provences['Regent'] == Target].copy()
            # with no un-neutralized castles
            temp_ = self.Provences[self.Provences['Castle']>0][['Provence', 'Castle']]
            allies, _ = self.allies_enemies(Regent)
            allies.append(pd.DataFrame([[Regent]], columns=['Regent']), ignore_index=True)
            temp = pd.merge(allies, self.Troops, on='Regent', how='left').fillna(0)
            temp = temp[temp['CR']>0]
            temp = temp[['Provence', 'Type']].groupby('Provence').count().reset_index()
            temp = pd.merge(temp_, temp, on='Provence', how='left').fillna(0)
            temp = temp[temp['Type']<temp['Castle']]  # otherwise neutralized
            temp['Castled Up'] = 1
            Provences = pd.merge(Provences, temp[['Provence', 'Castled Up']], on='Provence', how='left').fillna(0)
            Provences = Provences[Provences['Contested']==True]
            Provences = Provences[Provences['Castled Up']==0]
            
            # Holdings
            Holdings = self.Holdings[self.Holdings['Regent'] == Target]
            Holdings = Holdings[Holdings['Contested']==1]
            
            
            # get the cost
            cost = np.sum(Provences['Population']) + np.sum(Provences['Castle']) + np.sum(Holdings['Level'])
            success = False
            message = '{} Failed to divest {} of their contested assets'.format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
            if self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0] >= cost and Provences.shape[0] + Holdings.shape[0] > 0:
                dc = 10 + self.Regents[self.Regents['Regent']==Target]['Regency Bonus'].values[0]
                dc = self.set_difficulty(dc, Regent, Target, hostile=True)
                self.change_regent(Regent, Regency_Points= self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]-cost)
                success, crit = self.make_roll(Regent, dc, 'Regency Bonus')
                if success == True:
                    message = '{} divested {} of '.format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
                    for Provence in Provences['Provence']:
                        self.change_provence(Provence, Regent=Regent)
                        message = message + ' the provence of {}'.format(Provence)
                    for i, row in Holdings.iterrows():
                        self.change_holding(row['Provence'], Target, row['Type'], new_Regent=Regent)
                        message = message + ' a {} holding in {}'.format(row['Type'], row['Provence'])
            return success, cost*success, message
        elif Vassal == True:
            temp = self.Relationships[self.Relationships['Regent']==Regent].copy()
            temp = temp[temp['Other'] == Target]
            vas = 0
            if temp.shape[0] > 0:
                vas = vas - np.sum(temp['Vassalage'])
            self.add_relationship(Regent, Target, Vassalage=self.Regents[self.Regents['Regent']==Regent]['Regency Bonus'].values[0]+vas)
            # clear any alliance vassalage debris
            temp = self.Relationships[self.Relationships['Regent']==Target].copy()
            temp = temp[temp['Other'] == Regent]
            vas = 0
            if temp.shape[0] > 0:
                vas = vas - np.sum(temp['Vassalage'])
            self.add_relationship(Target, Regent, Vassalage=vas)
            return True, 0, "{} became {}'s Vassal".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
        elif Claim == True:
            dc = 10
            message = 'Failed to claim {}'.format(Target)
            success, crit = make_roll(Regent, dc, 'Regency Bonus')
            if self.Provences[self.Provences['Provence']==Target].shape[0] == 0 and self.Provences[self.Provences['Provence']==Target]['Regent'].values[0]!='':
                success = False
            else:
                 self.change_regent(Regent, Regency_Points= self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]-self.Provences[self.Provences['Provence']==Target]['Population'])
            if success == True:
                self.change_provence(Target, Regent=Regent)
                message = 'Claimed {}'.format(target)
            return success, self.Provences[self.Provences['Provence']==Target]['Population'], message
        return False, 0, 'Error'   
        
    def domain_action_rule(self, Regent, Holdings=True, Provence=''):
        '''
        Rule
        Type: Action
        Base Cost: RP -> new value, GB - 1 per
        Base Success: DC 10 (Cha)

        Regents who devote time to ruling their domain may increase the levels 
        of provinces and holdings. They are actively managing the minutiae of 
        their realm with the express purpose of expanding it and drawing a 
        larger population under their banner.

        Firstly, a regent may use this action to increase the level of any 
        single holding or collection of holdings. They must pay RP equal to the 
        new level of all holdings affected, as well as 1 GB for each affected 
        holding. Only one domain action check needs to be made to increase the 
        level of all holdings. Remember that the total level of all holdings of 
        a given Type cannot exceed the level of the province in which they are 
        located.

        For example, Ashira al-Sumari wishes to grow her holdings. She has a Law 
        (3) holding, a Guild (4) holding, and a Source (2) holding that she 
        wishes to improve. Ashira must spend 3 GB and 11 RP (4 + 5 + 3) and then 
        make her domain action check.

        Secondly, a regent may elect to rule a province; only one province can 
        be ruled at a time by this action. The cost to rule a province is equal
        to RP and GB equal to the new level of the affected province, and the 
        regent must succeed at a DC 10 domain action check.

        For example, Calimor the Magnificent wishes to increase the level of a 
        province, currently rated at level 3. He must pay 4 RP and 4 GB and 
        succeed at his domain action check.

        One important exception exists: elven regents ruling elven domains pay 
        double the normal amount to rule provinces and increase their levels. It
        is more difficult to steer the free-spirited elves into one place to 
        settle, and the extreme care they take in developing their societies 
        also means that they do not reduce a province’s source rating when its
        province level increases.

        Critical Success: The efforts of the regent are incredibly effective, and 
        the domain or holding increases its level by two. If this is not possible, 
        say because a holding would level past its province, the cost is instead 
        refunded.
        
        INFO NEEDED
        Holdings_Can_Increase_Level
        Has_Provences
        
        rule_holdings
        rule_provence
        '''
        rrow = self.Regents[self.Regents['Regent']==Regent].iloc[0]
        GB = rrow['Gold Bars']
        RP = rrow['Regency Points']
        if GB < 0:
            GB = 0
        if RP < 0:
            RP = 0
        reward = 0
        if Holdings==True and rrow['Player']==False:  # give players a choice later
            temp = self.Holdings[['Provence', 'Type', 'Level']].copy().groupby(['Provence', 'Type']).sum().reset_index()
            temp = pd.merge(self.Provences[['Provence', 'Population', 'Magic']], temp, on='Provence', how='left').fillna(0)
            temp_ = temp[temp['Type'] != 'Source']
            temp__ = temp[temp['Type']=='Source']
            temp__['Population'] = temp__['Magic']
            temp = pd.concat([temp_, temp__])
            temp = temp[['Provence', 'Type', 'Level', 'Population']]
            temp = pd.merge(self.Holdings[self.Holdings['Regent']==Regent], temp, on=['Provence','Type']).fillna(-1)
            temp = temp[temp['Contested'] == 0]
            temp = temp[temp['Level_y']<temp['Population']]
            # calculate the cost
            temp['Cost'] = temp['Level_x']+1
            RCost = np.sum(temp['Cost'])
            GCost = temp.shape[0]
            # do as many as the regent can
            while RCost > RP or GCost > GB:
                temp['rand'] = np.random.randint(1,100)
                temp = temp.iloc[:-1]
                RCost = np.sum(temp['Cost'])
                GCost = temp.shape[0]
            # spend it
            self.change_regent(Regent, Gold_Bars = GB - GCost, Regency_Points = RP - RCost)
            success = False
            message = '{} ruled their Holdings'.format(rrow['Full Name'])
            if temp.shape[0]>0:
                success, crit = self.make_roll(Regent, 10, 'Persuasion')
                if crit == True:
                    temp['Cost'] = temp['Cost'] + 1
                    temp_ = temp[temp['Cost']>temp['Population']]
                    temp_['Cost'] = temp_['Population']
                    temp = pd.concat([temp[temp['Cost']<=temp['Population']]
                                      , temp_], sort=False)
                temp['Increase'] = temp['Cost'] - temp['Level_x']
                for i, row in temp.iterrows():
                    self.change_holding(row['Provence'], Regent, row['Type'], Level= row['Increase'])
            reward = np.sum(temp['Cost'])
        elif Provence !='':
            message = '{} ruled over {}'.format(rrow['Full Name'], Provence)
            value = self.Provences[self.Provences['Provence']==Provence]['Population'].values[0]
            if rrow['Race'].lower() == 'elf':
                value = 2*value+1
            if GB < value+1 or RP < value+1:
                success = False
                crit = False
            else:
                self.change_regent(Regent, Gold_Bars = GB - value - 1, Regency_Points = RP - value - 1)
                success, crit = self.make_roll(Regent, 10, 'Persuasion')
                if success == True and crit == True:
                    self.change_provence(Provence, Population_Change=2)
                    reward = 5*(value+2)
                elif success == True:
                    self.change_provence(Provence, Population_Change=1)
                    reward = 5*(value+1)
        return success, reward, message
        
    def domain_action_trade_routes(self, Regent, Base, Target):
        '''
        Type: Action
        Base Cost: 1 RP, 1 GB
        Base Success: DC 10

        Creating trade routes is a surefire way to greatly increase seasonal
        income for a regent. In order to create a trade route, the regent must 
        own a guild holding in the home province and have permission from the 
        owner of the target province, (either through Diplomacy or if the target
        province is owned by a friendly player regent), who must also possess a 
        guild holding there. Further, the two provinces must be connected either
        by sea or by provinces with an appropriate network of roads, which are 
        constructed via the Build action.

        Each season, both regents draw Gold Bars equal to the average of the 
        levels of the two connected provinces. Trade routes cease to generate 
        income if the provinces or guild holdings at either end of the trade
        route become contested or occupied.

        Creation of a trade route can be challenged by regents who own law 
        holdings in either end of the route. They may contribute RP to increase 
        the DC of the domain action check accordingly. Both the regent making 
        the check and the regent at the other end of the connection can 
        contribute GB to add a bonus to the roll as usual.

        This action can create multiple trade routes at once, so long as they 
        all originate from the same province. The regent must pay each cost 
        separately, but only one domain action check need be made. Provinces up 
        to level 3 can only be the source of one trade route, provinces between 
        4 and 6 can be the source of two, and provinces of level 7 or higher can 
        support three.
        
        INFO_NEEDED
        trade_permission_granted
        waterways_can_have_routes
        provences_can_have_routes
        
        
        create_trade_route
        '''
        # do we have permission?
        Other = self.Provences[self.Provences['Provence']==Target]['Regent'].values[0]
        A = self.Relationships[self.Relationships['Regent']==Regent].copy()
        A = A[A['Other']==Other]
        B = self.Relationships[self.Relationships['Regent']==Other].copy()
        B = B[B['Other']==Regent]
        rrow = self.Regents[self.Regents['Regent']==Regent].iloc[0]
        temp = pd.concat([A, B])
        success = False
        reward = 0
        message = 'Failed to establish trade between {} and {}.'.format(Base, Target)
        if np.sum(temp['Trade Permission']) > 0 and rrow['Gold Bars'] >= 1 and rrow['Regency Points'] >= 1:
            # waterways?
            Waterway = False
            if self.Provences[self.Provences['Provence']==Base]['Waterway'] == True and elf.Provences[self.Provences['Provence']==Target]['Waterway'] == True:
                Waterway = True
            self.change_regent(Regent, Gold_Bars = rrow['Gold Bars'] - 1, Regency_Points =  rrow['Regency Points'] - 1)
            success, crit = self.make_roll(Regent, 10, 'Persuasion')
            if success == True:
                if Waterway == True:
                    self.add_geo(Base, Target, Shipping=1)
                    message = 'Shipping established between {} and {}.'.format(Base, Target)
                    reward = 15
                else:
                    self.add_geo(Base, Target, Caravan=1)
                    message = 'Caravan established between {} and {}.'.format(Base, Target)
                    reward = 10
        return success, reward, message
    
    def relam_magic_alchemy(self, Regent, Target, Amount):
        '''
        RP Cost: 4+
        GB Cost: 0
        Required Source: 3
        Duration: Permanent

        This realm spell allows the invoker to create wealth from inert
        materials. By expending 4 RP, the caster creates 1 GB of wealth 
        added immediately to the treasury of either the caster themselves 
        or the regent they serve. This spell can only be invoked once per 
        season, as the strain on the caster is great, but there is no 
        upper limit to the value of gold that can be transmuted in a 
        single casting of this spell so long as sufficient RP is 
        available.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Source'][['Type', 'Level']].groupby('Type').max().reset_index()
        success = False
        reward = 0
        message = 'Lacks the resources to cast Alchemy'
        temp = temp[temp['Level']>=3]
        if temp.shape[0] > 0:
            RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
            if RP >= 4*Amount:
                success = True
                message = "{} cast 'Alchemy', generating {} Gold Bars for {}".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], Amount, self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
                reward = Amount
                self.change_regent(Regent, Regency_Points = RP - 4*Amount)
                self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] + Amount)
        return success, reward, message
        
    def realm_magic_bless_land(self, Regent, Targets):
        '''
        RP Cost: 3 per province
        GB Cost: 1
        Required Temple: 1
        Duration: One season

        With a holy ceremony, the adherent invokes the blessing of 
        their deity upon a province. Each non-Source holding within 
        the province, and the province itself, immediately generate 
        an additional gold bar of revenue for their controlling 
        regents. The province also improves its loyalty by one grade.

        The regent may affect only one province with this spell at 
        first. At 5th level, they may affect two provinces. At 11, 
        they may affect up to three provinces. At 17th, they may 
        affect up to four provinces.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Temple'][['Type', 'Level']].groupby('Type').max().reset_index()
        success = False
        reward = 0
        message = 'Lacks the resources to cast Bless Land'
        temp = temp[temp['Level'] >= 1]
        if temp.shape[0] > 0:
            message = "{} cast 'Bless Land' on ".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0])
            # get limiting factors
            Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
            RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
            Limits = [1,5,11,17]

            # cast away!
            lst = []
            for i, Provence in enumerate(Targets):
                if i <= 3:
                    if Level >= Limits[i] and RP >= 3:
                        success = True
                        reward = reward + 3
                        lst.append(Provence)
                        RP = RP - 3
                        # The province also improves its loyalty by one grade.
                        self.change_loyalty(Provence, 1)
                        # gold increase for Provence itself.
                        Reg = self.Provences[self.Provences['Provence']==Provence]['Regent'].values[0]
                        self.change_regent(Reg, Gold_Bars = self.Regents[self.Regents['Regent']==Reg]['Gold Bars'].values[0] + 1 )
                        temp = self.Holdings[self.Holdings['Provence']==Provence]
                        for Reg in list(temp[temp['Type'] != 'Source']['Regent']):
                            if  self.Regents[self.Regents['Regent']==Reg].shape[0] > 0:
                                self.change_regent(Reg, Gold_Bars = self.Regents[self.Regents['Regent']==Reg]['Gold Bars'].values[0] + 1 )
            message = message + ', '.join(lst) + '.'
        return success, reward, message
        
    def realm_magic_blight(self, Regent, Targets):
        '''
        RP Cost: 3 per province
        GB Cost: 2
        Required Temple: 3
        Duration: One season

        Whereas the bless land realm spell brings fortune, the blight realm
        spell brings devastation. The targeted province suffers an intense 
        and immediate misfortune, causing all regents who control a holding 
        within the province to immediately lose 1 GB. The owner of the 
        province itself loses an additional gold bar, and the regent must 
        succeed on a Bloodline saving throw or the province’s loyalty is 
        reduced by one grade.

        The regent may affect only one province with this spell at first. At 
        5th level, they may affect two provinces. At 11, they may affect up 
        to three provinces. At 17th, they may affect up to four provinces.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Temple'][['Type', 'Level']].groupby('Type').max().reset_index()
        success = False
        reward = 0
        message = 'Lacks the resources to cast Blight'
        temp = temp[temp['Level'] >= 3]
        if temp.shape[0] > 0:
            message = "{} cast 'Blight' on ".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0])
            # get limiting factors
            Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
            RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
            Limits = [1,5,11,17]

            # cast away!
            lst = []
            for i, Provence in enumerate(Targets):
                if i <= 3:
                    if Level >= Limits[i] and RP >= 3:
                        success = True
                        reward = reward + 3
                        lst.append(Provence)
                        RP = RP - 3
                        
                        # gold increase for Provence itself.
                        Reg = self.Provences[self.Provences['Provence']==Provence]['Regent'].values[0]
                        # The province may also lose a grade of loyalty
                        save, _ = self.make_roll(Reg, 10+self.Regents[self.Regents['Regent']==Regent]['Regency Bonus'].values[0], 'Regency Bonus')
                        if save == False:
                            self.change_loyalty(Provence, -1)
                        if self.Regents[self.Regents['Regent']==Reg]['Gold Bars'].values[0] >= 1:
                            self.change_regent(Reg, Gold_Bars = self.Regents[self.Regents['Regent']==Reg]['Gold Bars'].values[0] - 1 )
                        temp = self.Holdings[self.Holdings['Provence']==Provence]
                        for Reg in list(temp[temp['Type'] != 'Source']['Regent']):
                            if  self.Regents[self.Regents['Regent']==Reg].shape[0] > 0:
                                if self.Regents[self.Regents['Regent']==Reg]['Gold Bars'].values[0] > 0:
                                    self.change_regent(Reg, Gold_Bars = self.Regents[self.Regents['Regent']==Reg]['Gold Bars'].values[0] - 1 )
            message = message + ', '.join(lst) + '.'
        return success, reward, message
      
    def realm_magic_death_plague(self, Regent, Target):
        '''
        RP Cost: 1 per target province level
        GB Cost: 2
        Required Source: 5

        Duration: Permanent

        By invoking this terrible realm spell, the caster creates a plague to 
        befall a target province. The sickness spreads quickly and terribly 
        throughout the month of its invocation, reducing the target province’s 
        level by 1.

        As the caster grows in power, so does the potential destruction of this 
        spell. Upon reaching 5th level, the caster can spend additional RP to 
        affect a second province that is adjacent to the initially targeted 
        province. At 11th level, they may affect a third in the same manner, so 
        long as it is in some way connected to one of the first two. At 17th, the 
        caster may affect four connected provinces. Only the initially-targeted 
        province need be one in which the caster possesses a Source holding or 
        suitable ley line connection.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Source'][['Type', 'Level', 'Provence']].groupby(['Type', 'Provence']).max().reset_index()
        success = False
        reward = 0
        lst = []
        message = 'Lacks the resources to cast Death Plague'
        temp = temp[temp['Level']>=5]
        if temp.shape[0] > 0:
            # we have the resources...
            valid = pd.concat([temp[['Provence']], self.LeyLines[self.LeyLines['Regent']==Regent][['Provence']]])
            valid = pd.merge(valid, self.Provences[self.Provences['Regent']==Target], on='Provence', how='inner')
            targets = pd.merge(valid[['Provence']], self.Geography, on='Provence', how='left').fillna(0)
            targets = pd.merge(targets[targets['Border']==1][['Neighbor']],self.Provences[self.Provences['Regent']==Target], left_on='Neighbor', right_on='Provence', how='left').fillna(0)
            targets = targets[targets['Provence'] != 0]
            targets = list(valid['Provence']) + list(targets['Provence'])
            # targets aquired...
            Limits = [1,5,11,17]
            if len(targets) == 0:
                return False, 0, message
            Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
            message = "{} cast 'Death Plague' on {}'s lands; ".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], elf.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
            
            RP = self.Regents[self.Regents['Regent'] == Regent]['Regency Points'].values[0]
            Limits = [1,5,11,17]
            for i, pro in enumerate(Targets):
                if i <= 3 and Level >= Limits[i]:
                    # do we have the RP...
                    Pop = self.Provences[self.Provences['Provence'] == Provence]['Population'].values[0]
                    if RP >= Pop:
                        RP = RP - Pop
                        # lower the population
                        self.change_provence(pro, Population_Change=-1)
                        lst.append(pro)
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] - 2, Regency_Points = RP)
        return True, 0, message + ', '.join(lst)

    def realm_magic_demagogue(self, Regent, Target, Increase=True):
        '''
        RP Cost: 5 per loyalty grade
        GB Cost: 1
        Required Source: 3
        Duration: See description

        A devious enchantment woven over a realm, the demagogue spell enables a regent to affect the loyalty of provinces for better or worse. By expending 5 RP per grade, the caster can increase or decrease the loyalty of the target province. Thus, a wizard regent can charm a rebellious province to increase the loyalty of its people to high by expending 15 RP. If this spell is cast on an opposing regent's domain, that regent is entitled to a Bloodline saving throw to avoid the effect.

        Beginning at 5th level, the regent can target up to two provinces with this spell, but must pay the cost for each province and loyalty grade they wish to affect. At 11th level, they can affect up to three provinces. At 17th, they can affect four provinces.
        
        CHANGING TO ONLY 1 GRADE EACH
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Source'][['Type', 'Level']].groupby('Type').max().reset_index()
        success = False
        reward = 0
        message = 'Lacks the resources to cast Demagogue'
        temp = temp[temp['Level']>=3]
        RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
        Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
        
        if temp.shape[0] > 0 and RP >= 5:
            temp = self.Provences[self.Provences['Regent'] == Target].copy()
            temp['Loyalty'] = temp['Loyalty'].str.replace('Rebellious','0').replace('Poor','1').replace('Average','2').replace('High','3').astype(int)
            success = True
            message = "{} cast 'Demagogue' on {}'s Provences: ".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], self.Regents[self.Regents['Regent']==Target]['Full Name'].values[0])
            if Increase == True:
                temp = temp.sort_values('Loyalty')
            else:
                temp = temp.sort_values('Loyalty', ascending=False)
            Limits = [1,5,11,17]
            lst = []
            if temp.shape[0] >= 0:
                for i, row in temp.iterrows():
                    if i <= 3:
                        if RP >= 5 and Limits[i] <= Level and i <= 3:
                            RP = RP - 5
                            if Increase == True:
                                self.change_loyalty(row['Provence'], 1)
                            else:
                                self.change_loyalty(row['Provence'], -1)
                            lst.append(row['Provence'])
                            reward += 3
            self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]-1, Regency_Points = RP)
            message = message + ', '.join(lst)
            if Increase == True:
                message = message + ' ; increasing their loyalty'
            else:
                message = message + ' ; decreasing their loyalty'
        return success, reward, message
            
    def realm_magic_legion_of_the_dead(self, Regent, Provence):
        '''
        Legion of the Dead
        RP Cost: 4 per unit
        GB Cost: 1 per unit
        Required Source: 3
        Duration: One season

        Through the use of this terrible necromantic realm spell, a regent 
        may raise armies of undead for use in war. Undead units have no 
        maintenance cost, can march day and night without rest, and strike 
        fear into the hearts of their enemies. The caster must remain within 
        the same province as the undead legion or the summoned units 
        immediately disband and are destroyed.

        The caster may summon one unit of undead with this spell. Upon reaching 
        5th level, they may summon two units, but must pay the cost for each. 
        At 11th level, they may summon three units, and at 17th level they may 
        summon four.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Source'][['Type', 'Level', 'Provence']]


        temp = temp[temp['Level']>=3]
        temp = pd.concat([temp[['Provence']], self.LeyLines[self.LeyLines['Regent']==Regent][['Provence']]])
        temp = temp[temp['Provence']==Provence]
        temp = pd.merge(temp[['Provence']], self.Holdings[self.Holdings['Type']=='Source'])
        temp = temp[temp['Regent']==Regent]
        success = False
        reward = 0
        message = 'Lacks the resources to cast Legion of the Dead'
        
        temp = temp[temp['Level']>=3]
        RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
        GB = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]
        Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
        Limits = [1,5,11,17]
        if temp.shape[0] > 0 and RP >= 4 and GB >= 1:
            N = 0
            for lim in Limits:
                if lim <= Level and RP >=4 and GB >=1:
                    RP = RP - 4
                    GB = GB - 1
                    N += 1
                    self.Troops.append(pd.DataFrame([[Regent, Provence, 'Undead Troops', 0, 2, 0, '', 0]], columns=self.Troops.keys()))
                    self.Projects.append(pd.DataFrame([[Regent, 'Undead Troops', '', 0]], columns=self.Projects.keys()))
            self.change_regent(Regent, Gold_Bars=GB, Regency_Points=RP)
            message = "{} Cast 'Legion of the Dead', summong {} Undead Troops in {}".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], N, Provence)
            reward = N
            
        return success, reward, message
    
    def realm_magic_mass_destruction(self, Regent, Provence):
        '''
        Mass Destruction
        RP Cost: 10 per unit
        GB Cost: 5
        Required Source: 5
        Duration: Instant

        Calling down rains of fire, explosive storms, or poisonous winds, the caster 
        can obliterate enemy armies within the target province. By paying the listed 
        cost, the regent may attempt to destroy any single unit in the target province. 
        Upon reaching 5th level, they may affect two units. At 11th, the regent can 
        instead affect three units. At 17th, they may affect four units. The regent 
        must pay the RP cost for each unit affected, and must be able to see the units 
        being affected.

        Targeted units are destroyed unless the controlling regent succeeds on a 
        Bloodline saving throw, which allows the unit to only suffer 25% casualties 
        instead.

        A dragon unit cannot be affected by this spell. Attached commanders on a unit 
        that is destroyed suffer 5d10 points of damage, Typed according to the caster’s 
        wishes. The caster can select the Type of damage at the time the spell is invoked 
        from among acid, fire, cold, force, lightning, poison, or thunder.

        The aftermath of the destruction lays waste to the surrounding countryside. The 
        populace suffers an immediate degradation of loyalty whether or not any units 
        were destroyed.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Source'][['Type', 'Level', 'Provence']]
        temp = temp[temp['Level']>=5]
        temp = pd.concat([temp[['Provence']], self.LeyLines[self.LeyLines['Regent']==Regent][['Provence']]])
        temp = temp[temp['Provence']==Provence]
        success = False
        reward = 0
        message = 'Lacks the resources to cast Legion of the Dead'
        
        RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
        RB = self.Regents[self.Regents['Regent']==Regent]['Regency Bonus'].values[0]
        GB = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]
        Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
        Limits = [1,5,11,17]
        if temp.shape[0] > 0 and RP >= 10 and GB >= 5:
            temp = self.Troops[self.Troops['Provence']==Provence].copy()
            N = 0
            for i, row in temp.iterrows():
                for i, row in temp.iterrows():
                    if N <= 3:
                        if Limits[N] <= Level and RP >= 10:
                            print(row['Regent'])
                            success, crit = self.make_roll(row["Regent"], 10+RB, 'Regency Bonus')
                            if success == False:
                                N += 1
                                self.disband_troops(row['Regent'], Provence, row['Type'], Killed=True)
                                RP = RP - 10
            self.change_regent(Regent, Gold_Bars=GB-5, Regency_Points = RP)
            self.change_loyalty(Provence, -1)
            success, reward, message = True, N*3, "{} cast 'Mass Destruction' on {}".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], Provence)
        return success, reward, message 
    
    def realm_magic_raze(self, Regent, Target):
        '''
        RP Cost: 10 per structure level
        GB Cost: 2 per damage level inflicted
        Required Source: 5
        Duration: Instant

        Powerful spellcasters can use this realm spell to devastate castles and similar 
        fortifications. The more expansive the castle, the more expensive this spell is 
        to cast, even if the damage you intend to cause is not equal to the level of the 
        castle. For example, a level 4 castle costs 40 RP to target with this realm spell, 
        though you may only have enough gold bars to damage it up to three levels. 
        Sometimes it is simply enough to send a message rather than obliterate a castle 
        outright.

        The damage caused happens instantaneously, but the caster must be within sight range 
        of the castle being affected throughout the period of time the spell is being cast. 
        As such, this realm spell is typically invoked while a regent’s armies are laying 
        siege to a province. The regent that owns the castle may attempt a Bloodline saving 
        throw to halve the damage to the castle in question.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Source'][['Type', 'Level', 'Provence']]
        temp = temp[temp['Level']>=5]
        temp = pd.concat([temp[['Provence']], self.LeyLines[self.LeyLines['Regent']==Regent][['Provence']]])
        temp = temp[temp['Provence']==Provence]
        success = False
        reward = 0
        message = 'Lacks the resources to cast Legion of the Dead'
        
        RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
        RB = self.Regents[self.Regents['Regent']==Regent]['Regency Bonus'].values[0]
        GB = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]
        Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
        
        if temp.shape[0] > 0 and RP >= 10 and GB >= 2:
            temp = pd.merge(self.Troops[self.Troops['Regent']=='Regent'][['Provence']], self.Provences[self.Provences['Regent']==Target], on='Provence', how='left')
            temp = temp[temp['Castle']>0]
            if temp.shape[0]>0:  # I have troops where an enemy has a castle
                Level = temp.iloc[0]['Castle']
                dmg = 0
                for i in range(Level):
                    if RP >= 10 and GB >= 2:
                        dmg += 1
                        RP = RP - 10
                        GB = GB - 2
                save, _ = self.make_roll(Target, 10+RB, 'Regency Bonus')
                if save == True:
                    dmg = int(dmg/2)
                    if dmg == 0:
                        dmg = 1
                self.change_provence(temp.iloc[0]['Provence'], Castle = Level - dmg)
                self.change_regent(Regent, Gold_Bars = GB, Regency_Points = RP)
                success = True
                reward = dmg*5
                message = "{} cast 'Raze' on {}".format(self.Regents[self.Regents['Regent']==Regent].copy(), temp.iloc[0]['Castle Name'])
        return success, reward, message 
            
    def realm_magic_stronghold(self, Regent, Provence, Perm=False):
        '''
        RP Cost: 6 RP per castle level
        GB Cost: 10
        Required Source: 7
        Duration: One season per caster level

        The invoker of this realm spell bends the land to their will to conjure a fortress
        in the target province. The RP cost is equivalent to constructing a fortress with 
        gold (6 RP per castle level), but the result is happens over the course of minutes 
        rather than months. The fortress remains for one season per level of the caster, 
        and crumbles to useless debris at the end of that period or if the caster dies.

        If the spellcaster is willing to pay double the RP cost, the castle can be made 
        permanent, though this act is extremely taxing on the spellcaster and ages them 
        10 years. It will not destroy itself if the caster is later killed or dies of 
        natural causes.
        '''
        temp = self.Holdings[self.Holdings['Regent'] == Regent].copy()
        temp = temp[temp['Type']=='Source'][['Type', 'Level', 'Provence']]
        temp = temp[temp['Level']>=7]
        temp = pd.concat([temp[['Provence']], self.LeyLines[self.LeyLines['Regent']==Regent][['Provence']]])
        temp = temp[temp['Provence']==Provence]
        success = False
        reward = 0
        message = 'Lacks the resources to cast Stronghold'
        
        RP = self.Regents[self.Regents['Regent']==Regent]['Regency Points'].values[0]
        RB = self.Regents[self.Regents['Regent']==Regent]['Regency Bonus'].values[0]
        GB = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0]
        Level = self.Regents[self.Regents['Regent']==Regent]['Level'].values[0]
        
        if temp.shape[0] > 0 and RP >= 6 and GB >= 10:
            temp = self.Provences[self.Provences['Provence']==Provence].copy()
            if temp.shape[0]>0:
                Pop = temp.iloc[0]['Population']
                castle = temp.iloc[0]['Castle']
                for i in range(Pop):
                    if Perm == False:
                        if RP >= 6:
                            RP = RP - 6
                            castle += 1
                    else:
                        if RP >= 12:
                            RP = RP - 12
                            castle += 1
                if castle > 0 :
                    self.change_provence(Provence, Castle=castle)
                    success = True
                    reward = castle*5
                    message = "{} cast 'Stronghold' in {}.".format(self.Regents[self.Regents['Regent']==Regent]['Full Name'].values[0], Provence)
                    if Perm == False:
                        self.Projects = self.Projects.append(pd.DataFrame([[Regent, 'Realm Magic Stronghold', (Provence, castle), Level*3]], columns=self.Projects.keys()))
            self.change_regent(Regent, Gold_Bars = GB - 10, Regency_Points=RP)
        return success, reward, message
        
    # The War 'Move'
    def war_move(self):
        '''
        Determine which provences have occupying troops (troops that belong to an active enemy 
        of the home regent).
        '''
        # track battles
        record = pd.DataFrame()
        year = self.game_year + int(self.Season/4)
        cal_season = self.Season - int(self.Season/4)
        time_reference = str(cal_season).replace('0', 'Winter').replace('1','Spring').replace('2','Summer').replace('3','Autumn') + ', year {} HC'.format(year)
        
        temp = self.Provences.copy()
        temp['Home Regent'] = temp['Regent']
        temp = pd.merge(self.Troops, temp[['Home Regent', 'Provence']], on='Provence', how='left')

        lst = []
        temp['Defense'] = 0
        temp['Offense'] = 0
        M = temp[temp['Regent'] == temp['Home Regent']]
        M['Defense'] = 1
        lst.append(M)
        temp =  temp[temp['Regent'] != temp['Home Regent']]
        for HR in temp['Home Regent']:
            allies, enemies = self.allies_enemies(HR)
            
            E = pd.merge(enemies, temp[temp['Home Regent']==HR], on='Regent', how='left').fillna(0)
            E['Offense'] = 1
            A = pd.merge(allies, temp[temp['Home Regent']==HR], on='Regent', how='left').fillna(0)
            A['Defense'] = 1
            lst.append(E)
            lst.append(A)
        temp = pd.concat(lst, sort=False)
        temp =  temp[temp['Provence'] !=0]

        defenders = temp[temp['Defense']==1]
        attackers = temp[temp['Offense']==1]
        
        
        for Provence in attackers['Provence']:
            message = ''
            Castle = self.Provences[self.Provences['Provence']==Provence]['Castle'].values[0]
            if attackers.shape[0] >= Castle and Castle > 0 and np.sum(attackers['Type'].str.lower().str.contains('artillery|engineer')) > 0:
                # Damage the Castle...
                    self.change_provence(Provence, Castle=Castle-1)
                    Castle = Castle - 1
                    if castle > 0:
                        message = message + 'Castle {} was destroyed.'.format(elf.Provecnes[self.Provences['Provence']==Provence]['Castle Name'].values[0])
                    else:
                        message = message + 'Castle {} was damaged.'.format(elf.Provecnes[self.Provences['Provence']==Provence]['Castle Name'].values[0])
            if defenders[defenders['Provence'] == Provence].shape[0] > 0:  # we have a war!
                '''
                Resolving Battles
                Herein is presented a method for quickly resolving engagements with hostile units. The 
                system is intended to be economical for time, based on automatic resolution contingent 
                on the number of units present on each side as well as their composition.

                To determine the result, calculate the total Battlefield Challenge Rating (BCR) of all 
                units present in the engagement on each side, then compare the forces. For each unit on 
                the field, roll 1d6 to determine its state at the end of the engagement and add 
                modifiers based on following table.
                '''
                offense = attackers[attackers['Provence'] == Provence]
                defense =  defenders[defenders['Provence'] == Provence]
                write = defense[['Type','Regent','CR']].copy().groupby(['Regent', 'Type']).count().reset_index()
                write['write'] = write['CR'].astype(str) + ' ' + write['Type']
                message = '{} with a force of '.format(self.Regents[self.Regents['Regent'] == write.iloc[0]['Regent']]['Full Name'].values[0]) + ', '.join(list(write['write'])) + '. ' + message
                write = offense[['Type','Regent','CR']].copy().groupby(['Regent', 'Type']).count().reset_index()
                write['write'] = write['CR'].astype(str) + ' ' + write['Type']
                message = '{} with a force of '.format(self.Regents[self.Regents['Regent'] == write.iloc[0]['Regent']]['Full Name'].values[0]) + ', '.join(list(write['write'])) + ' battled ' + message
                '''
                --Resolving Battles--
                Circumstance    Modifier
                
                On a result of zero or lower, the unit is destroyed. On a result of 1, 
                the unit has suffered 50% casualties;
                if the unit has already suffered 50% or greater casualties, it is destroyed. 
                On a result of 2 to 5, the unit suffers 25% casualties, but survives the engagement. 
                On a result of 6 or greater, the unit suffers no significant casualties.
                '''
                off_score = 0
                def_score = 0
                # Go until it's over
                days = 0
                while off_score-def_score < def_score and def_score-off_score < off_score and defense.shape[0]>0 and offense.shape[0]>0:
                    # --- Modifiers ---
                    offense_strength = offense[['Type']].copy()
                    days += 1
                    offense['mod'] = offense['Injury']
                    defense['mod'] = defense['Injury']
                    # Enemy force has Archer-class units and your force has no Cavalry-class units    -1
                    if np.sum(offense['Type'].str.lower().str.contains('archer')) >=1 and\
                       np.sum(defense['Type'].str.lower().str.contains('cavalry|knight')) == 0:
                        defense['mod'] = defense['mod'] - 1
                    if np.sum(defense['Type'].str.lower().str.contains('archer')) >=1 and\
                       np.sum(offense['Type'].str.lower().str.contains('cavalry|knight')) == 0:
                        offense['mod'] = offense['mod'] - 1
                    # Enemy force has Cavalry-class units and your force has no Pikemen or Cavalry-class units    -1
                    if np.sum(offense['Type'].str.lower().str.contains('cavalry|knight')) >=1 and\
                       np.sum(defense['Type'].str.lower().str.contains('cavalry|knight|pikem')) == 0:
                        defense['mod'] = defense['mod'] - 1
                    if np.sum(defense['Type'].str.lower().str.contains('archer')) >=1 and\
                       np.sum(offense['Type'].str.lower().str.contains('cavalry|knight|pikem')) == 0:
                        offense['mod'] = offense['mod'] - 1
                    # Per 2 total BCR the enemy force exceeds your own (maximum penalty -3)   -1
                    # Per 2 total BCR your force exceeds the enemy force (maximum bonus +3)   +1
                    for a in range(0,int((np.sum(defense['CR'])-np.sum(offense['CR']))/2)):
                        if a <= 2:
                            offense['mod'] = offense['mod']-1
                            defense['mod'] = defense['mod']+1
                    for a in range(0,int((np.sum(offense['CR'])-np.sum(defense['CR']))/2)):
                        if a <= 2:
                            offense['mod'] = offense['mod']+1
                            defense['mod'] = defense['mod']-1
                    # The unit has terrain advantage (elves in forest, dwarves in mountains)  +1 [Skipping for now]
                    # Your force has established fortifications and defenses and enemy force has no Artillery or Engineer-class units.    +1
                    if self.Provences[self.Provences['Provence']==Provence]['Castle'].values[0] > 0 and np.sum(offense['Type'].str.lower().str.contains('artillery|engineer')) == 0:
                            defense['mod'] = defense['mod'] + defense['Garrisoned']  # only those in the castle
                    # The unit possesses an attached commander.   +1  [May Add later]
                    offense['roll'] = np.random.randint(1,6,offense.shape[0]) + offense['mod']
                    defense['roll'] = np.random.randint(1,6,defense.shape[0]) + defense['mod']
                    # deal with causulties
                    offense_50 = offense[offense['roll']==1]
                    defense_50 = defense[defense['roll']==1]
                    offense_25 = offense[offense['roll']>=2]
                    defense_25 = defense[defense['roll']>=2]
                    offense_25 = offense_25[offense_25['roll']<=5]
                    defense_25 = defense_25[defense_25['roll']<=5]
                    offense_good = offense[offense['roll']>5]
                    defense_good = defense[defense['roll']>5]
                    offense_50['Injury'] = offense_50['Injury'] - 2
                    defense_50['Injury'] = defense_50['Injury'] - 2
                    offense_25['Injury'] = offense_25['Injury'] - 1
                    defense_25['Injury'] = defense_25['Injury'] - 1
                    dead = pd.concat([offense[offense['roll']<=0], defense[defense['roll']<=0]])
                    offense = pd.concat([offense_50,offense_25,offense_good])
                    defense = pd.concat([defense_50,defense_25,defense_good])
                    dead = pd.concat([dead, offense[offense['Injury']<=-4], defense[defense['Injury']<=-4]])
                    for i, row in dead.iterrows():
                        self.disband_troops(row['Regent'], row['Provence'], row['Type'], True)  # kill 'em
                    off_score = np.sum(offense['CR'])
                    def_score = np.sum(defense['CR'])
                # deal with injuries
                defense_ = defense[defense['Injury'] >= -3]
                offense_ = offense[offense['Injury'] >= -3]
                defense_ = defense_[['Regent', 'Provence', 'Type', 'Injury', 'CR', 'Home', 'Garrisoned']].groupby(['Regent', 'Provence', 'Type', 'Injury', 'Home', 'Garrisoned']).count().reset_index()
                defense_['Injury'] = defense_['Injury'].astype(str).str.replace('-2','0.5').replace('-1','0.75').replace('-3','0.25').replace('0','1').astype(float)
                defense_['CR'] = defense_['CR']*defense_['Injury']
                defense_ = defense_[['Regent', 'Provence', 'Type', 'CR', 'Garrisoned']].groupby(['Regent', 'Provence', 'Type', 'Garrisoned']).sum().reset_index()
                defense_['CR'] = (defense_['CR']+0.5).astype(int)
                offense_ = offense[['Regent', 'Provence', 'Type', 'Injury', 'CR', 'Home']].groupby(['Regent', 'Provence', 'Type', 'Injury', 'Home']).count().reset_index()
                offense_['Injury'] = offense_['Injury'].astype(str).str.replace('-2','0.5').replace('-1','0.75').replace('-3','0.25').replace('0','1').astype(float)
                offense_['CR'] = offense_['CR']*offense_['Injury']
                offense_ = offense_[['Regent', 'Provence', 'Type', 'CR']].groupby(['Regent', 'Provence', 'Type']).sum().reset_index()
                offense_['CR'] = (offense_['CR']+0.5).astype(int)
                message = message + ' The engagement lasted {} days, ending with '.format(days)
                # run away if alive     
                if def_score < off_score and Castle==0:
                    if defense.shape[0]>0:
                        if self.Provences[self.Provences['Regent'] == defense['Regent'].values[0]].shape[0] > 0:
                            temp = self.Provences[self.Provences['Regent'] == defense['Regent'].values[0]]
                            temp['Population'] = temp['Population'] + 3*temp['Capital']
                            temp = temp.sort_values('Population')
                            _, newp = self.get_travel_cost(defense['Regent'].values[0], Provence, temp.iloc[0]['Provence'], Path=True)
                            if len(newp) > 1:
                                defense_['Provence'] = newp[1]
                                defense_['Garrisoned'] = 0
                                # no friendly forces remain, so...
                                self.change_provence(Provence, Contested=True)
                elif def_score < off_score and Castle > 0:  
                    defense_['Garrisoned'] = 1
                elif off_score < def_score:
                    if offense.shape[0] > 0:
                        if self.Provences[self.Provences['Regent'] == offense['Regent'].values[0]].shape[0] > 0:
                            temp = self.Provences[self.Provences['Regent'] == offence['Regent'].values[0]]
                            temp['Population'] = temp['Population'] + 3*temp['Capital']
                            temp = temp.sort_values('Population')
                            _, newp = self.get_travel_cost(offense['Regent'].values[0], Provence, temp.iloc[0]['Provence'], Path=True)
                            if len(newp) > 1:
                                offense_['Provence'] = newp[1]
                # consolidate troops down... and officially move them
                for i, row in defense.iterrows():
                    self.disband_troops(row['Regent'], row['Provence'], row['Type'], Real=False)
                for i, row in offense.iterrows():
                    self.disband_troops(row['Regent'], row['Provence'], row['Type'], Real=False)
                for i, row in defense_.iterrows():
                    for a in range(int(row['CR'])):
                        # let flee to/out-of castle if needed
                        self.add_troops(row['Regent'], row['Provence'], row['Type'], Garrisoned = row['Garrisoned'])
                for i, row in offense_.iterrows():
                    for a in range(int(row['CR'])):
                        self.add_troops(row['Regent'], row['Provence'], row['Type'])
                offense_['write'] = offense_['CR'].astype(str) + ' ' +offense_['Type']
                defense_['write'] = defense_['CR'].astype(str) + ' ' +defense_['Type']
                if off_score > def_score:
                    message = message + '{} victorious, with a force of '.format(self.Regents[self.Regents['Regent']==offense_['Regent']]['Full Name'].values[0])
                    message = message + ', '.join(list(offense_['write']))
                    if deffense_.shape[0] == 0:
                        message = ' slaghtering {} Troops to a man.'.format(self.Regents[self.Regents['Regent']==deffense['Regent']]['Full Name'].values[0])
                    else:
                        if Castle == 0:
                            message = " forcing {}'s Troops; ".format(self.Regents[self.Regents['Regent']==deffense_['Regent']]['Full Name'].values[0])
                            message = ', '.join(list(defense_['write']))
                            message = '; to flee to {}'.format(defense_['Provence'].values[0])
                        else:
                            message = " forcing {}'s Troops; ".format(self.Regents[self.Regents['Regent']==deffense_['Regent']]['Full Name'].values[0])
                            message = ', '.join(list(defense_['write']))
                            message = '; to hole-up in {}'.format(self.Provences[self.Provences['Provence']==Provence])
                else:
                    message = message + '{} defended {}, with a force of '.format(self.Regents[self.Regents['Regent']==defense_.iloc[0]['Regent']]['Full Name'].values[0], Provence)
                    message = message + ', '.join(list(offense_['write']))
                    message = " forcing {}'s Troops; ".format(self.Regents[self.Regents['Regent']==offense.iloc[0]['Regent']]['Full Name'].values[0])
                    message = ', '.join(list(offense_['write']))
                    message = '; to flee to {}.'.format(defense_['Provence'].values[0])
                            
                record = record.append(pd.DataFrame([[time_reference, Provence, 'Battle of {}'.format(Provence), message]], columns=['Year','Location','Event','Notes']))
                
                # Loyalty Adjustment
                if def_score > off_score:
                    for Reg in set(defense['Regent']):
                        for Prov in set(self.Provences[self.Provences['Regent']==Reg]['Provence']):
                            self.change_loyalty(Prov, 1)
                elif off_score > def_score:
                    for Reg in set(offense['Regent']):
                        for Prov in set(self.Provences[self.Provences['Regent']==Reg]['Provence']):
                            self.change_loyalty(Prov, 1)
                '''
                The side that suffers the most results of 1 or lower is considered defeated, and must 
                retreat to a province with no hostile force present on the same turn of its defeat. 
                If the force cannot be relocated in this way, it remains where it is. If the defeated 
                force is entrenched in fortifications of any kind (such as a castle), it can choose not 
                to retreat (if garrissoned, will not retreat)

                If neither side is defeated, the battle is a stalemate (though all casualty results 
                stand) and the forces  clash again on the following domain action. This continues until 
                one force or another is either defeated or destroyed.

                In the event one force’s total BCR is at least twice that of the opposing force, the 
                other force is automatically destroyed and no dice need be rolled (won't do this,
                since this makes the Spartan thing impossible)
                
                --Changes--
                * Not sure when the author wanted to run this, I run at end of Season.
                * Rolls are made until one side wins (whoever got more 1's)
                * casualties will be a modifier if we have to roll again (-1 for 25%, -3 for 50%)
                
                When done, or when there are no enemies in the provence and you end there, your troops 
                will do one of theactions listed:
                '''
                
                
            elif Castle == 0:   # Castle must be neutralized...
                '''
                Occupation and Conquest
                In the event that hostile forces remain in a province unopposed and with no castles that 
                remain unneutralized, the province is considered occupied. The province generates no gold 
                bars or regency for any regent that possesses holdings within it until the invading army 
                is dislodged -- that is, no hostile force remains within the province, and a friendly 
                force remains to re-establish order.

                As pointed out under the section for Seasons, an occupying force can collect Severe Taxation 
                on occupied provinces during the taxation phase. This act permanently reduces the level of the 
                province by one. Occupying forces act as a temporary, overriding Law holding of a level equal 
                to the number of occupying units; this special form of Law can exceed the level of the province.
                
                [Only If we razed/vandalized everything else]
                '''
                pop = self.Provences[self.Provences['Provence']==Provence]['Population'].values[0]
                self.change_provence(Provence, Contested=True)
                self.change_loyalty(Provence, -1)
                Regent = attackers['Regent'].values[0]
                message = '{} occupied {} with '.format(Regent, Provence)
                write = attackers[['Type','Regent','CR']].copy().groupby(['Regent', 'Type']).count().reset_index()
                write['write'] = write['CR'].astype(str) + ' ' + write['Type']
                message = message + ', '.join(list(write['write']))
                '''
                During occupation on the phase of the turn when War Moves occur, in lieu of moving the occupying 
                force, the army can perform one of the following activities:

                Quash Law: 
                You permanently reduce the level of all Law holdings they choose in the province to zero.
                [Assuming there is a law Holding from an enemy, if not...]
                '''
                _, enemies = self.allies_enemies(Regent)
                temp = pd.merge(enemies, self.Holdings[self.Holdings['Provence']==Provence], on = 'Regent', how='left')
                if temp[temp['Type']=='Law'].shape[0] > 0:
                    message = message + ' quashing all rival law holdings.'
                    law = temp[temp['Type']=='Law'].copy()
                    for i, row in law.iterrows():
                        self.change_holding(Provence, row['Regent'], 'Law', mult_level=0)
                    '''
                    Disband Guilds: 
                    You permanently reduce the level of all Guild holdings they choose in the province to zero.
                    [Assuming they belong to enemies, if no enemies with a guild > 0...]
                    '''
                elif temp[temp['Type']=='Guild'].shape[0] > 0:
                    law = temp[temp['Type']=='Guild'].copy()
                    message = message + ' disbanding all rival guilds.'
                    for i, row in law.iterrows():
                        self.change_holding(Provence, row['Regent'], 'Guild', mult_level=0)
                    '''
                    Raze Temples: 
                    You permanently reduce the level of all Temple holdings they choose in the province to zero.
                    [Again, assuming they belong to enemies, if not...]
                    '''
                elif temp[temp['Type']=='Temple'].shape[0] > 0:
                    message = message + ' razing all rival temples.'
                    law = temp[temp['Type']=='Temple'].copy()
                    for i, row in law.iterrows():
                        self.change_holding(Provence, row['Regent'], 'Temple', mult_level=0)
                    '''
                    Vandalize Sources: 
                    You permanently reduce the level of all Source holdings they choose in the province by one.
                    [Again, only if enemies]
                    '''
                elif temp[temp['Type']=='Source'].shape[0] > 0:
                    message = message + ' vandalizing all rival Sources.'
                    law = temp[temp['Type']=='Source'].copy()
                    for i, row in law.iterrows():
                        self.change_holding(Provence, row['Regent'], 'Source', mult_level=0)
                    '''
                    Any holding damaged in this way can be leveled once more through domain actions should the 
                    province be liberated, or if the occupying army’s regent invests the province and becomes 
                    its rightful lord.
                            
                    '''
                else:  # here we tax once done with the ruining of guilds and the like
                    try:
                        a,b = self.provence_taxation[self.provence_taxation['Population']==pop]['Severe'].values[0]
                    except:
                        a,b = 0,1
                    tax = np.random.randint(a,b,1)[0]
                    self.change_regent(Regent, Gold_Bars = self.Regents[self.Regents['Regent']==Regent]['Gold Bars'].values[0] + tax)
                    self.change_provence(Provence, Population_Change=-1)
                    message = message + ' sacking and looting the provence.'
                record = record.append(pd.DataFrame([[time_reference, Provence, 'Occupation of {}'.format(Provence), message]], columns=['Year','Location','Event','Notes']))
        self.War.append(record)
  
    def clean_up(self):
        '''
        At the end of the season, after all three action rounds have been taken 
        and all war moves and battles are resolved, all active regents perform 
        this step. First, regents adjust loyalty in each province based on the 
        following conditions:

        Reduce loyalty by one category if:

        Severe taxes were collected, or moderate taxes were collected in a province with no Law holdings
        [In Tax System]
        Levies were mustered and sent to a foreign land
        Domain events that modify loyalty were not addressed
        [?]
        A rival regent completes Agitate actions in that province with the express purpose of causing unrest
        [Part of action]
        Province is under occupation by an enemy force
        '''
        # Levies in foriegn land
        temp = self.Troops[self.Troops['Type'] == 'Levies'].copy()
        temp = temp[temp['Provence'] != temp['Home']]
        temp = pd.merge(temp, self.Provences[['Provence', 'Domain']], on='Provence', how='left')    
        temp_ = self.Provences.copy()
        temp_['Home Domain'] = temp_['Domain']
        temp_['Home'] = temp_['Provence']
        temp = pd.merge(temp, temp_[['Home', 'Home Domain']], on='Home', how='left')
        temp = temp[temp['Home'] != temp['Home Domain']]
        for Provence in set(temp['Provence']):
            self.change_loyalty(Provence, -1)
        '''
        Improve loyalty by one category if:

        No taxes were collected
        A regent completes an Agitate action in that province with the purpose of improving loyalty
        A major battle was won against a hated enemy (improves loyalty in all provinces)
        '''
        
        # all of those were done where they happen
        
        # Now, for the Building projects and other Projects..
        self.Projects['Gold Bars Left'] = self.Projects['Gold Bars Left'] - np.random.randint(1,6,self.Projects.shape[0])
        temp = self.Projects[self.Projects['Gold Bars Left']<=0].copy()
        self.Projects = self.Projects[self.Projects['Gold Bars Left']>=1]
        for i, row in temp.iterrows():
            if row['Project Type']=='Castle':  # set the castle number
                castle = self.Provences[self.Provences['Provence']==row['Details'][0]].iloc[0]['Castle']
                self.change_provence(row['Details'][0], Castle = castle + row['Details'][1])
            elif row['Project Type']=='Road':  # add the road
                self.add_geo(row['Details'][0], row['Details'][1], Road=1)
            elif row['Project Type'] == 'Undead Troops':  # disband the troops
                tfinder = self.Troops[self.Troops['Regent']==row['Regent']].copy()
                prov = tfinder[tfinder['Type']=='Undead Troops'].iloc[0]['Provence']
                self.disband_troops(row['Regent'], prov, 'Undead Troops', Killed=False)
            elif row['Project Type'] == 'Realm Magic Stronghold':  # destroy the castle
                castle = self.Provences[self.Provences['Provence']==row['Details'][0]].iloc[0]['Castle']
                self.change_provence(row['Details'][0], Castle=castle - row['Details'][1] )
            elif row['Project Type'] == 'Troop Permission':
                self.add_relationship(row['Regent'], row['Details'], Vassalage=-1)
        # garrisoned/recently recruited Troops
        temp = self.Troops[self.Troops['Garrisoned']==1].copy()
        # free 'em all
        self.Troops['Garrisoned'] = 0
        # put 'em back...
        temp = pd.merge(temp, self.Provences[['Castle','Regent','Provence']], on=['Regent','Provence'], how='left').fillna(0)
        temp = temp[temp['Castle'] >= 1]
        if temp.shape[0] > 0:
            for Prov in set(temp['Provence']):
                N = 0
                for i, row in temp[temp['Provence']==Prov].iterrows():
                    if N < row['Castle']:
                        N += 1
                        # add the garrisoned flag...
                        df = self.Troops[self.Troops['Provence']==Prov]
                        df = df[df['Regent']==row['Regent']]
                        lst = df.index[df['Type'] == row['Type']]
                        self.Troops.loc[lst[0]]['Garrisoned'] = 1
            
        
    # tools    
    def set_difficulty(self, base, Regent, Target, hostile=False, assassination=False, player_rbid=None):
        '''
        This is how much money is thrown at the problem and how
        much regeny is used to oppose it
        '''
        rbid = 0
        gbid = 0
        base = int(base)
        temp = pd.concat([self.Regents[self.Regents['Regent']==a] for a in [Regent, Target]], sort=False)
        temp = pd.merge(temp, pd.concat([self.Relationships[self.Relationships['Other']==a] for a in [Regent, Target]], sort=False), on='Regent', how='left').fillna(0)
        mult = -1*hostile + 1-hostile
        # enemy spends Regency
        if player_rbid == None:
            if assassination:
                rbid = 10
            else:
                if temp[temp['Regent'] == Target].shape[0]>0:
                    rbid = mult*temp[temp['Regent'] == Target]['Diplomacy'].values[0]  # diplomacy = williness
                    if temp[temp['Regent'] == Target]['Attitude'].values[0] == 'Aggressive':
                        rbid = rbid + 2  # agressive will throw around more
                    elif temp[temp['Regent'] == Target]['Attitude'].values[0] == 'Xenophobic':
                        if temp[temp['Regent'] == Target]['Race'].values[0] != temp[temp['Regent'] == Regent]['Race'].values[0]:
                            rbid = rbid + 5  # xenophobic will oppose hard if not same race
            if temp[temp['Regent'] == Target].shape[0]>0:
                if rbid > temp[temp['Regent'] == Target]['Regency Points'].values[0]:
                    rbid = temp[temp['Regent'] == Target]['Regency Points'].values[0]  # cannot spend more than you have
            if rbid > 10:
                rbid = 10
            elif rbid < 0:
                rbid = 0
        else:
            rbid = player_rbid
        if temp.shape[0]>0:
            self.change_regent(Target, Regency_Points = temp[temp['Regent']==Target]['Regency Points'].values[0] - rbid)

        difficulty = base - gbid - rbid
        return difficulty
        
    def make_roll(self, Regent, dc, skill, adj=False, dis=False, player_gbid=None):
        '''
        Make the roll
        '''
        temp = self.Regents[self.Regents['Regent']==Regent].copy()
        
        gbid = 0
        try:
            bonus = self.Regents[self.Regents['Regent']==Regent][skill].values[0]
        except:
            self.errors.append[('Roll',Regent,skill)]
            bonus=0
        if player_gbid == None: 
            # Regent spends gold to counter...
            if dc > 10 + bonus and  temp[temp['Regent']==Regent]['Gold Bars'].values[0] > 10:
                gbid = dc - (10 + bonus)
        if gbid >= temp[temp['Regent'] == Regent]['Gold Bars'].values[0]:
            # can't spend what you don't have
            gbid = temp[temp['Regent'] == Regent]['Gold Bars'].values[0] - 1
        if gbid > 10:
            gbid = 10
        elif gbid < 0:
            gbid = 0
        dc = dc - gbid  # lowered the difficulty
        self.change_regent(Regent, Gold_Bars = temp[temp['Regent']==Regent]['Gold Bars'].values[0] - gbid)
        
        n = 1
        if adj:
            n == 2
        if dis == False:
            roll = np.max(np.random.randint(1,20,n))
        else:
            roll = np.min(np.random.randint(1,20,2))
        
        if roll == 1 or roll+bonus < dc:
            return False, False
        elif roll == 20:
            return True, True
        elif roll+bonus >= dc:
            return True, False
        else:
            return False, False
            
    def get_travel_cost(self, Regent, Provence, Target, unit='levies', Path=False):
        '''
        Given a Regent and two Provences, return the travel cost
        '''
        
        valid = pd.concat([self.Relationships[self.Relationships['Regent'] == Regent], self.Relationships[self.Relationships['Other']==Regent]], sort=False)
        valid = pd.concat([valid[valid['Vassalage']>0], valid[valid['At War']>0], valid[valid['Diplomacy']>2]])
        valid['War'] = 1*(valid['At War'] > 0)
        valid_ = valid.copy()
        valid_['Regent'] = valid['Other']
        valid = pd.concat([valid[['Regent', 'War']], valid_[['Regent', 'War']]]).groupby('Regent').max().reset_index()

        # get valid provences
        temp = pd.merge(valid, self.Provences.copy(), on='Regent', how='left').fillna(0)
        temp = temp[temp['Provence'] != 0]
        
        # racial modifiers
        if 'Elf' in unit.split():
            temp['Terrain'] = temp['Terrain'].str.replace('Forest', '1')
        if 'Dwarf' in unit.split():
            temp['Terrain'] = temp['Terrain'].str.replace('Mountains', '2').replace('Mountain', '2').replace('Glacier', '2')
            
        # get provence values
        lst = [('Desert', '2'), ('Tundra', '2')
              , ('Mountain', '4'), ('Mountains', '4'), ('Glacier', '4')
              , ('Forest', '2')
              , ('Hills', '2')
              , ('Plains', '2'), ('Farmland', '2'), ('Steppes', '2')
              , ('Swamp', '3'), ('Marsh','3')]
        for a in lst:
            temp['Terrain'] = temp['Terrain'].str.replace(a[0], a[1])
        travel = self.Geography[self.Geography['Border']==1].copy()
        travel = pd.merge(temp[['Provence', 'War']], travel, on='Provence', how='left')
        travel = pd.concat([travel[travel['Neighbor']==P] for P in list(temp['Provence'])], sort=False)
        temp['A'] = temp['Terrain'].astype(int)
        travel = pd.merge(travel, temp[['Provence', 'A', 'Regent', 'Castle']], on='Provence', how='left')
        temp['B'] = temp['Terrain'].astype(int)
        temp['Other'] = temp['Regent']
        temp['Neighbor'] = temp['Provence']
        travel = pd.merge(travel, temp[['Neighbor', 'B', 'Other']], on='Neighbor', how='left')

        # set costs
        travel['Cost'] = ((travel['A'] + travel['B'] + 1)/2).astype(int) - travel['Road']
        # not sure how to stop after, so... Rivers cost 10 to cross
        travel['Cost_Cal'] = travel['Cost'] + (travel['RiverChasm']-travel['Road'])*10
        
        # castles...
        temp_ = self.Provences[self.Provences['Castle']>0][['Provence', 'Castle']]
        allies, _ = self.allies_enemies(Regent)
        allies.append(pd.DataFrame([[Regent]], columns=['Regent']), ignore_index=True)
        temp = pd.merge(allies, self.Troops, on='Regent', how='left').fillna(0)
        temp = temp[temp['CR']>0]
        temp = temp[['Provence', 'Type']].groupby('Provence').count().reset_index()
        temp = pd.merge(temp_, temp, on='Provence', how='left').fillna(0)
        temp = temp[temp['Type']<temp['Castle']]  # otherwise neutralized
        temp['Castle_Cost'] = 20
        travel = pd.merge(travel, temp[['Provence', 'Castle_Cost']], on='Provence', how='left').fillna(0)
        travel['Cost_Cal'] = travel['Cost_Cal'] + travel['Castle_Cost']
        
        # same issue...
        travel['Cost'] = travel['Cost'].astype(str).str.replace('0.0', '1.0').astype(float).astype(int)
        travel = travel.drop_duplicates()

        # make network
        G = nx.from_pandas_edgelist(travel, source='Provence', target='Neighbor', edge_attr=['Cost', 'Cost_Cal'])
        if Path == False:
            return nx.shortest_path_length(G, Provence, Target, 'Cost_Cal')
        else:
            return nx.shortest_path_length(G, Provence, Target, 'Cost_Cal'), nx.shortest_path(G, Provence, Target, 'Cost_Cal')
          
    def allies_enemies(self, Regent):
        '''
        Figures out who you are at war with, allies with, and who your allies are allies with, at war with.
        
        Any further and World War I starts (seriously).
        
        needed for various and sundry troop functions.
        '''
        temp = pd.concat([self.Relationships[self.Relationships['Regent'] == Regent], self.Relationships[self.Relationships['Other']==Regent]], sort=False)

        allies = pd.DataFrame(pd.concat([temp[temp['Vassalage']>0]['Regent'], temp[temp['Vassalage']>0]['Other'], temp[temp['Diplomacy']>0]['Regent'], temp[temp['Diplomacy']>0]['Other']]).drop_duplicates(), columns=['Regent'])
        enemies =  pd.DataFrame(pd.concat([temp[temp['At War'] > 0]['Regent'], temp[temp['At War'] > 0]['Other'], temp[temp['Diplomacy'] < 0]['Regent'], temp[temp['Diplomacy'] < 0]['Other']]).drop_duplicates(), columns=['Regent'])

        temp = pd.merge(allies, self.Relationships)

        allies = pd.DataFrame(pd.concat([allies['Regent'], temp[temp['Vassalage']>0]['Regent'], temp[temp['Vassalage']>0]['Other']]).drop_duplicates(), columns=['Regent'])
        enemies = pd.DataFrame(pd.concat([enemies['Regent'], temp[temp['At War']>0]['Regent'], temp[temp['At War']>0]['Other']]).drop_duplicates(), columns=['Regent'])

        check = pd.merge(allies, enemies, on='Regent', how='inner')
        check['temp'] = 1
        if check.shape[0]>0:
            # remove allies from enemies list
            enemies = pd.merge(enemies, check, on='Regent', how='left').fillna(0)
            enemies = pd.DataFrame(enemies[enemies['temp']==0]['Regent'], columns=['Regent'])
            enemies = enemies[enemies['Regent'] != Regent]
                
        return allies, enemies
    