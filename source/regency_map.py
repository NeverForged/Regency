import os
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from PIL import Image
from random import randint
import matplotlib.pyplot as plt
from source.DQNAgent import DQNAgent
from IPython.display import clear_output


class Regency_Map(object):
    '''
    Mapping Held Seperate
    '''
    
    def __init__(self, game=None):
        '''
        '''
        self.Game = game
        
    def show_map(self, borders=False, roads=True, caravans=False, shipping=False, bg=True, adj=50, fig_size=(12,12)
               , cam_map='Birthright', map_alpha = 0.5, axis=False, regions=None, castle=False, domains=None, regents=None
               , holdings=True, Troops=False, Castles=True):
        '''
        Map it
        '''
        Game = self.Game
        Geography = Game.Geography.copy()
        if regions == None and domains==None and regents==None:
            Provences = Game.Provences.copy().reset_index()
        else:
            Provences = pd.DataFrame()
            if regions != None:
                Provences = pd.concat([Provences, pd.concat([ Game.Provences[ Game.Provences['Region']==Region] for Region in regions])], sort=False).reset_index()
            if domains != None:
                Provences = pd.concat([Provences, pd.concat([ Game.Provences[ Game.Provences['Domain']==Domain] for Domain in domains])], sort=False).reset_index()
            if regents != None:
                Provences = pd.concat([Provences, pd.concat([ Game.Provences[ Game.Provences['Regent']==regent] for regent in regents])], sort=False).reset_index()
            
        Regents = Game.Regents.copy()
        Diplomacy = Game.Relationships.copy()
        
        fig, ax = plt.subplots(1,1, figsize=fig_size)
        if bg:
            if cam_map=='Birthright':
                image = Image.open('maps/615dbe4e4e5393bb6ff629b50f02a6ee.jpg')
            else:
                image = Image.open('maps'+cam_map)
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
        
        if player_regents.shape[0] > 0:
            npc_regents = Regents[Regents['Player']==False]
            
            dip = pd.merge(Diplomacy,player_regents,on='Regent',how='left')
            dip['Rank'] = dip['Diplomacy'] + dip['Vassalage']
            dip = dip[['Other','Rank']].groupby('Other').sum().reset_index()
            dip['Regent'] = dip['Other']
            
            npc_regents = pd.merge(npc_regents, dip[['Regent', 'Rank']], on='Regent', how='outer').fillna(0)
        else:
            # no players, go by attitude:
            player_regents = Regents[Regents['Alignment'].str.contains('G')==True]
            npc_regents = Regents[Regents['Alignment'].str.contains('G')==False]
            npc_regents_e = npc_regents[npc_regents['Alignment'].str.contains('E')==True]
            npc_regents_n = npc_regents[npc_regents['Alignment'].str.contains('E')==False]
            npc_regents_e['Rank'] = -10
            npc_regents_n['Rank'] = 3
            npc_regents = pd.concat([npc_regents_e, npc_regents_n], sort=False)
        self.pos = pos    
        # player nodes
        nodes = []
        capitals = []
        nodelist = []
        node_size = []
        node_shape = []
        colors = []
        for reg in list(player_regents['Regent']):
            temp = Provences[Provences['Regent']==reg]
            nodes = nodes + list(temp[temp['Capital']==False]['Provence'])
            capitals = capitals + list(temp[temp['Capital']==True]['Provence'])
        nodes = list(set(nodes))
        capitals = list(set(capitals))
        for node in nodes:
            nodelist.append(node)
            node_size.append(50)
            colors.append('b')
            node_shape.append('o')
        for node in capitals:
            nodelist.append(node)
            node_size.append(50)
            colors.append('b')
            node_shape.append('*')
        '''
        self.A = nx.draw_networkx_nodes(G,pos,
                               nodelist=nodes,
                               node_color='b',
                               node_size=50,
                               alpha=0.25)
        self.B = nx.draw_networkx_nodes(G,pos,node_shape='*',
                               nodelist=capitals,
                               node_color='b',
                               node_size=500,
                               alpha=0.25)
        '''

        # friendly and neutral provences
        nodes = []
        capitals = []
        
        for reg in list(npc_regents[npc_regents['Rank']>=0]['Regent']):
            temp = Provences[Provences['Regent']==reg]
            nodes = nodes + list(temp[temp['Capital']==False]['Provence'])
            capitals = capitals + list(temp[temp['Capital']==True]['Provence'])
        nodes = list(set(nodes))
        capitals = list(set(capitals))
        for node in nodes:
            nodelist.append(node)
            node_size.append(50)
            colors.append('g')
            node_shape.append('o')
        for node in capitals:
            nodelist.append(node)
            node_size.append(50)
            colors.append('g')
            node_shape.append('*')
        '''
        self.C = nx.draw_networkx_nodes(G,pos,
                               nodelist=nodes,
                               node_color='g',
                               node_size=50,
                               alpha=0.25)
        self.D = nx.draw_networkx_nodes(G,pos,node_shape='*',
                               nodelist=capitals,
                               node_color='g',
                               node_size=500,
                               alpha=0.25)
        '''
        # enemy provences
        nodes = []
        capitals = []
        for reg in list(npc_regents[npc_regents['Rank']<0]['Regent']):
            temp = Provences[Provences['Regent']==reg]
            nodes = nodes + list(temp[temp['Capital']==False]['Provence'])
            capitals = capitals + list(temp[temp['Capital']==True]['Provence'])
        nodes = list(set(nodes))
        capitals = list(set(capitals))
        for node in nodes:
            nodelist.append(node)
            node_size.append(50)
            colors.append('r')
            node_shape.append('o')
        for node in capitals:
            nodelist.append(node)
            node_size.append(50)
            colors.append('r')
            node_shape.append('*')
        '''
        self.E = nx.draw_networkx_nodes(G,pos,
                               nodelist=nodes,
                               node_color='r',
                               node_size=50,
                               alpha=0.25)
        self.F = nx.draw_networkx_nodes(G,pos,node_shape='*',
                               nodelist=capitals,
                               node_color='r',
                               node_size=500,
                               alpha=0.25)
        '''
        self.Provence_Drawn = nx.draw_networkx_nodes(G,pos
                                                       , nodelist=nodelist
                                                       , node_color=colors
                                                       , node_size=node_size
                                                       , alpha=0.25)
        self.annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        # edges
        Plist = list(Provences['Provence'])
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
        fig.canvas.mpl_connect("motion_notify_event", self.hover)
        plt.show()
        
    def update_annot(self, ind, sc):
        pos = self.Provence_Drawn.get_offsets()[ind["ind"][0]]
        # pos = self.pos
        self.annot.xy = pos
        text = "{},\n {}".format(" ".join(list(map(str,ind["ind"]))), 
                               " ".join([names[n] for n in ind["ind"]]))
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
        self.annot.get_bbox_patch().set_alpha(0.4)

    
    def hover(self, event):
        vis = annot.get_visible()
        if event.inaxes == ax:
                cont, ind = self.Provence_Drawn.contains(event)
                if cont:
                    self.update_annot(ind, sc)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()