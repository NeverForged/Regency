import os
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from PIL import Image
import random as rand
from random import randint
import matplotlib.pyplot as plt
from source.DQNAgent import DQNAgent
from keras.utils import to_categorical
from IPython.display import clear_output


class Regency(object):
    '''
    Neverforged Regency Game.
    '''
    
    # Initialization
    def __init__(self, campaign='The Island', geography='sample_geography.csv', factions='sample_factions.csv',
                       areas='sample_areas.csv', relationships='sample_relationships.csv', vassalage='sample_vassalage.csv',
                       strongholds='sample_strongholds.csv'):
        '''
        Based on the Regency system I developed for 5e dnd.
        
        initialization of Regency class.
        Sets the dataframes based on saved-version
        
        campaign -> the name of the campaign
        geography -> neighbor graphs of the area
        factions -> a list of factions
        areas -> area information
        relationships -> relationship information, defined as how faction feels towards other, -1 = Hostile, 0 = Indifferent, 1 = Helpful, 2 = Friendly
        vassalage -> pay 10% gold per season and allow them to use your lands (they become friendly to you)
        
        Default Values are the samples in the main folder, which you can edit to your heart's content.
        
        self.faction_classes = the classes that factions can take
        self.level_modifiers = skill modifier by faction level
        self.population = population infromation for settlements
        self.strongholds = information for strongholds
        self.terrain = terrain information
        '''
        
        # Initialize class variables
        self.campaign = campaign
        self.season = 0
        self.seasons = pd.DataFrame(columns=['Faction'])
        self.geography = pd.read_csv(geography)
        self.factions = pd.read_csv(factions)
        self.areas = pd.read_csv(areas).fillna('')
        self.vassalage = pd.read_csv(vassalage)
        self.vassalage_checked = pd.DataFrame()
        self.strongholds = pd.read_csv(strongholds)
        self.relationships = pd.read_csv(relationships)
        self.faction_classes = pd.read_csv('data/faction_classes.csv')  
        self.level_modifiers = pd.read_csv('data/level_modifiers.csv') 
        self.population = pd.read_csv('data/population.csv')  
        self.stronghold_types = pd.read_csv('data/stronghold_types.csv')
        self.terrain = pd.read_csv('data/terrain.csv')
        self.new_roads = pd.DataFrame(columns=['Area','Neighbor'])
        
        self.check_vassalage()  # get initial value
        self.calculatelevels_faction()  # fix initial values
        self.calculate_magic()  # fix magic levels of areas
        
        self.IntDC = 9001  # set to determine random activity
        self.espionage = pd.DataFrame(columns=['Faction','Target'])
        self.construction = pd.DataFrame(columns=['Faction', 'Area', 'Type', 'Name','Seasons'])
        self.sieges = pd.DataFrame(columns=['Faction','Stronghold'])
        self.save_level = self.factions[['Name','Level']]
        self.save_level['Faction'] = self.save_level['Name']
        self.save_level = self.save_level[['Faction','Level']]
        
        try:
            self.agent = pickle.load( open( 'agents/agent.pickle', "rb" ) )
        except:
            self.agent = DQNAgent(self)
            # self.agent.save()
        self.last_season = pd.DataFrame()


    #   ---   FACTION FUNCTIONS   ---
    def add_faction(self,Name,Class,Culture='Human',Player=0,Gold=0):
        '''
        Add a faction to the game
        '''
        new_row = {'Name':Name,'Class':Class,'Culture':Culture,'Player':Player,'Gold':Gold}
        # valid class choice
        if self.faction_classes[self.faction_classes['Name']==Class].shape[0] == 1:
            # Valid Class
            temp = self.faction_classes[self.faction_classes['Name']==Class].copy()
            for a in list(self.factions.keys()):
                if a not in list(new_row.keys()) and a in list(temp.keys()):
                    new_row[a] = temp[a].values[0]
            self.factions = self.factions.append(new_row, ignore_index=True).fillna(0)
        else:  # Not a Valid Class
            print('Invalid Class Choice')
        # fix faction levels
        self.calculatelevels_faction()  # fix initial values
        new_row = {'Faction':Name, 'Level':self.factions[self.factions['Name']==Name]['Level'].values[0]}
        self.save_level = self.save_level.append(new_row, ignore_index=True).fillna(0)
            
    def edit_faction(self,faction,Property,value):
        '''
        Changes Property to Value
        '''
        self.factions.loc[self.factions[self.factions['Name']==faction].index[0],Property] = value
        
    def calculatelevels_faction(self):
        '''
        Fix the levels by:
            1 getting levels of strongholds by faction
            multiplying by vassalage
            adding together
            appending new value
        '''
        base = self.strongholds[['Faction','Level']].groupby('Faction').sum().reset_index()
        vassal = pd.merge(self.vassalage_checked,base,on='Faction',how='left')
        vassal['Add'] = np.ceil(vassal['Weight']*vassal['Level'])
        vassal = vassal[['Lord','Add']].groupby('Lord').sum().reset_index()
        vassal['Faction'] = vassal['Lord']
        vassal['Level'] = vassal['Add']
        new = pd.concat([base,vassal[['Faction','Level']]]).groupby('Faction').sum().reset_index()
        new['Level'] = new['Level'].astype(int)
        new['Name'] = new['Faction']
        new = new[['Name','Level']]
        lst = list(self.factions.keys())
        lst2 = lst.copy()
        lst.remove('Level')
        self.factions = pd.merge(self.factions[lst],new,on='Name',how='left').fillna(0)
        self.factions['Level'] = self.factions['Level'].astype(int)
        self.factions = self.factions[lst2]
        
        
    def remove_faction(self, faction):
        '''
        Removes the faction from all tables.
        '''
        # Faction Table
        self.factions = self.factions[self.factions['Name'] != faction].reset_index(drop=True)
        
        # Vassalage
        self.vassalage = self.vassalage[self.vassalage['Faction'] != faction].reset_index(drop=True)
        self.vassalage = self.vassalage[self.vassalage['Lord'] != faction].reset_index(drop=True)
        self.check_vassalage()  # fix vassalage in case this faction was a link
        
        # Strongholds
        self.strongholds = self.strongholds[self.strongholds['Faction'] != faction].reset_index(drop=True)
        
        # Relationships
        self.relationships = self.relationships[self.relationships['Faction'] != faction].reset_index(drop=True)
        self.relationships = self.relationships[self.relationships['Other'] != faction].reset_index(drop=True)
        
    #   ---   STRONGHOLD FUNCTIONS   ---
    def add_stronghold(self, Faction, Area, Type, Name, Level=0):
        '''
        Add a stronghold to the area
        '''
        if self.strongholds[self.strongholds['Name']==Name].shape[0] > 0:
            # print('Invalid Name (add_stronghold): {}'.format(Name))
            return False
        new_row = {'Name':Name, 'Area':Area, 'Type':Type, 'Faction':Faction, 'Level':Level, 'Sieged':0}
        ## Valid?
        if self.stronghold_types[self.stronghold_types['Stronghold']==Type].shape[0] == 1: # and self.factions[self.factions['Name']==Faction].shape[0] == 1 and self.areas[self.areas['Area']==Area].shape[0] == 1:
            # con bonus 
            con_bonus = int(self.factions[self.factions['Name']==Faction]['Con']/2-5)
            new_row['Hit Points'] = int(self.stronghold_types[self.stronghold_types['Stronghold']==Type]['HP'] + Level*con_bonus)
            self.strongholds = self.strongholds.append(new_row, ignore_index=True).fillna(0)
        else:
            print('Not a Valid Entry')
            
    def edit_stronghold(self,name,Property,value):
        '''
        Changes Property to Value
        '''
        self.strongholds.loc[self.strongholds[self.strongholds['Name']==name].index[0],Property] = value
        
    def drop_stronghold(self,name):
        '''
        remove a stronghold and fix tables
        '''
        if self.strongholds[self.strongholds['Name']==name].shape[0] == 1:
            self.strongholds = self.strongholds.drop([self.strongholds[self.strongholds['Name']==name].index[0]])
            self.strongholds = self.strongholds.reset_index(drop=True)
        else:
            print('Invalid name: {}'.format(name))
            
    def generate_stronghold_name(self, Faction, Culture, Area, Type, Terrain, Settlement, Stronghold):
        '''
        Generate names for Strongholds
        '''
        try:
            suffix = pd.read_csv('data/{}_{}_suffix.csv'.format(Culture,Type))
        except:
            suffix = pd.read_csv('data/castle_suffix.csv')
        try:
            prefix = pd.read_csv('data/{}_{}_prefix.csv'.format(Culture,Type))
        except:
            prefix = pd.read_csv('data/castle_prefix.csv')

        lst = [Faction, Area, Terrain]
        if Settlement != '':
            lst.append(Settlement)
        PPP = lst[rand.randint(0,len(lst)-1)]
        
        unique = False
        while unique == False:
            name = prefix['Name'].values[rand.randint(0,prefix.shape[0]-1)] + suffix['End'].values[rand.randint(0,suffix.shape[0]-1)]
            unique = self.is_name_unique(name, Type)

        return name.replace('PPP',PPP).replace('DDD',Stronghold.lower()).replace('_',' ').title().replace("'S","'s")    
    
    def is_name_unique(self, Name, Type):
        '''
        helper function
        '''
        if Type == 'Settlment':
            temp = self.areas[self.areas['Settlement Name']==Name]
            if temp.shape[0] == 0:
                return True
        else:
            temp = self.strongholds[self.strongholds['Name']==Name]
            if temp.shape[0] == 0:
                return True
        return False
        
    #   ---   VASSALAGE FUNCTIONS   ---
    def check_vassalage(self):
        '''
        recalculate vassalage_checked to make sure level calculations are correct
        '''
        self.vassalage_checked = self.vassalage.copy()
        # direct vassalage
        self.vassalage_checked['Weight'] = 0.5
        # next step
        temp =  self.vassalage_checked.copy()
        temp['Weight'] = temp['Weight']/2
        temp =  self.vassalage_checked.copy()
        while temp.shape[0] > 0:
            temp['Weight'] = temp['Weight']/2
            temp = pd.merge(temp,self.vassalage,left_on='Lord',right_on='Faction',how='left').dropna()
            temp['Faction'] = temp['Faction_x']
            temp['Lord'] = temp['Lord_y']
            temp = temp[['Faction','Lord','Weight']]
            self.vassalage_checked = pd.concat([self.vassalage_checked,temp])
        self.vassalage_checked = self.vassalage_checked.reset_index(drop=True)
        self.vassalage_checked = self.vassalage_checked[['Faction','Lord','Weight']]
        
    def add_vassalage(self, faction, lord):
        '''
        adds vassalage, recalculates levels
        '''
        new_row = {'Faction':faction, 'Lord':lord}
        self.vassalage = self.vassalage.append(new_row, ignore_index=True).fillna(0).drop_duplicates()
        self.check_vassalage()
        self.calculatelevels_faction()
        
    def drop_vassalage(self, faction, lord):
        '''
        drop vassalage, assuming it exists
        '''
        A = self.vassalage[self.vassalage['Faction']!=faction]
        B = self.vassalage[self.vassalage['Faction']==faction]
        B = B[B['Lord']!=lord]
        self.vassalage = pd.concat([A,B]).reset_index(drop=True)
        
        # immediate effects
        self.check_vassalage()
        self.calculatelevels_faction()
        
    #   ---   AREA FUNCTIONS   ---
    def add_area(self, Area, Name, Terrain, Population, Waterway):
        '''
        Add a stronghold to the area
        '''
        magic = self.terrain[self.terrain['Terrain']==Terrain]['Magic'].values[0] - Population
        new_row = {'Area':Area, 'Settlement Name':Name, 'Terrain':Terrain, 'Population':Population, 'Magic':magic, 'Waterway':Waterway}
        lst = list(self.areas.keys())
        self.areas = self.areas.append(new_row, ignore_index=True).fillna('').reset_index(drop=True)

    def drop_area(self,name):
        '''
        remove a stronghold and fix tables
        '''
        if self.areas[self.areas['Area']==name].shape[0] == 1:
            self.areas = self.areas.drop([self.areas[self.areas['Area']==name].index[0]])
            self.areas = self.areas.reset_index(drop=True)
        else:
            print('Invalid Area: {}'.format(name))
            
    def edit_area(self,area,property,value):
        '''
        Changes Property to Value
        '''
        self.areas.loc[self.areas[self.areas['Area']==area].index[0],property] = value
    
    def calculate_magic(self):
        '''
        Resets the magic rating of the areas based on their populations
        '''
        lst = list(self.areas.keys())
        lst2 = lst.copy()
        lst2.remove('Magic')
        self.areas = pd.merge(self.areas[lst2], self.terrain[['Terrain','Magic']], on='Terrain',how='left').fillna(0)
        self.areas['Magic'] = (self.areas['Magic'] - self.areas['Population']).astype(int)
        self.areas = self.areas[lst]
        
    #   ---   RELATIONSHIP FUNCTIONS   ---
    def edit_relationship(self, faction, other, change):
        '''
        change relationship by the amount listed, adds row if no relationship found
        '''
        # valid factions
        if self.factions[self.factions['Name']==faction].shape[0]==0 or self.factions[self.factions['Name']==other].shape[0]==0:
            print('Factions must be valid: {} not in factions'.format({}))
        elif self.relationships[(self.relationships['Faction']==faction) & (self.relationships['Other']==other)].shape[0] == 0:  # row not there yet
            new_row = {'Faction':faction, 'Other':other, 'Relationship':change}
            self.relationships = self.relationships.append(new_row, ignore_index=True).fillna('').reset_index(drop=True)
        else:
            self.relationships.loc[self.relationships[(self.relationships['Faction']==faction) & (self.relationships['Other']==other)].index[0],'Relationship'] = self.relationships.loc[self.relationships[(self.relationships['Faction']==faction) & (self.relationships['Other']==other)].index[0],'Relationship'] + change
            
        self.relationships = self.relationships.groupby(['Faction','Other']).sum().reset_index()
        # make sure they are all in range
        A = self.relationships[self.relationships['Relationship']>2].copy()
        B = self.relationships[self.relationships['Relationship']<=2].copy()
        A['Relationship'] = 2
        self.relationships = pd.concat([B, A])
        A = self.relationships[self.relationships['Relationship']<-1].copy()
        B = self.relationships[self.relationships['Relationship']>=-1].copy()
        A['Relationship'] = -1
        self.relationships = pd.concat([B, A])
        
        
    # ---   GAME FUNCTIONS  ---
    def get_revenue(self):
        '''
        Add up all stronghold Revenues, All Fealty Payments to the Faction.
        Subtract all Upkeeps, Lieutenants, and Fealty Payments.  
        
        If Positive, Faction gains that much gold.  
        If Negative, remove Lieutenants 1 at a time until Revenue is no longer negative or the Faction no longer has Lieutenants.  
        If still negative, remove all Level 0 strongholds.  
        If still negative, reduce ability scores 1 at a time, randomly, until Revenue is no longer negative.
       
        '''
        revenue = self.calculate_revenue()
        check = revenue[revenue['Revenue']<0]
        if check.shape[0]>0:
            while check.shape[0]>0:
                stronghold_check = pd.merge(revenue[['Faction']], self.strongholds[['Name','Faction','Level']], on='Faction',how='left')
                stronghold_check = stronghold_check[stronghold_check['Level']==0]
                for i, row in check.iterrows():
                    # fire a lieutenant
                    # get scores
                    scores = pd.merge(check[['Faction']],
                                      self.factions[['Name','Str','Dex','Con','Int','Wis','Cha']],
                                      left_on='Faction',right_on='Name',how='left')
                    scores['check'] = scores['Str']+scores['Dex']+scores['Con']+scores['Int']+scores['Wis']+scores['Cha'] - 60
                    if row['Lieutenants'] < 0:
                        lst = ['Athletics', 'Acrobatics', 'Stealth', 'Arcana', 'Investigation', 'Religion', 'Perception', 'Persuasion']
                        temp = self.factions[self.factions['Name']==row['Faction']].copy()
                        fclass = temp['Class'].values[0]
                        temp = temp[lst]
                        temps = self.faction_classes[self.faction_classes['Name']==fclass].copy()[lst]
                        lst2 = []
                        for a in lst:
                            if temps[a].values[0] != 1 and temp[a].values[0] > 0:
                                lst2.append(a)
                        if len(lst2)>0:
                            layoff = lst2[rand.randint(0,len(lst2)-1)]
                        else:
                            layoff = lst[rand.randint(0,len(lst)-1)]
                        self.edit_faction(row['Faction'],layoff,0)
                    elif stronghold_check[stronghold_check['Faction']==row['Faction']].shape[0] > 0:
                        # we have a level 0 stronghold and debt...
                        self.drop_stronghold(stronghold_check[stronghold_check['Faction']==row['Faction']]['Name'].values[-1])
                    elif scores.shape[0] > 0 and scores[scores['Faction']==row['Faction']]['check'].values[0] > 0:
                        lst = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
                        temp = pd.merge(self.factions[self.factions['Name']==row['Faction']][['Name', 'Class']+lst]
                                     ,self.faction_classes[['Name']+lst]
                                     ,left_on='Class', right_on='Name', how='left')
                        lst2 = []
                        for a in lst:
                            for b in range(temp[a+'_x'].values[0]):
                                lst2.append((a,temp[a+'_x'].values[0]))
                        if len(lst2) > 0:
                            tup = lst2[rand.randint(0,len(lst)-1)]
                            if tup[1] <= 20:
                                self.edit_faction(row['Faction'],tup[0],tup[1]-1)
                            else:
                                self.edit_faction(row['Faction'],tup[0],19)
                    else:  # drop a stronghold
                        sholds = self.strongholds[self.strongholds['Faction']==row['Faction']].sort_values('Level')
                        if sholds.shape[0]>0:
                            self.drop_stronghold(sholds['Name'].values[0])
                        else:
                            self.remove_faction(row['Faction'])

                    revenue = self.calculate_revenue()
                    check = revenue[revenue['Revenue']<0]
                    #check = pd.merge(revenue,self.factions[['Name','Gold']], left_on='Faction', right_on='Name')
                    #check = check[check['Gold']+check['Revenue'] <0]
            # Update the gold for Each Faction
            lst = list(self.factions.keys())
            temp = pd.merge(self.factions, revenue[['Faction','Revenue']], left_on='Name', right_on='Faction',how='left')
            temp = temp.fillna(0)
            temp['Gold'] = (temp['Gold'] + temp['Revenue']).astype(int)
            temp['Gold'] = temp['Gold'].astype(int)
            self.factions = temp[lst]
            self.factions = self.factions.drop_duplicates().reset_index(drop=True)
        return revenue
               
    def calculate_revenue(self):
        '''
        Add up all stronghold Revenues, All Fealty Payments to the Faction.
        Subtract all Upkeeps, Lieutenants, and Fealty Payments.
        '''
        # calculate revenue
        calculation = pd.merge(self.strongholds[['Faction','Level']], self.population[['Level','Revenue']],on='Level',how='left').groupby('Faction').sum().reset_index()
        temp = pd.merge(self.strongholds[['Faction','Type','Level']], self.stronghold_types[['Stronghold','Upkeep']],left_on='Type', right_on='Stronghold',how='left')
        # adjust upkeep by faction stats
        temp2 = self.factions.copy()
        temp2['Stats'] = temp2['Str'] + temp2['Dex'] + temp2['Con'] + temp2['Int'] +temp2['Wis'] + temp2['Cha'] - 60
        temp2['Faction'] = temp2['Name']
        temp2 =  temp2[['Faction','Stats']]
        temp = pd.merge(temp,temp2,on='Faction',how='left')
        temp['check'] = -1*temp['Upkeep']/2
        temp['adj'] = temp['Level']*temp['Level']*temp['Stats']*temp['Stats']
        # make sure weak factions don't profit too much from selling things off...
        A = temp[temp['adj'] < temp['check']].copy()
        B = temp[temp['adj'] >= temp['check']].copy()
        A['adj'] = A['check']
        temp = pd.concat([A,B])
        temp['Upkeep'] = (temp['Upkeep'] + temp['adj']).astype(int)
        temp = temp[['Faction','Upkeep','adj']].groupby('Faction').sum().reset_index()
        temp['Upkeep'] = temp['Upkeep']  *-1
        calculation = pd.merge(calculation, temp, on='Faction')
        # tithes to lords from vassals
        calculation['Tithe'] = (calculation['Revenue']*0.1).astype(int)
        calculation['Revenue'] = calculation['Revenue']+calculation['Upkeep']
        calculation = calculation[['Faction','Revenue','Tithe']]
        temp = pd.merge(self.vassalage,calculation,on='Faction',how='left')
        temp['Add'] = temp['Tithe']
        temp['Sub'] = -1*temp['Tithe']
        calculation = pd.merge(calculation,temp[['Faction', 'Sub']].groupby(['Faction']).sum().reset_index(), on='Faction',how='left').fillna(0)
        temp['Faction'] = temp['Lord']
        calculation = pd.merge(calculation,temp[['Faction', 'Add']].groupby(['Faction']).sum().reset_index(), on='Faction',how='left').fillna(0)
        calculation['Revenue'] = (calculation['Revenue'] + calculation['Add'] + calculation['Sub']).astype(int)
        calculation = calculation[['Faction','Revenue']]
        # lieutenants
        temp = pd.merge(self.factions, self.faction_classes,left_on='Class',right_on='Name',how='left')
        lst = ['Athletics', 'Acrobatics', 'Stealth', 'Arcana', 'Investigation', 'Religion', 'Perception', 'Persuasion']
        temp['Lieutenants'] = 0
        for a in lst:
            temp['Lieutenants'] = temp['Lieutenants'] + temp[a+'_y'] - temp[a+'_x']
        temp['Lieutenants'] =  temp['Lieutenants']*180
        temp['Faction'] = temp['Name_x']
        calculation = pd.merge(calculation,temp[['Faction','Lieutenants']].groupby(['Faction']).sum().reset_index(), on='Faction',how='left').fillna(0)
        calculation['Revenue'] = calculation['Revenue'] + calculation['Lieutenants']
        return calculation
    
        
    def make_decision(self, state, over=None):
        '''
        Have the Agent do a thing to make a decision.
        '''
        N = self.agent.action_size
        
        
        bonus = []
        action = []
        for i, row in state.iterrows():
            # get Int modifier
            mod = (self.factions[self.factions['Name']==row['Faction']]['Int'].values[0]-10)/2
            # predict action based on the old state
            prediction = self.agent.model.predict(np.transpose(np.array(row['State'])).reshape((1,self.agent.action_size)))
            roll = rand.randint(1, 20)   
            if roll < self.IntDC:   #Fails a dc 5 int check and does something random
                move = (to_categorical(rand.randint(0, 18), num_classes=N),to_categorical(rand.randint(19, 33), num_classes=N))
            else:
                move =  (to_categorical(np.argmax(prediction[0][:18]), num_classes=N),
                         to_categorical(np.argmax(prediction[0][19:]) + 19, num_classes=N))
            bonus.append(move[0])
            action.append(move[1])
        state['Bonus'] = bonus
        state['Action'] = action
        return state
        
    def roll_skill(self, Faction, Skill):
        '''
        Rolls Skill for Faction.  
        Advantage -1 = disadvantage, 
                   1 = advantage,
                   0 = normal (default)
        '''
        # set skill-ability thing
        dct = {}
        dct['Athletics']='Str'
        dct['Acrobatics']='Dex'
        dct['Stealth']='Dex'
        dct['Arcana']='Int'
        dct['Investigation']='Int'
        dct['Religion']='Int'
        dct['Perception']='Wis'
        dct['Persuasion']='Cha'
        
        # get ability mod
        ability = int((self.factions[self.factions['Name']==Faction][dct[Skill]].values[0]-10)/2)
        
        # get skill mod
        temp = pd.merge(self.factions, self.level_modifiers,left_on='Level',right_on='Faction Level',how='left').fillna(0)
        temp_ = temp[temp['Level']>20].copy()
        temp_['Skill Modifier'] = 6
        temp = pd.concat([temp[temp['Level']<=20],temp_])
        temp['mod'] = temp[Skill]*temp['Skill Modifier']
        mod = int(temp[temp['Name']==Faction]['mod'].values[0])
        
        roll = rand.randint(1,20)
        return roll + mod + ability
    
    def roll_opposed_skill(self, skills, factions):
        '''
        Rolls opposed skill and picks winner, loser
        '''
        lst = []
        for i, Faction in enumerate(factions):
            if type(skills) == str:
                skill = skills
            else:
                skill = skills[i]
            rolls = [0,0]
            rolls[0] = self.roll_skill(Faction, skill)
            temp = self.espionage[self.espionage['Faction']==Faction]
            if temp.shape[0]>0:
                for i, row in temp.iterrows():
                    if row['Target'] in factions:
                        rolls[1] = self.roll_skill(Faction, skill)
            lst.append((Faction, max(rolls)))
            lst.sort(key=lambda x:x[1])
        return lst[-1][0], lst[0][0], lst
        
    def contest_levels(self, Area, Type):
        '''
        When the combined power in a given category exceeds the maximum power of the category for 
        the area, a contest occurs.  All involved roll a Skill Check, lowest roll loses a point of 
        power in that area.  Continues until the combined power level is at the maximum.  

        Table: Contests by Type
        Type
        Skill Contest
        Guildhall
        Charisma (Persuasion)
        Temple
        Wisdom (Religion)
        Monasteries
        Charisma (Persuasion)
        Mystical (based on Caster Score)
        Intelligence, Wisdom, or Charisma (Arcana)*


        '''
        # get number
        Goal = self.areas[self.areas['Area']==Area]['Population'].values[0]
        skill = 'Persuasion'

        if Type == 'Mystic':
            skill = 'Arcana'
            Goal = self.areas[self.areas['Area']==Area]['Magic'].values[0]

        if Type == 'Temple':
            skill = 'Religion'

        temp = pd.merge(self.strongholds[self.strongholds['Area']==Area],
                        self.stronghold_types[self.stronghold_types['Type']==Type][['Stronghold']],
                        left_on='Type', right_on='Stronghold', how='left').dropna()



        while np.sum(temp['Level']) > Goal:
            factions = temp[['Faction']].drop_duplicates()
            _, loser, _ = self.roll_opposed_skill(skill, list(factions['Faction']))
            level = temp[temp['Faction']==loser]['Level'].values[0]
            name = temp[temp['Faction']==loser]['Name'].values[0]
            self.edit_stronghold(name, 'Level', level-1)
            temp = pd.merge(self.strongholds[self.strongholds['Area']==Area],
                        self.stronghold_types[self.stronghold_types['Type']==Type][['Stronghold']],
                        left_on='Type', right_on='Stronghold', how='left').dropna()

    
    #   ---   BONUS ACTIONS   ---
    def bonus_build_road(self, faction, area=None, target=None):
        '''
        Builds a road from one area where you have strongholds to another where none exist
        '''
        temp = pd.merge(self.strongholds[self.strongholds['Faction']==faction][['Area']].drop_duplicates(),self.geography,on='Area',how='left')
        temp = temp[temp['Road/Port']==0]

        # reduce to choices
        if area != None:
            temp = temp[temp['Area']==area]    
        if target != None:
            temp = temp[temp['Neighbor']==area]

        # make sure we have no nans
        temp = temp.dropna()

        # assign if NPC
        if temp.shape[0] > 0:
            if area == None or target == None:
                selection = temp.values[rand.randint(0,temp.shape[0]-1)]
                area = selection[0]
                target = selection[1]

        if temp.shape[0] > 0:
            # costs 500 gold
            gold = self.factions[self.factions['Name']==faction]['Gold'].values[0]
            if gold>=500:
                new_row = {'Area':area,'Neighbor':target}
                self.new_roads = self.new_roads.append(new_row, ignore_index=True).fillna(0)
                new_row = {'Area':target,'Neighbor':area}
                self.new_roads = self.new_roads.append(new_row, ignore_index=True).fillna(0)
                # pay the 500
                self.edit_faction(faction,'Gold',gold-500)
                return 'Build Road: Built a road/port from {} to {}'.format(area,target)
        return 'Build Road: Failed to build a road'
        
    def bonus_diplomacy(self, Faction, Target):
        '''
        Attempt to get in better with another Faction.  
        Make a Financial gift of 500 gp and roll a DC 15 Charisma (Persuasion) check.  
        If successful, they shift from Hostile -> Indifferent or Indifferent -> Friendly.

        '''
        gold = self.factions[self.factions['Name']==Faction]['Gold'].values[0]
        if gold >= 500:
            other_gold = self.factions[self.factions['Name']==Target]['Gold'].values[0]
            self.edit_faction(Faction,'Gold',gold-500)
            self.edit_faction(Target,'Gold',other_gold+500)
            if self.roll_skill(Faction,'Persuasion') > 15:
                self.edit_relationship(Target, Faction, 1)
                return "Diplomacy: Improved relations with {}".format(Target)
        return 'Diplomacy: Failed to Improve Relations with {}'.format(Target)
        
    def bonus_hire_lieutenant(self, Faction, Skill):
        '''
        Hire Lieutenant (Bonus Action)
        hire_general (athletics)
        hire_architect (acrobatics)
        hire_spymaster (stealth)
        hire_arcanist (Arcana)
        hire_inquisiter (investigation)
        hire_hierophant (religion)
        hire_musicians (Perception)
        hire_diplomat (Persuasion)
        Costs 180 gp.
        '''
        dct = {'Athletics':'a General', 'Acrobatics':'an Architect', 'Stealth':'a Spymaster', 'Arcana':'an Arcanist',
               'Investigation':'an Inquisitor', 'Religion':'a Hierophant', 'Perception':'some musicians',
               'Persuasion':'a Diplomat'}
        row = self.factions[self.factions['Name']==Faction]
        skill = row[Skill].values[0]
        gold = row['Gold'].values[0]
        
        if gold >= 180 and skill == 0:
            self.edit_faction(Faction,'Gold', gold-180)
            self.edit_faction(Faction, Skill, 1)
            return 'Hire Lieutenant: Hired {} ({})'.format(dct[Skill],Skill)
        return 'Hire Lieutenant: Failed to hire {} ({})'.format(dct[Skill],Skill)
        
    def bonus_increase_ability(self, Faction, Ability):
        '''
        Increase Ability Score (Bonus Action)
        hire_soldiers
        hire_scouts
        hire_engineers
        hire_sages
        lower_taxes
        hire_staff
        Up an ability score.  Costs 100*new value.
        '''
        dct = {'Str':'Hired soldiers', 'Dex':'Hired scouts', 'Con':'Hired engineers',
               'Int':'Hired sages', 'Wis':'Lowered taxes/tithes/dues', 'Cha':'Hired more staff & spent more on decor'}
        row = self.factions[self.factions['Name']==Faction]
        gold = row['Gold'].values[0]
        score = row[Ability].values[0]
        cost = int(100*(score+1))
        if gold >= cost:
            self.edit_faction(Faction,'Gold',gold-cost)
            self.edit_faction(Faction,Ability,score+1)
            return 'Increase Ability: {} ({} to {})'.format(dct[Ability],Ability,score+1)
        return 'Increase Ability: Failed to raise {} to {}'.format(Ability,score+1)
    
    def bonus_repair_strongholds(self, Faction):
        '''
        A stronghold can be repaired by spending 1/10th the building cost 
        to roll 1 hit dice + Constitution Modifier to make repairs that Season.

        '''
        # gather info
        temp = pd.merge(self.strongholds[self.strongholds['Sieged']==0],self.factions[['Name','Con','Gold']],left_on='Faction',right_on='Name',how='left')
        temp = pd.merge(temp,self.stronghold_types[['Stronghold','HP','Cost','Hit Dice']],left_on='Type',right_on='Stronghold',how='left')
        temp['Max HP'] = temp['HP'] + temp['Level']*((temp['Con']-10)/2).astype(int)
        temp = temp[temp['Hit Points']<temp['Max HP']]
        temp['Repair Cost'] = temp['Cost']/10
        temp['HD'] = temp['Hit Dice'].str.split('d')
        temp = temp[temp['Faction']==Faction]
        lst = []
        if temp.shape[0]>0:
            gold = temp['Gold'].values[0]
            for i, row in temp.iterrows():
                hd = int(row['HD'][1])
                repair_cost = int(row['Repair Cost'])
                bonus = int((row['Con']-10)/2)
                hp = int(row['Hit Points'])
                max_hp = int(row['Max HP'])
                hp = hp + rand.randint(1,hd) + bonus
                if hp > max_hp:
                    hp = max_hp
                if gold >= repair_cost:
                    gold = gold - repair_cost
                    self.edit_faction(Faction,'Gold',gold)
                    self.edit_stronghold(row['Name_x'],'Hit Points',hp)
                    lst.append(row['Name_x'])
        
        if len(lst) > 0:
            return 'Repair Strongholds: Repaired {}'.format(', '.join(lst))
        else:
            return 'Repair Strongholds: None.'
    
    def bonus_action_spy(self, Faction, Target):
        '''
        Make a Dexterity (Stealth) vs Wisdom (Perception) roll. 
        If successful, you have Advantage on an opposed roll you make as an action this season.  
        An opposed Dexterity (Stealth) vs Intelligence (Investigation) roll allows them to know it was you.
        '''
        mystring = 'Spy:'
        if self.roll_skill(Faction,'Stealth') > self.roll_skill(Faction,'Perception'):
            new_row = {'Faction':Faction, 'Target':Target}
            self.espionage = self.espionage.append(new_row, ignore_index=True).fillna(0).drop_duplicates()
            mystring = mystring + ' Spied on {}'.format(Target)
        else:
            mystring = mystring + ' Failed to Spy on {}'.format(Target)
        if self.roll_skill(Faction,'Investigation') > self.roll_skill(Faction,'Stealth'):
            self.edit_relationship(Target, Faction, -1)
            mystring = mystring + ' and got caught!'
        return mystring
    
    def action_build_stronghold(self, Faction, Stronghold, Location=None, Name=None, Settlement=None):
        '''
        Build or Expand stronghold (Action)
        Build_castle_1
        build_castle_2
        build_castle_3
        build_guild
        build_temple_1
        build_temple_3
        build_monestary
        build_mystic

        Builds a stronghold.  No roll needed, just money.  If this is an upgrade to a 
        current stronghold, the payment and time is the difference as the current building 
        is incorporated into the new one.  Must either be the first stronghold built OR 
        must have a stronghold adjacent to the area in which a stronghold will be built.
        '''
        if self.strongholds[self.strongholds['Faction']==Faction].shape[0] > 0:
            temp1 = self.strongholds[['Faction','Area']].copy()
            temp1['Neighbor'] = temp1['Area']
            if Stronghold not in ['Tower','Circle']:  # Mystic has no road restriction
                temp = pd.merge(self.strongholds[['Faction','Area']],self.geography[self.geography['Road/Port']==1][['Area','Neighbor']])
            else:
                temp = pd.merge(self.strongholds[['Faction','Area']],self.geography[['Area','Neighbor']])
            temp = pd.concat([temp,temp1])
            temp = temp[temp['Faction']==Faction].copy()
            temp = pd.merge(temp,self.strongholds[['Area','Type','Faction','Level']], left_on=['Neighbor','Faction'], right_on=['Area','Faction'], how='left').fillna('')
            areas = self.areas[self.areas['Waterway']==0][['Area','Population','Magic']].copy()
            temp = pd.merge(temp,areas,left_on='Neighbor',right_on='Area',how='inner')
        else:  # Any area will do
            temp = pd.merge(self.strongholds[['Faction','Area']],self.geography[['Area','Neighbor']])
            temp = pd.merge(temp,self.strongholds[['Area','Type','Faction','Level']], left_on=['Neighbor','Faction'], right_on=['Area','Faction'], how='left').fillna('')
            areas = self.areas[self.areas['Waterway']==0][['Area','Population','Magic']].copy()
            temp = pd.merge(temp,areas,left_on='Neighbor',right_on='Area',how='inner')

        # make sure they don't already have a thing there
        nolst = list(set(temp[temp['Type']==Stronghold]['Neighbor']))
        if Stronghold == 'Small Temple':
            nolst = list(set(nolst +  list(temp[temp['Type']=='Large Temple']['Neighbor'])))
        if Stronghold in ['Manor', 'Keep', 'Castle']:  # Castle Stuff
            if Stronghold == 'Manor' or Stronghold == 'Keep':
                nolst = list(set(nolst +  list(temp[temp['Type']=='Keep']['Neighbor']) + list(temp[temp['Type']=='Palace']['Neighbor'])))
            # check for castles in these areas already...
            temp1 = pd.merge(self.strongholds,temp['Area'].drop_duplicates(),on='Area',how='left')
            temp1 = pd.concat([temp1[
            temp1['Type']==a] for a in ['Manor', 'Keep', 'Castle']])
            temp1 = temp1[temp1['Faction'] != Faction]
            [nolst.append(a) for a in list(temp1['Area'])]
        elif Stronghold in ['Tower','Circle']:  # Magic needs Magic
            [nolst.append(a) for a in list(temp[temp['Magic']==0]['Neighbor'])]
        else:  # must be a temple, guild, or monastary, which means there needs to be people there
            [nolst.append(a) for a in list(temp[temp['Population']==0]['Neighbor'])]
        
        # make sure I didn't already start a project there...
        concheck = self.construction[self.construction['Faction']==Faction]
        concheck = concheck[concheck['Type']==Stronghold]
        if concheck.shape[0] > 0:
            [nolst.append(a) for a in list(concheck['Area'])]
            
        if len(nolst) > 0:
            for a in nolst:
                temp = temp[temp['Neighbor']!=a]
        lst = list(set(temp['Neighbor']))
        if Location == None and len(lst) > 0:
            Location = lst[rand.randint(0,len(lst)-1)]
        if Location not in lst:
            return 'Build {}: Failed to find a location.'.format(Stronghold)
        else:   
            temp = self.stronghold_types[self.stronghold_types['Stronghold']==Stronghold]
            cost = temp['Cost'].values[0]
            seasons = temp['Build Time'].values[0]
            stype = temp['Type'].values[0]
            temp = self.factions[self.factions['Name']==Faction]
            gold = temp['Gold'].values[0]
            
            # check if its an upgrade to an existant structure
            if Stronghold in ['Large Temple', 'Keep', 'Palace']:
                upgrade = self.strongholds[self.strongholds['Faction']==Faction]
                upgrade = pd.concat([upgrade[upgrade['Type']==a] for a in ['Small Temple', 'Manor', 'Keep']])
                temp1 = self.construction[self.construction['Faction']==Faction]
                temp1 = pd.concat([temp1[temp1['Type']==a] for a in ['Small Temple', 'Manor', 'Keep']])
                upgrade['Seasons'] = 0
                upgrade = pd.concat([upgrade[['Faction', 'Area', 'Type', 'Name', 'Seasons']], temp1])
                upgrade = pd.merge(upgrade, self.stronghold_types[['Stronghold','Cost','Build Time']], left_on='Type', right_on='Stronghold', how='left')
                upgrade = upgrade[upgrade['Area']==Location]
                upgrade['Subtract'] = upgrade['Build Time'] - upgrade['Seasons']
                if Stronghold == 'Large Temple':
                    upgrade = upgrade[upgrade['Type']=='Small Temple']
                else:
                    upgrade = upgrade[upgrade['Type']=='Small Temple']
                if upgrade.shape[0]>0:
                    cost = cost - np.sum(upgrade['Cost'])
                    seasons = seasons - np.sum(upgrade['Subtract'])

            
            if gold >= cost:
                culture = temp['Culture'].values[0]
                temp = self.areas[self.areas['Area']==Location]
                settlement = temp['Settlement Name'].values[0]
                terrain = temp['Terrain'].values[0]
                if settlement == '':
                    # name The Settlement
                    if Settlement == None:
                        settlement = self.generate_stronghold_name(Faction, culture, Location, 'Settlement', terrain, settlement, Stronghold)
                    else:
                        settlement = Settlement  # allows humans to name their own          
               
                # Name it
                if Name == None:
                    Name = self.generate_stronghold_name(Faction, culture, Location, stype, terrain, settlement, Stronghold)
                # pay for it
                self.edit_faction(Faction, 'Gold', int(gold-cost))
                # add it to build list
                new_row = {'Faction':Faction, 'Area':Location, 'Type':Stronghold, 'Name':Name,'Seasons':seasons}
                self.construction = self.construction.append(new_row, ignore_index=True)
                return 'Build {}: Built {} in {} ({}).'.format(Stronghold, Name, settlement, Location)
            else:
                return 'Build {}: Not enough gold.'.format(Stronghold)
                
                
    def action_expand_stronghold(self,Faction,Stronghold=None,Target=None):
        '''
        Increase stronghold Power (Action)
        expand_weakest_stronghold
        expand_stronghold_near_enemy
        This raises the value of a stronghold.  This has a gold cost and a Charisma (Persuasion) check DC.  
        This may also lead to contestments.  A stronghold may only be raised one point at a time.  
        A Castle stronghold’s Power Level raises the Population if the new power level would be larger 
        than the population.  Stronghold must be able to accommodate the new Power Level.
        
        Target should not be used by players, since this will lead to failures for no reason.

        '''
       
        temp = pd.merge(self.strongholds[self.strongholds['Faction']==Faction],self.areas,on='Area',how='left')
        if Target != None:  # targeting enemy
            temp = pd.merge(self.strongholds[self.strongholds['Faction']==Faction],self.areas,on='Area',how='left')
            temp1 = pd.merge(self.strongholds[self.strongholds['Faction']==Target]['Area'],self.geography, on='Area', how='left')
            temp2 = temp1.copy()
            temp1['Area'] = temp1['Neighbor']
            temp1 = pd.concat([temp1, temp2]).drop_duplicates()
            temp = pd.merge(temp1['Area'], temp, on='Area', how='left').dropna().drop_duplicates()
        temp = pd.merge(temp,self.stronghold_types, left_on='Type', right_on='Stronghold', how='left')
        types = ['Castle', 'Guild','Temple','Monastery','Mystic']
        lst = [temp[temp['Type_y']==a] for a in types]
        for n in [1,2,3]:
            lst[n] = lst[n][lst[n]['Level']<lst[n]['Population']]
            lst[n] = lst[n][lst[n]['Level']<lst[n]['Max Level']]
        lst[4] = lst[4][lst[4]['Level']<lst[4]['Magic']]
        lst[4] = lst[4][lst[4]['Level']<lst[4]['Max Level']]
        lst[0] = lst[0][lst[0]['Level']<3]
        temp = pd.concat(lst).sort_values('Level')
        if Stronghold != None:
            temp = temp[temp['Name']==Stronghold]
        
        if temp.shape[0]>0:
            if Stronghold == None:  # pick one!
                Stronghold = temp['Name'].values[0]
            # check gold
            gold = self.factions[self.factions['Name']==Faction]['Gold'].values[0]
            level = self.strongholds[self.strongholds['Name']==Stronghold]['Level'].values[0]
            cost = 100 * level * level

            if gold>cost:
                # can afford it
                self.edit_faction(Faction, 'Gold', int(gold-cost))  # spend it
                if self.roll_skill(Faction, 'Persuasion') > [0,10,13,15][level]:  # roll it
                    self.edit_stronghold(Stronghold,'Level',level+1)
                    return "Expand Stronghold: Raised {} to {}".format(Stronghold,int(level+1))
            return 'Expand Stronghold: Failed to Expand {}'.format(Stronghold)    

        return 'Expand Stronghold: Nothing to Expand'
    
    def action_rob_faction(self, Faction, Target):
        '''
        Make a Dexterity (Stealth) vs Wisdom (Perception) roll.  
        If successful, target losses 100 * your power level * the roll difference in gold, and you gain the same amount.  
        An opposed Dexterity (Stealth) vs Intelligence (Investigation) roll allows them to know it was you.  
        Must have a stronghold in the same settlement as the faction to be robbed.

        '''
        # is target valid?
        temp = pd.merge(self.strongholds[self.strongholds['Faction']==Faction]['Area'].drop_duplicates(),
                    self.strongholds[self.strongholds['Faction']==Target], on='Area', how='left')
        if temp.shape[0] <= 0:
            return 'Rob Faction: {} does not have a Stronghold in the settlement'.format(Target)
        else:
            # robbery
            winner, loser, rolls = self.roll_opposed_skill(['Stealth', 'Perception'], [Faction, Target])
            ret = 'Rob Faction: '
            if winner == Faction:
                # robbed 'em'
                gold = self.factions[self.factions['Name']==Target]['Gold'].values[0]
                difference = rolls[-1][1] - rolls[0][1]
                level = self.factions[self.factions['Name']==Faction]['Level'].values[0]
                fgold = self.factions[self.factions['Name']==Faction]['Gold'].values[0]
                amount = 100*difference*level
                if amount > gold:  # can't steal what isn't there
                    amount = gold
                self.edit_faction(Target,'Gold',int(gold-amount))
                self.edit_faction(Faction,'Gold',int(fgold+amount))
                ret = ret + 'Stole {} gold from {}'.format(amount,Target)
            else:
                ret = ret + 'Failed to rob {}'.format(Target)
            # did they notice
            if self.roll_opposed_skill(['Stealth', 'Investigation'], [Faction, Target])[0] == Target:
                self.edit_relationship(Target,Faction,-1)
                ret = ret + " (and was caught)."
        return ret
        
    def action_sabotage_stronghold(self, Faction, Enemy =None, Target=None):
        '''
        Make a Dexterity (Stealth) vs Wisdom (Perception) roll. 
        If successful, the opponent’s stronghold is damaged by 1d6+Dexterity Modifier.  
        An opposed Dexterity (Stealth) vs Intelligence (Investigation) roll allows them to know it was you.  
        
        Must have a stronghold in a settlement adjacent to a settlement in which the stronghold exists.


        '''
        # is there a target?
        if Target==None:
            temp = pd.merge(self.strongholds[self.strongholds['Faction']==Faction]['Area'].drop_duplicates(),
                           self.geography, on='Area', how='left')
            hold = temp.copy()
            temp['Area'] = temp['Neighbor']
            temp = pd.merge(pd.concat([hold['Area'], temp['Area']]).drop_duplicates(),
                            self.strongholds[self.strongholds['Faction']==Enemy], on='Area', how='left').dropna().sort_values('Hit Points')
            if temp.shape[0] > 0:
                Target = temp['Name'].values[0]
        ret = 'Sabotage Stronghold: '
        if Target==None:
            ret = ret + 'No valid targets for {}'.format(Enemy)
        else:
            # is Target valid?
            temp = pd.merge(self.strongholds[self.strongholds['Faction']==Faction]['Area'].drop_duplicates(),
                               self.geography, on='Area', how='left')
            hold = temp.copy()
            temp['Area'] = temp['Neighbor']
            temp = pd.merge(pd.concat([hold['Area'], temp['Area']]).drop_duplicates(),
                            self.strongholds[self.strongholds['Name']==Target], on='Area', how='left').dropna()
           
            if temp.shape[0] == 0:
                ret = ret + "{} not a valid target."
            else:
                # have a target, and its valid...
                Enemy = temp['Faction'].values[0]
                if self.roll_opposed_skill(['Stealth', 'Perception'], [Faction, Enemy])[0] == Faction:
                    # got it, time for damage....
                    dex = int((self.factions[self.factions['Name']==Faction]['Dex']-10)/2)
                    damage = rand.randint(1,6) + dex
                    hp = self.strongholds[self.strongholds['Name']==Target]['Hit Points'].values[0]
                    self.edit_stronghold(Target,'Hit Points',hp-damage)
                    ret = ret + 'Damaged {}'.format(Target)
                else:
                    ret = ret + "Failed to damage {}".format(Target)
                if self.roll_opposed_skill(['Stealth', 'Investigation'], [Faction, Enemy])[0] == Enemy:
                    self.edit_relationship(Enemy,Faction,-1)
                    ret = ret + " (and was caught)."
        return ret

            
    def action_siege_stronghold(self,Faction,Target=None,Enemy=None):
        '''
        Attack an enemy stronghold.  
        The cost to launch a war is the enemy’s stronghold Level Squared times 100 
        (100 gp, 400 gp, or 900 gp).  Opposed checks are made (as if a Grapple Check).  
        If the Attacker wins, he lays siege to the enemy stronghold, doing damage based on 
        faction level.  A Sieged stronghold may not be repaired While the Siege lasts.  
        
        Must have a stronghold in a settlement adjacent to a settlement in which the sieged 
        stronghold exists (or have a follower adjacent)   
        '''
        # do I have a target?
        if Target == None:
            # get self and all vassals
            temp = self.vassalage_checked[self.vassalage_checked['Lord']==Faction]
            temp = temp.append({'Faction':Faction, 'Lord': Faction, 'Weight':1.0}, ignore_index=True)
            # find all areas adjacent to them
            temp = pd.merge(temp['Faction'],self.strongholds,on='Faction',how='left').dropna()[['Area']].drop_duplicates()
            temp = pd.merge(temp,self.geography,on='Area',how='left')
            temp1 = temp.copy()
            temp['Area'] = temp['Neighbor']
            temp = pd.concat([temp1[['Area']],temp[['Area']]]).drop_duplicates()
            # find all that the enemy has in those areas
            temp = pd.merge(self.strongholds[self.strongholds['Faction']==Enemy],temp,on='Area',how='left')
            if temp.shape[0]>0:
                Target = temp['Name'].values[0]
        if Target == None:
            return 'Siege Stronghold: {} has no stronghold near enough to attack.'.format(Enemy)
        else: #we have a target...
            gold = self.factions[self.factions['Name']==Faction]['Gold'].values[0]
            level = self.strongholds[self.strongholds['Name']==Target]['Level'].values[0]
            cost = level*level*100
            if gold < cost:
                return 'Siege Stronghold: Cannot afford to attack {}.'.format(Target)
            else:
                # drop fealty...
                self.drop_vassalage(Faction,self.strongholds[self.strongholds['Name']==Target]['Faction'].values[0])
                # make aggressive
                self.edit_relationship(Faction,self.strongholds[self.strongholds['Name']==Target]['Faction'].values[0],-3)
                
                self.edit_faction(Faction,'Gold',gold-cost)
                self.sieges = self.sieges.append({'Faction':Faction, 'Stronghold':Target}, ignore_index=True)
                self.edit_stronghold(Target,'Sieged',1)
                return 'Siege Stronghold: Laying siege to {}'.format(Target)
        return 'Siege Stronghold: Error.'
        
    def action_swear_fealty(self,Faction,Lord):
        '''
        Swear_to_strongest_ally
        swear_to_weakest_enemy
        
        You become a Vassal of another Faction.  1/10th of your Revenue goes to that faction, and they gain 
        power equal to half of your power level (round up).  
        
        '''
        # Make sure there isn't a loop...
        temp = self.vassalage_checked[self.vassalage_checked['Faction']==Lord]
        temp = temp[temp['Lord']==Faction]
        if temp.shape[0]>0:
            return "Swear Fealty: Cannot Swear Fealty to your own Vassal."
        
        # make sure they are not already your lord...
        temp = self.vassalage[self.vassalage['Faction']==Faction]
        temp = temp[temp['Lord']==Lord]
        if temp.shape[0] > 0:
            return "Swear Fealty: {} is already {}'s Lord".format(Lord,Faction)
        
        # this will annoy your current Lord, if you have one
        if self.vassalage[self.vassalage['Faction']==Faction].shape[0] > 0:
            temp = self.vassalage[self.vassalage['Faction']==Faction]
            self.edit_relationship(temp['Lord'].values[0],Faction,-1)
            self.drop_vassalage(Faction,temp['Lord'].values[0])
            if self.roll_skill(Faction,'Persuasion') < 10:  # chance they become enemies...
                self.edit_relationship(temp['Lord'].values[0],Faction,-2)
        
     
        # do the thing...
        self.edit_relationship(Lord,Faction,2)
        self.add_vassalage(Faction,Lord)
        return 'Swear Fealty: Is now a Vassal of {}'.format(Lord)
    
    #  --- SIEGE FUNCTIONS ---
    def handle_siege(self, Faction, Target):
        '''
        Opposed checks are made (as if a Grapple Check).  
        If the Attacker wins, he lays siege to the enemy stronghold, doing damage based on 
        faction level.  A Sieged stronghold may not be repaired While the Siege lasts.  
        
                    Faction Level
                    Siege Damage
                    1-4
                    1d6 + Strength Modifier
                    5-10
                    2d6 + Strength Modifier
                    11-16
                    3d6 + Strength Modifier
                    17+
                    4d6 + Strength Modifier

        '''
        Besieged = self.strongholds[self.strongholds['Name']==Target]['Faction'].values[0]
        
        # get which skill they'll use...
        lst = ['Level', 'Str', 'Dex', 'Athletics', 'Acrobatics']
        rlst = []
        for a in lst:
            rlst.append([a,self.factions[self.factions['Name']==Besieged][a].values[0]])
            
        # levels are limited
        if rlst[0][1] <=1:
            rlst[0][1] = 1
        if rlst[0][1] >= 21:
            rlst[0][1] = 20
        mod = self.level_modifiers[self.level_modifiers['Faction Level']==rlst[0][1]]['Skill Modifier'].values[0]
        rlst[3][1] = int((rlst[1][1]-10)/2) + mod*rlst[3][1]
        rlst[4][1] = int((rlst[2][1]-10)/2) + mod*rlst[4][1]
        if rlst[-2][1] > rlst[-1][1]:
            skill = rlst[-2][0]
        else:
            skill = rlst[-1][0]

        # make the check
        tup = self.roll_opposed_skill(['Athletics',skill], [Faction,Besieged])
        if tup[0] == Faction:  # attackers won!
            siegerlevel = self.factions[self.factions['Name']==Faction]['Level'].values[0]
            siegerstr = int((self.factions[self.factions['Name']==Faction]['Level'].values[0]-10)/2)
            damage = rand.randint(1,6) + siegerstr
            if siegerlevel >= 5:
                damage = damage + rand.randint(1,6)
            if siegerlevel >= 11:
                damage = damage + rand.randint(1,6)
            if siegerlevel >= 17:
                damage = damage + rand.randint(1,6)
            HP = self.strongholds[self.strongholds['Name']==Target]['Hit Points']
            self.edit_stronghold(Target,'Hit Points',int(HP - damage))
            return "{} Sieged {}".format(Faction, Target)
        else:
            self.edit_stronghold(Target,'Sieged',0)
            return "The Siege of {} was broken".format(Target)
    
    #   ---   RUN SEASON   ---
    def run_season(self, train=False, train_often=False, dc=None, done=False):
        '''
        Initiates a Season.
        
        current_season = working DF that determines order and holds actions for the final report.
        '''
        # Int DC
        if dc != None:
            self.IntDC = dc
        
        # iterate season
        self.season = self.season + 1
        
        # add Factions to the season list if not there already
        for i, row in self.factions.iterrows():
            if row['Name'] not in list(self.seasons['Faction']):
                self.seasons = self.seasons.append({'Faction':row['Name']}, ignore_index=True).fillna('')
        
        # get revenue
        revenue = self.get_revenue()
        
        # get state  STARTEWX
        state = self.agent.get_state()
        state = pd.merge(state, self.factions[['Name','Level']],left_on='Faction',right_on='Name', how='left').fillna(0)
        state = state[['Faction', 'Enemy', 'Ally', 'State', 'Level']]
        
        
        # save the things from last time...  CHECK ONCE YOU HAVE STUFF
        if self.last_season.shape[0]>0 and train == True:
            lst = list(state.keys())
            state['New State'] = state['State']
            state['New Level'] = state['Level']
            
            self.last_season = pd.merge(self.last_season,state[['Faction','New State', 'New Level']],on='Faction',how='left')
            temp = self.save_level.copy()
            temp['Original Level'] = temp['Level']
            self.last_season = pd.merge(self.last_season, temp[['Faction','Original Level']], on='Faction', how='left')
            self.last_season['Reward'] = self.last_season['New Level'] - self.last_season['Original Level']
            state = state[lst]
            # training...
            for i, row in self.last_season.iterrows():
                self.agent.remember(state=row['State'], action=row['Bonus'], reward=row['Reward'], next_state=row['New State'], done=done)
                self.agent.remember(state=row['State'], action=row['Action'], reward=row['Reward'], next_state=row['New State'], done=done)
            if train_often == True:
                self.agent.replay_new()
            
            self.last_season = self.last_season[lst]
        # determine actions
        state = self.make_decision(state)
        
        # save actions
        self.last_season = state
        
        # run actions.
        blst = []
        alst = []
        for i, row in state.iterrows():
            
            # Bonus Action
            bonus = np.argmax(row['Bonus'])
            # Action
            action = np.argmax(row['Action'])
            
            if bonus == 0:  # build_road
                blst.append(self.bonus_build_road(row['Faction']))
            elif bonus == 1:  # diplomacy_enemy
                blst.append(self.bonus_diplomacy(row['Faction'],row['Enemy']))
            elif bonus == 2:  # diplomacy_ally
                blst.append(self.bonus_diplomacy(row['Faction'],row['Ally']))
            elif bonus == 3:  # hire_general
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Athletics'))
            elif bonus == 4:  # hire_architect
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Acrobatics'))
            elif bonus == 5:  # hire_spymaster
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Stealth'))
            elif bonus == 6:  # hire_arcanist
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Arcana'))
            elif bonus == 7:  # hire_inquisitor
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Investigation'))
            elif bonus == 8:  # hire_hierophant
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Religion'))
            elif bonus == 9:  # hire_musicians
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Perception'))
            elif bonus == 10: # hire_diplomat
                blst.append(self.bonus_hire_lieutenant(row['Faction'],'Persuasion'))
            elif bonus == 11: # hire_soldiers
                blst.append(self.bonus_increase_ability(row['Faction'],'Str'))
            elif bonus == 12: # hire_scouts
                blst.append(self.bonus_increase_ability(row['Faction'],'Dex'))    
            elif bonus == 13: # hire_engineers
                blst.append(self.bonus_increase_ability(row['Faction'],'Con'))
            elif bonus == 14: # hire_sages
                blst.append(self.bonus_increase_ability(row['Faction'],'Int'))
            elif bonus == 15: # lower_taxes
                blst.append(self.bonus_increase_ability(row['Faction'],'Wis'))
            elif bonus == 16: # hire_staff
                blst.append(self.bonus_increase_ability(row['Faction'],'Wis'))
            elif bonus == 17: # repair_strongholds
                blst.append(self.bonus_repair_strongholds(row['Faction']))
            elif bonus == 18: # spy_enemy
                blst.append(self.bonus_action_spy(row['Faction'],row['Enemy']))
            
            #   ---   ACTIONS   ---
            if action == 19:  # build_manor
                alst.append(self.action_build_stronghold(row['Faction'], 'Manor'))
            elif action == 20:  # build_keep
                alst.append(self.action_build_stronghold(row['Faction'], 'Keep'))
            elif action == 21:  # build_palace
                alst.append(self.action_build_stronghold(row['Faction'], 'Palace'))
            elif action == 22:  # build_guild
                alst.append(self.action_build_stronghold(row['Faction'], 'Guildhall'))
            elif action == 23:  # build_small_temple
                alst.append(self.action_build_stronghold(row['Faction'], 'Small Temple'))
            elif action == 24:  # build_large_temple
                alst.append(self.action_build_stronghold(row['Faction'], 'Large Temple'))
            elif action == 25:  # build_abbey
                alst.append(self.action_build_stronghold(row['Faction'], 'Abbey'))
            elif action == 26:  # build_tower
                alst.append(self.action_build_stronghold(row['Faction'], 'Tower'))
            elif action == 27:  # expand_weakest_stronghold
                alst.append(self.action_expand_stronghold(row['Faction']))
            elif action == 28:  # expand_stronghold_near_enemy
                alst.append(self.action_expand_stronghold(row['Faction'], Target=row['Enemy']))
            elif action == 29:  # rob_enemy
                alst.append(self.action_expand_stronghold(row['Faction'], Target=row['Enemy']))
            elif action == 30:  # sabotage_stronghold
                alst.append(self.action_sabotage_stronghold(row['Faction'], Enemy=row['Enemy']))   
            elif action == 31:  # attack_enemy_stronghold
                alst.append(self.action_siege_stronghold(row['Faction'], Enemy=row['Enemy']))
            elif action == 32:  # swear_fealty_ally
                alst.append(self.action_swear_fealty(row['Faction'], row['Ally']))
            elif action == 33:  # swear_fealty_enemy
                alst.append(self.action_swear_fealty(row['Faction'], row['Enemy']))
        
        # save it for humans
        state['A'] = alst
        state['B'] = blst
        state['Season {}'.format(self.season)] = state['A'] + ' \n[' + state['B'] + ']'
        self.seasons = pd.merge(self.seasons, state[['Faction','Season {}'.format(self.season)]], on='Faction',how='left').fillna('')
        
        # Cleanup
        if self.new_roads.shape[0] > 0:  # cleanup roads
            self.new_roads['Road/Port'] = 1
            self.geography = pd.concat([self.geography, self.new_roads]).groupby(['Area','Neighbor']).max().reset_index().fillna(0)
            self.geography['Road/Port'] = self.geography['Road/Port'].astype(int)
            self.new_roads = pd.DataFrame(columns=['Area','Neighbor'])
        if self.construction.shape[0]>0:  # build stuff
            self.construction['Seasons'] = self.construction['Seasons'] -1
            for i, row in self.construction[self.construction['Seasons']<=0].iterrows():
                self.add_stronghold(row['Faction'], row['Area'], row['Type'], row['Name'], Level=0)
            self.construction = self.construction[self.construction['Seasons']>0]
        if self.strongholds[self.strongholds['Sieged']==1].shape[0] > 0:
            for i, row in self.strongholds[self.strongholds['Sieged']==1].iterrows():
                if self.sieges[self.sieges['Stronghold']==row['Name']].shape[0]==0:
                    self.edit_stronghold(row['Name'],'Sieged',0)  # siege was ended by enemy doing something else
        if self.sieges.shape[0] > 0:  # handle combat
            for i, row in self.sieges.iterrows():
                self.handle_siege(row['Faction'],row['Stronghold'])
            self.sieges = pd.DataFrame(columns=['Faction','Stronghold'])  # clear sieges
            
        # clear wrecked strongholds
        for i, row in self.strongholds[self.strongholds['Hit Points'] < 0].iterrows():
            self.drop_stronghold(row['Name'])
            
        # contested levels...
        temp = pd.merge(self.strongholds[['Area','Type','Level']],
                 self.stronghold_types[['Stronghold','Type']],
                 left_on='Type', right_on='Stronghold',how='left')
        temp = temp[['Area','Level','Type_y']].groupby(['Area','Type_y']).sum().reset_index()
        temp = pd.merge(temp,self.areas[['Area','Population','Magic']],on='Area',how='left')

        # castles
        castles = temp[temp['Type_y']=='Castle']
        temp = temp[temp['Type_y']!='Castle']
        for i, row in  castles[castles['Level']>castles['Population']].iterrows():
            self.edit_area(row['Area'],'Population',row['Level'])
        # fix magic
        self.calculate_magic()
        for a in ['Temple','Guild','Monastery']:
            temp_ = temp[temp['Type_y']==a]
            for i, row in temp_[temp_['Level']>temp_['Population']].iterrows():
                self.contest_levels(row['Area'],a)
        temp_ = temp[temp['Type_y']=='Mystic']
        for i, row in temp_[temp_['Level']>temp_['Magic']].iterrows():
            self.contest_levels(row['Area'],'Mystic')
        
        # cleanup failed factions
        
        self.agent.save()
        
        