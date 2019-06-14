import os
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from PIL import Image
from random import randint
from DQNAgent import DQNAgent
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from IPython.display import clear_output


class Regency(object):
	'''
	Based on the 5e Conversion of the Regency system from Birthright,
	found here: https://www.gmbinder.com/share/-L4h_QHUKh2NeYhgD96A
	
	DataFrames:
	Provences: [Provence, Domain, Region, Regent, Terrain, Loyalty, Taxation, 
				Population, Magic, Castle, Capital, Position]
	Holdings: [Provence, Domain, Regent, Type, Level]
	Regents: [Regent, Full Name, Player, Class, Level, Alignment, Race, 
				Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion, 
				Regency Points, Gold Bars, Regency Bonus, Attitude]
	Geography: [Provence, Neighbor, Border, Road, Caravan, Shipping, RiverChasm]
	Relationship: [Regent, Other, Diplomacy, Payment, Vassalage, At War]
	Troops: [Regent, Provence, Type, Cost, CR, Garrisoned]
	Seasons: A dctionary of season-dataframes (to keep track of waht happened)
	Lieutenants: A List of regent lieutenant pairs
	LeyLines: [Regent, Provence, Other]
	'''
	
	# Initialization
	def __init__(self, world='Birthright', dwarves=True, elves=True, goblins=True, gnolls=True, halflings=True, jupyter=True):
		'''
		initialization of Regency class.
		Sets the dataframes based on saved-version
		Birthright is Default.
		'''
		self.jupyter = jupyter
		
		# Agents...
		self.agent = {}
		self.agent['Normal'] = pickle.load( open( 'agent_n.pickle', "rb" ) )
		self.agent['Peaceful'] = pickle.load( open( 'agent_p.pickle', "rb" ) )
		self.agent['Aggressive'] = pickle.load( open( 'agent_a.pickle', "rb" ) )
		
			
		# Provence Taxation Table
		dct = {}
		dct['Population'] = [a for a in range(11)]
		dct['Light'] = [(0,0), (-1,1), (0,1), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16)]
		dct['Moderate'] = [(0,0), (0,2), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16), (4,18)]
		dct['Severe'] =	 [(-1,1), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16), (4,18), (4,22)]
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
		
		
	#  World Loading
	def load_world(self, world):
		'''
		loads world-dictionary
		'''
		
		try:
			dct = pickle.load( open( world+'.pickle', "rb" ) )
			lst = ['Provences', 'Holdings', 'Regents', 'Geography', 'Relationships', 'Troops', 'Seasons', 'Lieutenants', 'LeyLines']
			self.Provences, self.Holdings, self.Regents, self.Geography, self.Relationships, self.Troops, self.Seasons, self.Lieutenants, self.LeyLines = [dct[a] for a in lst]
		except (OSError, IOError) as e:
			self.new_world(world)

	
	# AGENT STUFF
	def make_decision(self, attitude, N, type, state, Regent):
		'''
		Have the Agent do a thing to make a decision.
		'''
		agent = self.agent[attitude]
		
		# get Int modifier
		mod = self.Regents[self.Regents['Regent']==Regent]['Int'].values[0]
		# predict action based on the old state
		if type == 'Taxes':
			prediction = agent.tax_model.predict(state.reshape((1,19)))
		
		roll = randint(1, 20)
		if roll < 5-mod or roll == 1:  # Fails a dc 5 int check and does something random
			move =	to_categorical(randint(0, N-1), num_classes=N)
		else:
			move =	to_categorical(np.argmax(prediction[0]), num_classes=N)
		return move
		
	# World Building
	def new_world(self, world):
		# Holdings
		cols= ['Provence', 'Regent', 'Type', 'Level', 'Contested']
		self.Holdings = pd.DataFrame(columns=cols)
		
		# Provences
		cols = ['Provence', 'Domain', 'Region', 'Regent', 'Terrain', 'Loyalty', 'Taxation',
				'Population', 'Magic', 'Castle', 'Capital', 'Position', 'Contested']
		self.Provences = pd.DataFrame(columns=cols)
		
		# Regents
		cols = ['Regent', 'Full Name', 'Player', 
			 'Class', 'Level', 'Alignment', 'Race', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha',
			'Insight', 'Deception', 'Persuasion',
			 'Regency Points', 'Gold Bars', 'Regency Bonus', 'Attitude']
		self.Regents = pd.DataFrame(columns=cols)
		
		# Geography
		cols = ['Provence', 'Neighbor', 'Border', 'Road', 'Caravan', 'Shipping', 'RiverChasm']
		self.Geography = pd.DataFrame(columns=cols)
		
		# Relationships
		cols = ['Regent', 'Other', 'Diplomacy', 'Payment', 'Vassalage', 'At War']
		self.Relationships = pd.DataFrame(columns=cols)
		
		# Troops
		cols = ['Regent', 'Provence', 'Type', 'Cost', 'CR', 'Garrisoned']
		self.Troops = pd.DataFrame(columns=cols)
		
		# Lieutenants
		cols = ['Regent', 'Lieutenant']
		self.Lieutenants = pd.DataFrame(columns=cols)
		
		#Ley Lines
		cols = ['Regent', 'Provence', 'Other']
		self.LeyLines = pd.DataFrame(cols)
		
		# Seasons
		self.Seasons = {}
	
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
		
		with open(world + '.pickle', 'wb') as handle:
			pickle.dump(dct, handle, protocol=pickle.HIGHEST_PROTOCOL)
		
	def get_my_index(self, df, temp):
		'''
		Index finder-function (function code)
		'''
		df = df.copy()
		if len(temp) == 1:
			index = temp[0]
		else:
			try:
				index = max(df.index.tolist()) + 1
			except:
				print('new')
				index=0
		return index

	def add_holding(self, Provence, Regent, Type='Law', Level=1, Contested=0):
		'''
		 Provence: match to provence
		 Regent: match to regent
		 Type: 'Law', 'Guild', 'Temple', 'Source' 
		 Level: 1 to Population (or Magic for source)
		 
		 temp = Holdings[Holdings['Regent']==Regent]
		 temp = temp[temp['Type']==Type]
		 temp.index[temp['Provence'] == 'Bogsend' ].tolist()
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

	def remove_holding(self, Provence, Regent, Type, Level):
		'''
		Remove all rows where Regent, Provence, Type are
		equakl to those set.
		'''
		# Holdings
		df = self.Holdings.copy()
		
		temp = df[df['Provence']==Provence] # just the provence in question
		df = df[df['Provence'] != Provence] # all others are safe
		# add back all other regents in that provence
		df = pd.concat(df, temp[temp['Regent'] != Regent]) 
		# isolate regent
		temp = temp[temp['Regent'] == Regent]
		# add back all other types
		df = pd.concat(df, temp[temp['Regent'] != Type])
		
		#done
		self.Holdings = df

	def add_provence(self, Provence, Domain, Region, Regent, x, y
					 , Population=0, Magic=1, Law=None
					 , Capital=False, Terrain='Plains', Loyalty='Average', Taxation='Moderate'
					 , Castle=0, Contested=0):
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
		
		temp = df.index[df['Provence'] == 'Provence'].tolist()
		index = self.get_my_index(df, temp)
				
		df.loc[df.shape[0]] = [Provence, Domain, Region, Regent, Terrain, Loyalty, Taxation,
							   Population, Magic, Castle, Capital, np.array([x, y]), 0]
		df['Magic'] = df['Magic'].astype(int)
		df['Population'] = df['Population'].astype(int)
		df['Castle'] = df['Castle'].astype(int)
		df = df.drop_duplicates(subset='Provence', keep="last")
		
		self.Provences = df

	def change_provence(self, Provence, Regent=None, Region=None, Domain=None, Population_Change=0, Terrain=None, Loyalty=None
						, Taxation=None, Castle=None, Capital=None, x=None, y=None, Contested=None):
		'''
		None = not changed
		'''
		index = self.Provences.index[self.Provences['Provence'] == Provence].tolist()[0]
		old = self.Provences.iloc[index]
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
			Taxtion == old['Taxation']
		   
		Population = old['Population'] + Population_Change
		Magic = old['Magic'] - Population_Change
		
		if Magic <= 0:
			Magic = 1
		if Castle == None:
			Castle = old['Castle']
		if Capital == None:
			Capital = old['Capital']
		if x == None or y == None:
			pos = old['Position']
		else:
			pos = np.array(x, y)
		self.Provences.loc[index] = [Provence, Domain, Region, Regent, Terrain, Loyalty, Taxation,
									 Population, Magic, Castle, Capital, pos, Contested]

	def add_lieutenant(self, Regent, Lieutenant):
		'''
		Adds a lieutenant
		'''
		df = self.Lieutenants.copy()
		
		temp = df[df['Regent']==Regent]
		temp = temp.index[temp['Lieutenant']==Lieutenant].tolist()
		index = self.get_my_index(df, temp)
		
		df.loc[index] = [Regent, Lieutenant]
		
		# set the df...
		self.Lieutenants = df
		
	def add_regent(self, Regent, Name, Player=False, Class='Noble', Level=2, Alignment = 'NN', Race='Human'
				   , Str = 0, Dex = 1, Con = 0, Int = 1, Wis = 2, Cha = 3
				   , Insight = 4, Deception = 5, Persuasion = 5
				   , Regency_Points = 0, Gold_Bars = 0, Regency_Bonus = 1
				   , Attitude = 'Normal', Lieutenants=[], Archetype=None):
		'''
		Archetype: Allows for pre-loaded skill and ability mods based on NPC statblocks
		'''
		# Regents
		df = self.Regents.copy()
		
		temp = df.index[df['Regent'] == 'Regent'].tolist()
		index = self.get_my_index(df, temp)
		if Archetype != None:
			# set the stats based on archetype
			Class, Level, Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion = self.get_archetype(Archetype)

		df.loc[df.shape[0]] = [Regent, Name, Player, Class, Level, Alignment, Race, 
							   Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion,
							   Regency_Points, Gold_Bars, Regency_Bonus, Attitude]
		df = df.drop_duplicates(subset='Regent', keep='last')
		self.Regents = df
		for Lieutenant in Lieutenants:
			self.add_lieutenant(Regent, Lieutenant)

	def get_archetype(self, Archetype):
		'''
		return	Class, Level, Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion
		'''
		if Archetype == 'Noble':
			return 'Noble', 2, 0, 1, 0, 1, 2, 3, 4, 5, 5
		elif Archetype == 'Archmage':
			return 'Archmage', 18, 0, 2, 1, 5, 2, 3, 5, 3, 3
		elif Archetype == 'Assassin':
			return 'Assassin', 12, 0, 3, 2, 1, 0, 0, 1, 3, 0
		elif Archetype == 'Bandit' or Archetype == 'Bandit Captain':
			return 'Bandit Captain', 10, 2, 3, 2, 2, 0, 2, 2, 4, 2
		elif Archetype == 'Commoner':
			return 'Commoner', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0
		elif Archetype == 'Druid':
			return 'Druid', 5, 0, 1, 1, 1, 2, 0, 1, 0, 0
		elif Archetype == 'Knight':
			return 'Knight', 8, 3, 0, 2, 0, 0, 2, 0, 2, 2
		elif Archetype == 'Lich':
			return 'Lich', 18, 0, 3, 3, 5, 2, 3, 9, 3, 3
		elif Archetype == 'Mage':
			return 'Mage', 9, -1, 2, 0, 3, 1, 0, 3, 0, 0
		elif Archetype == 'Hag' or Archetype == 'Green Hag':
			return 'Green Hag', 11, 4, 1, 3, 1, 2, 2, 1, 4, 2
		elif Archetype == 'Priest':
			return 'Priest', 5, 0, 0, 1, 1, 3, 1, 1, 1, 3
		
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

	def add_relationship(self, Regent, Other, Diplomacy=0, Payment=0, Vassalage=0, At_War=0):
		'''
		Regent -> Whose Relationship
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
			temp_ = df[df['Regent'] == Provence].copy()
			temp_ = temp_[temp_['Other']==Neighbor]
			Diplomacy = Diplomacy + temp_['Diplomacy'].values[0]
			Paymernt = Paymernt + temp_['Paymernt'].values[0]
			Vassalage = Vassalage + temp_['Vassalage'].values[0]
		
		index = self.get_my_index(df, temp)
		df.loc[index] = [Regent, Other, Diplomacy, Payment, Vassalage, At_War]
		self.Relationships = df
		
	def add_troops(self, Regent, Provence, Type):
		'''
		This is fired after a decision to buy a troop is made
		OR for setting up troops in the begining
		'''
		df = self.Troops.copy()
		
		index = self.get_my_index(df, [])
		
		temp = self.troop_units[self.troop_units['Unit Type'] == Type]

		df.loc[index] = [Regent, Provence, Type, temp['Maintenance Cost'].values[0], temp['BCR'].values[0], 0]
		
		# set the df...
		self.Troops = df

	# Show
	def show_map(self, borders=False, roads=True, caravans=False, shipping=False, bg=True, adj=50, fig_size=(12,12),
				 cam_map='Birthright', map_alpha = 0.5, axis=False, regions=None, castle=False):
		'''
		Map it
		'''
		Geography = self.Geography.copy()
		if regions == None:
			Provences = self.Provences.copy()
		else:
			Provences = pd.concat([ self.Provences[ self.Provences['Region']==Region] for Region in regions])
		Regents = self.Regents.copy()
		Diplomacy = self.Relationships.copy()
		
		
			
		plt.figure(figsize=fig_size)
		if bg:
			if cam_map=='Birthright':
				image = Image.open('615dbe4e4e5393bb6ff629b50f02a6ee.jpg')
			else:
				image = Image.open(cam_map)
			plt.imshow(image, alpha=map_alpha)
			
		
		try:
			G = nx.from_pandas_edgelist(Geography, 'Provence', 'Neighbor', ['Border', 'Road', 'Caravan', 'Shipping'])
		except:

			G = nx.from_pandas_dataframe(Geography, 'Provence', 'Neighbor', ['Border', 'Road', 'Caravan', 'Shipping'])



		pos = {}
		xmin, xmax = Provences['Position'].values[0][0], Provences['Position'].values[0][0]
		ymin, ymax = Provences['Position'].values[0][1], Provences['Position'].values[0][1]
		for pro in list(Provences['Provence']):
			x =	 Provences[Provences['Provence']==pro]['Position'].values[0][0]
			y =	 Provences[Provences['Provence']==pro]['Position'].values[0][1]
			if x < xmin:
				xmin = x
			elif x > xmax:
				xmax = x
			if y < ymin:
				ymin = y
			elif y > ymax:
				ymax = y
			
			if bg:
				pos[pro] = Provences[Provences['Provence']==pro]['Position'].values[0]
			else:
				pos[pro] = Provences[Provences['Provence']==pro]['Position'].values[0]*np.array([1,-1])

		# node types
		player_regents = Regents[Regents['Player']==True]
		npc_regents = Regents[Regents['Player']==False]
		
		dip = pd.merge(Diplomacy,player_regents,on='Regent',how='left')
		dip['Rank'] = dip['Diplomacy'] + dip['Vassalage']
		dip = dip[['Other','Rank']].groupby('Other').sum().reset_index()
		dip['Regent'] = dip['Other']
		
		npc_regents = pd.merge(npc_regents, dip[['Regent', 'Rank']], on='Regent', how='outer').fillna(0)
		# player nodes
		nodes = []
		capitals = []
		for reg in list(player_regents['Regent']):
			temp = Provences[Provences['Regent']==reg]
			nodes = nodes + list(temp[temp['Capital']==False]['Provence'])
			capitals = capitals + list(temp[temp['Capital']==True]['Provence'])
		nodes = list(set(nodes))
		capitals = list(set(capitals))

		nx.draw_networkx_nodes(G,pos,
							   nodelist=nodes,
							   node_color='b',
							   node_size=50,
							   alpha=0.25)
		nx.draw_networkx_nodes(G,pos,node_shape='*',
							   nodelist=capitals,
							   node_color='b',
							   node_size=500,
							   alpha=0.25)


		# friendly and neutral provences
		nodes = []
		capitals = []
		
		for reg in list(npc_regents[npc_regents['Rank']>=0]['Regent']):
			temp = Provences[Provences['Regent']==reg]
			nodes = nodes + list(temp[temp['Capital']==False]['Provence'])
			capitals = capitals + list(temp[temp['Capital']==True]['Provence'])
		nodes = list(set(nodes))
		capitals = list(set(capitals))

		nx.draw_networkx_nodes(G,pos,
							   nodelist=nodes,
							   node_color='g',
							   node_size=50,
							   alpha=0.25)
		nx.draw_networkx_nodes(G,pos,node_shape='*',
							   nodelist=capitals,
							   node_color='g',
							   node_size=500,
							   alpha=0.25)
		# enemy provences
		nodes = []
		capitals = []
		for reg in list(npc_regents[npc_regents['Rank']<0]['Regent']):
			temp = Provences[Provences['Regent']==reg]
			nodes = nodes + list(temp[temp['Capital']==False]['Provence'])
			capitals = capitals + list(temp[temp['Capital']==True]['Provence'])
		nodes = list(set(nodes))
		capitals = list(set(capitals))

		nx.draw_networkx_nodes(G,pos,
							   nodelist=nodes,
							   node_color='r',
							   node_size=50,
							   alpha=0.25)
		nx.draw_networkx_nodes(G,pos,node_shape='*',
							   nodelist=capitals,
							   node_color='r',
							   node_size=500,
							   alpha=0.25)


		# edges
		Plist = list(Provences['Provence'])
		if caravans:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Caravan']==1].iterrows() 
						if row['Provence'] in Plist and	 row['Neighbor'] in Plist]
			nx.draw_networkx_edges(G,pos,edgelist,width=2.0,alpha=0.3,edge_color='xkcd:red',style='dotted')
		if shipping:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Shipping']==1].iterrows() 
						if row['Provence'] in Plist and	 row['Neighbor'] in Plist]
			nx.draw_networkx_edges(G,pos,edgelist,width=2.0,alpha=0.3,edge_color='xkcd:azure',style='dotted')
		if borders:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Border']==1].iterrows() 
						if row['Provence'] in Plist and	 row['Neighbor'] in Plist]
			nx.draw_networkx_edges(G,pos,edgelist,width=0.5,alpha=0.25,edge_color='xkcd:grey')
		if roads:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Road']==1].iterrows() 
						if row['Provence'] in Plist and	 row['Neighbor'] in Plist]
			nx.draw_networkx_edges(G,pos,edgelist,width=1.0,alpha=0.5,edge_color='xkcd:brown',style='dashed')
		

		# labels
		temp = Provences.copy()
		temp['Label'] = temp['Provence'] + '\n ' + temp['Population'].astype(int).astype(str) + '/' + temp['Magic'].astype(int).astype(str)
		labels={}
		for i, row in temp.iterrows():
			if row['Capital']:
				labels[row['Provence']] =  '*' + row['Label']
			else:
				labels[row['Provence']] =  row['Label']
		nx.draw_networkx_labels(G,pos,labels,font_size=10)
		
		if bg:
			plt.xlim(xmin-adj,xmax+adj)
			plt.ylim(ymax+adj, ymin-adj)
			
		if axis==False:
			plt.axis('off')
		plt.show()
		
		
	# The Season
	def random_events(self, override={}, style='Birthright', Threshold=50, Regions=None):
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

		if Threshold < 1:  # flaot to int
			Threshold = int(100*Threshold)
		temp = self.Regents[['Regent', 'Player']].copy()
		
		# filter to Regions
		if Regions != None:
			filter = pd.concat([self.Provences[self.Provences['Region']==Region].cpopy() for Region in Regions])[['Regent', 'Provence']].copy()
			filter_ = pd.merge(filter, self.Holdings.copy(), on='Provence', how='left')[['Regent', 'Provence']].copy()
			filter = pd.concat([filter, filter_])[['Regent', 'Player']].copy()
			temp = pd.merge(filter, temp, on='Regent', how='left')
			
		# seperate players from npcs
		npcs = temp[temp['Player']==False].copy()
		players = temp[temp['Player']==True].copy()

		npcs['Random Event'] = np.random.randint(1,100,npcs.shape[0])
		npcs
		npcs_y = npcs[npcs['Random Event']<Threshold].copy()
		npcs_n = npcs[npcs['Random Event']>=Threshold].copy()

		temp = pd.concat([players, npcs_y[['Regent', 'Player']]])
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

		for reg in override.keys():	 # Override is Override
			index = temp.index[temp['Regent'] == reg].tolist()[0]
			player = temp[temp['Regent'] == reg]['Player'].values[0]
			temp.loc[index] = [reg, player, override[reg]]

		try:
			# new season!
			self.Season = max(self.Seasons.keys())+1
		except:
			self.Season = 0
		
		self.Seasons[self.Season] = {}
		self.Seasons[self.Season]['Season'] = temp
		
		for key in self.agent.keys():
			if self.Season==0:
				self.agent[key].epsilon = 201
			else:
				self.agent[key].epsilon = 80 - self.Season
	
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
		df['Regency Points Add'] = df['Population']
		df = df[['Regent', 'Regency Points Add']]

		# holdings
		temp = self.Holdings.copy()
		temp['Regency Points Add'] = temp['Level']
		df = pd.concat([df, temp[['Regent','Regency Points Add']]])
		df = df.groupby('Regent').sum().reset_index()
		df = df.fillna(0)

		regents = pd.merge(regents.copy(), df, on='Regent', how='left')

		# tribute from Vassalage
		relationships = self.Relationships.copy()
		relationships = relationships[relationships['Vassalage']>0]
		relationships['Minus'] = relationships['Vassalage']

		regents = pd.merge(regents, relationships[['Regent','Minus']], on='Regent', how='left')
		regents = pd.merge(regents, relationships[['Other', 'Vassalage']], left_on='Regent', right_on='Other', how='left')

		regents = regents.fillna(0)

		# calculation
		regents['Regency Points'] = regents['Regency Points'] + regents['Regency Bonus'] + regents['Regency Points Add'] - regents['Minus'] + regents['Vassalage']
		regents['Regency Points'] = regents['Regency Points'].astype(int)
		
		self.Seasons[self.Season]['Season'] = pd.merge(self.Seasons[self.Season]['Season'], regents[['Regent', 'Regency Points']], on='Regent', how='left').fillna(0)
		self.Regents = regents[keys]
		
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
		
	def collect_gold_bars(self):
		'''
		At this phase of the season, each regent declares taxation and 
		collects income in the form of Gold Bars. This process can be 
		heavy on the rolls, so for groups who wish to expedite this 
		process, there are flat values that may be used instead.
		'''
		cols = self.Regents.copy().keys()
		
		# 4.1 & 4.2 Taxation From Provences
		df = pd.DataFrame()
		
		# set taxtation
		temp = self.Regents[self.Regents['Player']==True]
		law = self.Holdings.copy()
		law = law[law['Type']=='Law'].copy()
		
		for i, row in temp.iterrows():
			check = 0
			while check == 0:
				self.clear_screen()
				print('Taxation Settings for {}'.format(row['Full Name']))
				print('-'*33)
				temp_ = self.Provences[self.Provences['Regent']==row['Regent']][['Provence','Population', 'Loyalty', 'Taxation']]
				temp_ = pd.merge(temp_, law[law['Regent']==row['Regent']][['Provence', 'Type']].copy(), on='Provence', how='left').fillna('')
				print(temp_)
				print()
				p = input('Type a Provence name, or "DONE" if done:	 ')
				if p.lower() == 'done':
					check = 1
				else:
					if p in list(temp_['Provence']):
						tax = input('Change Taxation to: [0]None, [1]Light, [2]Moderate, [3]Severe:	 ') 
						
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
		save_states = pd.DataFrame(columns=['Regent', 'Provence', 'Agent', 'state', 'action'])
		for i, row in temp.iterrows():
			temp_ = self.Provences[self.Provences['Regent']==row['Regent']][['Provence','Population', 'Loyalty', 'Taxation']]
			temp_ = pd.merge(temp_, law[law['Regent']==row['Regent']][['Provence', 'Type']].copy(), on='Provence', how='left').fillna('')
			# pick for each... this can likely be more efficient
			for j, row_ in temp_.iterrows():
				state = self.agent[row['Attitude']].get_state('Taxes', row_)
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
				save_states.loc[save_states.shape[0]] = [row['Regent'], row_['Provence'], row['Attitude'], state, tax]
				
			
		# collect taxes
		for p in range(11):
			temp = self.Provences[self.Provences['Population'] == p].copy()
			if temp.shape[0] > 0:
				for t in ['Light', 'Moderate', 'Severe']:
					temp_ = temp[temp['Taxation'] == t].copy()
					if temp_.shape[0] > 0:
						a,b = self.provence_taxation[self.provence_taxation['Population'] == p][t].values[0]
						temp_['Revenue'] = np.random.randint(a,b,temp_.shape[0])
						df = pd.concat((df, temp_[['Regent', 'Revenue', 'Provence']].copy()))
		
			
		# make reward vector
		temp = self.Provences.copy()
		temp = pd.merge(temp, self.Holdings[self.Holdings['Type'] == 'Law'][['Provence', 'Type', 'Regent']], on=['Provence', 'Regent'], how='left').fillna('')
		temp['Relative'] = temp['Loyalty'].str.replace('Rebellious','4').replace('Poor','3').replace('Average','2').replace('High','1').astype(int)
		temp['Tax Effect'] = temp['Relative']*(-1)*((temp['Taxation']=='Severe') + (temp['Type'] != 'Law')*(temp['Taxation']=='Moderate')) + temp['Relative']*(temp['Taxation']=='None') + (-5)*(temp['Loyalty']=='Rebellious')
		temp = temp[['Tax Effect', 'Provence']]
		rewards = pd.merge(df, temp, on='Provence', how='left')	 # skips players
		rewards = pd.merge(rewards, self.Regents[self.Regents['Player']==False][['Regent', 'Attitude']].copy(), on='Regent', how='left')
		rewards = rewards.dropna()
		
		# Aggro Regents don't care if the people are unhappy as much as peaceful Regents
		rewards['tm'] = rewards['Attitude'].str.replace('Aggressive','1').replace('Normal','1').replace('Peaceful','2').astype(int)
		rewards['rm'] = rewards['Attitude'].str.replace('Aggressive','2').replace('Normal','1').replace('Peaceful','1').astype(int)
		rewards['Reward'] = rewards['Revenue']*rewards['rm'] + rewards['Tax Effect']*rewards['tm']
		
		# update memory
		save_states = pd.merge(save_states, rewards[['Provence', 'Reward']], on='Provence', how='left').fillna(0)
		lst = []
		for i, row in save_states.iterrows():
			# hate having to iterrow, but here we are
			temp = self.Provences.copy()
			temp = temp[temp['Regent'] == row['Regent']].copy()
			temp = temp[temp['Provence'] == row['Provence']].copy()
			temp = pd.merge(temp, law[law['Regent']==row['Regent']][['Provence', 'Type']].copy(), on='Provence', how='left').fillna('')
			new_state = (self.agent[row['Agent']].get_state('Taxes', list(temp.iterrows())[0][1]))
			self.agent[row['Agent']].remember(row['state'], row['action'], row['Reward'], new_state, 'Taxes')
			self.agent[row['Agent']].train_short_memory(row['state'], row['action'], row['Reward'], new_state, 'Taxes')
		
		# after rewards given
		df = df[df['Revenue']>0].copy()
		
		
		# 4.3 Taxation From Guild and Temple Holdings
		lst = [(0,1), (1,2), (1,3), (2,4), (2,5), (2,6)]
		for h in ['Guild', 'Temple']:
			temp = self.Holdings[self.Holdings['Type'] == h].copy()
			for i in range(6):
				temp_ = temp[temp['Level']==i].copy()
				if temp_.shape[0] > 0:
					temp_['Revenue'] = np.random.randint(lst[i][0],lst[i][1],temp_.shape[0])
					df = pd.concat((df, temp_[['Regent', 'Revenue']].copy()))
			temp_ = temp[temp['Level']>=6].copy()
			if temp_.shape[0] > 0:
				temp_['Revenue'] = np.random.randint(4,10,temp_.shape[0])
				df = pd.concat((df, temp_[['Regent', 'Revenue']].copy()))
		
		# 4.4 Claims from Law Holdings
		temp = pd.merge(self.Holdings.copy(),self.Provences.copy(), on='Provence')
		temp = temp[temp['Type']=='Law']
		temp = temp[temp['Regent_x'] != temp['Regent_y']].copy()
		temp['Level'] = (temp['Level']/2).astype(int)
		temp = temp[temp['Level']>0]
		temp['Revenue'] = temp['Level']
		temp['Regent'] = temp['Regent_x']
		# give to the poor
		df = pd.concat([df, temp[['Regent', 'Revenue']].copy()])
		# ... take from the rich
		temp['Regent'] = temp['Regent_y']
		temp['Revenue'] = temp['Level']*-1
		df = pd.concat([df, temp[['Regent', 'Revenue']].copy()])
		
		# 4.5 Trade Routes - Caravans
		temp = self.Provences[['Provence', 'Regent', 'Population']].copy()
		df_ = pd.concat([self.Geography[self.Geography['Caravan']==1].copy(), self.Geography[self.Geography['Shipping']==1].copy()])
		temp['A'] = temp['Population']
		temp['B'] = temp['Population']
		df_ = pd.merge(df_, temp[['Provence', 'A']], on='Provence', how='left')
		df_ = pd.merge(df_, temp[['Provence', 'B']], right_on='Provence', left_on='Neighbor', how='left').fillna(1)
		df_['Provence'] = df_['Provence_x']
		df_['Revenue'] = ((df_['A']+df_['B']+2*df_['Shipping'])/2).astype(int)
		df_ = pd.merge(df_, self.Provences.copy(), on='Provence', how='left')
		df = pd.concat([df, df_[['Regent', 'Revenue']]])
		
		
		# 4.6 Tribute (the greatest code in the world)
		temp = self.Relationships[self.Relationships['Payment']>0].copy()
		temp['Revenue'] = temp['Payment']*-1
		df = pd.concat([df, temp[['Regent', 'Revenue']]])

		temp['Regent'] = temp['Other']
		temp['Revenue'] = temp['Payment']
		df = pd.concat([df, temp[['Regent', 'Revenue']]])
		
		# 4.7 occupation and Pillaging
		# CODE NEEDED HERE

		# figure it all out
		df = df.groupby('Regent').sum().reset_index()
		temp_Regents =	pd.merge(self.Regents.copy(), df, on='Regent', how='left')
		temp_Regents['Gold Bars'] = temp_Regents['Gold Bars'].fillna(0).astype(int) + temp_Regents['Revenue'].fillna(0).astype(int)
		
		# Results!
		temp_Regents['Revenue'] = temp_Regents['Revenue'].fillna(0).astype(int)
		self.Seasons[self.Season]['Season'] = pd.merge(self.Seasons[self.Season]['Season'], temp_Regents[['Regent','Gold Bars', 'Revenue']], on='Regent', how='left').fillna(0)
		self.Regents = temp_Regents[cols]
	
	def maintenance_costs(self):
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
		df = pd.concat([df,temp[['Regent','Domain']]])
		temp = self.Holdings[self.Holdings['Type'] != 'Source'].copy()
		temp['Domain'] = 1
		df = pd.concat([df,temp[['Regent','Domain']]])
		df = df[['Regent','Domain']].groupby('Regent').sum().reset_index().fillna(0)
		df['Cost'] = ((df['Domain']+4)/5).astype(int)
		df = df[['Regent','Cost']].groupby('Regent').sum().reset_index()
		
		# 5.2 Pay Armies
		temp = self.Troops[['Regent', 'Cost']].copy()  # this would be easy, but we have to disband if we can't pay
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
				while cost > gb:
					for j, _row in _temp.iterrows():
						if cost > gb and _temp.shape[0]>0:
							try:
								# disband the troop
								self.Troops.drop(j, inplace=True)
								# start disbanding
								if _row['Type'].find('Mercenary') >= 0:
									# oh no, brigands!
									print('Replace with a disband mercenary thing')
								cost = cost - _row['Cost']	# make sure only the single troop cost
							except:
								None
							
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
					cost = cost - int(_temp.loc[dbnd]['Cost'])	# make sure only the single troop cost
					# disband the troop
					self.Troops.drop(dbnd, inplace=True, axis=0)
					_temp.drop(dbnd, inplace=True, axis=0)
		# now the easy step
		temp = self.Troops[['Regent', 'Cost']].copy()
		df = pd.concat([df, temp[['Regent','Cost']]], sort=False)
		df = df[['Regent','Cost']].groupby('Regent').sum().reset_index()	
		
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
			while cost > gb:
				for j, _row in _temp.iterrows():
					cost = cost - 1
					# disband the troop
					self.Lieutenants.drop(j, inplace=True)
		# now the money
		temp = self.Lieutenants.copy()
		temp['Cost'] = 1
		df = pd.concat([df, temp[['Regent','Cost']]], sort=False)
		df = df[['Regent','Cost']].groupby('Regent').sum().reset_index()
		
		# 5.4 Court Expenses - what can we afford
		temp_4 = self.Regents[self.Regents['Player'] == True][['Regent', 'Gold Bars']].copy()
		temp = self.Regents[self.Regents['Player'] == False][['Regent', 'Gold Bars']].copy()
		temp = pd.merge(temp, df, on='Regent', how='left').fillna(0)
		temp['Check'] = temp['Gold Bars'] - temp['Cost']
		temp_0 = temp[temp['Check'] <= 1].copy()
		temp_ = temp[temp['Check'] > 1].copy()
		temp_3 = temp_[temp_['Check'] >= 25].copy()
		temp_ = temp_[temp_['Check'] < 25].copy()
		temp_2 = temp_[temp_['Check'] >= 10].copy()
		temp_1 = temp_[temp_['Check'] < 10].copy()
		temp_0['Court'] = 'Dormant'	 # no cost
		
		temp_1['Court'] = 'Bare'	# 2 bars
		temp_1['Cost'] = temp_1['Cost'] + 2
		temp_2['Court'] = 'Average'	 # 5 bars
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
					temp_4.at[i, 'Cost'] =	row['Cost'] + int(ex)
					if ex == '2':
						temp_4.at[i, 'Court'] =	 'Bare'	 # 'Bare'
					elif ex == '5':
						temp_4.at[i, 'Court'] =	 'Average'	# 'Average'
					elif ex == '8':
						temp_4.at[i, 'Court'] = 'Rich'	# 'Rich'
					print(temp_4[temp_4['Regent']==row['Regent']][['Regent','Gold Bars','Cost']])
					check = 1	
		df = pd.concat([temp_0, temp_1, temp_2, temp_3, temp_4], sort=False)
		
		# add to the thing
		temp = pd.merge(self.Seasons[self.Season]['Season'], df[['Regent','Cost','Court']], on='Regent', how='left').fillna(0)
		temp['Cost'] = temp['Cost'].astype(int)
		self.Seasons[self.Season]['Season'] = temp
		
		# lets clear the gold bars
		temp['Gold Bars'] = temp['Gold Bars'] - temp['Cost']
		temp = pd.merge(self.Regents[['Regent', 'Full Name', 'Player', 'Class', 'Level', 'Alignment', 
										'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha',
										'Insight', 'Deception', 'Persuasion',
										'Regency Points', 'Regency Bonus', 'Attitude']], temp[['Regent', 'Gold Bars']])
		self.Regents = temp[['Regent', 'Full Name', 'Player', 
							 'Class', 'Level', 'Alignment', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha',
							 'Insight', 'Deception', 'Persuasion',
							 'Regency Points', 'Gold Bars', 'Regency Bonus', 'Attitude']]
		
	# here we go
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
		
		ENEMY/FRIEND: get nordering regent that is freind/foe by best/worst diplomacy
					if a vassal, friend = Liege
					if at war enemy = occupying force
		CAPITAL Provence
		HIGHEST POP Provence (not capital)
		LOWEST POP Provence
		
		
		'''
		
		
		
	def domain_action_adventure(self, Regent):
		'''
		Cost: None
		Success: Auto
		
		INFO NEEDED NONE
		adventure
		'''
		
	def domain_action_agitate(self, Regent, Target, Conflict, Bonus=False, Provences=None):
		'''
		Cost: 1 RP, 1 GB
		Check: 10 (Persuasion)
		
		Target is a regent.	 if a bonus action, will be a randomly determined provence
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
		
	def bonus_action_build(self, Regent, Provence, Road=None):
		'''
		Cost: varies
		Base Success: 5
		
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
		
		build_road (randomly pick a border to make a road on)
		'''
		
	def domain_action_contest(self, Regent, Target):
		'''
		Cost: 1 RP
		Sucess: DC 10
		
		INFO NEEDED:
		enemy_has_(type)_holding in my lands
		enemy_has_same_type_of_holding_as_me_somewhere_i_have_holding
		i have contested holding
		i have contested provence
		enemy_has_contested_holding
		enemy_has_contested_provence
		enemy_has_no_law_holdings_and_rebellious_or_poor_loyalty_in_a_province
		
		
		contest_holding
		contest_provence
		'''
		
	def domain_action_create_holding(self, Regent, Target):
		'''
		Base: 1 GB
		Sucess: 10 (+ population) (Persuasion)
		
		INFO NEEDED:
		space for a holding nearby where I don't have a holding of that type and it's a type I can make
		
		create_holding
		'''
		
	
	def domain_action_declare_war(self, Regent, Target):
		'''
		WA- (headline continued on page 3)
		
		INFO NEEDED:
		at_war (someone declared war on me)
		
		
		declare_war
		'''
		
	def bonus_action_decree(self, Regent, Type='Asset Seizure'):
		'''
		Type: Bonus

		Base Cost: 1 GB

		Base Success: DC 10

		A Decree encompasses a number of policies and processes that are not otherwise encompassed by other domain actions. While the list provided below is not the limit of what a Decree can do, any action that can be referred to as a Decree must fulfill the following criteria:

		The decree cannot affect another regent’s holdings or provinces.
		The decree cannot change the loyalty or level of any province or holding.
		Decrees cannot affect armies or assets in any way.
		Some examples of common Decrees are as follows. Game Masters and players are encouraged to use Decree whenever no other action is suitable, but care must be taken not to go overboard with what a Decree can accomplish.

		A tax or asset seizure is enacted, generating 1d6 Gold Bars for your - treasury.
		A roustabout or rumormonger is arrested.
		A festival is declared throughout your domain.
		A bounty is offered for local monsters, which may draw adventurers to your territory.
		A minor act of legislation is passed regarding changes to the law, acceptable behaviors, or cultural integration.
		A minor event is dealt with by placating the petitioning party through offerings and compensation.
		Furthermore, the condition of the regent’s court may cause this check to be made at advantage or disadvantage, or not at all. See the section on Court Expenses for more details.
		
		
		decree_festival
		decree_asset_seizure
		'''
		
	def domain_action_diplomacy(self, Regent, Target, Type='form_alliance'):
		'''
		ype: Domain

		Base Cost: 1 RP, 1 GB

		Base Success: DC 10+ (or Automatic)

		Neighboring regents can generally be assumed to remain in correspondence with one another throughout the course of a season. The Diplomacy action has a much wider impact, and is typically a court affair with dignitaries, soirees, and document signings. Typically, this action is taken in relation to NPC regents or random events; if a player character regent is the target of the Diplomacy action, they can determine whether it is automatically successful (but the expense of GB and action must be made in order to gain the effects).

		The DC of the domain action check depends on the specific action being taken. Diplomacy checks are typically simple affairs, but care must be taken with the proposals and the mood and standing of a regent. If a deal is outright insulting, the Game Master can rule the action has no chance of success.

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
		diplomacy_respons_to_unrest
		diplomacy_respond_to_feud
		'''
		
	def bonus_action_disband(self, Regent):
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
		
	def domain_action_espionage(self, Regent, Target, Type, Bonus=False):
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

		For hostile Espionage actions, the target DC is modified by the level of the province in which Espionage is being performed, as well as the levels of any Law holdings within those provinces. For example, Erin Velescarpe wishes to send agents to investigate rumors of Baron Gavin Tael forming a secret alliance with the Gorgon to expand his own holdings. Her base DC of 15 is increased by the level of the Baron’s capital province (6) and the Law holding in his capital province (4). This increases her DC to 25 -- Erin will be spending a great deal of gold financing this endeavor.

		If the roll fails by 10 or more, then the regent’s spy is caught and 
		imprisoned. They may attempt to rescue the agent with additional 
		Espionage attempts, and the Game Master should secretly determine if 
		the agent is successfully interrogated.

		Espionage is dangerous, difficult, and requires a massive investment of 
		Gold Bars to have a solid chance at success. However, the rewards for 
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
		
	def bonus_action_fianances(self, regent, number=1):
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
		
		
		'''
		
	def domain_action_forge_ley_line(self, Provence, Holding):
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
		
		
		forge_ley_line
		'''
        
    def domain_action_fortify(self, provence):
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
        
    def bonus_action_grant(self, Regent):
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
        '''
        
    def domain_action_investiture(self, Regent, Target):
        '''
        Type: Action

        Base Cost: Varies

        Base Success: Varies

        To enact Investiture, a priest capable of casting the realm spell of 
        the same name must be present for the ceremony. This ceremony is 
        critical for passing rightful ownership of holdings and provinces to 
        new rulers, and without it, a regent cannot draw Regency Points or Gold 
        Bars from either asset type.

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
        '''