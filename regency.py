import os
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from PIL import Image
import matplotlib.pyplot as plt

class Regency(object):
	'''
	Based on the 5e Conversion of the Regency system from Birthright,
	found here: https://www.gmbinder.com/share/-L4h_QHUKh2NeYhgD96A
	
	DataFrames:
	Provences: [Provence, Domain, Regent, Terrain, Loyalty, Taxation, 
				Population, Magic, Castle, Capital, Position, Troops]
	Holdings: [Provence, Domain, Regent, Type, Level]
	Regents: [Regent, Full Name, Player, Class, Level, Alignment, 
				Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion, 
				Regency Points, Gold Bars, Regency Bonus, Attitude, Lieutenants]
	Geography: [Provence, Neighbor, Border, Road, Caravan, Shipping]
	Relationship: [Regent, Other, Diplomacy, Payment, Vassalage]
	Troops: [Regent, Provence, Type, Cost, CR]
	Seasons: A dctionary of season-dataframes (to keep track of waht happened)
	'''
	
	# Initialization
	def __init__(self, world='Birthright'):
		'''
		initialization of Regency class.
		Sets the dataframes based on saved-version
		Birthright is Default.
		'''
		self.load_world(world)
		
	
	
	#  World Loading
	def load_world(self, world):
		'''
		loads world-dictionary
		'''
		
		try:
			dct = pickle.load( open( world+'.pickle', "rb" ) )
			lst = ['Provences', 'Holdings', 'Regents', 'Geography', 'Relationships', 'Troops', 'Seasons']
			self.Provences, self.Holdings, self.Regents, self.Geography, self.Relationships, self.Troops, self.Seasons = [dct[a] for a in lst]
		except (OSError, IOError) as e:
			self.new_world(world)

	
	# World Building
	def new_world(self, world):
		# Holdings
		cols= ['Provence', 'Regent', 'Type', 'Level']
		self.Holdings = pd.DataFrame(columns=cols)
		
		# Provences
		cols = ['Provence', 'Domain', 'Regent', 'Terrain', 'Loyalty', 'Taxation',
				'Population', 'Magic', 'Castle', 'Capital', 'Position', 'Troops']
		self.Provences = pd.DataFrame(columns=cols)
		
		# Regents
		cols = ['Regent', 'Full Name', 'Player', 
			 'Class', 'Level', 'Alignment', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha',
			'Insight', 'Deception', 'Persuasion',
			 'Regency Points', 'Gold Bars', 'Regency Bonus', 'Attitude', 'Lieutenants']
		self.Regents = pd.DataFrame(columns=cols)
		
		# Geography
		cols = ['Provence', 'Neighbor', 'Border', 'Road', 'Caravan', 'Shipping']
		self.Geography = pd.DataFrame(columns=cols)
		
		# Relationships
		cols = ['Regent', 'Other', 'Diplomacy', 'Payment', 'Vassalage']
		self.Relationships = pd.DataFrame(columns=cols)
		
		# Troops
		cols = ['Regent', 'Provence', 'Type', 'Cost', 'CR']
		self.Troops = pd.DataFrame(columns=cols)
		
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

	def add_holding(self, Provence, Regent, Type='Law', Level=1):
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
		
		df.loc[index] = [Provence, Regent, Type, Level]
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

	def add_provence(self, Provence, Domain, Regent, x, y
					 , Population=0, Magic=1, Law=None
					 , Capital=False, Terrain='Plains', Loyalty='Average', Taxation='Moderate'
					 , Castle=0, Troops=0):
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
				
		df.loc[df.shape[0]] = [Provence, Domain, Regent, Terrain, Loyalty, Taxation,
							   Population, Magic, Castle, Capital, np.array([x, y]), Troops]
		df['Magic'] = df['Magic'].astype(int)
		df['Population'] = df['Population'].astype(int)
		df['Castle'] = df['Castle'].astype(int)
		df = df.drop_duplicates(subset='Provence', keep="last")
		
		self.Provences = df

	def add_regent(self, Regent, Name, Player=False, Class='Noble', Level=2, Alignment = 'NN'
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

		df.loc[df.shape[0]] = [Regent, Name, Player, Class, Level, Alignment, 
							   Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion,
							   Regency_Points, Gold_Bars, Regency_Bonus, Attitude, Lieutenants]
		df = df.drop_duplicates(subset='Regent', keep='last')
		self.Regents = df

	def get_archetype(self, Archetype):
		'''
		return  Class, Level, Str, Dex, Con, Int, Wis, Cha, Insight, Deception, Persuasion
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
		
	def add_geo(self, Provence, Neighbor, Border=0, Road=0, Caravan=0, Shipping=0):
		'''
		Geography Connection
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
		# bi-directional

		df.loc[index] = [Provence, Neighbor, Border, Road, Caravan, Shipping]
		temp = df[df['Provence'] == Neighbor].copy()
		temp = temp.index[temp['Neighbor']==Provence].tolist()
		index = self.get_my_index(df, temp)

		df.loc[index] = [Neighbor, Provence, Border, Road, Caravan, Shipping]
		
		# fix to zeroes and ones...
		for col in ['Border', 'Road', 'Caravan', 'Shipping']:
			df[col] = (1*(df[col]>=1)).astype(int)

		self.Geography = df 

	def add_relationship(self, Regent, Other, Diplomacy=0, Payment=0, Vassalage=0):
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
		df.loc[index] = [Regent, Other, Diplomacy, Payment, Vassalage]
		self.Relationships = df
		
	
	# Show
	def show_map(self, borders=False, roads=True, caravans=False, shipping=False, bg=True, adj=50, fig_size=(12,12),
				 cam_map='Birthright', map_alpha = 0.5, axis=False):
		'''
		Map it
		'''
		Geography = self.Geography.copy()
		Provences = self.Provences.copy()
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
			x =  Provences[Provences['Provence']==pro]['Position'].values[0][0]
			y =  Provences[Provences['Provence']==pro]['Position'].values[0][1]
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
		if caravans:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Caravan']==1].iterrows()]
			nx.draw_networkx_edges(G,pos,edgelist,width=2.0,alpha=0.3,edge_color='xkcd:gold',style='dotted')
		if shipping:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Shipping']==1].iterrows()]
			nx.draw_networkx_edges(G,pos,edgelist,width=2.0,alpha=0.3,edge_color='xkcd:azure',style='dotted')
		if borders:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Border']==1].iterrows()]
			nx.draw_networkx_edges(G,pos,edgelist,width=0.5,alpha=0.25,edge_color='xkcd:grey')
		if roads:
			edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Road']==1].iterrows()]
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
	def random_events(self, override={}, style='Birthright', Threshold=50):
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
		'''

		if Threshold < 1:  # flaot to int
			Threshold = int(100*Threshold)
		temp = self.Regents[['Regent', 'Player']].copy()
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

		for reg in override.keys():  # Override is Override
			index = temp.index[temp['Regent'] == reg].tolist()[0]
			player = temp[temp['Regent'] == reg]['Player'].values[0]
			temp.loc[index] = [reg, player, override[reg]]

		try:
			# new season!
			self.Season = max(self.Seasons.keys())+1
		except:
			self.Season = 0
		
		self.Seasons[self.Season] = temp
	
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
		
		self.Seasons[self.Season] = pd.merge(self.Seasons[self.Season], regents[['Regent', 'Regency Points']], on='Regent', how='left').fillna(0)
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
		
		Season = pd.merge(self.Seasons[self.Season], temp[['Regent', 'Initiative']], on='Regent', how='left')
		self.Seasons[self.Season] = Season.sort_values('Initiative', ascending=False)
		
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
		dct = {}
		dct['Population'] = [a for a in range(11)]
		dct['Light'] = [(0,0), (-1,1), (0,1), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16)]
		dct['Moderate'] = [(0,0), (0,2), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16), (4,18)]
		dct['Severe'] =  [(-1,1), (1,3), (1,4), (2,5), (2,7), (2,9), (2,11), (2,13), (2,16), (4,18), (4,22)]
		provence_taxation = pd.DataFrame(dct)
		
		for p in range(11):
			temp = self.Provences[self.Provences['Population'] == p].copy()
			if temp.shape[0] > 0:
				for t in ['Light', 'Moderate', 'Severe']:
					temp_ = temp[temp['Taxation'] == t]
					if temp_.shape[0] > 0:
						a,b = provence_taxation[provence_taxation['Population'] == p][t].values[0]
						temp_['Revenue'] = np.random.randint(a,b,temp_.shape[0])
						df = pd.concat((df, temp_[['Regent', 'Revenue']].copy()))
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
		df_ = pd.merge(df_, temp[['Provence', 'B']], right_on='Provence', left_on='Neighbor', how='left')
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
		temp_Regents =  pd.merge(self.Regents.copy(), df, on='Regent', how='left')
		temp_Regents['Gold Bars'] = temp_Regents['Gold Bars'].fillna(0).astype(int) + temp_Regents['Revenue'].fillna(0).astype(int)
		
		# Results!
		temp_Regents['Revenue'] = temp_Regents['Revenue'].fillna(0).astype(int)
		self.Seasons[self.Season] = pd.merge(self.Seasons[self.Season], temp_Regents[['Regent','Gold Bars', 'Revenue']], on='Regent', how='left').fillna(0)
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
		
		# 5.2 Pay Armies
		# DO THIS WHEN I HAVE ARMIES - use lieutenant code as base
		
		# 5.3 Lieutenants
		temp = self.Regents[self.Regents['Lieutenants'].str.len()>0][['Regent', 'Lieutenants', 'Gold Bars']].copy()
		temp = pd.merge(temp, df, on='Regent', how='left').fillna(0)
		lst = []
		for i, row in temp.iterrows():
			lst.append(len(row['Lieutenants']))
			# add in a way to disband if there is not enough money
		temp['Cost'] = lst
		df = pd.concat([df, temp[['Regent','Cost']]], sort=True)
		
		# 5.4 Court Expenses - what can we afford
		df = df[['Regent','Cost']].groupby('Regent').sum().reset_index()
		temp = self.Regents[['Regent', 'Gold Bars']]
		temp = pd.merge(temp, df, on='Regent', how='left').fillna(0)
		temp['Check'] = temp['Gold Bars'] - temp['Cost']
		temp_0 = temp[temp['Check'] <= 1].copy()
		temp_ = temp[temp['Check'] > 1].copy()
		temp_3 = temp_[temp_['Check'] >= 25].copy()
		temp_ = temp_[temp_['Check'] < 25].copy()
		temp_2 = temp_[temp_['Check'] >= 10].copy()
		temp_1 = temp_[temp_['Check'] < 10].copy()
		temp_0['Court'] = 'Dormant'  # no cost
		temp_1['Court'] = 'Bare'	# 2 bars
		temp_1['Cost'] = temp_1['Cost'] = 2
		temp_2['Court'] = 'Average'  # 5 bars
		temp_2['Cost'] = temp_2['Cost'] + 5
		temp_3['Court'] = 'Rich'  # 8 bars
		temp_3['Cost'] = temp_3['Cost'] + 8
		df = pd.concat([temp_0, temp_1, temp_2, temp_3], sort=True)
		
		# add to the thing
		temp = pd.merge(self.Seasons[self.Season], df[['Regent','Cost','Court']], on='Regent', how='left').fillna(0)
		temp['Cost'] = temp['Cost'].astype(int)
		self.Seasons[self.Season] = temp
		
		# lets clear the gold bars
		temp['Gold Bars'] = temp['Gold Bars'] - temp['Cost']
		temp = pd.merge(self.Regents[['Regent', 'Full Name', 'Player', 'Class', 'Level', 'Alignment', 
										'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha',
										'Insight', 'Deception', 'Persuasion',
										'Regency Points', 'Regency Bonus', 'Attitude', 'Lieutenants']], temp[['Regent', 'Gold Bars']])
		self.Regents = temp[['Regent', 'Full Name', 'Player', 
							 'Class', 'Level', 'Alignment', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha',
							 'Insight', 'Deception', 'Persuasion',
							 'Regency Points', 'Gold Bars', 'Regency Bonus', 'Attitude', 'Lieutenants']]
		