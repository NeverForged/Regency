import pandas as pd
import networkx as nx
from PIL import Image
import matplotlib.pyplot as plt

class Mapping(object):
    '''
    Draws the maps
    '''
    
    def __init__(self, Game, cam_map='Birthright'):
        '''
        '''
        self.Game = Game
        #try:
        self.G = nx.from_pandas_edgelist(Game.Geography, 'Province', 'Neighbor', ['Border', 'Road', 'Caravan', 'Shipping'])
        #except:
        #    self.G = nx.from_pandas_dataframe(Game.Geography, 'Province', 'Neighbor', ['Border', 'Road', 'Caravan', 'Shipping'])
        self.node_list = list(self.G.nodes)
        if cam_map=='Birthright':
            self.image = Image.open('maps/615dbe4e4e5393bb6ff629b50f02a6ee.jpg')
        else:
            self.image = Image.open('maps'+cam_map)
        self.troop_provinces = []
        
        
    def focus_regents(self, Regents):
        '''
        Only those that border or involve the regent
        '''
        Game = self.Game
        Province_List = []
        Troop_List = []
        self.suptitle = 'Lands & Holdings: '
        lst = []
        for Regent in Regents:
            lst.append(Game.Regents[Game.Regents['Regent']==Regent]['Full Name'].values[0])
            temp = pd.concat([Game.Provinces[Game.Provinces['Regent']==Regent][['Province']]
                     , Game.Holdings[Game.Holdings['Regent']==Regent][['Province']]], sort=False)
            Province_List = list(set(Province_List + list(temp['Province'])))
            # troop stuff
            temp = Game.Troops[Game.Troops['Regent']==Regent].copy()
            temp2 = temp[temp['Type'].str.lower().str.contains('scout')]
            temp2 = pd.merge(temp2[['Province']], Game.Geography[Game.Geography['Border']==1].copy(), on='Province', how='left')
            temp = pd.concat([temp[['Province']], temp2[['Neighbor']]], keys=['Province'])
            Troop_List = list(set(Province_List + list(temp['Province'])))
        self.suptitle = self.suptitle + ', '.join(lst)
        temp = pd.merge(temp, Game.Geography[Game.Geography['Border']==1].copy(), on='Province')
        Province_List = list(set(Province_List + list(temp['Neighbor'])))
        self.node_list = Province_List
        self.troop_provinces = Troop_List
        
        
        
    def focus_domains(self, domains):
        '''
        '''
        Game = self.Game
        Province_List = []
        self.suptitle = 'Map of {}'.format(', '.join(domains))
        for domain in domains:
            Province_List = list(set(Province_List + list(Game.Provinces[Game.Provinces['Domain']==domain]['Province'])))
        self.node_list = Province_List  
        self.troop_provinces = Province_List
        
    def focus_regions(self, regions):
        '''
        '''
        Game = self.Game
        Province_List = []
        self.suptitle = 'Map of {}'.format(', '.join(regions))
        for region in regions:
            Province_List = list(set(Province_List + list(Game.Provinces[Game.Provinces['Region']==region]['Province'])))
        self.node_list = Province_List
        self.troop_provinces = Province_List        
        
    def update_annot(self, ind):
        '''
        Needed to turn on annotation
        '''
        pos = self.sc.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        N = ind["ind"][0]
        text = self.text_list[N]
        self.annot.set_text(text)
        self.annot.get_bbox_patch()


    def hover(self, event):
        '''
        Hover event settings
        '''
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.sc.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()
        self.fired = True
    
    def travel_cost(self, Start, End):
        '''
        Get travel costs, and shortest distances
        '''
        Game = self.Game
        temp = Game.Provences.copy()
        lst = [('Desert', '2'), ('Tundra', '2')
              , ('Mountains', '4'), ('Mountain', '4'), ('Glacier', '4')
              , ('Forest', '2')
              , ('Hills', '2')
              , ('Plains', '2'), ('Farmland', '2'), ('Steppes', '2')
              , ('Swamp', '3'), ('Marsh','3')]
        for a in lst:
            temp['Terrain'] = temp['Terrain'].str.replace(a[0], a[1])
        travel = Game.Geography[Game.Geography['Border']==1]
        travel = pd.concat([travel[travel['Neighbor']==P] for P in list(temp['Provence'])], sort=False)
        temp['A'] = temp['Terrain'].astype(int)
        travel = pd.merge(travel, temp[['Provence', 'A', 'Regent']], on='Provence', how='left')
        temp['B'] = temp['Terrain'].astype(int)
        temp['Other'] = temp['Regent']
        temp['Neighbor'] = temp['Provence']
        travel = pd.merge(travel, temp[['Neighbor', 'B', 'Other']], on='Neighbor', how='left')
        travel = travel.fillna(1)
        # set costs
        travel['Cost'] = ((travel['A'] + travel['B'] + 1)/2).astype(int) - travel['Road']
        # not sure how to stop after, so... Rivers cost 10 to cross
        travel['Cost_Cal'] = travel['Cost'] + (travel['RiverChasm']-travel['Road'])*10
        travel = travel[travel['Provence'] != 0]
        travel = travel[travel['Neighbor'] != 0]
        G = nx.from_pandas_edgelist(travel, source='Provence', target='Neighbor', edge_attr=['Cost', 'Cost_Cal'])
        return nx.shortest_path(G, Start, End, 'Cost_Cal')
        
    def show(self, fig_size=(10,10), bg=True, map_alpha=0.5, adj=100, line_len=90
                , caravans=True, shipping=False, roads=True, borders=False, show_holdings = True
                , show_abbreviations=False, show_troops=False, show_castle=True, show_ships=True
				, printable=False):
        '''
        Show the map
        '''
        
        # make sure we have all provinces for caravans
        Game = self.Game
        '''
        if caravans == True:  # this is for caravan routes, disabled but kept
            temp = pd.merge(pd.DataFrame(self.node_list, columns=['Province']), Game.Geography[Game.Geography['Caravan']>=1]
                            , on='Province', how='left').fillna(0)
            temp = temp[temp['Neighbor']!=0]
            lst = []
            if temp.shape[0]>0:
                for i, row in temp.iterrows():
                    lst = lst + self.travel_cost(row['Province'], row['Neighbor'])
                lst = list(set(lst))
                self.node_list = list(set(self.node_list + lst))
        '''      
            
        node_list = self.node_list
        G = self.G
        
        self.fig, self.ax = plt.subplots(1,1, figsize=fig_size, num=self.suptitle)
        fig = self.fig
        ax = self.ax
        if bg == True:
            ax.imshow(self.image, alpha=map_alpha)

        # Positions
        pos = {}
        Provinces = pd.merge(pd.DataFrame(node_list, columns=['Province']), Game.Provinces, on='Province', how='left')
        xmin, xmax = Provinces['Position'].values[0][0], Provinces['Position'].values[0][0]
        ymin, ymax = Provinces['Position'].values[0][1], Provinces['Position'].values[0][1]
        for pro in list(node_list):
            x =  Game.Provinces[Game.Provinces['Province']==pro]['Position'].values[0][0]
            y =  Game.Provinces[Game.Provinces['Province']==pro]['Position'].values[0][1]
            if x < xmin:
                xmin = x
            elif x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            elif y > ymax:
                ymax = y

            if bg == True:
                pos[pro] = Game.Provinces[Game.Provinces['Province']==pro]['Position'].values[0]
            else:
                pos[pro] = Game.Provinces[Game.Provinces['Province']==pro]['Position'].values[0]*np.array([1,-1])
        nx.draw_networkx_nodes(G, pos
                               ,nodelist=node_list
                               ,alpha=0)

        # edges
        Plist = node_list
        Geography = Game.Geography.copy()
        if caravans:
            edgelist = [(row['Province'], row['Neighbor']) for i, row in Geography[Geography['Caravan']==1].iterrows()
                        if row['Province'] in Plist and  row['Neighbor'] in Plist]
            #temp = pd.merge(pd.DataFrame(self.node_list, columns=['Province']), Game.Geography[Game.Geography['Caravan']>=1]
            #                , on='Province', how='left').fillna(0)
            #temp = pd.merge(pd.DataFrame(self.node_list, columns=['Neighbor']), temp[temp['Neighbor']!=0].copy()
            #                , on='Neighbor', how='left').fillna(0)
            #done_lst = []
            #temp = temp[temp['Province']!=0]
            #temp = temp[temp['Neighbor']!=0]
            #for i, row in temp.iterrows():
            #    if (row['Province'], row['Neighbor']) not in done_lst:
            #        done_lst.append((row['Neighbor'],row['Province']))
            #        lst = self.travel_cost(row['Province'], row['Neighbor'])
            #        edgelist = [(lst[i],lst[i+1]) for i in range(len(lst)-1)]
            nx.draw_networkx_edges(G,pos,edgelist,width=3.0,alpha=0.3,edge_color='xkcd:red', style='dashed')
        if shipping:
            edgelist = [(row['Province'], row['Neighbor']) for i, row in Geography[Geography['Shipping']==1].iterrows() 
                        if row['Province'] in Plist and  row['Neighbor'] in Plist]
            nx.draw_networkx_edges(G,pos,edgelist,width=3.0,alpha=0.3,edge_color='xkcd:azure', style='dashed')
        if borders:
            edgelist = [(row['Province'], row['Neighbor']) for i, row in Geography[Geography['Border']==1].iterrows() 
                        if row['Province'] in Plist and  row['Neighbor'] in Plist]
            nx.draw_networkx_edges(G,pos,edgelist,width=5,alpha=0.25,edge_color='xkcd:grey')
        if roads:
            edgelist = [(row['Province'], row['Neighbor']) for i, row in Geography[Geography['Road']==1].iterrows() 
                        if row['Province'] in Plist and  row['Neighbor'] in Plist]
            nx.draw_networkx_edges(G,pos,edgelist,width=2.0,alpha=0.5,edge_color='xkcd:brown')

        # labels
        temp = pd.merge(pd.DataFrame(node_list, columns=['Province']), Game.Provinces.copy(), on='Province', how='left')
        temp['Label'] = temp['Province'] + '\n ' + temp['Population'].astype(int).astype(str) + '/' + temp['Magic'].astype(int).astype(str)
        labels={}
        for i, row in temp.iterrows():
            if row['Capital']:
                labels[row['Province']] =  '*' + row['Label']
            else:
                labels[row['Province']] =  row['Label']
        nx.draw_networkx_labels(G,pos,labels,font_size=10)
        
        # scaterplot
        X = []
        Y = []

        
        Names = []
        for key, value in pos.items():
            X.append(value[0])
            Y.append(value[1])
            Names.append(key)
        self.sc = ax.scatter(X, Y, s=500, alpha=0)
        self.annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                        bbox=dict(boxstyle="square", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        # annotation text
        self.text_list = []
        self.regents_list =[]
        for Prov in node_list:
            text = ''
            name = []
            for word in Prov.split():
                name.append(r"$\bf{" + word + "}$")
            
            text = text + ' '.join(name)
            text = text +' '+ r"$\bf{" + '{}/{}'.format(Game.Provinces[Game.Provinces['Province']==Prov]['Population'].values[0], Game.Provinces[Game.Provinces['Province']==Prov]['Magic'].values[0]) +"}$"
            # capital
            if Game.Provinces[Game.Provinces['Province']==Prov]['Capital'].values[0] == True:
                text = text + ' [Capital]'
            # Regent
            name = []
            text = text+'\n' + r"$\bf{" + '[' + "}$"
            for word in Game.Provinces[Game.Provinces['Province']==Prov]['Domain'].values[0].split():
                name.append(r"$\bf{" + word + "}$")
            
            text = text + ' '.join(name) + r"$\bf{" + ']' + r"}$"
            # add regent name
            if Game.Regents[Game.Regents['Regent'] == Game.Provinces[Game.Provinces['Province']==Prov]['Regent'].values[0]].shape[0]>0:
                text = text + '\n' + Game.Regents[Game.Regents['Regent'] == Game.Provinces[Game.Provinces['Province']==Prov]['Regent'].values[0]]['Full Name'].values[0]
            else:
                text = text + '\n(Unclaimed)' 
            if show_castle:
                if Game.Provinces[Game.Provinces['Province']==Prov]['Castle'].values[0] > 0:
                    text = text+'\n'+Game.Provinces[Game.Provinces['Province']==Prov]['Castle Name'].values[0] + ' (Castle '+ str(Game.Provinces[Game.Provinces['Province']==Prov]['Castle'].values[0])+')'
            if show_holdings:
                # holdings!
                text = text +'\n'
                for holdtype in ['Law', 'Temple', 'Guild', 'Source']:
                    temp = pd.merge(Game.Holdings[Game.Holdings['Province']==Prov],Game.Regents[['Regent', 'Full Name']], on='Regent', how='left')
                    temp = temp[temp['Type']==holdtype]
                    #temp['Regent'] = temp['Full Name'].str[:20]
                    temp = temp.sort_values('Level', ascending=False)
                    if temp.shape[0] > 0:  # in case there are no Holdings of that type
                        text = text +'\n'+temp[['Regent', 'Type', 'Level']].to_string(index=False, col_space=8, header=False, justify='left')
                    self.regents_list = list(set(self.regents_list + list(temp['Regent'])))  
            if show_troops:
                temp = Game.Troops[Game.Troops['Province']==Prov].copy()
                temp['units'] = 1
                temp = temp[['Regent', 'Type', 'units']].groupby(['Regent', 'Type']).sum().reset_index()
                if Prov in self.troop_provinces and temp.shape[0] > 0:
                    text = text +'\n\n'+temp[['Regent', 'units', 'Type']].to_string(index=False, col_space=8, header=False, justify='left')
                    self.regents_list = list(set(self.regents_list + list(temp['Regent'])))  
                elif temp.shape[0] > 0:
                    # figure out allies or enemies
                    allies, enemies = Game.allies_enemies(Game.Provinces[Game.Provinces['Province']==Prov]['Regent'].values[0])
                    temp2 = pd.merge(temp, allies, on='Regent')
                    if temp2.shape[0] > 0:
                        text = text +'\n\n'+'Allied Units Present'
                    
                    temp2 = pd.merge(temp, enemies, on='Regent')
                    if temp2.shape[0] > 0:
                        text = text +'\n\n'+'Enemy Units Present'
                self.regents_list = list(set(self.regents_list + list(temp['Regent'])))
            if show_ships:
                temp = Game.Navy[Game.Navy['Province']==Prov].copy()
                temp = temp.sort_values('Troop Capacity', ascending=False)
                temp['Ship'] = '(' + temp['Ship'].astype(str) + ')'
                temp['Name'] = '"' + temp['Name'].astype(str) + '"'
                if temp.shape[0]>0:
                    text = text +'\n\n'+temp[['Name', 'Ship']].to_string(index=False, col_space=8, header=False, justify='left')
            
                self.regents_list = list(set(self.regents_list + list(temp['Regent'])))        
            self.text_list.append(text)

        # limit size
        if bg == True:
            plt.xlim(xmin-adj,xmax+adj)
            plt.ylim(ymax+adj, ymin-adj)
        if show_abbreviations == True:
            xlabel = []
            for reg in self.regents_list:
                try:
                    xlabel.append(reg+' = '+Game.Regents[Game.Regents['Regent']==reg].iloc[0]['Full Name'])
                except:
                    print(reg)
			
            xtext =  r"$\bf{"+ 'Abbreviations:'+ r"}$" + ' ' +'; '.join(xlabel) 
            N = line_len
            while N < len(xtext):
                N = xtext.find(' ', N)
                xtext = xtext[:N] + '\n' + xtext[N+1:]
                N = line_len + N - N%line_len
				
			if printable == True:
				xtext = xtext + '\n\n'+'\n\n'.join(self.text_list)
            ax.set_xlabel(xtext)

        # Turn off tick labels
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
       
        plt.show()
