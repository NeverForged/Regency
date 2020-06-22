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
        vassalage -> pay 500 gold per season and allow them to use your lands (they become friendly to you)
        extortions -> pay 500 gold per season
        
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
            print('Invalid Name')
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
            print('Factions must be valid')
        elif self.relationships[(self.relationships['Faction']==faction) & (self.relationships['Other']==other)].shape[0] == 0:  # row not there yet
            new_row = {'Faction':faction, 'Other':other, 'Relationship':change}
            self.relationships = self.relationships.append(new_row, ignore_index=True).fillna('').reset_index(drop=True)
        else:
            self.relationships.loc[self.relationships[(self.relationships['Faction']==faction) & (self.relationships['Other']==other)].index[0],'Relationship'] = self.relationships.loc[self.relationships[(self.relationships['Faction']==faction) & (self.relationships['Other']==other)].index[0],'Relationship'] + change
            
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
            if roll < self.IntDC or roll == 1:   #Fails a dc 5 int check and does something random
                move = (to_categorical(rand.randint(0, 18), num_classes=N),to_categorical(rand.randint(19, 33), num_classes=N))
            else:
                move =  (to_categorical(np.argmax(prediction[0][:18]), num_classes=N), to_categorical(np.argmax(prediction[0][19:]), num_classes=N))
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
        temp = pd.merge(self.strongholds,self.factions[['Name','Con','Gold']],left_on='Faction',right_on='Name',how='left')
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
    

                
    #   ---   RUN SEASON   ---
    def run_season(self, train=False, train_often=False, dc=None):
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
            if row['Name'] not in self.seasons['Faction']:
                self.seasons = self.seasons.append({'Faction':row['Name']}, ignore_index=True).fillna('')
        
        # get revenue
        revenue = self.get_revenue()
        
        # get state
        state = self.agent.get_state()
        state = pd.merge(state, revenue[['Faction','Revenue']],on='Faction',how='left').fillna(0)
        
        
        # save the things from last time...  CHECK ONCE YOU HAVE STUFF
        if self.last_season.shape[0]>0 and train == True:
            lst = list(state.keys())
            state['New State'] = state['State']
            self.last_season = pd.merge(self.last_season,state[['Faction','New State']],on='Faction',how='left')
            state = state[lst]
            lst = list(revenue.keys())
            revenue['New Revenue'] = revenue['Revenue']
            self.last_season = pd.merge(self.last_season,revenue[['Faction','New Revenue']],on='Faction',how='left')
            revenue = revenue[lst]
            self.last_season['Reward'] = self.last_season['New Revenue'] - self.last_season['Revenue']
            
            # training...
            for i, row in self.last_season.iterrows():
                self.agent.remember(self, state=row['State'], action=row['Action1'], reward=row['Reward'], next_state=row['New State'], done=False)
                self.agent.remember(self, state=row['State'], action=row['Action2'], reward=row['Reward'], next_state=row['New State'], done=False)
        
            
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
            
            # ---   BONUS ACTIONS   ---
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
                
            #   ---   ACTION   ---
            if action == 19:  # build_manor
                alst.append(action_build_stronghold(row['Faction'], 'Manor'))
            elif action == 20:  # build_keep
                alst.append(action_build_stronghold(row['Faction'], 'Keep'))
            elif action == 21:  # build_palace
                alst.append(action_build_stronghold(row['Faction'], 'Palace'))
            elif action == 22:  # build_guild
                alst.append(action_build_stronghold(row['Faction'], 'Guildhall'))
            elif action == 23:  # build_small_temple
                alst.append(action_build_stronghold(row['Faction'], 'Small Temple'))
            elif action == 24:  # build_large_temple
                alst.append(action_build_stronghold(row['Faction'], 'Large Temple'))
            elif action == 25:  # build_abbey
                alst.append(action_build_stronghold(row['Faction'], 'Abbey'))
            elif action == 26:  # build_tower
                alst.append(action_build_stronghold(row['Faction'], 'Tower'))
                
        # Cleanup
        if self.new_roads.shape[0] > 0:  # cleanup roads
            self.new_roads['Road/Port'] = 1
            self.geography = pd.concat([self.geography, self.new_roads]).groupby(['Area','Neighbor']).max().reset_index().fillna(0)
            self.geography['Road/Port'] = self.geography['Road/Port'].astype(int)
            self.new_roads = pd.DataFrame(columns=['Area','Neighbor'])
        