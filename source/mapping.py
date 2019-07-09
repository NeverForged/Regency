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
        self.fired = False
        
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
        
    def update_annot(self, ind):

        pos = self.sc.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        N = ind["ind"][0]
        text = self.text_list[N]
        self.annot.set_text(text)
        self.annot.get_bbox_patch()


    def hover(self, event):
        
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
                    
    def show(self, fig_size=(7,7), bg=True, map_alpha=0.5, adj=50
                , caravans=True, shipping=False, roads=True, borders=False, show_holdings = True):
        '''
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
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="-"))
        self.annot.set_visible(False)


        self.text_list = []
        for Prov in node_list:
            text = Prov
            if show_holdings:
                text = text + '\n\nHoldings:'
                temp = Game.Holdings[Game.Holdings['Provence']==Prov]
                for i, row in temp.iterrows():
                    text = text+'\n   {}\n      ({} {})'.format(Game.Regents[Game.Regents['Regent']==row['Regent']]['Full Name'].values[0]
                                                      , row['Type']
                                                      , row['Level'])
                                                      
            self.text_list.append(text)

        # limit size
        if bg == True:
            plt.xlim(xmin-adj,xmax+adj)
            plt.ylim(ymax+adj, ymin-adj)
            

        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        plt.show()
