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
        self.G = nx.from_pandas_edgelist(Game.Geography, 'Provence', 'Neighbor', ['Border', 'Road', 'Caravan', 'Shipping'])
        #except:
        #    self.G = nx.from_pandas_dataframe(Game.Geography, 'Provence', 'Neighbor', ['Border', 'Road', 'Caravan', 'Shipping'])
        self.node_list = list(self.G.nodes)
        if cam_map=='Birthright':
            self.image = Image.open('maps/615dbe4e4e5393bb6ff629b50f02a6ee.jpg')
        else:
            self.image = Image.open('maps'+cam_map)
        self.troop_provences = []
        
    def focus_regent(self, Regent):
        '''
        Only those that border or involve the regent
        '''
        Game = self.Game
        temp = pd.concat([Game.Provences[Game.Provences['Regent']==Regent][['Provence']]
                     , Game.Holdings[Game.Holdings['Regent']==Regent][['Provence']]], sort=False)
        Provence_List = list(set(temp['Provence']))
        temp = pd.merge(temp, Game.Geography, on='Provence')
        Provence_List = list(set(Provence_List + list(temp['Neighbor'])))
        self.node_list = Provence_List
        temp = Game.Troops[Game.Troops['Regent']==Regent].copy()
        temp2 = temp[temp['Type'].str.lower().str.contains('scout')]
        temp2 = pd.merge(temp2[['Provence']], Game.Geography, on='Provence', how='left')
        temp = pd.concat([temp[['Provence']], temp2[['Neighbor']]], keys=['Provence'])

        self.troop_provences = list(set(temp['Provence']))
        
    def focus_regents(self, Regents):
        '''
        Only those that border or involve the regent
        '''
        Game = self.Game
        Provence_List = []
        Troop_List = []
        for Regent in Regents:
            temp = pd.concat([Game.Provences[Game.Provences['Regent']==Regent][['Provence']]
                     , Game.Holdings[Game.Holdings['Regent']==Regent][['Provence']]], sort=False)
            Provence_List = list(set(Provence_List + list(temp['Provence'])))
            # troop stuff
            temp = Game.Troops[Game.Troops['Regent']==Regent].copy()
            temp2 = temp[temp['Type'].str.lower().str.contains('scout')]
            temp2 = pd.merge(temp2[['Provence']], Game.Geography, on='Provence', how='left')
            temp = pd.concat([temp[['Provence']], temp2[['Neighbor']]], keys=['Provence'])
            Troop_List = list(set(Provence_List + list(temp['Provence'])))
        temp = pd.merge(temp, Game.Geography, on='Provence')
        Provence_List = list(set(Provence_List + list(temp['Neighbor'])))
        self.node_list = Provence_List
        self.troop_provences = Troop_List
        
        
    def focus_domain(self, domains):
        '''
        '''
        Game = self.Game
        Provence_List = []
        for domain in domains:
            Provence_List = list(set(Provence_List + list(Game.Provences[Game.Provences['Domain']==domain]['Provence'])))
        self.node_list = Provence_List  
        self.troop_provences = Provence_List
        
    def focus_regions(self, regions):
        '''
        '''
        Game = self.Game
        Provence_List = []
        for region in regions:
            Provence_List = list(set(Provence_List + list(Game.Provences[Game.Provences['Region']==region]['Provence'])))
        self.node_list = Provence_List
        self.troop_provences = Provence_List        
        
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
                    
    def show(self, fig_size=(10,10), bg=True, map_alpha=0.5, adj=100, line_len=150
                , caravans=True, shipping=False, roads=True, borders=False, show_holdings = True
                , show_abbreviations=False, show_troops=False, show_castle=True):
        '''
        Show the map
        '''
        Game = self.Game
        node_list = self.node_list
        G = self.G
        
        self.fig, self.ax = plt.subplots(1,1, figsize=fig_size)
        fig = self.fig
        ax = self.ax
        if bg == True:
            ax.imshow(self.image, alpha=map_alpha)

        # Positions
        pos = {}
        xmin, xmax = Game.Provences['Position'].values[0][0], Game.Provences['Position'].values[0][0]
        ymin, ymax = Game.Provences['Position'].values[0][1], Game.Provences['Position'].values[0][1]
        for pro in list(node_list):
            x =  Game.Provences[Game.Provences['Provence']==pro]['Position'].values[0][0]
            y =  Game.Provences[Game.Provences['Provence']==pro]['Position'].values[0][1]
            if x < xmin:
                xmin = x
            elif x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            elif y > ymax:
                ymax = y

            if bg == True:
                pos[pro] = Game.Provences[Game.Provences['Provence']==pro]['Position'].values[0]
            else:
                pos[pro] = Game.Provences[Game.Provences['Provence']==pro]['Position'].values[0]*np.array([1,-1])
        nx.draw_networkx_nodes(G, pos
                               ,nodelist=node_list
                               ,alpha=0)

        # edges
        Plist = node_list
        Geography = Game.Geography.copy()
        if caravans:
            edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Caravan']==1].iterrows() 
                        if row['Provence'] in Plist and  row['Neighbor'] in Plist]
            nx.draw_networkx_edges(G,pos,edgelist,width=2.0,alpha=0.3,edge_color='xkcd:red',style='dotted')
        if shipping:
            edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Shipping']==1].iterrows() 
                        if row['Provence'] in Plist and  row['Neighbor'] in Plist]
            nx.draw_networkx_edges(G,pos,edgelist,width=2.0,alpha=0.3,edge_color='xkcd:azure',style='dotted')
        if borders:
            edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Border']==1].iterrows() 
                        if row['Provence'] in Plist and  row['Neighbor'] in Plist]
            nx.draw_networkx_edges(G,pos,edgelist,width=0.5,alpha=0.25,edge_color='xkcd:grey')
        if roads:
            edgelist = [(row['Provence'], row['Neighbor']) for i, row in Geography[Geography['Road']==1].iterrows() 
                        if row['Provence'] in Plist and  row['Neighbor'] in Plist]
            nx.draw_networkx_edges(G,pos,edgelist,width=1.0,alpha=0.5,edge_color='xkcd:brown',style='dashed')

        # labels
        temp = pd.merge(pd.DataFrame(node_list, columns=['Provence']), Game.Provences.copy(), on='Provence', how='left')
        temp['Label'] = temp['Provence'] + '\n ' + temp['Population'].astype(int).astype(str) + '/' + temp['Magic'].astype(int).astype(str)
        labels={}
        for i, row in temp.iterrows():
            if row['Capital']:
                labels[row['Provence']] =  '*' + row['Label']
            else:
                labels[row['Provence']] =  row['Label']
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
            # Regent
            name = []
            text = text+'\n' + r"$\bf{" + '[' + "}$"
            for word in Game.Provences[Game.Provences['Provence']==Prov]['Domain'].values[0].split():
                name.append(r"$\bf{" + word + "}$")
            
            text = text + ' '.join(name) + r"$\bf{" + ']' + "}$"
            text = text + '\n' + Game.Regents[Game.Regents['Regent'] == Game.Provences[Game.Provences['Provence']==Prov]['Regent'].values[0]]['Full Name'].values[0] + '\n'
            if show_castle:
                if Game.Provences[Game.Provences['Provence']==Prov]['Castle'].values[0] > 0:
                    text = text+Game.Provences[Game.Provences['Provence']==Prov]['Castle Name'].values[0] + '(Castle '+ str(Game.Provences[Game.Provences['Provence']==Prov]['Castle'].values[0])+')'+'\n'
            if show_holdings:
                temp = pd.merge(Game.Holdings[Game.Holdings['Provence']==Prov],Game.Regents[['Regent', 'Full Name']], on='Regent', how='left')
                #temp['Regent'] = temp['Full Name'].str[:20]
                temp['Holding'] = temp['Type']
                text = text +'\n'+temp[['Regent', 'Holding', 'Level']].to_string(index=False, col_space=8, header=False, justify='left') + '\n'
                self.regents_list = list(set(self.regents_list + list(temp['Regent'])))  
            if show_troops:
                temp = Game.Troops[Game.Troops['Provence']==Prov]
                temp['units'] = 1
                temp = temp[['Regent', 'Type', 'units']].groupby(['Regent', 'Type']).sum().reset_index()
                if Prov in self.troop_provences and temp.shape[0] > 0:
                    text = text +'\n'+temp[['Regent', 'units', 'Type']].to_string(index=False, col_space=8, header=False, justify='left')
                    self.regents_list = list(set(self.regents_list + list(temp['Regent'])))  
                elif temp.shape[0] > 0:
                    # figure out allies or enemies
                    allies, enemies = Game.allies_enemies(Game.Provences[Game.Provences['Provence']==Prov]['Regent'].values[0])
                    temp2 = pd.merge(temp, allies, on='Regent')
                    if temp2.shape[0] > 0:
                        text = text +'\n'+'Allied Units Present'
                    
                    temp2 = pd.merge(temp, enemies, on='Regent')
                    if temp2.shape[0] > 0:
                        text = text +'\n'+'Enemy Units Present'
                    
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
            xtext =  r"$\bf{"+ 'Abbreviations: '+ "}$" + ' ' +'; '.join(xlabel) 
            N = line_len
            while N < len(text):
                N = text.find(' ', N)
                text = text[:N] + '\n' + text[N+1:]
                N = line_len + N - N%line_len
            ax.set_xlabel(xtext)

        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
       
        plt.show()
