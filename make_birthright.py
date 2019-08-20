import os
from source.regency import Regency
import pandas as pd


def main():
    Game = Regency('Birthright')
    # EASTERN MARCHES
    Region = 'The Eastern Marches'
    domain='Coeranys'
    Game.add_relationship('Sw2', 'WM', Vassalage=2)
    Game.add_relationship('LPA', 'EC', Diplomacy=3, Vassalage=3)
    Game.add_relationship('EC', 'LPA', Diplomacy=3)
    p = 'Bogsend'
    Game.add_province(p, domain, Region, 'EC', 1543, 1985, Population=3, Magic=2, Terrain='Swamp')
    Game.add_holding(p, 'EC', 'Law', 1)
    Game.add_holding(p, 'LPA', 'Temple', 1)
    Game.add_holding(p, 'GH', 'Guild', 3)
    Game.add_holding(p, 'Sw2', 'Source', 2)
    p = 'Caudraight'
    Game.add_province(p, domain, Region, 'EC', 1556, 1914, Population=4, Magic=1)
    Game.add_holding(p, 'EC', 'Law', 2)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'HA', 'Temple', 2)
    Game.add_holding(p, 'DW', 'Guild', 2)
    Game.add_holding(p, 'GH', 'Guild', 2)
    p = 'Deepshadow'
    Game.add_province(p, domain, Region, 'EC', 1550, 1828, Population=3, Magic=2)
    Game.add_holding(p, 'EC', 'Law', 2)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'DW', 'Guild', 3)
    Game.add_holding(p, 'TBM', 'Source', 3)
    p = 'Duornil'
    Game.add_province(p, domain, Region, 'EC', 1606, 1837, Population=2, Magic=3, Waterway=True)
    Game.add_holding(p, 'EC', 'Law', 2)
    Game.add_holding(p, 'LPA', 'Temple', 1)
    Game.add_holding(p, 'DW', 'Guild', 3)
    Game.add_holding(p, 'TBM', 'Source', 2)

    p = 'Mistil'
    Game.add_province(p, domain, Region, 'EC', 1667, 1956, Population=2, Magic=3, Waterway=True)
    Game.add_holding(p, 'EC', 'Law', 1)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'DW', 'Guild', 2)
    Game.add_holding(p, 'TBM', 'Source', 3)

    p = 'Ranien'
    Game.add_province(p, domain, Region, 'EC', 1642, 1912, Population=2, Magic=3, Waterway=True)
    Game.add_holding(p, 'EC', 'Law', 1)
    Game.add_holding(p, 'LPA', 'Temple', 1)
    Game.add_holding(p, 'DW', 'Guild', 2)
    Game.add_holding(p, 'TBM', 'Source', 3)

    p = 'Ruorven'
    Game.add_province(p, domain, Region, 'EC', 1610, 2053, Population=4, Magic=1, Terrain='Swamp', Capital=True, Waterway=True)
    Game.add_holding(p, 'EC', 'Law', 3)
    Game.add_holding(p, 'LPA', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 1)
    Game.add_holding(p, 'EL', 'Guild', 2)
    Game.add_holding(p, 'DW', 'Guild', 2)

    Game.add_geo('Deepshadow', 'Duornil', Border=1)
    Game.add_geo('Caudraight', 'Duornil', Border=1)
    Game.add_geo('Deepshadow', 'Caudraight', Border=1)
    Game.add_geo('Caudraight', 'Ranien', Border=1)
    Game.add_geo('Caudraight', 'Bogsend', Border=1)
    Game.add_geo('Mistil', 'Ranien', Border=1)
    Game.add_geo('Mistil', 'Ruorven', Border=1)
    Game.add_geo('Bogsend', 'Ruorven', Border=1)
    Game.add_geo('Bogsend', 'Ranien', Border=1)
    Game.add_geo('Ranien', 'Ruorven', Border=1)
    Game.add_geo('Ranien', 'Duornil', Border=1)

    domain='Osoerde'

    Game.add_geo('Brothendar', 'Algael', Border=1)
    Game.add_geo('Brothendar', 'Ghalliere', Border=1)
    Game.add_geo('Brothendar', 'Gulfport', Border=1)
    Game.add_geo('Moergen', 'Ghalliere', Border=1)
    Game.add_geo('Moergen', 'Gulfport', Border=1)
    Game.add_geo('Moriel', 'Ghalliere', Border=1)
    Game.add_geo('Moriel', 'Gulfport', Border=1)
    Game.add_geo('Moriel', 'Brothendar', Border=1)
    Game.add_geo('Moriel', 'Moergen', Border=1)
    Game.add_geo('Spiritsend', 'Algael', Border=1)
    Game.add_geo('Spiritsend', 'Gulfport', Border=1)
    Game.add_geo('Spiritsend', 'Brothendar', Border=1)
    Game.add_geo('Spiritsend', 'Moriel', Border=1)
    Game.add_geo('Sunken Lands', 'Gulfport', Border=1)
    Game.add_geo('Sunken Lands', 'Moergen', Border=1, RiverChasm=1)

    Game.add_geo('Sunken Lands', 'Bogsend', Border=1, RiverChasm=1)
    Game.add_geo('Bogsend', 'Moergen', Border=1, RiverChasm=1)
    Game.add_geo('Sunken Lands', 'Ruorven', Border=1, RiverChasm=1)



    Game.add_relationship('JR', 'WM', Diplomacy=-2)
    Game.add_relationship('WM', 'JR', Diplomacy=-3)

    p = 'Algael'
    Game.add_province(p, domain, Region, 'JR', 1355, 2226, Population=2, Magic=3, Terrain='Swamp')
    Game.add_holding(p, 'JR', 'Law', 2)
    Game.add_holding(p, 'IHH', 'Temple', 2)
    Game.add_holding(p, 'DW', 'Guild', 2)
    Game.add_holding(p, 'Sw', 'Source', 3)

    p = 'Brothendar'
    Game.add_province(p, domain, Region, 'JR', 1377, 2177, Population=3, Magic=2, Waterway=True)
    Game.add_holding(p, 'JR', 'Law', 3)
    Game.add_holding(p, 'CSH', 'Temple', 3)
    Game.add_holding(p, 'GH', 'Guild', 3)
    Game.add_holding(p, 'Sw', 'Source', 2)

    p = 'Ghalliere'
    Game.add_province(p, domain, Region, 'JR', 1394, 2110, Population=2, Magic=3)
    Game.add_holding(p, 'JR', 'Law', 1)
    Game.add_holding(p, 'IHH', 'Temple', 2)
    Game.add_holding(p, 'GH', 'Guild', 2)
    Game.add_holding(p, 'Sw2', 'Source', 3)

    p = 'Gulfport'
    Game.add_province(p, domain, Region, 'JR', 1515, 2154, Population=3, Magic=2, Waterway=True)
    Game.add_holding(p, 'JR', 'Law', 3)
    Game.add_holding(p, 'CSH', 'Temple', 2)
    Game.add_holding(p, 'Sw2', 'Source', 2)

    p = 'Moergen'
    Game.add_province(p, domain, Region, 'JR', 1471, 2067, Population=2, Magic=3, Waterway=True)
    Game.add_holding(p, 'WM', 'Law', 2)
    Game.add_holding(p, 'IHH', 'Temple', 2)
    Game.add_holding(p, 'DW', 'Guild', 2)
    Game.add_holding(p, 'Sw2', 'Source', 3)

    p = 'Moriel'
    Game.add_province(p, domain, Region, 'JR', 1448, 2138, Population=4, Magic=1, Capital=True)
    Game.add_holding(p, 'WM', 'Law', 1)
    Game.add_holding(p, 'JR', 'Law', 3)
    Game.add_holding(p, 'CSH', 'Temple', 3)
    Game.add_holding(p, 'TCV', 'Temple', 1)
    Game.add_holding(p, 'DW', 'Guild', 2)
    Game.add_holding(p, 'Sw2', 'Source', 1)

    p = 'Spiritsend'
    Game.add_province(p, domain, Region, 'JR', 1466, 2231, Population=2, Magic=6, Terrain='Swamp', Waterway=True)
    Game.add_holding(p, 'JR', 'Law', 1)
    Game.add_holding(p, 'DW', 'Guild', 2)
    Game.add_holding(p, 'Sw', 'Source', 6)

    p = 'Sunken Lands'
    Game.add_province(p, domain, Region, 'JR',  1541, 2085, Population=2, Magic=6, Terrain='Swamp', Waterway=True)
    Game.add_holding(p, 'WM', 'Law', 2)
    Game.add_holding(p, 'CSH', 'Temple', 2)
    Game.add_holding(p, 'Sw2', 'Source', 6)


    # Baruk-Azhik
    domain = 'Baruk-Azhik'

    for a in range(4):
        Game.add_troops('GG', "Rivenrock", 'Dwarf Guards')
        Game.add_troops('GG', "Rivenrock", 'Dwarf Crossbows')
        

    Game.add_relationship('MF', "GG", Diplomacy=10, Payment=10, Vassalage=2)
    Game.add_relationship('DW', "GG", Diplomacy=10, Payment=10, Vassalage=2)


    p = "Bran's Retreat"
    Game.add_province(p, domain, Region, 'GG', 1599, 1728, Population=4, Magic=1)
    Game.add_holding(p, 'GG', 'Law', 4)
    Game.add_holding(p, 'MF', 'Temple', 4)
    Game.add_holding(p, 'EL', 'Guild', 2)
    Game.add_holding(p, 'DW', 'Guild', 2)

    p = "Cliff's Lament"
    Game.add_province(p, domain, Region, 'GG', 1645, 1790, Population=4, Magic=1, Waterway=True)
    Game.add_holding(p, 'GG', 'Law', 4)
    Game.add_holding(p, 'MF', 'Temple', 4)
    Game.add_holding(p, 'EL', 'Guild', 2)
    Game.add_holding(p, 'DW', 'Guild', 2)

    p = "Land's Victory"
    Game.add_province(p, domain, Region, 'GG', 1743, 1745, Population=3, Magic=6, Terrain='Mountain')
    Game.add_holding(p, 'GG', 'Law', 3)
    Game.add_holding(p, 'MF', 'Temple', 3)
    Game.add_holding(p, 'EL', 'Guild', 3)

    p = "The Promontory"
    Game.add_province(p, domain, Region, 'GG', 1693, 1766, Population=3, Magic=6, Terrain='Mountain')
    Game.add_holding(p, 'GG', 'Law', 3)
    Game.add_holding(p, 'MF', 'Temple', 3)
    Game.add_holding(p, 'EL', 'Guild', 3)

    p = "Rivenrock"
    Game.add_province(p, domain, Region, 'GG', 1678, 1704, Population=5, Magic=4, Capital=True, Terrain='Mountain')
    Game.add_holding(p, 'GG', 'Law', 5)
    Game.add_holding(p, 'MF', 'Temple', 5)
    Game.add_holding(p, 'ML', 'Guild', 3)
    Game.add_holding(p, 'DW', 'Guild', 2)

    Game.add_geo("Bran's Retreat", 'Deepshadow', Border=1)
    Game.add_geo("Cliff's Lament", 'Deepshadow', Border=1)
    Game.add_geo("Cliff's Lament", 'Duornil', Border=1)
    Game.add_geo("Cliff's Lament", "Bran's Retreat", Border=1)
    Game.add_geo("Bran's Retreat", "Rivenrock", Border=1)
    Game.add_geo("Cliff's Lament", "The Promontory", Border=1)
    Game.add_geo("Rivenrock", "The Promontory", Border=1)
    Game.add_geo("Rivenrock", "Land's Victory", Border=1)
    Game.add_geo("The Promontory", "Land's Victory", Border=1)
    Game.add_geo("Bran's Retreat", "The Promontory", Border=1)

    Game.add_geo("Rivenrock", "Ruorven", Caravan=1)
    Game.add_geo("Rivenrock", "Fhylallien", Caravan=1)

    Game.add_relationship('DW', 'GG', Diplomacy=3, Vassalage=1)
    Game.add_relationship('GG', 'DW', Diplomacy=3)


    domain='The Chimaeron'
    lst = ['Barniere', 'Careine', 'Hamein', 'Lyssan', 'Mhowe', 'Ruorkhe', 'Salviene']


    for i, p in enumerate(lst):
        if i == 0:
            x, y, Population, Magic, Terrain, Capital, Waterway = 1798, 1906, 1, 4, 'Plains', False, True
        elif i == 1:
            x, y, Population, Magic, Terrain, Capital, Waterway = 1672, 1875, 2, 6, 'Hills', False, True
        elif i == 2:
            x, y, Population, Magic, Terrain, Capital, Waterway = 1797, 1977, 1, 5, 'Plains', False, True
        elif i == 3:
            x, y, Population, Magic, Terrain, Capital, Waterway = 1736, 1947, 2, 7, 'Mountain', True, True
        elif i == 4:
            x, y, Population, Magic, Terrain, Capital, Waterway = 1830, 2078, 2, 4, 'Hills', False, True
        elif i == 5:
            x, y, Population, Magic, Terrain, Capital, Waterway = 1751, 1851, 1, 6, 'Mountain', False, True
        elif i == 6:
            x, y, Population, Magic, Terrain, Capital, Waterway = 1762, 2031, 1, 5, 'Mountain', False, True
        Game.add_province(p, domain, Region, 'CoL', x, y, Population=Population, Magic=Magic, Capital=Capital, Waterway=Waterway)
        
        if i == 0:
            Game.add_holding(p, 'CoL', 'Law', 1)
            Game.add_holding(p, 'Ch', 'Source', 4)
            Game.add_geo(p, 'Hamein', Border=1)
            Game.add_geo(p, "Lyssan", Border=1)
            Game.add_geo(p, "Ruorkhe", Border=1)
        elif i == 1:
            Game.add_holding(p, 'CoL', 'Law', 1)
            Game.add_holding(p, 'TF', 'Temple', 1)
            Game.add_holding(p, 'CoL', 'Guild', 2)
            Game.add_holding(p, 'Ch', 'Source', 5)
            Game.add_geo(p, "Cliff's Lament", Border=1)
            Game.add_geo(p, "Duornil", Border=1, RiverChasm=1)
            Game.add_geo(p, "Ranien", Border=1, RiverChasm=1)
            Game.add_geo(p, "Mistil", Border=1, RiverChasm=1)
            Game.add_geo(p, "Ruorkhe", Border=1)
            Game.add_geo(p, "Lyssan", Border=1)
        elif i == 2:
            Game.add_holding(p, 'CoL', 'Law', 1)
            Game.add_holding(p, 'WB', 'Temple', 1)
            Game.add_holding(p, 'CoL', 'Guild', 1)
            Game.add_holding(p, 'TBM', 'Source', 4)
            Game.add_geo(p, "Lyssan", Border=1)
            Game.add_geo(p, "Salviene", Border=1)
            Game.add_geo(p, "Mhowe", Border=1)
        elif i == 3:
            Game.add_holding(p, 'CoL', 'Law', 2)
            Game.add_holding(p, 'WB', 'Temple', 1)
            Game.add_holding(p, 'TF', 'Temple', 1)
            Game.add_holding(p, 'CoL', 'Guild', 2)
            Game.add_holding(p, 'Ch', 'Source', 7)
            Game.add_geo(p, "Ruorkhe", Border=1)
            Game.add_geo(p, "Mistil", Border=1, RiverChasm=1)
            Game.add_geo(p, "Salviene", Border=1)
            Game.add_geo(p, "Ruorkhe", Border=1)
        elif i == 4:
            Game.add_holding(p, 'CoL', 'Law', 2)
            Game.add_holding(p, 'CoL', 'Guild', 2)
            Game.add_holding(p, 'TBM', 'Source', 4)
            Game.add_geo(p, "Salviene", Border=1)
        elif i == 5:
            Game.add_holding(p, 'CoL', 'Law', 1)
            Game.add_holding(p, 'CoL', 'Guild', 1)
            Game.add_holding(p, 'Ch', 'Source', 6)
            Game.add_geo(p, "The Promontory", Border=1)
            Game.add_geo(p, "Cliff's Lament", Border=1)
        elif i == 6:
            Game.add_holding(p, 'CoL', 'Law', 1)
            Game.add_holding(p, 'Ch', 'Source', 5)
            
    Game.add_relationship('TBM', 'Ch', Diplomacy=-1)
    Game.add_relationship('Col', 'Ch', Diplomacy=-1, Vassalage=1)
    Game.add_relationship('Ch', 'CoL', Diplomacy=1)
    Game.add_relationship('Ch', 'TBM', Diplomacy=-1)

    domain='The Sielwode'
    lst = ['Annydwr', 'Cu Haellyrd', 'Fhylallien', 'Ghyllwn', 'Hoehnaen', 'Iseare', 'Llewhoellen', 'Tuar Llyrien', 'Ywrndor']

    for i, p in enumerate(lst):
        if i == 0:
            x, y, Population, Magic, Capital = 1360, 1640, 2, 6, False
            Game.add_geo(p, 'Ghyllwn', Border=1)
            Game.add_geo(p, 'Llewhoellen', Border=1)
        if i == 1:
            x, y, Population, Magic, Capital = 1650, 1610, 3, 6, False
            Game.add_geo(p, 'Iseare', Border=1)
            Game.add_geo(p, 'Rivenrock', Border=1)
            Game.add_geo(p, 'Tuar Llyrien', Border=1)
        if i == 2:
            x, y, Population, Magic, Capital = 1520, 1680, 6, 5, True
            Game.add_geo(p, "Bran's Retreat", Border=1)
            Game.add_geo(p, 'Ywrndor', Border=1)
            Game.add_geo(p, 'Iseare', Border=1)
            Game.add_geo(p, 'Tuar Llyrien', Border=1)
            Game.add_geo(p, 'Llewhoellen', Border=1)
        if i == 3:
            x, y, Population, Magic, Capital = 1440, 1615, 2, 6, False
            Game.add_geo(p, 'Tuar Llyrien', Border=1)
            Game.add_geo(p, 'Llewhoellen', Border=1)
        if i == 4:
            x, y, Population, Magic, Capital = 1420, 1790, 3, 6, False
            Game.add_geo(p, 'Ywrndor', Border=1)
            Game.add_geo(p, 'Llewhoellen', Border=1)
        if i == 5:
            x, y, Population, Magic, Capital = 1610, 1640, 4, 5, False
            Game.add_geo(p, 'Rivenrock', Border=1)
            Game.add_geo(p, "Bran's Retreat", Border=1)
            Game.add_geo(p, 'Tuar Llyrien', Border=1)
            Game.add_geo(p, 'Ywrndor', Border=1)
        if i == 6:
            x, y, Population, Magic, Capital = 1450, 1685, 3, 6, False
            Game.add_geo(p, 'Tuar Llyrien', Border=1)
        if i == 7:
            x, y, Population, Magic, Capital = 1520, 1610, 2, 6, False
        if i == 8:
            x, y, Population, Magic, Capital = 1495, 1780, 2, 6, False
        Game.add_province(p, domain, Region, 'Is', x, y, Population=Population, Magic=Magic, Terrain='Forest', Capital=Capital)
        Game.add_holding(p, 'Is', 'Law', Population)
        Game.add_holding(p, 'Is', 'Source', Magic)
        
    Game.add_relationship('Is', 'GG', Diplomacy=1)
    Game.add_relationship('GG', 'Is', Diplomacy=1)
    
    Game.add_regent('EC', 'Eluvie Cariele', Archetype='Noble', Alignment='CG', Regency_Bonus=2
                , Attitude='Peaceful', Lieutenants=['Aedric Bherenstae']
                , Bloodline='Ma', Culture='A')
    Game.add_regent('LPA', 'Life and Protection of Avanalae (Medhlorie Haensen)', Archetype='Priest'
                    , Regency_Bonus=3, Bloodline='An', Culture='A')

    Game.add_regent('Sw2', 'Second Swamp Mage', Archetype='Mage', Alignment='NG', Regency_Points=9
                    , Gold_Bars=3, Bloodline='Vo', Regency_Bonus=-1, Culture='A')

    Game.add_regent('DW', "Diirk Watersold (Royal Guild of Baruk-Azhir)", Archetype='Bandit Captain'
                    , Alignment='NG', Race='Dwarf', Regency_Points=45, Gold_Bars=33, Regency_Bonus=1
                    , Bloodline='An', Culture='D')
    Game.add_regent('TBM', "Three Brother Mages", Archetype='Mage', Culture='A', Bloodline='Vo', Regency_Bonus=1)

    Game.add_regent('MF', "Moradin's Forge (Ruarch Rockhammer)", Archetype='Cult Fanatic', Alignment='LG', Race='Dwarf'
                    , Regency_Points=42, Gold_Bars = 28, Culture='D', Bloodline='An')

    Game.add_regent('JR', 'Jaison Raenech', Archetype='Knight', Alignment='LE', Regency_Bonus=3
                         , Attitude='Aggressive', Lieutenants=['Terence Gryphon'], Culture='A', Bloodline='Br')
    Game.add_regent('WM', 'Willaim Moergen', Archetype='Noble', Alignment='CG', Regency_Bonus=3
                    , Culture='A', Bloodline='An')
    Game.add_regent('GG', 'Overthane Grimm Graybeard', Class='Fighter/Cleric', Race='Dwarf', Alignment='LG', Regency_Bonus=3
                        , Regency_Points=35, Gold_Bars=40, Bloodline='An', Culture='D'
                        , Str=4, Dex=0, Con=4, Int=2, Wis=3, Cha=2, Divine=True, Level=16
                        , Attitude='Peaceful', Lieutenants=['Thane Thorvold', 'Thane Dorn', 'Thane Baldur', 'Thane Gimli'])

    Game.add_regent('Ch', 'The Chimera', Archetype='Archmage', Race='Elf', Alignment='CE', Regency_Bonus=5
                    , Attitude='Aggressive', Bloodline='Az')
    Game.change_regent('Ch', Class='Awnsheghlien')
    Game.add_regent('Is', 'Emerald Queen Isaelie', Race='Elf', Alignment='NN', Archetype='Archmage'
                    , Regency_Bonus=4, Lieutenants = ['Corwin Rhysdiordan'], Attitude='Xenophobic'
                    , Culture = 'E', Bloodline = 'Vo')
    Game.add_regent('CoL', 'Council of Leaders', Alignment='CE', Culture='A', Bloodline='An', Regency_Bonus=0
                    , Lieutenants = ['Constable of ' + a for a in lst], Archetype='Commoner')

    Game.add_regent('Sw', 'Swamp Mage', Archetype='Mage', Alignment='N', Regency_Points=9
                    , Gold_Bars=3, Bloodline='Vo', Regency_Bonus=0, Culture='A')


    Game.add_geo('Ywrndor', 'Deepshadow', Border=1)

    Game.add_regent('CSH', "Church of Storm's Height (Wincae Raenech)", Alignment='CN', Bloodline='Br', Regency_Bonus=3
                    , Archetype='Priest')
    Game.add_relationship('CSH', 'JR', Diplomacy=1)
    Game.add_relationship('JR', 'CSH', Diplomacy=1)

    Game.add_regent('TCV', 'One True Church of Vosgaard (Sugat Tsorich)', Culture='V', Bloodline='Ma', Regency_Bonus=2
                    , Archetype='Priest', Alignment='CE')

    Game.add_regent('TF', 'The Fortress (Tugaere Issimane)', Archetype='Cult Fanatic', Culture='A', Bloodline='An'
                    , Alignment='CG', Regency_Bonus=3)

    Game.add_regent('WB', "Water's Blessing (Phisiad Uriene)", Archetype='Priest', Alignment='NG', Culture='A'
                   ,Bloodline='Vo', Regency_Bonus=1)
                   
    for a in range(3):
        Game.add_ship('JR', 'Gulfport', 'Galleon')
        Game.add_ship('JR', 'Gulfport', 'Caravel')
        Game.add_ship('JR', 'Gulfport', 'Caravel')
        Game.add_ship('EC', 'Ruorven', 'Caravel')
        if a != 2:
            Game.add_ship('JR', 'Gulfport', 'Coaster')
            
    Region = 'The Heartlands'
    d = 'Avanil'
    Game.add_regent('DA', 'Darien Avan', Class='Fighter', Level=9, Alignment='LN', Regency_Bonus=5
                    , Regency_Points=110, Gold_Bars=160, Culture='A', Bloodline='An'
                    , Str=3, Dex=4, Con=1, Int=3, Wis=1, Cha=3, Insight=5, Deception=7, Persuasion=7
                    , Attitude='Aggressive', Lieutenants=['Dheraene Bhailie'])
    lst = ['Anuire', 'Avarien', 'Bherin', 'Caulnor', 'Daulton', 'Duriene', 'Nentril', 'Taliern', 'Vanilen']

    p = lst[0]
    Game.add_province(p, d, Region, 'DA', Population=7, Magic=0, x=790, y=2215, Waterway=True)
    Game.add_holding(p, 'DA', 'Law', 7)
    Game.add_holding(p, 'WIT', 'Temple', 4)
    Game.add_holding(p, 'CJS', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 4)
    Game.add_holding(p, 'EM', 'Guild', 2)
    Game.add_holding(p, 'AV', 'Source', 0)
    Game.add_holding(p, 'HK', 'Source', 0)
    Game.add_geo(p, 'Caulnor', Border=1)
    Game.add_geo(p, 'Daulton', Border=1)
    Game.add_troops('DA', p, 'Cavalry')
    p = lst[1]
    Game.add_province(p, d, Region, 'DA', Population=3, Magic=4, x=710, y=2025)
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 3)
    Game.add_holding(p, 'HK', 'Source', 3)
    Game.add_geo(p, 'Duriene', Border=1)
    Game.add_geo(p, 'Vanilen', Border=1)
    Game.add_geo(p, 'Nentril', Border=1)
    Game.add_troops('DA', p, 'Archers')
    Game.add_troops('DA', p, 'Infantry')
    Game.add_troops('DA', p, 'Knights')
    p = lst[2]
    Game.add_province(p, d, Region, 'DA',  Population=4, Magic=1, x=770, y=2110)
    Game.add_holding(p, 'DA', 'Law', 4)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'CJS', 'Temple', 2)
    Game.add_holding(p, 'PAI', 'Guild', 2)
    Game.add_holding(p, 'EM', 'Guild', 2)
    Game.add_holding(p, 'HK', 'Source', 1)
    Game.add_geo(p, 'Caulnor', Border=1)
    Game.add_geo(p, 'Duriene', Border=1)
    Game.add_geo(p, 'Taliern', Border=1)
    Game.add_geo(p, 'Daulton', Border=1)
    Game.add_troops('DA', p, 'Artillerists')
    Game.add_troops('DA', p, 'Elite Infantry')
    Game.add_troops('DA', p, 'Knights')
    p = lst[3]
    Game.add_province(p, d, Region, 'DA',  Population=5, Magic=0, x=820, y=2150, Waterway=True) 
    Game.add_holding(p, 'DA', 'Law', 5)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'CJS', 'Temple', 2)
    Game.add_holding(p, 'PAI', 'Guild', 2)
    Game.add_holding(p, 'AV', 'Guild', 2)
    Game.add_holding(p, 'HK', 'Source', 1)
    Game.add_geo(p, 'Daulton', Border=1)
    Game.add_troops('DA', p, 'Archers')
    Game.add_troops('DA', p, 'Pikemen')
    p = lst[4]
    Game.add_province(p, d, Region, 'DA',  Population=5, Magic=0, x=720, y=2200, Terrain='Mountains', Capital=True)
    Game.add_holding(p, 'DA', 'Law', 5)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'CJS', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 3)
    Game.add_holding(p, 'AV', 'Guild', 2)
    Game.add_holding(p, 'HK', 'Source', 2)
    Game.add_geo(p, 'Taliern', Border=1)
    Game.add_troops('DA', p, 'Archers')
    Game.add_troops('DA', p, 'Artillerists')
    Game.add_troops('DA', p, 'Cavalry')
    Game.add_troops('DA', p, 'Infantry')
    Game.add_troops('DA', p, 'Infantry')
    Game.add_troops('DA', p, 'Elite Infantry')
    Game.add_troops('DA', p, 'Knights')
    Game.add_troops('DA', p, 'Knights')
    Game.add_troops('DA', p, 'Pikemen')
    Game.add_troops('DA', p, 'Pikemen')
    p = lst[5]
    Game.add_province(p, d, Region, 'DA',  Population=4, Magic=1, x=740, y=2070) 
    Game.add_holding(p, 'DA', 'Law', 4)
    Game.add_holding(p, 'WIT', 'Temple', 1)
    Game.add_holding(p, 'CJS', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 3)
    Game.add_holding(p, 'EM', 'Guild', 1)
    Game.add_holding(p, 'HK', 'Source', 1)
    Game.add_geo(p, 'Taliern', Border=1)
    Game.add_geo(p, 'Vanilen', Border=1)
    Game.add_troops('DA', p, 'Cavalry')
    Game.add_troops('DA', p, 'Elite Infantry')
    Game.add_troops('DA', p, 'Pikemen')
    p = lst[6]
    Game.add_province(p, d, Region, 'DA',  Population=3, Magic=4, x=670, y=2000, Terrain='Mountains') 
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 3)
    Game.add_holding(p, 'HK', 'Source', 4)
    Game.add_geo(p, 'Vanilen', Border=1)
    Game.add_troops('DA', p, 'Infantry')
    p = lst[7]
    Game.add_province(p, d, Region, 'DA',  Population=3, Magic=4, x=690, y=2115, Terrain='Mountains') 
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 3)
    Game.add_holding(p, 'EM', 'Guild', 0)
    Game.add_holding(p, 'HK', 'Source', 4)
    Game.add_geo(p, 'Vanilen', Border=1)
    Game.add_troops('DA', p, 'Infantry')
    p = lst[8]
    Game.add_province(p, d, Region, 'DA',  Population=3, Magic=4, x=665, y=2065, Terrain='Mountains') 
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 3)
    Game.add_holding(p, 'HK', 'Source', 4)
    Game.add_troops('DA', p, 'Infantry')

    # GHOERE
    Game.add_regent('GT', 'Gavin Tael', Archetype='Noble', Alignment='LE', Regency_Bonus=4
                    , Regency_Points=49, Gold_Bars=38, Culture='A', Bloodline='Re'
                    , Attitude='Aggressive', Lieutenants=['Johnathan Miechale'])
    d = 'Ghoere'
    p = 'Achiese'
    Game.add_province(p, d, Region, 'GT',  Population=4, Magic=1, x=1305, y=2100)
    Game.add_geo(p, 'Brothendar', Border=1)
    Game.add_geo(p, 'Ghalliere', Border=1)
    Game.add_holding(p, 'GT', 'Law', 3)
    Game.add_holding(p, 'HA', 'Temple', 3)
    Game.add_holding(p, 'LPA', 'Temple', 1)
    Game.add_holding(p, 'GH', 'Guild', 4)
    Game.add_holding(p, 'SM', 'Source', 1)
    p = 'Bhalaene'
    Game.add_province(p, d, Region, 'GT',  Population=6, Magic=0, x=1170, y=2085, Terrain='Hills'
                      , Capital=True, Castle=6, Castle_Name="Rook's Roost")
    Game.add_geo(p, 'Achiese', Border=1)
    Game.add_holding(p, 'GT', 'Law', 4)
    Game.add_holding(p, 'MOC', 'Temple', 5)
    Game.add_holding(p, 'HA', 'Temple', 1)
    Game.add_holding(p, 'GH', 'Guild', 4)
    Game.add_holding(p, 'ML', 'Guild', 2)
    Game.add_holding(p, 'SM', 'Source', 0)
    for a in range(3):
        Game.add_troops('GT', p, 'Archers')
        Game.add_troops('GT', p, 'Cavalry')
        Game.add_troops('GT', p, 'Elite Infantry')
        Game.add_troops('GT', p, 'Knights')
        Game.add_troops('GT', p, 'Pikemen')
        Game.add_troops('GT', p, 'Mercenary Cavalry')
    p = 'Bheline'
    Game.add_province(p, d, Region, 'GT',  Population=4, Magic=1, x=1140, y=2170)
    Game.add_geo(p, 'Bhalaene', Border=1)
    Game.add_holding(p, 'GT', 'Law', 4)
    Game.add_holding(p, 'MOC', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 1)
    Game.add_holding(p, 'GH', 'Guild', 4)
    Game.add_holding(p, 'SM', 'Source', 1)
    p = 'Conallier'
    Game.add_province(p, d, Region, 'GT',  Population=2, Magic=3, x=1200, y=1970, Waterway=True)
    Game.add_holding(p, 'GT', 'Law', 2)
    Game.add_holding(p, 'Mh', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 0)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'ML', 'Guild', 2)
    Game.add_holding(p, 'SM', 'Source', 3)
    p = 'Danaroene'
    Game.add_province(p, d, Region, 'GT',  Population=4, Magic=1, x=1220, y=2160)
    Game.add_geo(p, 'Bheline', Border=1)
    Game.add_geo(p, 'Achiese', Border=1)
    Game.add_geo(p, 'Bhalaene', Border=1)
    Game.add_holding(p, 'GT', 'Law', 3)
    Game.add_holding(p, 'MOC', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 1)
    Game.add_holding(p, 'GH', 'Guild', 2)
    Game.add_holding(p, 'SM', 'Source', 1)
    p = 'Ghiere'
    Game.add_province(p, d, Region, 'GT',  Population=5, Magic=0, x=1030, y=2060, Waterway=True)
    Game.add_holding(p, 'GT', 'Law', 3)
    Game.add_holding(p, 'Mh', 'Law', 2)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'HA', 'Temple', 3)
    Game.add_holding(p, 'GH', 'Guild', 3)
    Game.add_holding(p, 'GK', 'Guild', 2)
    Game.add_holding(p, 'SM', 'Source', 0)
    p = 'Rhumannen'
    Game.add_province(p, d, Region, 'GT',  Population=4, Magic=1, x=1055, y=2095, Terrain='Hills')
    Game.add_geo(p, 'Bhalaene', Border=1)
    Game.add_geo(p, 'Bheline', Border=1)
    Game.add_geo(p, 'Ghiere', Border=1)
    Game.add_holding(p, 'GT', 'Law', 2)
    Game.add_holding(p, 'Mh', 'Law', 2)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'HA', 'Temple', 2)
    Game.add_holding(p, 'GH', 'Guild', 3)
    Game.add_holding(p, 'GK', 'Guild', 1)
    Game.add_holding(p, 'SM', 'Source', 1)
    p = 'Thoralinar'
    Game.add_province(p, d, Region, 'GT',  Population=3, Magic=2, x=1230, y=2030, Terrain='Hills')
    Game.add_geo(p, 'Bhalaene', Border=1)
    Game.add_geo(p, 'Achiese', Border=1)
    Game.add_geo(p, 'Conallier', Border=1)
    Game.add_holding(p, 'GT', 'Law', 3)
    Game.add_holding(p, 'LPA', 'Temple', 3)
    Game.add_holding(p, 'GH', 'Guild', 3)
    Game.add_holding(p, 'SM', 'Source', 2)
    p = 'Tireste'
    Game.add_province(p, d, Region, 'GT',  Population=5, Magic=0, x=980, y=2110, Waterway=True)
    Game.add_geo(p, 'Rhumannen', Border=1)
    Game.add_geo(p, 'Ghiere', Border=1)
    Game.add_holding(p, 'GT', 'Law', 5)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'HA', 'Temple', 3)
    Game.add_holding(p, 'GH', 'Guild', 1)
    Game.add_holding(p, 'GK', 'Guild', 4)
    Game.add_holding(p, 'SM', 'Source', 0)
    p = 'Tornilen'
    Game.add_province(p, d, Region, 'GT',  Population=3, Magic=2, x=1130, y=2045, Waterway=True)
    Game.add_geo(p, 'Conallier', Border=1)
    Game.add_geo(p, 'Thoralinar', Border=1)
    Game.add_geo(p, 'Bhalaene', Border=1)
    Game.add_geo(p, 'Rhumannen', Border=1)
    Game.add_geo(p, 'Ghiere', Border=1)
    Game.add_holding(p, 'GT', 'Law', 2)
    Game.add_holding(p, 'Mh', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 0)
    Game.add_holding(p, 'GH', 'Guild', 2)
    Game.add_holding(p, 'ML', 'Guild', 0)
    Game.add_holding(p, 'SM', 'Source', 2)
    
    # MHORIED
    d = 'Mhoried'
    Game.add_regent('Mh', 'The Mhor, Daeric Mhoried', Archetype='Bandit Captain' , Alignment='CG', Regency_Bonus=4
                    , Regency_Points=38, Gold_Bars=20, Bloodline='Br', Culture='A'
                    , Attitude='Peaceful', Lieutenants=['Michael Mhoried'])
    Game.add_regent('Rg', 'Regien', Archetype='Mage', Alignment='CN', Regency_Bonus=3, Bloodline='Vo'
                    , Culture='A')
    Game.add_relationship('Rg', 'Mh', Diplomacy=1)
    Game.add_relationship('Mh', 'Rg', Diplomacy=1)
    p = 'Balteruine'
    Game.add_province(p, d, Region, 'Mh',  Population=2, Magic=3, x=1290, y=1810, Waterway=True)
    Game.add_holding(p, 'Mh', 'Law', 1)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'ML', 'Guild', 2)
    Game.add_holding(p, 'Rg', 'Source', 2)
    p = 'Bevaldruor'
    Game.add_province(p, d, Region, 'Mh',  Population=6, Magic=3, x=1200, y=1780, Terrain='Forest', Capital=True, Waterway=True)
    Game.add_geo(p, 'Balteruine', Border=1)
    Game.add_holding(p, 'Mh', 'Law', 4)
    Game.add_holding(p, 'MOC', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 3)
    Game.add_holding(p, 'ML', 'Guild', 3)
    Game.add_holding(p, 'Mh', 'Guild', 0)
    Game.add_holding(p, 'GTh', 'Guild', 1)
    Game.add_holding(p, 'Rg', 'Source', 3)
    Game.add_geo("Rivenrock", "Bevaldruor", Caravan=1)
    for a in range(2):
        Game.add_troops('Mh', p, 'Archers')
        Game.add_troops('Mh', p, 'Cavalry')
        Game.add_troops('Mh', p, 'Elite Infantry')
        Game.add_troops('Mh', p, 'Knights')
        Game.add_troops('Mh', p, 'Pikemen')
    p = 'Byrnnor'
    Game.add_province(p, d, Region, 'Mh',  Population=3, Magic=2, x=1080, y=1800, Waterway=True)
    Game.add_geo(p, 'Bevaldruor', Border=1)
    Game.add_holding(p, 'Mh', 'Law', 3)
    Game.add_holding(p, 'OA', 'Temple', 2)
    Game.add_holding(p, 'HA', 'Temple', 2)
    Game.add_holding(p, 'ML', 'Guild', 3)
    Game.add_holding(p, 'Mh', 'Guild', 0)
    Game.add_holding(p, 'GTh', 'Guild', 1)
    Game.add_holding(p, 'Rg', 'Source', 1)
    p = 'Cwlldon'
    Game.add_province(p, d, Region, 'Mh',  Population=3, Magic=2, x=1160, y=1895, Waterway=True)
    Game.add_geo(p, 'Byrnnor', Border=1)
    Game.add_geo(p, 'Conallier', Border=1, RiverChasm=1)
    Game.add_holding(p, 'Mh', 'Law', 3)
    Game.add_holding(p, 'GT', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 0)
    Game.add_holding(p, 'HA', 'Temple', 2)
    Game.add_holding(p, 'ML', 'Guild', 0)
    Game.add_holding(p, 'GH', 'Guild', 2)
    Game.add_holding(p, 'SM', 'Source', 2)
    p = 'Dhalsiel'
    Game.add_province(p, d, Region, 'Mh',  Population=2, Magic=3, x=1220, y=1685, Waterway=True)
    Game.add_geo(p, 'Bevaldruor', Border=1)
    Game.add_geo(p, 'Byrnnor', Border=1)
    Game.add_holding(p, 'Mh', 'Law', 2)
    Game.add_holding(p, 'OA', 'Temple', 2)
    Game.add_holding(p, 'ML', 'Guild', 2)
    Game.add_holding(p, 'Rg', 'Source', 3)
    p = 'Maesilar'
    Game.add_province(p, d, Region, 'Mh',  Population=3, Magic=2, x=1230, y=1870, Waterway=True)
    Game.add_geo(p, 'Bevaldruor', Border=1)
    Game.add_geo(p, 'Balteruine', Border=1)
    Game.add_geo(p, 'Cwlldon', Border=1)
    Game.add_geo(p, 'Conallier', Border=1)
    Game.add_geo(p, 'Byrnnor', Border=1)
    Game.add_holding(p, 'Mh', 'Law', 0)
    Game.add_holding(p, 'GT', 'Law', 3)
    Game.add_holding(p, 'MOC', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 0)
    Game.add_holding(p, 'ML', 'Guild', 3)
    Game.add_holding(p, 'Mh', 'Guild', 0)
    Game.add_holding(p, 'Rg', 'Source', 2)
    p = "Marloer's Gap"
    Game.add_province(p, d, Region, 'Mh',  Population=2, Magic=3, x=1170, y=1670, Terrain='Hills', Waterway=True)
    Game.add_geo(p, 'Dhalsiel', Border=1)
    Game.add_holding(p, 'Mh', 'Law', 1)
    Game.add_holding(p, 'OA', 'Temple', 0)
    Game.add_holding(p, 'HA', 'Temple', 1)
    Game.add_holding(p, 'ML', 'Guild', 2)
    Game.add_holding(p, 'Rg', 'Source', 3)
    p = 'Tenarien'
    Game.add_province(p, d, Region, 'Mh',  Population=3, Magic=2, x=1115, y=1960, Waterway=True)
    Game.add_geo(p, 'Cwlldon', Border=1)
    Game.add_geo(p, 'Conallier', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Tornilen', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Ghiere', Border=1, RiverChasm=1)
    Game.add_holding(p, 'Mh', 'Law', 3)
    Game.add_holding(p, 'GT', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 0)
    Game.add_holding(p, 'ML', 'Guild', 0)
    Game.add_holding(p, 'GH', 'Guild', 3)
    Game.add_holding(p, 'Rg', 'Source', 0)
    Game.add_holding(p, 'SM', 'Source', 2)
    p = "Torien's Watch"
    Game.add_province(p, d, Region, 'Mh',  Population=3, Magic=6, x=1075, y=1630, Terrain='Forest', Waterway=True)
    Game.add_holding(p, 'Mh', 'Law', 2)
    Game.add_holding(p, 'OA', 'Temple', 3)
    Game.add_holding(p, 'GTh', 'Guild', 3)
    Game.add_holding(p, 'Rg', 'Source', 6)
    Game.add_geo(p, "Marloer's Gap", Border=1)
    Game.add_troops('Mh', p, 'Archers')
    Game.add_troops('Mh', p, 'Archers')
    Game.add_troops('Mh', p, 'Cavalry')
    Game.add_troops('Mh', p, 'Elite Infantry')
    Game.add_troops('Mh', p, 'Knights')
    Game.add_troops('Mh', p, 'Pikemen')
    p = 'Winoene'
    Game.add_province(p, d, Region, 'Mh',  Population=3, Magic=2, x=1080, y=1725, Terrain='Hills', Waterway=True)
    Game.add_geo(p, "Torien's Watch", Border=1)
    Game.add_geo(p, "Marloer's Gap", Border=1)
    Game.add_geo(p, 'Byrnnor', Border=1)
    Game.add_holding(p, 'HA', 'Temple', 3)
    Game.add_holding(p, 'GTh', 'Guild', 3)
    Game.add_holding(p, 'ML', 'Guild', 0)
    Game.add_holding(p, 'Rg', 'Source', 2)
    Game.add_holding(p, 'Mh', 'Law', 3)

    Game.add_relationship('ML', 'Mh', Diplomacy=1, Payment=5)
    Game.add_relationship('Mh', 'ML', Diplomacy=1)
    Game.add_relationship('GT', 'Mh', Diplomacy=-1)
    Game.add_relationship('Mh', 'GT', Diplomacy=-1)
    
    # Tuornen
    d = 'Tuornen'
    p = 'Alamsreft'
    Game.add_province(p, d, Region, 'LF',  Population=3, Magic=2, x=850, y=2005, Waterway=True)
    Game.add_holding(p, 'LF', 'Law', 1)
    Game.add_holding(p, 'DA', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 3)
    Game.add_holding(p, 'WIT', 'Temple', 0)
    Game.add_holding(p, 'MB', 'Guild', 3)
    Game.add_holding(p, 'Ca', 'Source', 2)
    p = 'Elevesnemiere'
    Game.add_province(p, d, Region, 'LF',  Population=2, Magic=5, x=750, y=1950, Terrain='Hills')
    Game.add_holding(p, 'LF', 'Law', 2)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'PAI', 'Guild', 2)
    Game.add_holding(p, 'Ca', 'Source', 5)
    Game.add_geo(p, 'Avarien', Border=1)
    Game.add_geo(p, 'Nentril', Border=1)
    p = 'Ghonallison'
    Game.add_province(p, d, Region, 'LF',  Population=2, Magic=3, x=840, y=1775, Terrain='Hills')
    Game.add_holding(p, 'AB', 'Law', 2)
    Game.add_holding(p, 'LF', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'MB', 'Guild', 2)
    p = 'Haesrien'
    Game.add_province(p, d, Region, 'LF',  Population=5, Magic=0, x=815, y=1940, Terrain='Hills', Capital=True, Waterway=True)
    Game.add_holding(p, 'LF', 'Law', 3)
    Game.add_holding(p, 'AB', 'Law', 2)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'EM', 'Guild', 3)
    Game.add_holding(p, 'LF', 'Guild', 2)
    Game.add_holding(p, 'MB', 'Guild', 0)
    Game.add_holding(p, 'Ca', 'Source', 0)


    Game.add_geo(p, 'Alamsreft', Border=1)
    Game.add_geo(p, 'Elevesnemiere', Border=1)
    Game.add_troops('LF', p, 'Archers')
    Game.add_troops('LF', p, 'Archers')
    Game.add_troops('LF', p, 'Pikemen')
    Game.add_troops('LF', p, 'Pikemen')
    Game.add_troops('LF', p, 'Pikemen')
    Game.add_troops('LF', p, 'Knights')
    Game.add_troops('LF', p, 'Knights')
    p = 'Monsedge'
    Game.add_province(p, d, Region, 'LF',  Population=3, Magic=2, x=815, y=1835, Terrain='Hills')
    Game.add_holding(p, 'LF', 'Law', 1)
    Game.add_holding(p, 'AB', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 0)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'MB', 'Guild', 3)
    Game.add_holding(p, 'Rh', 'Source', 2)

    Game.add_geo(p, 'Haesrien', Border=1)
    Game.add_geo(p, 'Ghonallison', Border=1)
    p = 'Nabhriene'
    Game.add_province(p, d, Region, 'LF',  Population=3, Magic=2, x=800, y=2015)
    Game.add_holding(p, 'LF', 'Law', 2)
    Game.add_holding(p, 'AB', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 0)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'EM', 'Guild', 3)
    Game.add_holding(p, 'PAI', 'Guild', 0)
    Game.add_holding(p, 'Ca', 'Source', 2)
    Game.add_geo(p, 'Avarien', Border=1)
    Game.add_geo(p, 'Duriene', Border=1)
    Game.add_geo(p, 'Bhrein', Border=1)
    Game.add_geo(p, 'Alamsreft', Border=1)
    Game.add_geo(p, 'Haesrien', Border=1)
    Game.add_geo(p, 'Elevesnemiere', Border=1)
    p = 'Pechalinn'
    Game.add_province(p, d, Region, 'LF',  Population=2, Magic=5, x=740, y=1860, Terrain='Mountains')
    Game.add_holding(p, 'LF', 'Law', 2)
    Game.add_holding(p, 'AB', 'Law', 0)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'PAI', 'Guild', 2)
    Game.add_holding(p, 'Rh', 'Source', 5)
    Game.add_geo(p, 'Haesrien', Border=1)
    Game.add_geo(p, 'Monsedge', Border=1)
    Game.add_geo(p, 'Elevesnemiere', Border=1)
    p = "Tuor's Hold"
    Game.add_province(p, d, Region, 'LF',  Population=2, Magic=5, x=850, y=2075, Terrain='Mountains', Waterway=True)
    Game.add_holding(p, 'DA', 'Law', 2)
    Game.add_holding(p, 'LF', 'Law', 0)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'PAI', 'Guild', 3)
    Game.add_holding(p, 'Ca', 'Source', 2)
    Game.add_geo(p, 'Alamsreft', Border=1)
    Game.add_geo(p, 'Nabhriene', Border=1)
    Game.add_geo(p, 'Bhrein', Border=1)
    Game.add_geo(p, 'Caulnor', Border=1)

    Game.add_regent('LF', 'Laela Flaertes (Tuornen)', Archetype='Bard', Alignment='NG'
                    , Regency_Bonus=2, Bloodline='Br', Culture='A'
                    , Lieutenants=['Braedonnal Tuare'], Regency_Points=21, Gold_Bars=8)
    Game.add_relationship('Mh', 'LF', Diplomacy=1)
    Game.add_relationship('LF', 'Mh', Diplomacy=1)
    Game.add_relationship('LF', 'AD', Diplomacy=1)
    Game.add_relationship('AD', 'LF', Diplomacy=1)
    Game.add_relationship('LF', 'CA', Diplomacy=-1)
    Game.add_relationship('CA', 'LF', Diplomacy=-3)
    
    # Alamie
    d = 'Alamie'
    p = 'Alaroine'
    Game.add_province(p, d, Region, 'CA',  Population=5, Magic=0, x=960, y=1935)
    Game.add_holding(p, 'CA', 'Law', 4)
    Game.add_holding(p, 'CJS', 'Temple', 3)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'MB', 'Guild', 3)
    Game.add_holding(p, 'GH', 'Guild', 3)

    p = 'Deseirain'
    Game.add_province(p, d, Region, 'CA',  Population=3, Magic=2, x=885, y=1915, Capital=True, Waterway=True)
    Game.add_holding(p, 'CA', 'Law', 2)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'MB', 'Guild', 3)
    Game.add_holding(p, 'Ca', 'Source', 2)
    Game.add_geo(p, 'Alaroine', Border=1)
    Game.add_geo(p, 'Haesrien', Border=1, RiverChasm = 1, Road=1)
    Game.add_geo(p, 'Alamsreft', Border=1, RiverChasm = 1)
    Game.add_geo(p, 'Monsedge', Border=1)

    p = 'Hildon'
    Game.add_holding(p, 'CA', 'Law', 1)
    Game.add_holding(p, 'CJS', 'Temple', 2)
    Game.add_holding(p, 'MB', 'Guild', 2)
    Game.add_province(p, d, Region, 'CA',  Population=2, Magic=3, x=930, y=1825)
    Game.add_geo(p, 'Monsedge', Border=1)
    Game.add_geo(p, 'Deseirain', Border=1)
    Game.add_geo(p, 'Alaroine', Border=1)
    Game.add_geo(p, 'Ghonallison', Border=1)

    p = 'Laraeth'
    Game.add_province(p, d, Region, 'CA',  Population=3, Magic=2, x=1030, y=1940, Terrain='Swamp', Waterway=True)
    Game.add_holding(p, 'CA', 'Law', 2)
    Game.add_holding(p, 'GK', 'Law', 0)
    Game.add_holding(p, 'CJS', 'Temple', 3)
    Game.add_holding(p, 'GH', 'Guild', 2)
    Game.add_holding(p, 'Ca', 'Source', 2)
    Game.add_geo(p, 'Alaroine', Border=1)
    Game.add_geo(p, 'Ghiere', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Tenarien', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Cwlldon', Border=1, RiverChasm=1)

    p = 'Maesford'
    Game.add_province(p, d, Region, 'CA',  Population=2, Magic=3, x=920, y=2065, Waterway=True)
    Game.add_holding(p, 'GK', 'Law', 0)
    Game.add_holding(p, 'CA', 'Law', 1)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'GK', 'Guild', 2)
    Game.add_holding(p, 'Ca', 'Source', 3)
    Game.add_geo(p, 'Tireste', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Ghiere', Border=1, RiverChasm=1)
    Game.add_geo(p, "Tuor's Hold", Border=1, RiverChasm=1)
    Game.add_geo(p, "Almsreft", Border=1, RiverChasm=1)

    p = 'Nortmoor'
    Game.add_province(p, d, Region, 'CA',  Population=1, Magic=4, x=1000, y=1785, Waterway=True)
    Game.add_holding(p, 'CJS', 'Temple', 1)
    Game.add_holding(p, 'MB', 'Guild', 1)
    Game.add_geo(p, "Byrnnor", Border=1, RiverChasm=1)
    Game.add_geo(p, "Winoene", Border=1, RiverChasm=1)
    Game.add_geo(p, "Hildon", Border=1)

    p = 'Sorelies'
    Game.add_province(p, d, Region, 'CA',  Population=1, Magic=4, x=935, y=1760, Terrain='Hills')
    Game.add_holding(p, 'WIT', 'Temple', 1)
    Game.add_holding(p, 'MB', 'Guild', 1)
    Game.add_geo(p, 'Ghonallison', Border=1)
    Game.add_geo(p, 'Hildon', Border=1)
    Game.add_geo(p, 'Nortmoor', Border=1)

    p = 'Soutmoor'
    Game.add_province(p, d, Region, 'CA',  Population=2, Magic=3, x=1005, y=1875, Waterway=True)
    Game.add_holding(p, 'CJS', 'Temple', 2)
    Game.add_holding(p, 'GH', 'Guild', 1)
    Game.add_geo(p, 'Nortmoor', Border=1)
    Game.add_geo(p, 'Laraeth', Border=1)
    Game.add_geo(p, 'Alaroine', Border=1)
    Game.add_geo(p, 'Hildon', Border=1)
    Game.add_geo(p, "Byrnnor", Border=1, RiverChasm=1)
    Game.add_geo(p, 'Cwlldon', Border=1, RiverChasm=1)
                 
    p = 'Traiward'
    Game.add_province(p, d, Region, 'CA',  Population=3, Magic=2, x=940, y=2000, Waterway=True)
    Game.add_holding(p, 'GK', 'Law', 0)
    Game.add_holding(p, 'CA', 'Law', 2)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'GK', 'Guild', 3)
    Game.add_holding(p, 'Ca', 'Source', 2)
    Game.add_geo(p, 'Deseirain', Border=1)
    Game.add_geo(p, 'Alaroine', Border=1)
    Game.add_geo(p, 'Laraeth', Border=1)
    Game.add_geo(p, 'Maesford', Border=1)
    Game.add_geo(p, 'Ghiere', Border=1, RiverChasm=1)
    Game.add_geo(p, "Alamsreft", Border=1, RiverChasm=1)
                 
    Game.add_regent('CA', 'Carilon Alam', Regency_Bonus=3, Alignment='NE', Attitude='Aggressive'
                    , Lieutenants=['Cousin A', 'Cousin B', "Carilon's Daughter"]
                    , Bloodline='Ba', Culture='A')             


    d = 'Imperial City of Anuire'
    p = 'City of Anuire'
    Game.add_province(p, d, Region, 'CD',  Population=10, Magic=0, x=794, y=2259, Waterway=True, Capital=True)
    Game.add_holding(p, 'CD', 'Law', 3)
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'AB', 'Law', 2)
    Game.add_holding(p, 'HD', 'Law', 2)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'MOC', 'Temple', 2)
    Game.add_holding(p, 'CJS', 'Temple', 1)
    Game.add_holding(p, 'GK', 'Guild', 2)
    Game.add_holding(p, 'PAI', 'Guild', 2)
    Game.add_holding(p, 'ML', 'Guild', 1)
    Game.add_holding(p, 'COS', 'Source', 2)
    Game.add_geo(p, 'Anuire', Border=1)

    Game.add_regent('CD', 'Caliedhe Dosiere (Chamberlain)', Class='Fighter/Wizard(Diviner)', Level = 20, Alignment='LG'
                    , Regency_Bonus=6, Attitude='Peaceful', Bloodline='An', Culture='A'
                    , Str=0, Dex=2,  Con=1, Int=4, Wis=3, Cha=2, Insight=9, Deception=8, Persuasion=8
                    , Lieutenants=['Imperial Servent {}'.format(a+1) for a in range(8)])
    
    d = 'Elinie'
    p = 'Ansien'
    Game.add_province(p, d, Region, 'AD',  Population=5, Magic=0, x=1415, y=1950, Capital=True)
    Game.add_holding(p, 'AD', 'Law', 3)
    Game.add_holding(p, 'LPA', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 2)
    Game.add_holding(p, 'EL', 'Guild', 5)
    p = 'Chalsedon'
    Game.add_province(p, d, Region, 'AD',  Population=3, Magic=2, x=1350, y=2010)
    Game.add_holding(p, 'AD', 'Law', 1)
    Game.add_holding(p, 'HA', 'Temple', 3)
    Game.add_holding(p, 'EL', 'Guild', 3)
    Game.add_holding(p, 'SM', 'Source', 2)
    Game.add_geo(p, 'Ansien', Border=1)
    Game.add_geo(p, 'Achiese', Border=1)
    Game.add_geo(p, 'Thoralinar', Border=1)
    Game.add_geo(p, 'Ghalliere', Border=1)
    p = "Hope's Demise"
    Game.add_province(p, d, Region, 'AD',  Population=2, Magic=6, x=1485, y=1885, Terrain='Swamp')
    Game.add_holding(p, 'AD', 'Law', 1)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'EL', 'Guild', 1)
    Game.add_holding(p, 'Sw2', 'Source', 5)
    Game.add_geo(p, 'Ansien', Border=1)
    Game.add_geo(p, 'Bogsend', Border=1)
    Game.add_geo(p, 'Caudraight', Border=1)
    Game.add_geo(p, 'Deepshadow', Border=1)
    p = 'Mholien'
    Game.add_province(p, d, Region, 'AD',  Population=3, Magic=2, x=1350, y=1870, Terrain='Hills')
    Game.add_holding(p, 'AD', 'Law', 1)
    Game.add_holding(p, 'HA', 'Temple', 2)
    Game.add_holding(p, 'EL', 'Guild', 2)
    Game.add_holding(p, 'Sw2', 'Source', 2)
    Game.add_holding(p, 'Rg', 'Source', 1)
    Game.add_geo(p, 'Ansien', Border=1)
    Game.add_geo(p, 'Chalsedon', Border=1)
    Game.add_geo(p, 'Balteruine', Border=1)
    p = 'Osoeriene'
    Game.add_province(p, d, Region, 'AD',  Population=3, Magic=2, x=1435, y=2010, Waterway=True)
    Game.add_holding(p, 'AD', 'Law', 3)
    Game.add_holding(p, 'LPA', 'Temple', 3)
    Game.add_holding(p, 'EL', 'Guild', 3)
    Game.add_holding(p, 'SM', 'Source', 2)
    Game.add_geo(p, 'Ansien', Border=1)
    Game.add_geo(p, 'Chalsedon', Border=1)
    Game.add_geo(p, 'Ghalliere', Border=1)
    Game.add_geo(p, 'Moergen', Border=1)
    Game.add_geo(p, 'Bogsend', Border=1, RiverChasm=1)
    Game.add_geo(p, "Hope's Demise", Border=1)
    p = 'Sendouras'
    Game.add_province(p, d, Region, 'AD',  Population=3, Magic=2, x=1270, y=1915, Terrain='Hills')
    Game.add_holding(p, 'AD', 'Law', 1)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'EL', 'Guild', 3)
    Game.add_holding(p, 'SM', 'Source', 2)
    Game.add_geo(p, 'Mholien', Border=1) 
    Game.add_geo(p, 'Maesilar', Border=1)
    Game.add_geo(p, 'Conallier', Border=1)
    Game.add_geo(p, 'Thoralinar', Border=1)
    Game.add_geo(p, 'Chalsedon', Border=1)
    p = 'Soileite'
    Game.add_province(p, d, Region, 'AD',  Population=3, Magic=2, x=1425, y=1850)
    Game.add_holding(p, 'AD', 'Law', 1)
    Game.add_holding(p, 'LPA', 'Temple', 2)
    Game.add_holding(p, 'EL', 'Guild', 2)
    Game.add_holding(p, 'Sw2', 'Source', 3)
    Game.add_geo(p, 'Ansien', Border=1)
    Game.add_geo(p, "Hope's Demise", Border=1)
    Game.add_geo(p, 'Hoehnaen', Border=1)
    Game.add_geo(p, 'Ywrndor', Border=1)
    Game.add_geo(p, 'Mholien', Border=1)

    Game.add_regent('AD', "Assan ibn Daouta", Archetype='Knight', Regency_Bonus=4, Alignment='LG'
                    , Attitude='Peaceful', Culture='Kh', Bloodline='Ba'
                    , Lieutenants = ['Son {}'.format(a+1) for a in range(3)] + ['Daughter {}'.format(a+1) for a in range(3)])
    
    d = 'Endier'
    p = 'Endier'
    Game.add_province(p, d, Region, 'GK',  Population=6, Magic=0, x=883, y=2129, Castle=2, Castle_Name='Caer Endier', Capital=True)
    Game.add_geo(p, 'Caulnor', Border=1, Road=1, RiverChasm=1)
    Game.add_geo(p, "Tuor's Hold", Border=1, Road=1, RiverChasm=1)
    Game.add_geo(p, "Maesford", Border=1, Road=1, RiverChasm=1)
    Game.add_geo(p, 'Tireste', Border=1, Road=1, RiverChasm=1)
    Game.add_holding(p, 'GK', 'Law', 6)
    Game.add_holding(p, 'CJS', 'Temple', 3)
    Game.add_holding(p, 'WIT', 'Temple', 3)
    Game.add_holding(p, 'GK', 'Guild', 6)
    Game.add_holding(p, 'Ca', 'Source', 0)


    Game.add_regent('GK', "Guilder Kalien (Endier, Heartlanders Outfitters)", Alignment='NE'
                    , Regency_Bonus=3, Regency_Points=42, Gold_Bars=45, Class='Rogue', Level=5
                    , Str=1, Dex=4, Con=1, Int=3, Wis=1, Cha=3, Insight=4, Deception=6, Persuasion=6
                    , Bloodline='Ba', Culture='A')
    Game.add_relationship('GK', 'Ca', Diplomacy=1)
    Game.add_relationship('Ca', 'GK', Diplomacy=1)
    
    Game.add_regent('SM', "Sword Mage", Archetype='Archmage', Regency_Bonus=3, Alignment='LE'
                , Regency_Points=15, Bloodline='Vo', Culture='V')
    Game.add_relationship('SM', 'GT', Diplomacy=5, Vassalage=3)
    Game.add_regent('EL', "Elamien Lamier", Archetype='Scout', Regency_Bonus=1, Alignment='LN'
                    , Bloodline='Br', Culture='A')
    Game.add_regent('PAI', "Parnien Anuvier Iniere (Prince's Pride)", Archetype='Bandit', Regency_Bonus=1
                    , Bloodline='Br', Culture='A')
    Game.add_regent('Ca', "Caine", Archetype='Mage', Regency_Bonus=2, Alignment='NG',  Bloodline='Vo', Culture='A')
    Game.add_regent('WIT', 'Western Imperial Temple of Haelyn (Rhobber Nichaleir)', Archetype='Priest'
                    , Alignment='LG', Regency_Points=25, Gold_Bars=40, Regency_Bonus=5, Culture='A', Bloodline='An')
    Game.add_regent('GH', 'Ghorien Hiriele (Highland/Overland Traders)', Archetype='Bandit', Alignment='CE'
                    , Bloodline='An', Culture='A')
    Game.add_regent('ML', "Moerele Lannaman (Maesil Shippers)", Alignment='CG', Archetype='Bandit'
                    , Regency_Bonus=3, Bloodline='Br', Culture='A')
        
    Game.add_regent('MOC', "Militant Order of Cuiraecen (Fhylie the Sword)", Archetype='Priest', Bloodline='An'
                   , Regency_Bonus=2, Alignment='CG', Regency_Points=39, Gold_Bars=26, Culture='A', Race='Elf')

    Game.add_regent('HA', "Haelyn's Aegis (Anita Maricoere)", Archetype='Priest', Alignment='LG', Regency_Bonus=4
                   , Bloodline='An', Culture='A')
                   
    Game.add_regent('COS', "College of Sorcery", Archetype='Archmage', Culture='A', Bloodline='Vo', Regency_Bonus=3)


    Game.add_geo("Tuor's Hold", 'Bherin', Border=1)
    Game.add_geo("Soutmoor", 'Laraeth', Border=1)
    Game.add_geo("Winoene", 'Dhalsiel', Border=1)
    Game.add_geo("Osoeriene", 'Moergen', Border=1)
    
    Game.add_geo('Daulton', 'Ilien', Shipping=1)
    Game.add_geo('Anuire', 'Seaward', Shipping=1)

    Game.add_ship('DA', 'Anuire', 'Galleon')
    Game.add_ship('DA', 'Anuire', 'Galleon')
    Game.add_ship('DA', 'Anuire', 'Galleon')
    for a in range(4):
        Game.add_ship('DA', 'Anuire', 'Galleon')
        Game.add_ship('DA', 'Anuire', 'Coaster')
        Game.add_ship('DA', 'Anuire', 'Caravel')
    
    Region = 'The Southern Coast'
    d = 'Roesone'
    p = 'Abbatuor'
    Game.add_province(p, d, Region, 'MR', Population=3, Magic=4, x=1185, y=2450, Terrain='Forest', Waterway=True)
    Game.add_holding(p, 'MR', 'Law', 1)
    Game.add_holding(p, 'IHH', 'Temple', 2)
    Game.add_holding(p, 'OT', 'Guild', 3)
    Game.add_holding(p, 'EH', 'Guild', 0)
    Game.add_holding(p, 'HMA', 'Source', 3)
    Game.add_holding(p, 'RA', 'Source', 0)
    p = 'Bellam'
    Game.add_province(p, d, Region, 'MR', Population=3, Magic=2, x=1265, y=2220)
    Game.add_holding(p, 'MR', 'Law', 2)
    Game.add_holding(p, 'IHH', 'Temple', 3)
    Game.add_holding(p, 'OT', 'Guild', 3)
    Game.add_holding(p, 'SG', 'Guild', 0)
    Game.add_holding(p, 'HMA', 'Source', 2)
    Game.add_geo(p, 'Algael', Border=1)
    Game.add_geo(p, 'Brothendar', Border=1)
    Game.add_geo(p, 'Danaroene', Border=1)
    Game.add_geo(p, 'Achiese', Border=1)
    Game.add_geo(p, 'Bevaldruor', Caravan=1)
    p = 'Caercas'
    Game.add_province(p, d, Region, 'MR', Population=4, Magic=1, x=1105, y=2300, Capital=True, Waterway=True)
    Game.add_holding(p, 'MR', 'Law', 2)
    Game.add_holding(p, 'IHH', 'Temple', 3)
    Game.add_holding(p, 'RCS', 'Temple', 1)
    Game.add_holding(p, 'OT', 'Guild', 0)
    Game.add_holding(p, 'EH', 'Guild', 2)
    Game.add_holding(p, 'SG', 'Guild', 2)
    Game.add_holding(p, 'RA', 'Source', 1)
    Game.add_troops('MR', p, 'Archers')
    Game.add_troops('MR', p, 'Archers')
    Game.add_troops('MR', p, 'Archers')
    Game.add_troops('MR', p, 'Artillerists')
    Game.add_troops('MR', p, 'Knights')
    Game.add_troops('MR', p, 'Pikemen')
    Game.add_troops('MR', p, 'Pikemen')
    Game.add_troops('MR', p, 'Pikemen')
    Game.add_troops('MR', p, 'Infantry')
    Game.add_geo(p, 'Ilien', Caravan=1)  # MAY NEED FIXING
    p = 'Duerlin'
    Game.add_province(p, d, Region, 'MR', Population=3, Magic=2, x=1190, y=2390, Waterway=True)
    Game.add_holding(p, 'MR', 'Law', 1)
    Game.add_holding(p, 'IHH', 'Temple', 2)
    Game.add_holding(p, 'EH', 'Guild', 3)
    Game.add_holding(p, 'RA', 'Source', 2)
    Game.add_geo(p, 'Caercas', Border=1)
    Game.add_geo(p, 'Abbatuor', Border=1)
    p = 'Edlin'
    Game.add_province(p, d, Region, 'MR', Population=3, Magic=2, x=1195, y=2345)
    Game.add_holding(p, 'MR', 'Law', 1)
    Game.add_holding(p, 'IHH', 'Temple', 2)
    Game.add_holding(p, 'EH', 'Guild', 3)
    Game.add_holding(p, 'HMA', 'Source', 2)
    Game.add_geo(p, 'Caercas', Border=1)
    Game.add_geo(p, 'Duerlin', Border=1)

    p = 'Fairfield'
    Game.add_province(p, d, Region, 'MR', Population=3, Magic=2, x=1195, y=2255)
    Game.add_holding(p, 'MR', 'Law', 1)
    Game.add_holding(p, 'IHH', 'Temple', 2)
    Game.add_holding(p, 'SG', 'Guild', 3)
    Game.add_holding(p, 'OT', 'Guild', 0)
    Game.add_holding(p, 'HMA', 'Source', 2)
    Game.add_geo(p, 'Caercas', Border=1)
    Game.add_geo(p, 'Bellam', Border=1)
    Game.add_geo(p, 'Edlin', Border=1)
    Game.add_geo(p, 'Bheline', Border=1)
    Game.add_geo(p, 'Danaroene', Border=1)
    p = 'Ghoried'
    Game.add_province(p, d, Region, 'MR', Population=3, Magic=2, x=1125, y=2225, Waterway=True)
    Game.add_holding(p, 'MR', 'Law', 1)
    Game.add_holding(p, 'IHH', 'Temple', 1)
    Game.add_holding(p, 'SG', 'Guild', 2)
    Game.add_holding(p, 'HMA', 'Source', 2)
    Game.add_geo(p, 'Caercas', Border=1)
    Game.add_geo(p, 'Fairfield', Border=1)
    Game.add_geo(p, 'Bheline', Border=1)
    
    
    d = 'Aerenwe'
    p= "Banien's Deep"
    Game.add_province(p, d, Region, 'LS', Population=1, Magic=6, Terrain='Forest', x=1430, y=2425, Waterway=True)
    Game.add_holding(p, 'LS', 'Law', 1)
    Game.add_holding(p, 'SG', 'Guild', 1)
    Game.add_holding(p, 'HMA', 'Source', 3)
    Game.add_holding(p, 'RA', 'Source', 3)
    p = 'Calrie'
    Game.add_province(p, d, Region, 'LS', Population=6, Magic=0, Capital=True, x=1395, y=2300, Castle=6, Castle_Name='Caer Callin', Waterway=True)
    Game.add_geo(p,'Spiritsend', Border=1, RiverChasm=1)
    Game.add_geo(p,'Algael', Border=1, RiverChasm=1)
    Game.add_geo(p,"Banien's Deep", Border=1)
    Game.add_holding(p, 'LS', 'Law', 6)
    Game.add_holding(p, 'ETN', 'Temple', 6)
    Game.add_holding(p, 'SG', 'Guild', 3)
    Game.add_holding(p, 'HMA', 'Source', 0)
    p = 'Dhoneel'
    Game.add_province(p, d, Region, 'LS', Population=5, Magic=0, x=1295, y=2300, Waterway=True)
    Game.add_geo(p,'Calrie', Border=1)
    Game.add_geo(p,'Algael', Border=1)
    Game.add_geo(p,'Bellam', Border=1)
    Game.add_geo(p,'Fairfield', Border=1)
    Game.add_geo(p,'Edlin', Border=1)
    Game.add_holding(p, 'LS', 'Law', 5)
    Game.add_holding(p, 'ETN', 'Temple', 5)
    Game.add_holding(p, 'SG', 'Guild', 3)
    Game.add_holding(p, 'HMA', 'Source', 0)
    p = 'Halried'
    Game.add_province(p, d, Region, 'LS', Population=5, Magic=0, x=1280, y=2360)
    Game.add_geo(p,'Calrie', Border=1)
    Game.add_geo(p,'Dhoneel', Border=1)
    Game.add_geo(p,"Banien's Deep", Border=1)
    Game.add_geo(p,'Edlin', Border=1)
    Game.add_geo(p,'Duerlin', Border=1)
    Game.add_holding(p, 'LS', 'Law', 5)
    Game.add_holding(p, 'ETN', 'Temple', 5)
    Game.add_holding(p, 'SG', 'Guild', 3)
    Game.add_holding(p, 'HMA', 'Source', 0)
    p = 'Northvale'
    Game.add_province(p, d, Region, 'LS', Population=1, Magic=6, x=1465, y=2320, Terrain='Forest', Waterway=True)
    Game.add_geo(p,'Calrie', Border=1)
    Game.add_geo(p,"Banien's Deep", Border=1)
    Game.add_holding(p, 'LS', 'Law', 1)
    Game.add_holding(p, 'HMA', 'Source', 5)
    Game.add_holding(p, 'RA', 'Source', 1)
    p = 'Shadowgreen'
    Game.add_province(p, d, Region, 'LS', Population=1, Magic=6, x=1360, y=2470, Terrain='Forest', Waterway=True)
    Game.add_geo(p,'Halried', Border=1)
    Game.add_geo(p,"Banien's Deep", Border=1)
    Game.add_holding(p, 'LS', 'Law', 1)
    Game.add_holding(p, 'ETN', 'Temple', 1)
    Game.add_holding(p, 'MA', 'Guild', 1)
    Game.add_holding(p, 'HMA', 'Source', 5)
    Game.add_holding(p, 'RA', 'Source', 1)
    p = 'Westmarch'
    Game.add_province(p, d, Region, 'LS', Population=1, Magic=6, x=1260, y=2440, Terrain='Forest', Waterway=True)
    Game.add_geo(p,'Halried', Border=1)
    Game.add_geo(p,'Shadowgreen', Border=1)
    Game.add_geo(p,'Abbatuor', Border=1)
    Game.add_holding(p, 'LS', 'Law', 1)
    Game.add_holding(p, 'SG', 'Guild', 1)
    Game.add_holding(p, 'HMA', 'Source', 3)
    Game.add_holding(p, 'RA', 'Source', 3)


    d = 'Diemed'
    p= 'Aerele'
    Game.add_province(p, d, Region, 'HD', Population=4, Magic=1, x=870, y=2385, Capital=True, Waterway=True)
    Game.add_holding(p, 'HD', 'Law', 3)
    Game.add_holding(p, 'DA', 'Law', 0)
    Game.add_holding(p, 'OIT', 'Temple', 4)
    Game.add_holding(p, 'EH', 'Guild', 2)
    Game.add_holding(p, 'OT', 'Guild', 2)
    Game.add_holding(p, 'He', 'Source', 1)
    p = 'Blinene'
    Game.add_province(p, d, Region, 'HD', Population=3, Magic=6, x=750, y=2385, Terrain='Mountains', Waterway=True)
    Game.add_geo(p,'Aerele', Border=1)
    Game.add_holding(p, 'HD', 'Law', 2)
    Game.add_holding(p, 'OIT', 'Temple', 3)
    Game.add_holding(p, 'EH', 'Guild', 3)
    Game.add_holding(p, 'He', 'Source', 4)
    p = 'Ciliene'
    Game.add_province(p, d, Region, 'HD', Population=6, Magic=0, x=815, y=2305, Waterway=True)
    Game.add_geo(p,'Aerele', Border=1)
    Game.add_geo(p,'Blinene', Border=1)
    Game.add_geo(p,'Anuire', Border=1, RiverChasm = 1)
    Game.add_geo(p,'City of Anuire', Border=1, RiverChasm = 1, Road=1)
    Game.add_holding(p, 'HD', 'Law', 4)
    Game.add_holding(p, 'DA', 'Law', 2)
    Game.add_holding(p, 'OIT', 'Temple', 6)
    Game.add_holding(p, 'EH', 'Guild', 3)
    Game.add_holding(p, 'GK', 'Guild', 3)
    p = 'Duene'
    Game.add_province(p, d, Region, 'HD', Population=3, Magic=2, x=905, y=2355, Waterway=True)
    Game.add_geo(p,'Aerele', Border=1)
    Game.add_geo(p,'Ciliene', Border=1)
    Game.add_holding(p, 'HD', 'Law', 3)
    Game.add_holding(p, 'OIT', 'Temple', 3)
    Game.add_holding(p, 'OT', 'Guild', 3)
    Game.add_holding(p, 'He', 'Source', 2)
    p = 'Moere'
    Game.add_province(p, d, Region, 'HD', Population=5, Magic=0, x=870, y=2260, Waterway=True)
    Game.add_geo(p,'Duene', Border=1)
    Game.add_geo(p,'Ciliene', Border=1)
    Game.add_geo(p,'Anuire', Border=1, RiverChasm = 1)
    Game.add_geo(p,'Caulnor', Border=1, RiverChasm = 1)
    Game.add_geo(p,'Endier', Border=1, Road=1)
    Game.add_holding(p, 'HD', 'Law', 3)
    Game.add_holding(p, 'DA', 'Law', 1)
    Game.add_holding(p, 'OIT', 'Temple', 3)
    Game.add_holding(p, 'OT', 'Guild', 1)
    Game.add_holding(p, 'GK', 'Guild', 4)
    p = 'Tier'
    Game.add_province(p, d, Region, 'HD', Population=2, Magic=3, x=935, y=2275)
    Game.add_geo(p,'Duene', Border=1)
    Game.add_geo(p,'Moere', Border=1)
    Game.add_holding(p, 'HD', 'Law', 1)
    Game.add_holding(p, 'OIT', 'Temple', 2)
    Game.add_holding(p, 'GK', 'Guild', 2)
    Game.add_holding(p, 'He', 'Source', 1)

    Game.add_geo('Ciliene', 'Seaward', Shipping=1)

    d = 'Ilien'
    p= 'Ilien'
    Game.add_province(p, d, Region, 'RA', Population=7, Magic=0, x=1085, y=2400
                      , Capital=True, Waterway=True, Castle=7, Castle_Name='Towers of Ilien')
    Game.add_geo(p,'Abbatuor', Border=1, RiverChasm=1)
    Game.add_geo(p,'Duerlin', Border=1, RiverChasm=1)
    Game.add_geo(p,'Caercas', Border=1, RiverChasm=1)
    Game.add_holding(p, 'RA', 'Law', 7)
    Game.add_holding(p, 'IHH', 'Temple', 4)
    Game.add_holding(p, 'ETN', 'Temple', 3)
    Game.add_holding(p, 'EH', 'Guild', 7)
    Game.add_holding(p, 'RA', 'Source', 0)
    Game.add_geo(p, 'Ruorven', Shipping=1)


    d = 'Medoere'
    p = 'Alamier'
    Game.add_province(p, d, Region, 'RCS', Population=4, Magic=1, x=960, y=2360, Waterway=True)
    Game.add_geo(p,'Duene', Border=1)
    Game.add_geo(p,'Tier', Border=1)
    Game.add_holding(p, 'RCS', 'Law', 3)
    Game.add_holding(p, 'RCS', 'Temple', 4)
    Game.add_holding(p, 'IHH', 'Temple', 0)
    Game.add_holding(p, 'OT', 'Guild', 2)
    Game.add_holding(p, 'EH', 'Guild', 2)
    Game.add_holding(p, 'RA', 'Source', 1)

    p = 'Braeme'
    Game.add_province(p, d, Region, 'RCS', Population=3, Magic=2, x=1030, y=2340, Waterway=True, Capital=True)
    Game.add_geo(p,'Ilien', Border=1)
    Game.add_geo(p,'Caercas', Border=1, RiverChasm=1)
    Game.add_geo(p,'Alamier', Border=1)
    Game.add_holding(p, 'RCS', 'Law', 3)
    Game.add_holding(p, 'RCS', 'Temple', 3)
    Game.add_holding(p, 'OT', 'Guild', 3)
    Game.add_holding(p, 'He', 'Source', 1)
    p = 'Caerwil'
    Game.add_province(p, d, Region, 'RCS', Population=2, Magic=3, x=1000, y=2260, Waterway=True)
    Game.add_geo(p,'Caercas', Border=1, RiverChasm=1)
    Game.add_geo(p,'Ghoried', Border=1, RiverChasm=1)
    Game.add_geo(p,'Braeme', Border=1)
    Game.add_geo(p,'Tier', Border=1)
    Game.add_geo(p,'Alamier', Border=1)
    Game.add_holding(p, 'GK', 'Law', 2)
    Game.add_holding(p, 'RCS', 'Temple', 2)
    Game.add_holding(p, 'GK', 'Guild', 2)
    Game.add_holding(p, 'He', 'Source', 3)

    d = 'Mieres'
    p = 'Brenlie'
    Game.add_province(p, d, Region, 'AV', Population=3, Magic=4, Terrain='Mountains', x=640, y=2665, Waterway=True)
    Game.add_holding(p, 'AV', 'Law', 1)
    Game.add_holding(p, 'EOM', 'Temple', 3)
    Game.add_holding(p, 'AV', 'Guild', 3)
    Game.add_holding(p, 'Mhi', 'Source', 0)

    p = 'Crenier'
    Game.add_province(p, d, Region, 'AV', Population=2, Magic=5, Terrain='Forest', x=890, y=2640, Waterway=True)
    Game.add_holding(p, 'AV', 'Law', 1)
    Game.add_holding(p, 'CJS', 'Temple', 2)
    Game.add_holding(p, 'AV', 'Guild', 2)
    Game.add_holding(p, 'Mhi', 'Source', 3)

    p = 'Dhalier'
    Game.add_province(p, d, Region, 'AV', Population=1, Magic=6, Terrain='Forest', x=790, y=2720, Waterway=True)
    Game.add_geo(p, 'Crenier', Border=1)
    Game.add_holding(p, 'DA', 'Law', 1)
    Game.add_holding(p, 'VOM', 'Temple', 1)
    Game.add_holding(p, 'AV', 'Guild', 1)
    Game.add_holding(p, 'Mhi', 'Source', 0)


    p = 'Ghaele'
    Game.add_province(p, d, Region, 'AV', Population=2, Magic=3, x=615, y=2615, Waterway=True)
    Game.add_geo(p, 'Brenlie', Border=1)
    Game.add_holding(p, 'AV', 'Law', 1)
    Game.add_holding(p, 'ETN', 'Temple', 2)
    Game.add_holding(p, 'AV', 'Guild', 2)
    Game.add_holding(p, 'Mhi', 'Source', 3)

    p = 'Lathier'
    Game.add_province(p, d, Region, 'AV', Population=3, Magic=4, Terrain='Forest', x=825, y=2600, Waterway=True)
    Game.add_geo(p, 'Crenier', Border=1)
    Game.add_holding(p, 'AV', 'Law', 1)
    Game.add_holding(p, 'EOM', 'Temple', 3)
    Game.add_holding(p, 'AV', 'Guild', 2)
    Game.add_holding(p, 'Mhi', 'Source', 4)

    p = 'Mielien'
    Game.add_province(p, d, Region, 'AV', Population=2, Magic=5, Terrain='Forest', x=730, y=2600, Waterway=True)
    Game.add_geo(p, 'Brenlie', Border=1)
    Game.add_geo(p, 'Ghaele', Border=1)
    Game.add_geo(p, 'Lathier', Border=1)
    Game.add_holding(p, 'AV', 'Law', 1)
    Game.add_holding(p, 'EOM', 'Temple', 2)
    Game.add_holding(p, 'AV', 'Guild', 2)
    Game.add_holding(p, 'Mhi', 'Source', 5)

    p = 'Seaward'
    Game.add_province(p, d, Region, 'AV', Population=4, Magic=3, Terrain='Forest', x=935, y=2595
                      , Waterway=True, Capital=True)
    Game.add_geo(p, 'Lathier', Border=1)
    Game.add_geo(p, 'Crenier', Border=1)
    Game.add_holding(p, 'AV', 'Law', 2)
    Game.add_holding(p, 'DA', 'Law', 2)
    Game.add_holding(p, 'EOM', 'Temple', 3)
    Game.add_holding(p, 'VOM', 'Temple', 1)
    Game.add_holding(p, 'AV', 'Guild', 4)
    Game.add_holding(p, 'Mhi', 'Source', 0)

    p = 'Serien'
    Game.add_province(p, d, Region, 'AV', Population=4, Magic=3, Terrain='Forest', x=760, y=2660)
    Game.add_geo(p, 'Brenlie', Border=1)
    Game.add_geo(p, 'Crenier', Border=1)
    Game.add_geo(p, 'Dhalier', Border=1)
    Game.add_geo(p, 'Lathier', Border=1)
    Game.add_geo(p, 'Mielien', Border=1)
    Game.add_holding(p, 'AV', 'Law', 1)
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'ETN', 'Temple', 4)
    Game.add_holding(p, 'AV', 'Guild', 4)
    Game.add_holding(p, 'Mhi', 'Source', 0)

    d = 'Albiele Island'
    p = 'Albiele'
    Game.add_province(p, d, Region, '', Population=0, Magic=5, x=1140, y=2610, Waterway=True)
    
    d = 'The Spiderfell'
    p = 'The Spiderfell'
    Game.add_province(p, d, Region, 'Sp', Population=0, Magic=7, x=1015, y=2185, Capital=True, Terrain='Forest')
    Game.add_geo(p,'Caerwil', Border=1)
    Game.add_geo(p,'Ghoried', Border=1)
    Game.add_geo(p,'Bheline', Border=1)
    Game.add_geo(p,'Rhumannen', Border=1)
    Game.add_geo(p,'Endier', Border=1)
    Game.add_geo(p,'Tireste', Border=1)
    Game.add_geo(p,'Moere', Border=1)
    Game.add_geo(p,'Tier', Border=1)
    Game.add_holding(p, 'Sp', 'Law', 0)
    Game.add_holding(p, 'Ca', 'Source', 1)
    
    
    Game.add_regent('MR', 'Marlae Roesone', Bloodline='Br', Culture='A', Regency_Bonus=4
                    , Regency_Points=30, Gold_Bars=15)
    Game.add_regent('SG', 'Siele Ghoried (Spider River Traders)', Bloodline='Ma', Culture='A', Archetype='Scout'
                    , Alignment='LG', Regency_Bonus=1, Attitude='Aggressive')
    Game.add_regent('OT', 'Orthien Tane', Bloodline='An', Culture='A', Archetype='Thug'
                    , Alignment='CN', Regency_Bonus=-1, Attitude='Aggressive')
    Game.add_relationship('MR', 'GT', Diplomacy = -2)
    Game.add_relationship('GT', 'MR', Diplomacy = -1)
    Game.add_relationship('MR', 'HD', Diplomacy = -2)
    Game.add_relationship('HD', 'MR', Diplomacy = -1)

    Game.add_regent('LS', 'Liliene Swordswraith', Archetype='Bandit', Bloodline='An', Culture='A'
                    , Regency_Bonus=3, Alignment='NG', Lieutenants=['Cole Alwier', 'Cale Alwier']
                    , Attitude='Peaceful')
    Game.add_regent('HMA', 'High mage Aelies', Archetype='Archmage', Culture='E', Bloodline='Vo'
                    , Regency_Bonus=3, Alignment='LN', Regency_Points=35)
    Game.add_regent('MA', 'Mourde Alondir', Archetype='Scout', Culture='A', Bloodline='Ma'
                    , Regency_Bonus=1, Alignment='LN')
    Game.add_relationship('LS', 'MR', Diplomacy = 1)

    Game.add_regent('HD', 'Heirl Diem', Archetype='Knight', Bloodline='Br', Culture='A'
                    , Regency_Bonus=4, Alignment='LN', Lieutenants=['Lasca Diem', 'Assistant 1', 'Assistant 2', 'Assistant 3'])
    Game.add_regent('OIT', 'Orthodox Imperial Temple of Haelyn (Lavalan Briesen)', Archetype='Priest'
                   , Culture='A', Bloodline='An', Regency_Bonus=3)
    Game.add_relationship('OIT', 'WIT', Diplomacy = -1)

    Game.add_regent('RA', 'Rogr Aglondier', Archetype='Mage', Culture='A', Bloodline='Ma'
                    , Regency_Bonus=1, Alignment='NG', Lieutenants=['Lady Alliene Aglondir'])
    Game.add_relationship('RCS', 'RA', Diplomacy = 1)
    Game.add_relationship('RA', 'RCS', Diplomacy = 1)
    Game.add_relationship('MR', 'RA', Diplomacy = 1)
    Game.add_relationship('RA', 'MR', Diplomacy = 1)
    Game.add_regent('EH', 'Guilder el-Hadid (Point of Call Exchange)', Culture='Kh', Bloodline='Br', Regency_Bonus=-1
                    , Archetype='Scout', Alignment='LE', Gold_Bars=43, Regency_Points=10)

    Game.add_regent('RCS', "Suris Enlien (Rournils' Celestial Spell)", Archetype='Priest', Culture='A', Bloodline='Re'
                    , Regency_Bonus=4, Alignment='NG', Lieutenants=['Lord Kotrin Skirvin'])
    Game.add_relationship('HD', 'RCS', Diplomacy = -1)
    Game.add_relationship('GK', 'RCS', Diplomacy = -1)
    Game.add_relationship('RCS', 'GK', Diplomacy = -1)
    Game.add_regent('He', "Hermedhie", Archetype='Mage', Culture='A', Bloodline='Vo'
                    , Regency_Bonus=3, Alignment='LN')
    Game.add_relationship('RCS', 'He', Diplomacy = 5)
    Game.add_relationship('He', 'RCS', Diplomacy = 5)

    # https://i.stack.imgur.com/8f5ui.png
    Game.add_regent('Sp', 'The Spider', Class='Awnsheghlien', Level=17, Race='Goblin'
                    , Str=3, Dex=3, Con=4, Int=0, Wis=2, Cha=2, Insight=2, Persuasion=2, Deception=2
                    , Regency_Bonus=8, Bloodline='Az', Culture='G', Alignment='CE', Gold_Bars =25)

    Game.add_regent('IHH', 'Impregnable Heart of Haelyn (Hubaere Armeindin)', Archetype='Priest'
                    , Culture='A', Bloodline='An', Regency_Bonus=4, Alignment='LG'
                    , Regency_Points=35, Gold_Bars = 31)

    Game.add_regent('AV', 'Arron Vaumel', Archetype='Mage', Culture='A', Bloodline='Br'
                    , Regency_Bonus=1, Alignment='NE', Attitude='Aggressive')
    Game.add_relationship('AV', 'DA', Diplomacy=1, Vassalage=1)

    Game.add_regent('Mhi', 'Mhistecai', Archetype='Mage', Culture='A', Bloodline='Vo'
                    , Regency_Bonus=4, Alignment='NN')
    Game.add_relationship('AV', 'Mh', Diplomacy=-1)
    Game.add_relationship('Mh', 'AV', Diplomacy=-1)

    #Game.add_geo('Cilene', 'City of Anuire', Border=1)

    Game.add_regent('ETN', 'Eastern Temple of Nesirie (Maire Cwllmie)', Archetype='Priest', Culture='A',
                    Regency_Bonus=3, Bloodline='Ma', Alignment='NG')
    Game.add_regent('VOM', 'Vos of Mieres (Pyotr Selenie)', Archetype='Priest', Culture='A',
                    Regency_Bonus=1, Bloodline='Az', Alignment='NE')
    Game.add_regent('EOM', 'Eloele of Mieres (Sarae Somellin)', Archetype='Priest', Culture='A',
                    Regency_Bonus=1, Bloodline='Az', Alignment='CE')
    # From Birthright.Net -> A not so silent war, expecially in urbanized areas, has begun in the last years with the violent temple Vos of Mieres.
    Game.add_relationship('EOM', 'VOM', Diplomacy=-2)
    Game.add_relationship('VOM', 'EOM', Diplomacy=-2)
    Game.add_regent('CJS', 'Celestial Jewel of Sarimie (Temias Coumain)', Culture='A', Bloodline='Br', Regency_Bonus=4
                   , Archetype='Cultist', Alignment='CN')



    Game.add_ship('MR', 'Abbatuor', 'Caravel')
    Game.add_ship('MR','Abbatuor', 'Caravel')
    Game.add_ship('MR','Abbatuor', 'Coaster')

    for a in range(2):
        Game.add_ship('LS', 'Calrie', 'Galleon')
        Game.add_ship('LS','Calrie', 'Coaster')
        for a in range(3):
            Game.add_ship('LS', 'Calrie', 'Caravel')
            
    Game.add_ship('HD', 'Aerele', 'Galleon')
    Game.add_ship('HD','Ciliene', 'Galleon')
    Game.add_ship('HD','Ciliene', 'Caravel')
    for a in range(3):
        Game.add_ship('HD','Ciliene', 'Caravel')
        Game.add_ship('HD','Aerele', 'Caravel')
        Game.add_ship('HD','Ciliene','Coaster')
        
    p = 'Ilien'
    for a in range(2):
        Game.add_ship('RA', p, 'Galleon')
        Game.add_ship('RA',p, 'Caravel')
        Game.add_ship('RA',p, 'Caravel')
        Game.add_ship('RA',p, 'Coaster')
        
    for a in range(4):
        Game.add_ship('RCS', 'Alamier', 'Caravel')
    
    Region = 'The Western Coast'
    d = 'Boeruine'
    p = 'Bacaele'
    Game.add_province(p, d, Region, 'AB', Population=3, Magic=2, x=475, y=1830, Waterway=True)
    Game.add_holding(p, 'AB', 'Law', 3)
    Game.add_holding(p, 'HTC', 'Temple', 3)
    Game.add_holding(p, 'Bor', 'Guild', 3)
    Game.add_holding(p, 'AI', 'Source', 2)
    Game.add_geo(p, 'Biliene', Shipping=1)
    p = 'Calant'
    Game.add_province(p, d, Region, 'AB', Population=3, Magic=4, x=590, y=1765, Terrain = 'Forest')
    Game.add_holding(p, 'AB', 'Law', 3)
    Game.add_holding(p, 'TD', 'Temple', 2)
    Game.add_holding(p, 'HTC', 'Temple', 0)
    Game.add_holding(p, 'Bor', 'Guild', 3)
    Game.add_holding(p, 'AI', 'Source', 4)
    p = 'Dhalaese'
    Game.add_province(p, d, Region, 'AB', Population=3, Magic=4, x=750, y=1745, Terrain = 'Forest')
    Game.add_geo(p, 'Ghonallison', Border=1)
    Game.add_geo(p, 'Monsedge', Border=1)
    Game.add_geo(p, 'Pechalinn', Border=1)
    Game.add_holding(p, 'AB', 'Law', 3)
    Game.add_holding(p, 'TD', 'Temple', 0)
    Game.add_holding(p, 'HTC', 'Temple', 3)
    Game.add_holding(p, 'Bor', 'Guild', 0)
    Game.add_holding(p, 'GTh', 'Guild', 3)
    Game.add_holding(p, 'AI', 'Source', 4)
    p = 'Fhoruile'
    Game.add_province(p, d, Region, 'AB', Population=3, Magic=4, x=607, y=1675, Terrain = 'Forest')
    Game.add_geo(p, 'Calant', Border=1)
    Game.add_holding(p, 'AB', 'Law', 3)
    Game.add_holding(p, 'TD', 'Temple', 2)
    Game.add_holding(p, 'Bor', 'Guild', 3)
    Game.add_holding(p, 'AI', 'Source', 4)
    p = 'Nieter'
    Game.add_province(p, d, Region, 'AB', Population=3, Magic=4, x=670, y=1810, Terrain = 'Forest')
    Game.add_geo(p, 'Calant', Border=1)
    Game.add_geo(p, 'Dhalaese', Border=1)
    Game.add_geo(p, 'Pechalinn', Border=1)
    Game.add_geo(p, 'Monsedge', Border=1)
    Game.add_holding(p, 'AB', 'Law', 3)
    Game.add_holding(p, 'HTC', 'Temple', 3)
    Game.add_holding(p, 'GTh', 'Guild', 3)
    Game.add_holding(p, 'AI', 'Source', 4)
    p = 'Redoubt'
    Game.add_province(p, d, Region, 'AB', Population=3, Magic=4, x=590, y=1860, Terrain = 'Forest')
    Game.add_geo(p, 'Calant', Border=1)
    Game.add_geo(p, 'Nieter', Border=1)
    Game.add_geo(p, 'Bacaele', Border=1)
    Game.add_holding(p, 'AB', 'Law', 3)
    Game.add_holding(p, 'HTC', 'Temple', 3)
    Game.add_holding(p, 'Bor', 'Guild', 3)
    Game.add_holding(p, 'GTh', 'Guild', 0)
    Game.add_holding(p, 'AI', 'Source', 4)
    p = 'Rivien'
    Game.add_province(p, d, Region, 'AB', Population=6, Magic=1, x=660, y=1700, Terrain = 'Hills')
    Game.add_geo(p, 'Dhalaese', Border=1)
    Game.add_geo(p, 'Fhoruile', Border=1)
    Game.add_geo(p, 'Calant', Border=1)
    Game.add_geo(p, 'Nieter', Border=1)
    Game.add_holding(p, 'AB', 'Law', 6)
    Game.add_holding(p, 'TD', 'Temple', 6)
    Game.add_holding(p, 'Bor', 'Guild', 5)
    Game.add_holding(p, 'GTh', 'Guild', 1)
    Game.add_holding(p, 'AI', 'Source', 1)
    p = 'Seasedge'
    Game.add_province(p, d, Region, 'AB', Population=6, Magic=0, x=520, y=1780, Waterway=True
                      , Capital=True, Castle=6, Castle_Name='Seaharrow')
    Game.add_geo(p, 'Calant', Border=1)
    Game.add_geo(p, 'Bacaele', Border=1)
    Game.add_geo(p, 'Redoubt', Border=1)
    Game.add_holding(p, 'AB', 'Law', 6)
    Game.add_holding(p, 'HTC', 'Temple', 3)
    Game.add_holding(p, 'TD', 'Temple', 3)
    Game.add_holding(p, 'Bor', 'Guild', 5)
    Game.add_holding(p, 'AI', 'Source', 0)
    Game.add_geo(p, 'Ilien', Shipping=1)
    Game.add_geo(p, 'City of Anuire', Shipping=1)
    Game.add_geo(p, 'Seasdeep', Shipping=1)
    for a in range(2):
        Game.add_troops('AB', p, 'Archers')
        Game.add_troops('AB', p, 'Archers')
        Game.add_troops('AB', p, 'Artillerists')
        Game.add_troops('AB', p, 'Infantry')
        Game.add_troops('AB', p, 'Infantry')
    for a in range(3):
        Game.add_troops('AB', p, 'Elite Infantry')
        Game.add_troops('AB', p, 'Knights')
        Game.add_troops('AB', p, 'Pikemen')
        Game.add_troops('AB', p, 'Scouts')  
    p = 'Tariene'
    Game.add_province(p, d, Region, 'AB', Population=6, Magic=0, x=535, y=1690, Waterway=True)
    Game.add_geo(p, 'Calant', Border=1)
    Game.add_geo(p, 'Fhoruile', Border=1)
    Game.add_geo(p, 'Seasedge', Border=1)
    Game.add_holding(p, 'AB', 'Law', 6)
    Game.add_holding(p, 'HTC', 'Temple', 1)
    Game.add_holding(p, 'TD', 'Temple', 5)
    Game.add_holding(p, 'Bor', 'Guild', 4)
    Game.add_holding(p, 'SH', 'Guild', 2)
    Game.add_holding(p, 'AI', 'Source', 0)
    Game.add_geo(p, 'Seasdeep', Shipping=1)
        

    d = 'Talinie'
    p = 'Freestead'
    Game.add_province(p, d, Region, 'TD', Population=2, Magic=5, x=755, y=1525, Terrain='Hills')
    Game.add_holding(p, 'TD', 'Law', 1)
    Game.add_holding(p, 'TD', 'Temple', 2)
    Game.add_holding(p, 'SH', 'Guild', 2)
    Game.add_holding(p, 'TA', 'Source', 5)
    p = 'Greensward'
    Game.add_province(p, d, Region, 'TD', Population=2, Magic=5, x=590, y=1540, Terrain='Forest', Waterway=True)
    Game.add_geo(p, 'Fhoruile', Border=1, RiverChasm=1)
    Game.add_holding(p, 'TD', 'Law', 1)
    Game.add_holding(p, 'TD', 'Temple', 2)
    Game.add_holding(p, 'BA', 'Guild', 2)
    Game.add_holding(p, 'TA', 'Source', 5)
    Game.add_troops('TD', p, 'Archers')
    Game.add_geo(p, 'Seasdeep', Shipping=1)
    for a in range(3):
        Game.add_troops('TD', p, 'Infantry')
    Game.add_troops('TD', p, 'Scouts')
    Game.add_troops('TD', p, 'Mercenary Cavalry')
    p = 'Ice Haven'
    Game.add_province(p, d, Region, 'TD', Population=3, Magic=4, x=645, y=1495, Terrain='Forest'
                      , Waterway=True, Capital=True)
    Game.add_geo(p, 'Greensward', Border=1)
    Game.add_holding(p, 'TD', 'Law', 2)
    Game.add_holding(p, 'TD', 'Temple', 3)
    Game.add_holding(p, 'BA', 'Guild', 2)
    Game.add_holding(p, 'SH', 'Guild', 0)
    Game.add_holding(p, 'TA', 'Source', 4)
    p = 'Lindholme'
    Game.add_province(p, d, Region, 'TD', Population=5, Magic=2, x=660, y=1600, Terrain='Forest'
                      , Waterway=True)
    Game.add_geo(p, 'Fhoruile', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Rivien', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Greensward', Border=1)
    Game.add_holding(p, 'TD', 'Law', 3)
    Game.add_holding(p, 'AB', 'Law', 2)
    Game.add_holding(p, 'TD', 'Temple', 4)
    Game.add_holding(p, 'BA', 'Guild', 3)
    Game.add_holding(p, 'SH', 'Guild', 2)
    Game.add_holding(p, 'TA', 'Source', 2)
    Game.add_geo(p, 'Seasdeep', Shipping=1)
    p = 'Seaport'
    Game.add_province(p, d, Region, 'TD', Population=1, Magic=4, x=525, y=1610, Waterway=True)
    Game.add_geo(p, 'Greensward', Border=1)
    Game.add_geo(p, 'Fhoruile', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Tariene', Border=1, RiverChasm=1)
    Game.add_holding(p, 'AB', 'Law', 1)
    Game.add_holding(p, 'TD', 'Temple', 0)
    Game.add_holding(p, 'SH', 'Guild', 1)
    Game.add_holding(p, 'TA', 'Source', 3)

    p = 'Serimset'
    Game.add_province(p, d, Region, 'TD', Population=2, Magic=5, x=685, y=1530, Terrain='Forest')
    Game.add_geo(p, 'Lindholme', Border=1, Road=1)
    Game.add_geo(p, 'Greensward', Border=1)
    Game.add_geo(p, 'Freestead', Border=1, Road=1)
    Game.add_geo(p, 'Ice Haven', Border=1)
    Game.add_holding(p, 'TD', 'Law', 1)
    Game.add_holding(p, 'TD', 'Temple', 2)
    Game.add_holding(p, 'BA', 'Guild', 2)
    Game.add_holding(p, 'TA', 'Source', 5)
    p = "Winter's Deep"
    Game.add_province(p, d, Region, 'TD', Population=3, Magic=4, x=710, y=1460, Terrain='Forest')
    Game.add_geo(p, 'Ice Haven', Border=1)
    Game.add_geo(p, 'Serimset', Border=1)
    Game.add_geo(p, 'Freestead', Border=1)
    Game.add_holding(p, 'TD', 'Law', 2)
    Game.add_holding(p, 'TD', 'Temple', 2)
    Game.add_holding(p, 'SH', 'Guild', 3)
    Game.add_holding(p, 'TA', 'Source', 4)

    d = 'Brosengae'
    p = 'Bindier'
    Game.add_province(p, d, Region, 'EM', Population=4, Magic=1, x=640, y=2280, Capital=True)
    Game.add_holding(p, 'EM', 'Law', 4)
    Game.add_holding(p, 'PSN', 'Temple', 2)
    Game.add_holding(p, 'EM', 'Guild', 4)
    Game.add_geo(p, 'Crenier')

    p = 'Coere'
    Game.add_province(p, d, Region, 'EM', Population=4, Magic=3, x=665, y=2205, Terrain='Mountains')
    Game.add_geo(p, 'Bindier', Border=1)
    Game.add_geo(p, 'Daulton', Border=1)
    Game.add_geo(p, 'Taliern', Border=1)
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'EM', 'Law', 1)
    Game.add_holding(p, 'PSN', 'Temple', 2)
    Game.add_holding(p, 'TOF', 'Temple', 2)
    Game.add_holding(p, 'EM', 'Guild', 4)
    p = 'Marilen'
    Game.add_province(p, d, Region, 'EM', Population=4, Magic=3, x=620, y=2170, Terrain='Mountains')
    Game.add_geo(p, 'Bindier', Border=1)
    Game.add_geo(p, 'Coere', Border=1)
    Game.add_geo(p, 'Taliern', Border=1)
    Game.add_geo(p, 'Vanilen', Border=1)
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'EM', 'Law', 1)
    Game.add_holding(p, 'TOF', 'Temple', 2)
    Game.add_holding(p, 'EM', 'Guild', 4)


    d = 'Rhuobhe'
    p = 'Rhuobhe'
    Game.add_province(p, d, Region, 'Rh', Population=2, Magic=9, x=685, y=1925
                      , Capital=True, Terrain='Mountains', Castle=2
                      , Castle_Name='Tower Ruannoch')
    Game.add_holding(p, 'Rh', 'Law', 2)
    Game.add_holding(p, 'Rh', 'Source', 9)
    Game.add_geo(p, 'Redoubt', Border=1)
    Game.add_geo(p, 'Nieter', Border=1)
    Game.add_geo(p, 'Pechalinn', Border=1)
    Game.add_geo(p, 'Elevesnemiere', Border=1)
    Game.add_geo(p, 'Nentril', Border=1)
    
    
    d = 'Taeghas'
    p = 'Bayside'
    Game.add_province(p, d, Region, 'HK', Population=3, Magic=2, x=535, y=2000)
    Game.add_holding(p, 'DA', 'Law', 2)
    Game.add_holding(p, 'AB', 'Law', 0)
    Game.add_holding(p, 'PSN', 'Temple', 3)
    Game.add_holding(p, 'FS', 'Guild', 2)
    Game.add_holding(p, 'HK', 'Source', 2)
    p = 'Bhaine'
    Game.add_province(p, d, Region, 'HK', Population=6, Magic=0, x=465, y=2040, Terrain='Hills')
    Game.add_geo(p, 'Bayside', Border=1)
    Game.add_holding(p, 'DA', 'Law', 3)
    Game.add_holding(p, 'HK', 'Law', 3)
    Game.add_holding(p, 'PSN', 'Temple', 4)
    Game.add_holding(p, 'WIT', 'Temple', 4)
    Game.add_holding(p, 'FS', 'Guild', 2)
    Game.add_holding(p, 'HK', 'Source', 0)
    Game.add_geo(p, 'Abbatuor', Shipping=1)

        
    p = 'Brosien'
    Game.add_province(p, d, Region, 'HK', Population=2, Magic=6, x=560, y=2100, Terrain='Mountains')
    Game.add_geo(p, 'Bhaine', Border=1)
    Game.add_geo(p, 'Marilen', Border=1)
    Game.add_geo(p, 'Taliern', Border=1)
    Game.add_geo(p, 'Vanilen', Border=1)
    Game.add_holding(p, 'DA', 'Law', 1)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'FS', 'Guild', 2)
    Game.add_holding(p, 'HK', 'Source', 6)
    p = 'Islien'
    Game.add_province(p, d, Region, 'HK', Population=3, Magic=4, x=485, y=2175, Terrain='Forest')
    Game.add_holding(p, 'DA', 'Law', 2)
    Game.add_holding(p, 'PSN', 'Temple', 3)
    Game.add_holding(p, 'FS', 'Guild', 3)
    Game.add_holding(p, 'HK', 'Source', 4)
    Game.add_geo(p, 'Brosien', Border=1)
    p = 'Portage'
    Game.add_province(p, d, Region, 'HK', Population=3, Magic=2, x=510, y=1925, Terrain='Forest')
    Game.add_geo(p, 'Bacaele', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Redoubt', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Bayside', Border=1)
    Game.add_holding(p, 'DA', 'Law', 2)
    Game.add_holding(p, 'AB', 'Law', 0)
    Game.add_holding(p, 'PSN', 'Temple', 3)
    Game.add_holding(p, 'FS', 'Guild', 2)
    Game.add_holding(p, 'HK', 'Source', 2)
    p = 'Seamist'
    Game.add_province(p, d, Region, 'HK', Population=2, Magic=6, x=588, y=2051, Terrain='Mountains')
    Game.add_geo(p, 'Bayside', Border=1)
    Game.add_geo(p, 'Nentril', Border=1)
    Game.add_geo(p, 'Vanilen', Border=1)
    Game.add_geo(p, 'Brosien', Border=1)
    Game.add_holding(p, 'DA', 'Law', 1)
    Game.add_holding(p, 'WIT', 'Temple', 2)
    Game.add_holding(p, 'HK', 'Source', 6)
    p = 'Seasdeep'
    Game.add_province(p, d, Region, 'HK', Population=3, Magic=4, x=460, y=2100, Terrain='Forest', Capital=True)
    Game.add_geo(p, 'Islien', Border=1)
    Game.add_geo(p, 'Bhaine', Border=1)
    Game.add_geo(p, 'Brosien', Border=1)
    Game.add_holding(p, 'DA', 'Law', 2)
    Game.add_holding(p, 'PSN', 'Temple', 3)
    Game.add_holding(p, 'FS', 'Guild', 1)
    Game.add_holding(p, 'HK', 'Source', 4)

    p = "Wilder's Gorge"
    Game.add_province(p, d, Region, 'HK', Population=1, Magic=6, x=600, y=1930, Terrain='Forest')
    Game.add_geo(p, 'Portage', Border=1)
    Game.add_geo(p, 'Redoubt', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Rhuobhe', Border=1)
    Game.add_geo(p, 'Nentril', Border=1)
    Game.add_geo(p, 'Seamist', Border=1)
    Game.add_geo(p, 'Bayside', Border=1)
    Game.add_holding(p, 'DA', 'Law', 1)
    Game.add_holding(p, 'AB', 'Law', 0)
    Game.add_holding(p, 'WIT', 'Temple', 1)
    Game.add_holding(p, 'HK', 'Source', 6)
    
    
    Game.add_regent('AB', "Aeric Boeruine (Boeruine)", Culture='A', Level=12, Class='Fighter'
               , Str=3, Dex=2, Con=2, Int=2, Wis=1, Cha=3, Alignment='LN', Regency_Bonus=4
               , Insight=5, Persuasion=8, Deception=3, Attitude='Aggressive', Regency_Points=100
               , Gold_Bars=151)
    Game.add_relationship('CA', 'AB', Diplomacy=1)
    Game.add_relationship('AB', 'CA', Diplomacy=1)
    Game.add_relationship('LF', 'AB', Diplomacy=1)
    Game.add_relationship('AB', 'LF', Diplomacy=1)
    Game.add_relationship('AB', 'DA', Diplomacy=-2)
    Game.add_relationship('DA', 'AB', Diplomacy=-3)
    Game.add_regent('AI', 'Arlen Innis', Archetype='Mage', Culture='A', Bloodline='Vo', Alignment='LN'
                   , Regency_Bonus=2)
    Game.add_relationship('AI', 'AB', Vassalage=2)
    Game.add_regent('Bor', 'Arien Borthein', Archetype='Scout', Culture='A', Bloodline='Re'
                    ,Regency_Bonus=1, Alignment='CN')
    Game.add_relationship('Bor', 'AB', Vassalage=2)


    Game.add_regent('TD', 'Thuriene Donalls (Northern Imperial Temple of Haelyn)', Culture='A'
                    , Bloodline='An', Archetype='Cult Fanatic', Regency_Bonus=3, Alignment='LG'
                    , Gold_Bars=22, Regency_Points=33, Lieutenants=['Torias Griene'])
    Game.add_relationship('TD', 'AB', Vassalage=3, Diplomacy=3)
    Game.add_relationship('AB', 'TD', Diplomacy=3)
    Game.add_relationship('DA', 'TD', Diplomacy=-3)
    Game.add_regent('TA', 'Torele Anviras', Archetype='Mage', Culture='A', Bloodline='An'
                    , Regency_Bonus=3, Alignment='NG')

    Game.add_geo('Lindholm', 'Seasdeep', Shipping=1)


    Game.add_regent('EM', 'Duchess Eriene Mierelen (Brosengae Royal Guild)', Culture='A', Race='Human', Bloodline='Ba'
                    , Archetype='Spy', Regency_Bonus=3, Alignment='NE'
                    , Lieutenants=['Royal Guildsman {}'.format(a+1) for a in range(3)])
    Game.add_relationship('EM', 'DA', Vassalage=3)
    Game.add_relationship('DA', 'EM', Diplomacy=3)
    Game.add_relationship('EM', 'AB', Diplomacy=3)
    Game.add_relationship('AB', 'EM', Diplomacy=3)


    Game.add_regent('Rh', 'Rhuobhe "Manslayer"', Race='Elf', Attitude='Aggressive'
                    , Str=4, Dex=4, Con=2, Int=4, Wis=2, Cha=3, Level=20, Regency_Bonus=8
                    , Class='Awnsheghlien', Insight=8, Persuasion=9, Deception=9
                    , Bloodline='Az', Alignment='NE', Arcane=True, Culture='E')

    Game.add_regent('HK', "Harald Khorien", Archetype='Mage', Culture='A', Bloodline='An', Regency_Bonus=3
                    , Alignment='NG', Lieutenants=['{} of the Four'.format(a+1) for a in range(4)]
                    , Regency_Points=50, Gold_Bars=15)
    Game.add_relationship('HK', 'DA', Vassalage=3)
    Game.add_relationship('HK', 'EM', Diplomacy=-1)
    Game.add_relationship('AB', 'HK', Diplomacy=-1)

    Game.add_regent('FS', 'Facellies Sloere', Culture='A', Archetype='Scout', Bloodline='An'
                    ,Regency_Bonus=-1, Alignment='CG')

    Game.add_regent('SH', 'Stjordvik Traders (Storm Holtson)', Culture='Rj', Race='Human', Archetype='Bandit'
                   , Bloodline='BR', Regency_Bonus=2, Alignment='CN')

    Game.add_regent('TOF', "Sarimie's Temple of Fortune (Hyde Termonie)", Culture='Br', Bloodline='An'
                    , Archetype='Priest', Alignment='CN', Regency_Bonus=1)

    Game.add_regent('PSN', 'Peaceful Seas of Nesirie (Daffyd Tamaere)', Culture='A', Bloodline='An', Alignment='CG'
                    , Regency_Bonus=3,  Archetype='Priest')


    for a in range(6):
        Game.add_ship('AB', 'Tariene', 'Galleon')
        Game.add_ship('AB', 'Tariene', 'Caravel')
        if a != 5:
            Game.add_ship('AB', 'Tariene', 'Caravel')
            Game.add_ship('AB', 'Tariene', 'Coaster')
            
            
    Game.add_ship('TD', 'Seaport', 'Galleon')
    for a in range(6):
        Game.add_ship('TD', 'Seaport', 'Caravel')
    Game.add_ship('TD', 'Seaport', 'Coaster')

    Game.add_ship('HK', 'Seasdeep', 'Caravel')
    for a in range(2):
        Game.add_ship('HK', 'Seasdeep', 'Galleon')
        Game.add_ship('HK', 'Seasdeep', 'Coaster')
        Game.add_ship('HK', 'Seasdeep', 'Caravel')
        Game.add_ship('HK', 'Seasdeep', 'Caravel')
        
    for a in range(5):
        Game.add_ship('EM', 'Bindier', 'Caravel')
        
        
    Region = 'The Northern Marches'
    d = 'Dhoesone'
    p = 'Bjondrig'
    Game.add_province(p, d, Region, 'FD', Population=1, Magic=4, x=820, y=1265, Waterway=True)
    Game.add_holding(p, 'SH', 'Law', 1)
    Game.add_holding(p, 'FD', 'Law', 0)
    Game.add_holding(p, 'OA', 'Temple', 1)
    Game.add_holding(p, 'SH', 'Guild', 1)
    Game.add_holding(p, 'CD', 'Source', 4)
    p = 'Dharilen'
    Game.add_province(p, d, Region, 'FD', Population=1, Magic=4, x=1090, y=1120, Waterway=True, Terrain='Hills')
    Game.add_holding(p, 'FD', 'Law', 1)
    Game.add_holding(p, 'AD', 'Law', 0)
    Game.add_holding(p, 'HBT', 'Temple', 1)
    Game.add_holding(p, 'AD', 'Guild', 1)
    Game.add_holding(p, 'CD', 'Source', 4)
    p = "Giant's Fastness"
    Game.add_province(p, d, Region, 'FD', Population=1, Magic=4, x=1145, y=1195, Terrain='Hills', Waterway=True)
    Game.add_holding(p, 'GTh', 'Law', 1)
    Game.add_holding(p, 'FD', 'Law', 0)
    Game.add_geo(p, 'Dharilen', Border=1)
    Game.add_holding(p, 'HBT', 'Temple', 2)
    Game.add_holding(p, 'GTh', 'Guild', 1)
    Game.add_holding(p, 'DD', 'Source', 5)
    p = 'Hidaele'
    Game.add_province(p, d, Region, 'FD', Population=2, Magic=3, x=1030, y=1180, Waterway=True)
    Game.add_geo(p, "Giant's Fastness", Border=1)
    Game.add_holding(p, 'FD', 'Law', 1)
    Game.add_holding(p, 'BA', 'Law', 0)
    Game.add_holding(p, 'HBT', 'Temple', 2)
    Game.add_holding(p, 'BA', 'Guild', 1)
    Game.add_holding(p, 'CD', 'Source', 3)
    Game.add_geo(p, "Giant's Fastness", Border=1)
    Game.add_geo(p, 'Romiene', Border=1)
    Game.add_geo(p, 'Dharilen', Border=1)
    p = 'Nolien'
    Game.add_province(p, d, Region, 'FD', Population=3, Magic=2, x=910, y=1350, Waterway=True)
    Game.add_geo(p, 'Bjondrig', Border=1)
    Game.add_holding(p, 'FD', 'Law', 2)
    Game.add_holding(p, 'SH', 'Law', 0)
    Game.add_holding(p, 'HBT', 'Temple', 0)
    Game.add_holding(p, 'NRC', 'Temple', 3)
    Game.add_holding(p, 'SH', 'Guild', 3)
    Game.add_holding(p, 'CD', 'Source', 2)
    Game.add_geo(p, "Ice Haven", Shipping=1)
    Game.add_geo(p, "Riverford", Shipping=1)

    p = 'Riverside'
    Game.add_province(p, d, Region, 'FD', Population=2, Magic=3, x=890, y=1225, Waterway=True)
    Game.add_geo(p, 'Bjondrig', Border=1)
    Game.add_geo(p, 'Nolien', Border=1)
    Game.add_holding(p, 'FD', 'Law', 1)
    Game.add_holding(p, 'SH', 'Law', 0)
    Game.add_holding(p, 'OA', 'Temple', 2)
    Game.add_holding(p, 'SH', 'Guild', 2)
    Game.add_holding(p, 'CD', 'Source', 3)
    p = 'Romiene'
    Game.add_province(p, d, Region, 'FD', Population=1, Magic=4, x=955, y=1180, Waterway=True)
    Game.add_geo(p, 'Riverside', Border=1)
    Game.add_holding(p, 'FD', 'Law', 0)
    Game.add_holding(p, 'BA', 'Law', 1)
    Game.add_holding(p, 'OA', 'Temple', 1)
    Game.add_holding(p, 'BA', 'Guild', 1)
    Game.add_holding(p, 'CD', 'Source', 4)
    p = 'Ruidewash'
    Game.add_province(p, d, Region, 'FD', Population=2, Magic=5, x=1085, y=1365, Terrain='Forest', Waterway=True)
    Game.add_geo(p, 'Sidhuire', Border=1)
    Game.add_holding(p, 'FD', 'Law', 1)
    Game.add_holding(p, 'AD', 'Law', 0)
    Game.add_holding(p, 'HBT', 'Temple', 1)
    Game.add_holding(p, 'NRC', 'Temple', 1)
    Game.add_holding(p, 'BA', 'Guild', 2)
    Game.add_holding(p, 'DD', 'Source', 5)
    p = 'Sidhuire'
    Game.add_province(p, d, Region, 'FD', Population=2, Magic=5, x=1130, y=1300, Waterway=True, Terrain='Forest')

    Game.add_holding(p, 'FD', 'Law', 1)
    Game.add_holding(p, 'AD', 'Law', 0)
    Game.add_holding(p, 'HBT', 'Temple', 2)
    Game.add_holding(p, 'NRC', 'Temple', 0)
    Game.add_holding(p, 'AD', 'Guild', 2)
    Game.add_holding(p, 'DD', 'Source', 5)
    p = 'Soniele'
    Game.add_province(p, d, Region, 'FD', Population=1, Magic=6, x=1070, y=1240, Terrain='Forest')
    Game.add_geo(p, 'Hidaele', Border=1)
    Game.add_geo(p, "Giant's Fastness", Border=1)
    Game.add_geo(p, 'Sidhuire', Border=1)
    Game.add_geo(p, 'Romiene', Border=1)
    Game.add_holding(p, 'GTh', 'Law', 1)
    Game.add_holding(p, 'FD', 'Law', 0)
    Game.add_holding(p, 'OA', 'Temple', 1)
    Game.add_holding(p, 'GTh', 'Guild', 1)
    Game.add_holding(p, 'DD', 'Source', 6)
    p = 'Sonnelind'
    Game.add_province(p, d, Region, 'FD', Population=4, Magic=3, x=1025, y=1305, Terrain='Forest', Capital=True)
    Game.add_geo(p, 'Nolien', Border=1)
    Game.add_geo(p, 'Ruidewash', Border=1, Road=1)
    Game.add_geo(p, 'Soniele', Border=1)
    Game.add_geo(p, 'Romiene', Border=1)
    Game.add_geo(p, 'Riverside', Border=1)
    Game.add_holding(p, 'MB', 'Law', 1)
    Game.add_holding(p, 'FD', 'Law', 3)
    Game.add_holding(p, 'HBT', 'Temple', 3)
    Game.add_holding(p, 'NRC', 'Temple', 1)
    Game.add_holding(p, 'MB', 'Guild', 2)
    Game.add_holding(p, 'AD', 'Guild', 2)
    Game.add_holding(p, 'DD', 'Source', 3)
    Game.add_troops('FD', p, 'Irregulars')
    Game.add_troops('FD', p, 'Goblin Infantry')
    Game.add_geo(p, 'Mergarrote', Caravan=1)
    for a in ['Elf Archers', 'Elf Archers', 'Elf Cavalry', 'Knights', 'Knights']: 
        A = pd.DataFrame([['FD', p, a, 0, Game.troop_units[Game.troop_units['Unit Type'] == a]['BCR'].values[0], 0, '', 0]]
                        , columns=Game.Troops.keys())
        Game.Troops = Game.Troops.append(A)
    p = 'Tradebhein'
    Game.add_province(p, d, Region, 'FD', Population=2, Magic=5, x=1000, y=1395, Waterway=True, Terrain='Forest')
    Game.add_geo(p, 'Nolien', Border=1)
    Game.add_geo(p, 'Sonnelind', Border=1)
    Game.add_geo(p, 'Ruidewash', Border=1)
    Game.add_holding(p, 'MB', 'Law', 0)
    Game.add_holding(p, 'FD', 'Law', 1)
    Game.add_holding(p, 'NRC', 'Temple', 2)
    Game.add_holding(p, 'HBT', 'Temple', 0)
    Game.add_holding(p, 'MB', 'Guild', 2)
    Game.add_holding(p, 'DD', 'Source', 5)  
        
    d = "The Gorgon's Crown"
    p = 'Abattoir'
    Game.add_province(p, d, Region, 'Go', Population=3, Magic=6, x=1540, y=1350, Terrain='Mountains')
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'Go', 'Source', 6)

    p = 'Anathar'
    Game.add_province(p, d, Region, 'Go', Population=1, Magic=6, x=1670, y=1100, Terrain='Hills', Waterway=True)
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Source', 4)

    p = 'Elfseyes'
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=7, x=1590, y=1230, Terrain='Mountains')
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'Go', 'Source', 7)

    p = 'Jogh Warren'
    Game.add_province(p, d, Region, 'Go', Population=3, Magic=3, x=1675, y=1430, Terrain='Hills', Waterway=True)
    Game.add_holding(p, 'Go', 'Law', 3)
    Game.add_holding(p, 'Go', 'Source', 2)

    p = 'Kal-Saitharak'
    Game.add_province(p, d, Region, 'Go', Population=4, Magic=5, x=1580, y=1290, Terrain='Forest', Capital=True
                     , Castle=4, Castle_Name='Battlewaite')
    Game.add_holding(p, 'Go', 'Law', 4)
    Game.add_holding(p, 'HOA', 'Temple', 4)
    Game.add_holding(p, 'Go', 'Source', 5)
    Game.add_geo(p, 'Elfseyes', Border=1)
    Game.add_geo(p, 'Abattoir', Border=1)
    Game.add_troops('Go', p, 'Dwarf Guards')
    Game.add_troops('Go', p, 'Goblin Infantry')
    Game.add_troops('Go', p, 'Goblin Infantry')
    Game.add_troops('Go', p, 'Goblin Cavalry')
    for a in range(3):
        Game.add_troops('Go', p, 'Dwarf Guards')
        Game.add_troops('Go', p, 'Dwarf Crossbows')
        Game.add_troops('Go', p, 'Goblin Infantry')
        Game.add_troops('Go', p, 'Goblin Cavalry')
        Game.add_troops('Go', p, 'Mercenary Gnoll Infantry')
        Game.add_troops('Go', p, 'Mercenary Gnoll Marauders')
        Game.add_troops('Go', p, 'Mercenary Infantry')
    Game.add_troops('Go', p, 'Mercenary Cavalry')
    Game.add_troops('Go', p, 'Mercenary Cavalry')
    Game.add_troops('Go', p, 'Scouts')
    p = 'Mettles'
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=4, x=1690, y=1215, Terrain='Hills')
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'Go', 'Source', 3)
    Game.add_geo(p, 'Elfseyes', Border=1)
    Game.add_geo(p, 'Anathar', Border=1)

    p = 'Motile'
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=3, x=1615, y=1395, Terrain='Hills')
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'Go', 'Source', 3)
    Game.add_geo(p, 'Jogh Warren', Border=1)
    Game.add_geo(p, 'Abattoir', Border=1)

    p = "Mutian's Point"
    Game.add_province(p, d, Region, 'Go', Population=1, Magic=6, x=1610, y=1080, Terrain='Hills', Waterway=True)
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Source', 4)
    Game.add_geo(p, 'Anathar', Border=1)

    p = "Orog's Head"
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=5, x=1440, y=1235, Terrain='Hills', Waterway=True)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'Go', 'Source', 4)

    p = 'Pelt'
    Game.add_province(p, d, Region, 'Go', Population=1, Magic=6, x=1535, y=1470, Terrain='Forest')
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'Go', 'Source', 4)
    Game.add_geo(p, 'Motile', Border=1)
    Game.add_geo(p, 'Abattoir', Border=1)

    p = 'Plumbago'
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=5, x=1485, y=1320, Terrain='Mountains')
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'Go', 'Source', 5)
    Game.add_geo(p, 'Abattoir', Border=1)
    Game.add_geo(p, "Orog's Head", Border=1)
    Game.add_geo(p, 'Kal-Saitharak', Border=1)

    p = "Sage's Fen"
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=5, x=1515, y=1210, Terrain='Hills')
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'HOA', 'Temple', 2)
    Game.add_holding(p, 'Go', 'Source', 5)
    Game.add_geo(p, 'Kal-Saitharak', Border=1)
    Game.add_geo(p, 'Elfseyes', Border=1)
    Game.add_geo(p, "Orog's Head", Border=1)
    Game.add_geo(p, 'Plumbago', Border=1)


    p = "Sere's Hold"
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=4, x=1675, y=1310, Terrain='Hills')
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'Go', 'Source', 4)
    Game.add_geo(p, 'Mettles', Border=1)
    Game.add_geo(p, 'Elfseyes', Border=1)
    Game.add_geo(p, 'Kal-Saitharak', Border=1)
    Game.add_geo(p, 'Abattoir', Border=1)
    Game.add_geo(p, 'Motile', Border=1)
    Game.add_geo(p, 'Mettles', Border=1)

    p = 'Sideath'
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=7, x=1425, y=1385, Terrain='Forest')
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'HOA', 'Temple', 2)
    Game.add_holding(p, 'Go', 'Source', 5)
    Game.add_geo(p, 'Abattoir', Border=1)
    Game.add_geo(p, 'Plumbago', Border=1)


    p = "Stone's End"
    Game.add_province(p, d, Region, 'Go', Population=1, Magic=6, x=1465, y=1460, Terrain='Mountains')
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Source', 4)
    Game.add_geo(p, 'Abattoir', Border=1)
    Game.add_geo(p, 'Pelt', Border=1)

    Game.add_geo(p, 'Sideath', Border=1)

    p = 'Sunder Falls'
    Game.add_province(p, d, Region, 'Go', Population=1, Magic=4, x=1555, y=1140, Waterway=True)
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Source', 3)
    Game.add_geo(p, "Mutian's Point", Border=1)
    Game.add_geo(p, "Sage's Fen", Border=1)

    p = 'Zaptig'
    Game.add_province(p, d, Region, 'Go', Population=2, Magic=5, x=1615, y=1160)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'Go', 'Source', 4)
    Game.add_geo(p, "Mutian's Point", Border=1)
    Game.add_geo(p, 'Anathar', Border=1)
    Game.add_geo(p, 'Mettles', Border=1)
    Game.add_geo(p, "Sage's Fen", Border=1)
    Game.add_geo(p, "Elfseyes", Border=1)
    Game.add_geo(p, "Sunder Falls", Border=1)
    
    
    d = 'Tuarhievel'
    p = 'Awallaigh'
    Game.add_province(p, d, Region, 'Fh', Population=2, Magic=6, x=1160, y=1420, Terrain='Forest', Waterway=True)
    Game.add_holding(p, 'FD', 'Law', 1)
    Game.add_holding(p, 'Fh', 'Law', 0)
    Game.add_holding(p, 'MB', 'Guild', 2)
    Game.add_holding(p, 'Fh', 'Source', 5)
    Game.add_geo(p, 'Ruidewash', Border=1, RiverChasm=1, Road=1)
    Game.add_geo(p, 'Sidhuire', Border=1,  RiverChasm=1)
    p = 'Bhindraith'
    Game.add_province(p, d, Region, 'Fh', Population=2, Magic=6, x=1215, y=1470, Terrain='Forest')
    Game.add_holding(p, 'Fh', 'Law', 1)
    Game.add_holding(p, 'MB', 'Guild', 2)
    Game.add_holding(p, 'Fh', 'Guild', 0)
    Game.add_holding(p, 'Fh', 'Source', 4)
    Game.add_geo(p, 'Awallaigh', Border=1)
    p = 'Braethindyr'
    Game.add_province(p, d, Region, 'Fh', Population=4, Magic=5, x=1215, y=1325, Terrain='Forest', Waterway=True)
    Game.add_holding(p, 'FD', 'Law', 2)
    Game.add_holding(p, 'Fh', 'Law', 2)
    Game.add_holding(p, 'AD', 'Guild', 2)
    Game.add_holding(p, 'Fh', 'Guild', 2)
    Game.add_holding(p, 'Fh', 'Source', 4)
    Game.add_geo(p, 'Awallaigh', Border=1)
    Game.add_geo(p, 'Sidhuire', Border=1,  RiverChasm=1)
    Game.add_geo(p, "Giant's Fastness", Border=1,  RiverChasm=1)
    p = 'Cwmbheir'
    Game.add_province(p, d, Region, 'Fh', Population=6, Magic=5, x=1275, y=1410, Terrain='Forest', Capital=True)
    Game.add_holding(p, 'FD', 'Law', 2)
    Game.add_holding(p, 'Fh', 'Law', 4)
    Game.add_holding(p, 'AD', 'Guild', 3)
    Game.add_holding(p, 'Fh', 'Guild', 0)
    Game.add_holding(p, 'MB', 'Guild', 2)
    Game.add_holding(p, 'Fh', 'Source', 5)
    Game.add_geo(p, 'Awallaigh', Border=1, Road=1)
    Game.add_geo(p, 'Bhindraith', Border=1)
    Game.add_geo(p, 'Braethindyr', Border=1)
    Game.add_geo(p, 'Sonnielind', Caravan=1)
    for a in range(3):
        Game.add_troops('Fh', p, 'Elf Archers')
        Game.add_troops('Fh', p, 'Elf Archers')
        Game.add_troops('Fh', p, 'Elf Cavalry')
    Game.add_troops('Fh', p, 'Elf Archers')
    p = 'Cymyr'
    Game.add_province(p, d, Region, 'Fh', Population=3, Magic=5, x=1335, y=1310, Terrain='Forest', Waterway=True)
    Game.add_holding(p, 'Fh', 'Law', 2)
    Game.add_holding(p, 'Fh', 'Source', 5)
    Game.add_geo(p, 'Braethindyr', Border=1)
    Game.add_geo(p, 'Cwmbheir', Border=1)
    Game.add_geo(p, "Orog's Head", Border=1)
    Game.add_geo(p, 'Plumbago', Border=1)
    p = 'Dhoneaghmiere'
    Game.add_province(p, d, Region, 'Fh', Population=3, Magic=5, x=1250, y=1260, Terrain='Forest', Waterway=True)
    Game.add_holding(p, 'Fh', 'Law', 2)
    Game.add_holding(p, 'Fh', 'Source', 5)
    Game.add_geo(p, 'Braethindyr', Border=1)
    Game.add_geo(p, 'Sidhuire', Border=1,  RiverChasm=1)
    Game.add_geo(p, "Giant's Fastness", Border=1,  RiverChasm=1)
    Game.add_geo(p, 'Cymyr', Border=1)
    p = 'Llyrandor'
    Game.add_province(p, d, Region, 'Fh', Population=2, Magic=6, x=1355, y=1425, Terrain='Forest', Waterway=True)
    Game.add_geo(p, 'Plumbago', Border=1)
    Game.add_geo(p, 'Sideath', Border=1)
    Game.add_geo(p, 'Cymyr', Border=1)
    Game.add_geo(p, 'Cwmbheir', Border=1)

    d = 'Cariele'
    p = 'Mhelliviene'
    Game.add_province(p, d, Region, 'EG', Population=5, Magic=2, x=1030, y=1525, Terrain='Forest')
    Game.add_geo(p, "Torien's Watch", Border=1)
    Game.add_holding(p, 'MB', 'Law', 3)
    Game.add_holding(p, 'EG', 'Law', 2)
    Game.add_holding(p, 'NRC', 'Temple', 5)
    Game.add_holding(p, 'HA', 'Temple', 0)
    Game.add_holding(p, 'MB', 'Guild', 5)
    Game.add_holding(p, 'DD', 'Source', 0)
    p = 'Mountainsedge'
    Game.add_province(p, d, Region, 'EG', Population=3, Magic=4, x=1125, y=1490, Terrain='Forest', Waterway=True)
    Game.add_geo(p, "Torien's Watch", Border=1, RiverChasm=1)  #Chasm
    Game.add_geo(p, "Mhelliviene", Border=1, Road=1)
    Game.add_geo(p, "Bhindraith", Border=1, RiverChasm=1)
    Game.add_geo(p, "Awallaigh",Border=1, RiverChasm=1 )
    Game.add_holding(p, 'MB', 'Law', 2)
    Game.add_holding(p, 'EG', 'Law', 1)
    Game.add_holding(p, 'NRC', 'Temple', 3)
    Game.add_holding(p, 'HA', 'Temple', 0)
    Game.add_holding(p, 'MB', 'Guild', 3)
    Game.add_holding(p, 'EO', 'Source', 0)
    p = 'Riverford'
    Game.add_province(p, d, Region, 'EG', Population=5, Magic=2, x=1075, y=1465, Terrain='Forest', Waterway=True, Capital=True)
    Game.add_geo(p, "Mhelliviene", Border=1, Road=1)
    Game.add_geo(p, "Mountainsedge", Border=1, Road=1)
    Game.add_geo(p, "Awallaigh",Border=1, RiverChasm=1 )
    Game.add_geo(p, "Ruidewash",Border=1, RiverChasm=1, Road=1)
    Game.add_geo(p, "Tradebhein",Border=1, RiverChasm=1)
    Game.add_holding(p, 'MB', 'Law', 3)
    Game.add_holding(p, 'EG', 'Law', 2)
    Game.add_holding(p, 'NRC', 'Temple', 5)
    Game.add_holding(p, 'OA', 'Temple', 0)
    Game.add_holding(p, 'MB', 'Guild', 5)
    Game.add_holding(p, 'DD', 'Source', 0)
    Game.add_holding(p, 'EO', 'Source', 0)


    d = 'The Five Peaks'
    p = 'The Gorge'
    Game.add_province(p, d, Region, 'TKotG', Population=3, Magic=4, x=765, y=1580, Terrain='Forest', Capital=True)
    Game.add_regent('TKotG',"The King of the Gorge", Archetype='Bugbear', Race='Goblin', Culture='G', Bloodline='Az'
                    , Regency_Bonus=1, Alignment='CE', Attitude='Aggressive')
    Game.add_geo(p, 'Freestead', Border=1)
    Game.add_geo(p, 'Serimset', Border=1)
    Game.add_geo(p, 'Lindholme', Border=1)
    Game.add_holding(p, 'EO', 'Source', 4) 
    p = 'Floodspath'
    Game.add_province(p, d, Region, 'LfBn', Population=3, Magic=6, x=860, y=1595, Terrain='Forest', Capital=True)
    Game.add_geo(p, 'The Gorge', Border=1)
    Game.add_regent('LfBn', 'Lifesbane', Race='Goblin', Culture='G', Class='Ancient Red Dragon', Alignment='LE'
                    , Level=28, Str=10, Dex=0, Con=9, Int=4, Wis=2, Cha=6, Insight=2, Deception=6, Persuasion=6
                    , Regency_Bonus=5, Gold_Bars=200, Attitude='Xenophobic')
    Game.add_holding(p, 'EO', 'Source', 6) 
    p = 'Helmshaven'
    Game.add_province(p, d, Region, 'VFP', Population=3, Magic=4, x=765, y=1660, Terrain='Forest', Capital=True, Waterway=True)
    Game.add_geo(p, 'The Gorge', Border=1)
    Game.add_geo(p, 'Floodspath', Border=1)
    Game.add_regent('VFP', 'Vos of the Five Peaks', Archetype='Priest', Bloodline='Az', Regency_Bonus=1, Alignment='CE'
                    , Culture='A', Race='Human', Attitude='Aggressive')
    Game.add_geo(p, 'Rivien', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Dhalaese', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Lindholme', Border=1, RiverChasm=1)
    Game.add_holding(p, 'EO', 'Source', 4)
    Game.add_holding(p, 'VFP', 'Temple', 2)
    p = 'Puinol'
    Game.add_province(p, d, Region, 'LJE', Population=3, Magic=4, x=995, y=1620, Terrain='Forest', Capital=True)
    Game.add_geo(p, 'Mhelliviene', Border=1, RiverChasm=1)
    Game.add_geo(p, "Torien's Watch", Border=1, RiverChasm=1)
    Game.add_geo(p, "Floodspath", Border=1)
    Game.add_regent('LJE',"Lord Jerj Elfsbane", Archetype='Hobgoblin', Race='Goblin', Culture='G', Bloodline='Az'
                    , Regency_Bonus=1, Alignment='LE', Attitude='Aggressive')
    Game.add_holding(p, 'EO', 'Source', 4)
    Game.add_holding(p, 'VFP', 'Temple', 0)
    p = 'Sufhanie'
    Game.add_province(p, d, Region, 'KtR', Population=3, Magic=4, x=930, y=1710, Terrain='Hills', Capital=True, Waterway=True)
    Game.add_regent('KtR',"Kruss the Red", Archetype='Goblin', Race='Goblin', Culture='G', Bloodline='Az'
                    , Regency_Bonus=1, Alignment='NE', Attitude='Aggressive')
    Game.add_geo(p, 'Ghonallison', Border=1)
    Game.add_geo(p, 'Sorelies', Border=1)
    Game.add_geo(p, 'Nortmoor', Border=1)
    Game.add_geo(p, 'Puinol', Border=1)
    Game.add_geo(p, 'Winoene', Border=1, RiverChasm=1)
    Game.add_holding(p, 'EO', 'Source', 2)
    p = 'Thasbyrn'
    Game.add_province(p, d, Region, 'RvKg', Population=3, Magic=4, x=820, y=1695, Terrain='Hills', Capital=True, Waterway=True)
    Game.add_geo(p, 'Ghonallison', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Dhalaese', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Helmshaven', Border=1)
    Game.add_geo(p, 'Sufhanie', Border=1)
    Game.add_holding(p, 'EO', 'Source', 4)
    Game.add_holding(p, 'HTC', 'Temple', 1)
    Game.add_regent('RvKg',"The Raven King", Archetype='Bandit', Race='Human', Culture='A', Bloodline='An'
                    , Regency_Bonus=2, Alignment='NE', Attitude='Aggressive')
    Game.add_regent('HTC', "Hidden Church of Cuiraecen (Linias Baccaere)", Archetype='Priest', Culture='A', Bloodline='Re'
                    , Race='Human', Alignment='CN', Regency_Bonus=1)
    p = 'Torain'
    Game.add_province(p, d, Region, 'KItG', Population=3, Magic=4, x=875, y=1650, Terrain='Hills', Capital=True)
    Game.add_regent('KItG',"King Ithic the Goblinking", Archetype='Goblin', Race='Goblin', Culture='G', Bloodline='Az'
                    , Regency_Bonus=1, Alignment='LE', Attitude='Aggressive')
    Game.add_geo(p, 'Sufhanie', Border=1)
    Game.add_geo(p, 'Thasbyrn', Border=1)
    Game.add_geo(p, 'Floodspath', Border=1)
    Game.add_geo(p, 'Puinol', Border=1)
    Game.add_holding(p, 'EO', 'Source', 4)

    for a in ['TKotG', 'VFP', 'LJE', 'KItG', 'KtR']:
        for b in ['TKotG', 'VFP', 'LJE', 'KItG', 'KtR']:
            if a != b:
                Game.add_relationship(a, b, Diplomacy = -1)


    d = 'Markazor'
    p = 'Brushfire'
    Game.add_province(p, d, Region, 'RF', Population=2, Magic=3, x=1345, y=1700, Waterway=True)
    Game.add_geo(p, 'Annydwr', Border=1)
    Game.add_geo(p, 'Llewhoellen', Border=1)
    Game.add_geo(p, 'Dhalsiel', Border=1, RiverChasm=1)
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'RF', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'ATM', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Guild', 1)
    Game.add_holding(p, 'Go', 'Source', 3)
    p = "Dwarf's Hold"
    Game.add_province(p, d, Region, 'RF', Population=4, Magic=1, x=1385, y=1575, Terrain='Hills')
    Game.add_geo(p, 'Annydwr', Border=1)
    Game.add_geo(p, 'Ghyllwn', Border=1)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'RF', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'ATM', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Guild', 1)
    Game.add_holding(p, 'Go', 'Source', 1)
    p = 'Elfsdemise'
    Game.add_province(p, d, Region, 'RF', Population=3, Magic=2, x=1375, y=1495, Terrain='Hills')
    Game.add_geo(p, 'Bhindraith', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Cwmbheir', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Llyrandor', Border=1)
    Game.add_geo(p, "Stone's End", Border=1)
    Game.add_geo(p, "Dwarf's Hold", Border=1)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'RF', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'ATM', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Guild', 1)
    Game.add_holding(p, 'Go', 'Source', 1)
    p = 'Periltrees'
    Game.add_province(p, d, Region, 'RF', Population=3, Magic=2, x=1285, y=1730, Waterway=True)
    Game.add_geo(p, 'Bevaldruor', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Balteruine', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Dhalsiel', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Brushfire', Border=1)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'RF', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'ATM', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Guild', 1)
    Game.add_holding(p, 'Go', 'Source', 1)
    p = 'Riverspring'
    Game.add_province(p, d, Region, 'RF', Population=3, Magic=2, x=1230, y=1600, Waterway=True)
    Game.add_geo(p, 'Dhalsiel', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Brushfire', Border=1)
    Game.add_geo(p, "Marloer's Gap", Border=1, RiverChasm=1)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'RF', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'ATM', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Guild', 1)
    Game.add_holding(p, 'Go', 'Source', 1)
    p = 'Shattered Hills'
    Game.add_province(p, d, Region, 'RF', Population=4, Magic=1, x=1300, y=1585, Terrain='Hills'
                      , Capital=True)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'RF', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'ATM', 'Temple', 1)
    Game.add_holding(p, 'Go', 'Guild', 1)
    Game.add_holding(p, 'Go', 'Source', 1)
    Game.add_geo(p, 'Riverspring', Border=1)
    Game.add_geo(p, 'Brushfire', Border=1)
    Game.add_geo(p, 'Annydwr', Border=1)
    Game.add_geo(p, "Dwarf's Hold", Border=1)
    Game.add_geo(p, 'Elfsdemise', Border=1)
    Game.add_geo(p, 'Bhindraith', Border=1)
    p = 'Sutren Hills'
    Game.add_province(p, d, Region, 'RF', Population=1, Magic=4, x=1350, y=1770, Terrain='Hills')
    Game.add_geo(p, 'Brushfire', Border=1)
    Game.add_geo(p, 'Hoehnaen', Border=1)
    Game.add_geo(p, 'Soileite', Border=1)
    Game.add_geo(p, 'Mholien', Border=1)
    Game.add_geo(p, 'Balteruine', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Periltrees', Border=1)
    Game.add_holding(p, 'Go', 'Law', 1)
    Game.add_holding(p, 'RF', 'Law', 0)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'ATM', 'Temple', 0)
    Game.add_holding(p, 'Go', 'Guild', 1)
    Game.add_holding(p, 'Go', 'Source', 1)
    p = 'Hidden Forest'
    Game.add_province(p, d, Region, 'RF', Population=0, Magic=7, x=1195, y=1555, Terrain='Forest'
                      , Waterway=True)
    Game.add_geo(p, 'Riverspring', Border=1)
    Game.add_geo(p, "Marloer's Gap", Border=1, RiverChasm=1)
    Game.add_geo(p, "Torien's Watch", Border=1, RiverChasm=1)
    Game.add_geo(p, 'Mountainsedge', Border=1)
    Game.add_geo(p, 'Bhindraith', Border=1)
    Game.add_geo(p, 'Shattered Hills', Border=1)

    d = 'Mur-Kilad'
    p = 'Crushing Rock'
    Game.add_province(p, d, Region, 'GoT', Population=5, Magic=4, x=1520, y=1525, Terrain='Mountains')
    Game.add_geo(p, 'Pelt', Border=1)
    Game.add_geo(p, 'Tuar Llyrien', Border=1)
    Game.add_geo(p, "Stone's End", Border=1)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'GoT', 'Law', 2)
    Game.add_holding(p, 'HOA', 'Temple', 2)
    Game.add_holding(p, 'MF', 'Temple', 2)
    Game.add_holding(p, 'Go', 'Guild', 2)
    Game.add_holding(p, 'Go', 'Source', 2)
    Game.add_holding(p, 'PM', 'Source', 2)
    p = 'Fallen Rock'
    Game.add_province(p, d, Region, 'GoT', Population=3, Magic=6, x=1455, y=1560, Terrain='Mountains')
    Game.add_geo(p, 'Tuar Llyrien', Border=1)
    Game.add_geo(p, 'Ghyllwn', Border=1)
    Game.add_geo(p, "Dwarf's Hold", Border=1)
    Game.add_geo(p, 'Crushing Rock', Border=1)
    Game.add_holding(p, 'Go', 'Law', 2)
    Game.add_holding(p, 'GoT', 'Law', 1)
    Game.add_holding(p, 'HOA', 'Temple', 1)
    Game.add_holding(p, 'MF', 'Temple', 2)
    Game.add_holding(p, 'Go', 'Guild', 2)
    Game.add_holding(p, 'Go', 'Source', 3)
    Game.add_holding(p, 'PM', 'Source', 3)
    
    d = 'Thurazor'
    p = 'Bloodbay'
    Game.add_province(p, d, Region, 'TG', Population=2, Magic=5, x=890, y=1455, Terrain='Forest'
                      , Waterway=True)
    Game.add_geo(p, 'Nolien', Border=1, RiverChasm=1)
    Game.add_holding(p, 'TG', 'Law', 1)
    Game.add_holding(p, 'GTr', 'Temple', 1)
    Game.add_holding(p, 'AD', 'Guild', 1)
    Game.add_holding(p, 'EO', 'Source', 2)
    Game.add_holding(p, 'TA', 'Source', 2)
    p = 'Crushing Hills'
    Game.add_province(p, d, Region, 'TG', Population=3, Magic=4, x=825, y=1540, Terrain='Forest')
    Game.add_geo(p, 'Freestead', Border=1, RiverChasm=1)
    Game.add_geo(p, 'The Gorge', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Floodspath', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Bloodbay', Border=1, RiverChasm=1)
    Game.add_holding(p, 'TG', 'Law', 2)
    Game.add_holding(p, 'GTr', 'Temple', 2)
    Game.add_holding(p, 'GTh', 'Guild', 2)
    Game.add_holding(p, 'TA', 'Source', 2)
    p = "Doom's Peak"
    Game.add_province(p, d, Region, 'TG', Population=2, Magic=6, x=945, y=1520, Terrain='Forest')
    Game.add_geo(p, 'Puinol', Border=1)
    Game.add_geo(p, 'Floodspath', Border=1)
    Game.add_geo(p, 'Crushing Hills', Border=1)
    Game.add_geo(p, 'Bloodbay', Border=1)
    Game.add_geo(p, 'Mhlliviene', Border=1)
    Game.add_holding(p, 'TG', 'Law', 1)
    Game.add_holding(p, 'GTr', 'Temple', 1)
    Game.add_holding(p, 'AD', 'Guild', 1)
    Game.add_holding(p, 'EO', 'Source', 2)
    Game.add_holding(p, 'TA', 'Source', 2)
    p = 'Falling Timber'
    Game.add_province(p, d, Region, 'TG', Population=4, Magic=3, x=830, y=1415, Terrain='Forest'
                     , Waterway=True)
    Game.add_geo(p, 'Nolien', Border=1, RiverChasm=1)
    Game.add_geo(p, 'Bloodbay', Border=1)
    Game.add_geo(p, 'Falling Timber', Border=1)
    Game.add_geo(p, 'Crushing Hills', Border=1)
    Game.add_geo(p, "Winter's Deep", Border=1)
    Game.add_holding(p, 'TG', 'Law', 2)
    Game.add_holding(p, 'AD', 'Law', 2)
    Game.add_holding(p, 'GTr', 'Temple', 1)
    Game.add_holding(p, 'HTC', 'Temple', 1)
    Game.add_holding(p, 'AD', 'Guild', 1)
    Game.add_holding(p, 'GTh', 'Guild', 1)
    Game.add_holding(p, 'EO', 'Source', 2)
    p = 'Mergarrote'
    Game.add_province(p, d, Region, 'TG', Population=4, Magic=3, x=975, y=1455, Terrain='Forest'
                     , Capital=True, Waterway=True)
    Game.add_geo(p, "Doom's Peak", Border=1)
    Game.add_geo(p, "Mhelliviene", Border=1)
    Game.add_geo(p, "Riverford", Border=1)
    Game.add_geo(p, "Tradebhein", Border=1, RiverChasm=1)
    Game.add_geo(p, "Nolien", Border=1, RiverChasm=1)
    Game.add_geo(p, "Bloodbay", Border=1)
    Game.add_holding(p, 'TG', 'Law', 2)
    Game.add_holding(p, 'GTh', 'Law', 2)
    Game.add_holding(p, 'GTr', 'Temple', 2)
    Game.add_holding(p, 'HTC', 'Temple', 2)
    Game.add_holding(p, 'AD', 'Guild', 2)
    Game.add_holding(p, 'GTh', 'Guild', 2)
    Game.add_holding(p, 'EO', 'Source', 3)

    p = "Storm's Release"
    Game.add_province(p, d, Region, 'TG', Population=3, Magic=4, x=780, y=1380, Terrain='Forest'
                     ,Waterway=True)
    Game.add_geo(p, "Winter's Deep", Border=1)
    Game.add_geo(p, "Falling Timber", Border=1)
    Game.add_holding(p, 'TG', 'Law', 2)
    Game.add_holding(p, 'GTr', 'Temple', 2)
    Game.add_holding(p, 'GTh', 'Guild', 2)
    Game.add_holding(p, 'EO', 'Source', 3)
    
    Game.add_regent('AD', "Adaere Doniem (Northern Imports and Exports)", Archetype='Bandit'
               , Regency_Bonus=1, Culture='A', Bloodline='Re', Alignment='CE')
    Game.add_regent('GTh', "Gaelin Thuried (Upper Anuire Traders)", Culture='A', Archetype='Thug', Regency_Bonus=0
                    , Bloodline='Br', Alignment='CN')
    Game.add_regent('BA', "Bannier Andien (Andien and Sons)", Culture='A', Archetype='Spy', Regency_Bonus=1
                    , Bloodline='An', Alignment='LE')
    Game.add_relationship('MB', 'GTh', Diplomacy=-1)
    Game.add_relationship('GTh', 'MB', Diplomacy=-1)
    Game.add_relationship('BA', 'MB', Diplomacy=-1)
    Game.add_relationship('MB', 'BA', Diplomacy=-1)
    Game.add_relationship('BA', 'GTh', Diplomacy=-1)
    Game.add_relationship('GTh', 'BA', Diplomacy=-1)
    Game.add_relationship('MB', 'FD', Diplomacy=-1)
    Game.add_relationship('GTh', 'FD', Diplomacy=-1)
    Game.add_relationship('BA', 'FD', Diplomacy=-1)
    Game.add_relationship('AD', 'MB', Diplomacy=-1)
    Game.add_relationship('MB', 'AD', Diplomacy=-1)
    Game.add_relationship('AD', 'GTh', Diplomacy=-1)
    Game.add_relationship('GTh', 'AD', Diplomacy=-1)
    Game.add_relationship('AD', 'FD', Diplomacy=-1)

    Game.add_regent('CD', "Clumine Dhoesone", Culture='A', Archetype='Mage', Regency_Bonus=2
                    , Bloodline='Vo', Alignment='LG')
    Game.add_regent('DD', "Daeric Dhoesone", Culture='A', Archetype='Mage', Regency_Bonus=1
                    , Bloodline='An', Alignment='CG')
    Game.add_relationship('CD', 'DD', Diplomacy=-1)
    Game.add_relationship('DD', 'CD', Diplomacy=-1)
    Game.add_relationship('CD', 'FD', Diplomacy=3, Vassalage=2)
    Game.add_relationship('DD', 'FD', Diplomacy=3, Vassalage=1)

    Game.add_regent('FD', "Fhiele Dhoesone", Regency_Points=21, Gold_Bars=14, Archetype='Spy', Race='Elf', Culture='A'
                   , Regency_Bonus=3, Bloodline='Re', Alignment='NN', Lieutenants=['Helaene Dosiere'])
    Game.add_relationship('FD', 'Fh', Diplomacy=2)
    Game.add_relationship('Fh', 'FD', Diplomacy=2)
    Game.add_relationship('FD', 'EG', Diplomacy=-1)
    Game.add_relationship('EG', 'FD', Diplomacy=-3)
    Game.add_relationship('TG', 'FD', Diplomacy=2)
    Game.add_relationship('FD', 'TG', Diplomacy=2)

    Game.add_regent('Go', 'The Gorgon', Class='Awnsheghlien', Level=20, Bloodline='Az', Culture='A', Race='Human' 
                    , Regency_Bonus=9, Str=5, Dex=2, Con=5, Int=4, Wis=4, Cha=4, Deception=12, Insight=12, Persuasion=12
                    , Alignment='LE', Regency_Points=200, Gold_Bars=150, Attitude='Aggressive', Arcane=True
                    , Lieutenants=['Kiras Earthcore'])

    Game.add_regent('HOA', 'Hand of Azrai', Culture='Kh', Bloodline='Az', Regency_Bonus=1, Alignment='LE')
    Game.add_relationship('HOA', 'Go', Diplomacy=5, Vassalage=1)
    Game.add_relationship('Go', 'HOA', Diplomacy=1)

    Game.add_regent('Fh', "Fhieleraenne (Tuarhievel)", Regency_Points=67, Gold_Bars=34, Archetype='Mage', Race='Elf'
                    , Culture='E', Regency_Bonus=6, Bloodline='Re', Alignment='CN', Lieutenants=['Llytha Damaan'])
    Game.add_relationship('Fh', 'Is', Diplomacy=3)
    Game.add_relationship('Is', 'Fh', Diplomacy=3)
    Game.add_relationship('Fh', 'Go', Diplomacy=-3)

    Game.add_regent('EG', 'Entier Gladanil', Culture='A', Bloodline='An', Regency_Bonus=2, Alignment='NE', Archetype='Noble')
    Game.add_relationship('EG', 'MB', Diplomacy=3, Vassalage=1)  # in pocket of guilds
    Game.add_relationship('MB', 'EG', Diplomacy=1)
    Game.add_regent('MB', "Mheallie Bireon (Stonecrown Coster, Source of the Maesil, Northlands Exchange)", Culture='A'
                    , Bloodline='Br', Regency_Bonus=4, Alignment='NE', Archetype='Spy', Attitude='Aggressive')

    Game.add_regent('NRC', 'Larra Nieliems (Northern Reformed Church of Sarimie)', Culture='A', Bloodline='Br', Regency_Bonus=3
                    , Alignment='NE', Archetype='Priest', Regency_Points=21, Gold_Bars=30)

    Game.add_regent('EO', 'The Eyeless One', Culture='A', Race='Human', Archetype='Mage', Bloodline='Vo', Regency_Bonus=3
                    , Alignment='CE')

    Game.add_regent('GoT', 'Godar Thurinson', Race='Dwarf', Culture='D', Regency_Bonus=-1
                    , Bloodline='Vo', Alignment='LE', Archetype='Thug', Attitude='Xenophobic')
    Game.add_regent('RF', 'Queen Razzik Fanggrabber', Race='Goblin', Culture='G', Regency_Bonus=-1
                    , Bloodline='Az', Alignment='LE', Archetype='Goblin', Attitude='Xenophobic')
    Game.add_relationship('GoT', 'Go', Diplomacy=3, Vassalage=1)
    Game.add_relationship('RF', 'Go', Diplomacy=3, Vassalage=1)
    Game.add_relationship('Go', 'GoT', Diplomacy=1)
    Game.add_relationship('Go', 'RF', Diplomacy=1)
    Game.add_relationship('GoT', 'RF', Diplomacy=2)
    Game.add_relationship('RF', 'GoT', Diplomacy=2)

    Game.add_regent('PM', 'Peak Mage', Archetype='Mage', Culture='A', Bloodline='An', Regency_Bonus=3)

    Game.add_regent('TG', "Tie'skar Graecher", Race='Goblin', Culture='G', Bloodline='Az', Regency_Bonus=2
                   ,Str=2, Dex=0, Con=2, Int=2, Wis=-1, Cha=1, Level=7, Class='Fighter', Insight=2
                   , Deception=4, Persuasion=4, Alignment='LE')
    Game.add_regent('GTr', "Kral Two-Toes (Goblin's Triumph)", Race='Goblin', Bloodline='AZ', Regency_Bonus=-1
                   , Archetype='Priest', Alignment='LE')
    Game.add_relationship('TG', 'GTr', Diplomacy=3)
    Game.add_relationship('GTr', 'TG', Diplomacy=3, Vassalage=1)

    Game.add_regent('ATM', 'Approved Temple of Markazor (Nysa Redeye)', Alignment='LE', Gold_Bars=3, Regency_Points=5
                    ,Archetype='Priest', Race='Goblin', Culture='G', Regency_Bonus=1, Bloodline='Az')
    Game.add_relationship('ATM', 'HOA', Diplomacy=-1)

    Game.add_regent('OA', 'Oaken Grove of Aeric (Euric Aelis)', Culture='A', Alignment='CN', Bloodline='Re'
                    , Regency_Bonus=1, Archetype='Druid')

    Game.add_regent('HBT', "Haelyn's Bastion of Truth (James Ardannt)", Alignment='LG', Bloodline='An', Regency_Bonus=2
                   , Culture='A', Archetype='Priest')



    Game.add_ship('FD', 'Nolien', 'Caravel')
    for a in range(2):
        Game.add_ship('FD', 'Nolien', 'Caravel')
        Game.add_ship('FD', 'Nolien', 'Knarr')
        Game.add_ship('FD', 'Nolien', 'Caravel')
        Game.add_ship('FD', 'Nolien', 'Knarr')
        Game.add_ship('FD', 'Nolien', 'Coaster')
        
        
    Game.add_ship('TG', 'Mergarrote', 'Longship')
    Game.add_ship('TG', 'Mergarrote', 'Caravel')
    
    Game.save_world('Birthright')
    print('done')
if __name__ == '__main__':

    main()
