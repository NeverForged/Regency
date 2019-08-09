# Regency
Network Modeling and other machine learning uses aimed towards a system for adding an *AD&D 2nd Edition Birthright*-like regency system to a 5e 
 D&D World of my own design.

## Goals
- Write out [regency system](https://www.gmbinder.com/share/-L4h_QHUKh2NeYhgD96A) from *Birthright* as a python program to manage it for me so that I can run it without dealing with it for my daughter when she's old enough to start wanting to be a princess.
- Add an Agent so that the NPCs can play the game themselves.  Well, three agents: *Normal*, *Peaceful*, and *Aggressive*.
- Add ways to view the network models created in order to see the geography, see trade, view roads, etc.  And also to see how the various regents are getting along with each other.
  

## Basis
-  * **Birthright** AD&D 2nd Edition Boxed Set* was used to set the Provences/Regents/etc. for the default campaign.
- * [**Birthright** 5e Conversion](https://www.gmbinder.com/share/-L4h_QHUKh2NeYhgD96A)* was used for the bulk of the work, in order to have a stable (and accessable) system that was more compatable with 5e (and my ultimate plans to use this for my own world)
- *[maurock/snake-ga](https://github.com/maurock/snake-ga)* is where I lifted the *Agent* class from.

## Python Classes
The following are the classes that run this program.

### regency.py
Based on the 5e Conversion of the Regency system from Birthright,
	found [here](https://www.gmbinder.com/share/-L4h_QHUKh2NeYhgD96A).
	
**DataFrames:**

- **Provences:** *['Provence', 'Domain', 'Region', 'Regent', 'Terrain', 'Loyalty',
       'Taxation', 'Population', 'Magic', 'Castle', 'Castle Name', 'Capital',
       'Position', 'Contested', 'Waterway', 'Brigands']*
- **Holdings:** *['Provence', 'Regent', 'Type', 'Level', 'Contested']*
- **Regents:**  *['Regent', 'Full Name', 'Bloodline', 'Culture', 'Player', 'Class',
       'Level', 'Alignment', 'Race', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha',
       'Insight', 'Deception', 'Persuasion', 'Regency Points', 'Gold Bars',
       'Regency Bonus', 'Attitude', 'Alive', 'Divine', 'Arcane']*
- **Geography:** *['Provence', 'Neighbor', 'Border', 'Road', 'Caravan', 'Shipping',
       'RiverChasm']*
- **Relationships:** *['Regent', 'Other', 'Diplomacy', 'Payment', 'Vassalage', 'At War',
       'Trade Permission']*
- **Troops:** *['Regent', 'Provence', 'Type', 'Cost', 'CR', 'Garrisoned', 'Home',
       'Injury']*
- **Navy:** *['Regent', 'Provence','Ship','Hull','Troop Capacity', 'Seaworthiness', 'Name']*
- **LeyLines:** *['Regent', 'Provence', 'Other']*
- **Seasons:** A dictionary of season-dataframes (to keep track of what happened)
- **Lieutenants:** A List of regent-lieutenant pairs

### DQNAgent.py
Lifted from [maurock/snake-ga](https://github.com/maurock/snake-ga), this was used to make the agents that play the game, using a model for each of the following activities:

- Determining taxation strategies based on money gained and influence lost.
- Choosing an action or bonus action from the lists of [actions](https://www.gmbinder.com/share/-L4h_QHUKh2NeYhgD96A) based on a huge array of information about the regent and their neighbors.
- Determine how many gold bars to spend on an action
- Determine how much regency to spend on a thing.

### mapping.py
This shows maps of the world based on the parameters entered by the user.