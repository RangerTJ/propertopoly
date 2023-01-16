# Propertopoly: A (Mildly Sassy) Text-Based Property Game
This is a text-based property game programmed in Python 3.10, for 2 to 30 players (plays like a "Monopoly Lite").
Players roll dice to travel around a circular game board with 25 spaces buying and renting property until there is only one player left with any money (the winner). When landing on, or passing the first space again, players are given their income for the lap. Prints a graphic history of player performance over the course of the game at the end.

The manually-played version is the "real" game and prompts for a number of players and player names. It then manually prompts users for player input on decisions throughout the game. Turn order is based on the order that player names are entered. 
The simulated version is fully automated and simulates a 30 person game. It assumes that players buy property whenever they have the fiscal capacity to do so (random dice rolls for movements being the wildcard variable in the simulation). In the "real" game, players can strategically choose whether or not that would like to purchase a given property.

Requires random and matplotlib Python modules to be installed.

Thanks for playing!
