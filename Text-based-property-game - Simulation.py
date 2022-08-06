# Author: Raptor2k1
# Date: 6/3/2022
# Description:  Simulates a 30-person property trading boardgame that plays similar to Monopoly.
#               Players travel around a circular game board with 25 spaces buying and renting property until there is
#               only one player left with any money (the winner). When landing on, or passing the first space again,
#               players are given a specified amount of money as a sort of "income per lap."
#               Prints a graphic history of player performance over the course of the game at the end.

import random
from matplotlib import pyplot


class RealEstateGame:
    """
    This object represents a simplified version of the boardgame Monopoly. The object contains a dictionary of spaces
    (the players) and a dictionary of locations (the game board), along with a list of default place names to name the
    game board's locations. It has additional data members to track the amount of cash received by players when passing
    or landing on the first space ("Go").

    Class Interactions: The players of the game are Player class objects stored in a dictionary keyed to the player's
                        name. The locations in the game are Property class objects that are stored in a dictionary
                        keyed to the integer that represents the location's position on the board (starting at position
                        0 for "Go"). Objects of these types have relationships defined by their internal methods such
                        that movement, property ownership, etc. are all updated to match the RealEstateGame object's
                        methods of playing the game.

    Methods: __init__, create_spaces, create_player, get_player_account_balance, get_player_current_position,
             buy_space, move_player, check_game_over, delete_player (for testing), start_game (for game loop)
    """

    def __init__(self):
        """
        Creates a game by initializing an empty player dictionary, creating the "Go" space, and creating a list of names
        for the 24 additional places that will be created. Initializes the amount of cash for passing "Go" as None and
        a count of players as 0. Also initializes the game over and start check conditions as false, for use in an
        automated game loop.

        The player_count data member is used to track how many players have been created, so that
        the program knows how many players started the game, even if some are later removed from the player dictionary.
        It is also used to check whether the game can even start (no moving allowed if fewer than 2 players), and to
        filter early-termination of the check_game_over method (since a game can't be over if it hasn't started).
        """

        # Core data members required for both manual gameplay and game loop automation
        self._player_dict = {}                            # Keyed to name: Player Objects
        self._location_dict = {0: Property("Go", 0, 0)}   # Keyed to board position integer: Property Objects
        self._place_names = ["Go", "Place 1", "Place 2", "Place 3", "Place 4", "Place 5", "Place 6", "Place 7",
                             "Place 8", "Place 9", "Place 10", "Place 11", "Place 12", "Place 13", "Place 14",
                             "Place 15", "Place 16", "Place 17", "Place 18", "Place 19", "Place 20", "Place 21",
                             "Place 22", "Place 23", "Place 24"]
        self._go_cash = None                                    # Cash collected for passing "Go"
        self._player_count = 0                                  # Counts players added to game
        self._rent_list = []                                    # Used for reference; determined by create_spaces()

        # The following data members are only used in a game loop
        self._game_over = False         # Used in the game loop to determine when to stop the game loop
        self._start_check = False       # Used in the game loop to verify that starting conditions are valid

    def get_spaces(self):
        """Returns the dictionary of locations within the game."""
        return self._location_dict

    def get_players(self):
        """Returns the dictionary of current players."""
        return self._player_dict

    def create_spaces(self, go_cash, rent_array):
        """
        Generates a game board using a rent array argument, a specified amount of funds for passing or landing on Go,
        and the default list of place names. Creates a Property class object for each intended space on the game board
        and assigns it to the location dictionary (the effective game board, for purposes here), keyed to the position
        of the space on the game board (which is defined here by the rent index variable). If a duplicate name is
        detected, returns nothing and aborts the process, since the place name list illegitimate/has duplicates.
        (This shouldn't happen with the default name list, but may be relevant if custom name lists are used later).

        Property References: Property object created
        """

        # Copies the rent array for reference by other methods
        self._rent_list = rent_array

        # Checks to make sure all rents are legitimate
        for rent in rent_array:
            if rent <= 0:
                # print("All places must charge at least SOME amount of rent. And definitely can't be negative.")
                return

        # Define cash for passing "Go"
        self._go_cash = go_cash

        # Create 24 new spaces:
        rent_index = 1
        temp_name_list = ["Go"]                                         # Temporary name blackout list
        for rent in rent_array:
            if self._place_names[rent_index] in temp_name_list:         # Cancels if duplicate found
                # print("create_spaces: A property by this name already exists.")
                return

            # Creates a property based on rent/place name and assigns keys it to the correct position
            self._location_dict[rent_index] = Property(self._place_names[rent_index], rent_index, rent)
            temp_name_list.append(self._place_names[rent_index])        # Puts the place name on the blackout
            rent_index += 1                                             # Makes sure next space is at next position

    def create_player(self, player_name, start_cash):
        """
        Creates a Player class object based on input player name string and starting cash amount, and adds it to the
        RealEstateGame object's player dictionary (keyed to their name), so that the player can be used in the game.
        Assigns the "Go" Property object from the location dictionary to the player object's location by using the
        player object's update_location method. Returns nothing/cancels the operation if a player by the same name
        already exists. The player's number is assigned based on the current number of players in the game.

        Player References: Player object create and its update_location method is called
        Property References: 1st property object in location dictionary (key 0) is used as argument for update_location
        """
        # Cancel operation without doing anything if the player already exists
        if player_name in self._player_dict:
            # print("create_player: They already exist!")
            return

        # Checks to make sure the starting cash is legitimate; if they can't buy anything the game might never end.
        # Check only happens if internal rent list is populated. No way to enforce this, outside of programming order,
        # which is why this is just skipped with no consequence if the list is currently empty.
        if self._rent_list:
            if start_cash <= min(self._rent_list):
                # print("It's hard to play if you don't have the cash to buy anything.")
                return

        # Increments Player Count / Determines the "Player Number" of the new player (for use in a game loop)
        self._player_count += 1

        # Creates the player and moves them to "Go"
        self._player_dict[player_name] = Player(player_name, start_cash, self._player_count)
        self._player_dict[player_name].update_location(self._location_dict[0])

    def get_player_account_balance(self, player_name):
        """
        Returns the account balance of the argument player name's balance using the matching Player object's
        get_cash method, from the player dictionary. Returns empty if the player is not found.

        Player References: Player object's get_cash method is called
        """

        if player_name in self._player_dict:
            return self._player_dict[player_name].get_cash()
        return  # returns None if the player's name wasn't found as a key in the dictionary

    def get_player_current_position(self, player_name, get_name=False):
        """
        Returns the player location on the board (based on player name argument) by using the matching Player object's
        get_location method, from the player dictionary. Returns empty if the player is not found.
        Indirectly accesses an object from the place dictionary using the player object's get_location method.

        Player References: Player object's get_location method is called
        """

        # Can add "True" flag for get_name parameter to return the location's name instead
        if get_name is True:
            return self._player_dict[player_name].get_loc().get_name()

        # By default, the program returns the position of the player as an integer, unless flagged to return otherwise
        if player_name in self._player_dict:
            return self._player_dict[player_name].get_loc().get_position()
        return  # returns None if the player's name wasn't found as a key in the dictionary

    def buy_space(self, player_name):
        """
        Determines whether a space can be purchased and purchases it, if it can be, based on the player name parameter.
        Returns True if the transaction is successful and False if it is not, for any reason (for testing purposes).
        Uses information found in the matching Player object found in the player dictionary. Indirectly accesses a
        property object from the location dictionary by calling the player object's get_location method.

        Player References: Player object's get_location, get_cash, update_cash, and update_holdings methods are called
        Property References: For the property object returned by the player object's get_location: get_rent, get_owner,
                             get_price, and update_owner methods are called

        """

        # If the player doesn't exist / is out of the game
        if player_name not in self._player_dict:
            # print("buy_space: This player doesn't exist - they can join then next game, THEN try to buy this.")
            return False

        # Temp. Readability Variables
        player = self._player_dict[player_name]
        current_loc = self._player_dict[player_name].get_loc()
        current_rent = self._player_dict[player_name].get_loc().get_rent()
        current_loc_owner = self._player_dict[player_name].get_loc().get_owner()
        player_cash = self._player_dict[player_name].get_cash()
        current_loc_price = self._player_dict[player_name].get_loc().get_price()

        # If the player tries to buy "Go"
        if current_rent == 0:
            # print("buy_space: Can't buy 'Go', silly!")
            return False                            # Caused by being silly and trying to buy "Go"

        # If the property is already owned by someone else
        if current_rent != 0 and current_loc_owner is not None:
            # print("buy_space: Can't buy someone else's property either!")
            return False                            # Caused by trying to by owned land

        # If the player has an account balance greater than the purchase price
        # (Note: they can't buy something that would put them at 0, as they would then lose the game)
        if player_cash > current_loc_price:
            charge = -1 * current_loc_price
            player.update_cash(charge)
            player.update_holdings(current_loc)     # Location added to player inventory
            current_loc.update_owner(player)        # Player assigned to property as its owner
            return True
        # print("buy_space: No dough, no show.")
        return False                                # Caused by insufficient funds

    def move_player(self, player_name, spaces_moved):
        """
        Moves a player (player_name) based on a die roll (space_moved) and has them collect cash for
        passing or landing on the "Go" space. If they land in a space owned by another player, they pay rent to them.
        If they have insufficient funds to pay rent, they lose, and the Player object's lose method is called to resolve
        property changes, final rent payment, and to remove the player from the game.

        Player References: Calls player object's get_cash, get_location, update_location, update_cash, and loser methods
        Property References: Player get_location method objects use the get_position, get_owner, and get_rent methods

        Important Note: Once a player has lost, they are deleted entirely from the player dictionary. As such, results
        of None should be expected for calls using the methods within the RealEstateGame object. Any commands that
        attempt to make calls using methods from within the Player object itself will result in an error, since the
        player object no longer exists, and thus the methods called won't exist either (crashing the program).
        """

        # Check to make sure player exists in dictionary
        if player_name not in self._player_dict:
            # print("move_player: I don't think that player is 'all there'.")
            return  # Cancel everything if the player doesn't exist, or no longer exists/lost the game

        # Only let players move if there are enough players. Not needed for buy_space, since players can't buy "Go"
        # and cannot move to a buy-able space without getting past this filter in the move_player method.
        if self._player_count < 2:
            # print("move_player: Please wait for more players.")
            return

        # Player object shortcut for more readable code, as long as they exist
        player = self._player_dict[player_name]

        # If the player's account balance is 0
        if player.get_cash() == 0:
            # print("move_player: No moving for you, penniless foo!")
            return  # Redundant with my program implementation, but readme specifies checking for this

        # The number of spaces to move will be an integer between 1 and 6
        if 0 > spaces_moved or spaces_moved > 6:
            # print("move_player: Illegal Move: Stop using weird dice! (Movement must be 1 through 6).")
            return  # illegal move

        # The method will advance the player around the circular board by the number of spaces
        next_position = spaces_moved + player.get_loc().get_position()
        if next_position < 25:
            player.update_location(self._location_dict[next_position])

        # Player moves into another lap and passes or lands on Go (and collects their money)
        if next_position > 24:
            player.update_location(self._location_dict[next_position - 25])   # -25 because of "Go"
            player.update_cash(self._go_cash)

        # After the move is complete the player will pay rent for the new space occupied, if necessary
        if player.get_loc().get_owner() == player:
            return  # No self dealing!

        if player.get_loc().get_owner() is None:
            if player.get_loc().get_rent() == 0:
                return  # No paying rent on "Go"!
            return  # this is where a buy prompt would happen in an automated game loop - may expand later

        # If you made it this far down the loop, then you HAVE to pay somebody something
        rent_due = player.get_loc().get_rent()
        land_lord = player.get_loc().get_owner()

        # The current player has enough money and pays it to the landlord player
        if player.get_cash() > rent_due:
            player.update_cash((-1 * rent_due))
            land_lord.update_cash(rent_due)
            return

        # Landlord takes all the player's remaining money
        land_lord.update_cash(player.get_cash())            # Gets all the $$$
        player.update_cash((-1 * player.get_cash()))        # Loses all the $$$ (may not be needed due to deleting them)
        player.loser()                                      # Clears all their holdings and their name from all holdings
        # print(player_name, "has been defeated. They have been removed from the game and all their properties freed.")
        del self._player_dict[player_name]                  # Player deleted from player list
        return

    def check_game_over(self):
        """
        Checks if the conditions have been met to end the game (no parameters). That is, this method checks if there is
        still more than 1 player (or less) remaining in the game. If so, it returns an empty string. If there are one or
        fewer players remaining, it returns the name of the winner.

        Player References: Calls the winning player object's get_name method
        """

        # Kill the check if the game can't start yet due to too few players - can only play with 2+ people
        if self._player_count < 2:
            # print("check_game_over: Please wait for more players. The game hasn't started yet.")
            return ""

        # If there are enough players, check to see if the game is over
        if len(self._player_dict) > 1:                          # If more than 1 player is left, game on!
            return ""

        for player in self._player_dict:                        # Triggers once there is one player or less left
            self._game_over = True                              # For use in game loop; flag to end the loop
            # print("Winner!")
            return self._player_dict[player].get_name()         # Declare the name of the person left: The Winner!

    def delete_player(self, player_name):
        """
        Clears a player's holdings and deletes them from the player dictionary, based on player name parameter.
        Primarily to streamline testing the program.
        """
        if player_name not in self._player_dict:
            # print("delete_player: Player doesn't exist.")
            return

        player = self._player_dict[player_name]
        player.loser()                              # Clears all their holdings and their name from all holdings
        del self._player_dict[player_name]          # The player is deleted from the active players dictionary

    def start_game(self, manual=False):
        """
        Checks that initial game conditions are valid, and if they are, runs a game until there is a winner. The
        manual parameter defaults to False and determines whether players have agency, or if the whole game will
        be automated. If the default value of False is overridden as True, then players will be prompted to roll the
        dice and make purchasing decisions (and be given the option to quit if they don't want to roll the dice).
        """

        # Starting Check: Make sure we have a legal board and enough players:
        print("Before we start, let's check things over to make sure everything is legit...")
        if self._start_check is False:

            # Check player count and the board
            if self._player_count < 2:
                return print("You need at least 2 players to start the game. Please add more players and try again.")
            if len(self._location_dict) != 25:
                return print("Game board illegal. The board must have exactly 25 spaces. Please correct the board.")
            if self._location_dict[0].get_name() != "Go":
                return print("The first position must be named 'Go'. Please correct the board.")
            if "None" in self._rent_list:
                return print("At least one space has illegitimate rent.")

            # Make sure players all have at least some starting cash
            for player in self._player_dict:
                if self._player_dict[player].get_cash() <= 0:
                    return print("All players need to have at least *some* starting cash")

                # Check all players' minimum cash to make sure everyone has at least a chance of buying something.
                if self._player_dict[player].get_cash() < min(self._rent_list):
                    return print("The board is too expensive for players. Either give them more cash, or make"
                                 "a game board with cheaper property.")

            # If there are enough players (with money) and the board is good, game on!
            self._start_check = True
            print("Everything looks good! Let's get started!")

        # Starts tracking the round of the game and generates lists to store money snapshots at the end of each player's
        # turn from that round.
        game_history_dict = {}
        game_round = 0
        for player_name in self._player_dict:
            # Records starting cash at round 0 each player key's first value
            game_history_dict[player_name] = [(game_round, self._player_dict[player_name].get_cash())]
        game_round += 1  # First turn data will reflect status at the end of the round 1 for each player

        # The Primary Game Loop: This runs until the game hits a game over state yet
        while self._game_over is False:
            for player_name in list(self._player_dict):
                if self.check_game_over() == "":

                    # The variables are used for readability; need to rebind after changes
                    current_location_name = self._player_dict[player_name].get_loc().get_name()
                    player_cash = self._player_dict[player_name].get_cash()

                    print("\nIt's your turn: ", player_name)
                    print(player_name, "currently has", "$" + str(player_cash))
                    print(player_name, "is currently at", current_location_name)
                    temp_holding_names = []
                    for place in self._player_dict[player_name].get_holdings():
                        temp_holding_names.append(place.get_name())
                    print("Currently owns:", temp_holding_names)

                    # Manual Movement Prompt / Quitting Opportunity
                    if manual is True:
                        play = None
                        while play != "y":
                            play = input("Would you like to roll the dice and keep playing? (y/n)\n")
                            if play == "n":
                                quit_game = input("Would you like to quit? (y/n)\n")
                                if quit_game == "n":
                                    play = None
                                if quit_game == "y":
                                    print(player_name, "has left the game.")
                                    self._player_dict[player_name].loser()          # Clears holdings
                                    del self._player_dict[player_name]              # Removes the player
                                    play = "y"

                    # Digital rolling of the dice happens automatically here, as long as the player still exists
                    if player_name in self._player_dict:
                        dice_roll = random.randint(1, 6)
                        print(player_name, "has rolled a", dice_roll)
                        self.move_player(player_name, dice_roll)

                        # Need to re-check that player is in the dictionary, since if they lost they were deleted
                        if player_name in self._player_dict:
                            current_location_name = self._player_dict[player_name].get_loc().get_name()
                            print(player_name, "has moved to", current_location_name)

                            # Buying Property
                            if self._player_dict[player_name].get_loc().get_owner() is None:
                                if self._player_dict[player_name].get_loc().get_rent() != 0:
                                    print("You may purchase this property!")

                                    # Manual mode - player can decide purchase
                                    if manual is True:
                                        purchase = None
                                        while purchase != "n":
                                            purchase = input("Would you like to buy this property for $" +
                                                             str(self._player_dict[player_name].get_loc().get_price())
                                                             + "? (y/n)\n")
                                            if purchase == "y":
                                                self.buy_space(player_name)
                                                player_cash = self._player_dict[player_name].get_cash()
                                                if player_cash > self._player_dict[player_name].get_loc().get_price():
                                                    if self._player_dict[player_name].get_loc().get_name() != "Go":
                                                        print(player_name, "has purchased", current_location_name)
                                                    print(player_name, "now has $" + str(player_cash))
                                                else:
                                                    print("Woops, looks you can't afford that!")
                                                    print(player_name, "now has $" + str(player_cash))
                                                purchase = "n"

                            # Auto/Simulation mode - purchase happens automatically
                            if manual is False:
                                self.buy_space(player_name)
                                player_cash = self._player_dict[player_name].get_cash()
                                print(player_name, "has purchased", current_location_name)
                                print(player_name, "now has $" + str(player_cash))

                            # Rent payment status, if it can't be bought and isn't owned by None
                            player = self._player_dict[player_name]
                            player_cash = self._player_dict[player_name].get_cash()
                            if player.get_loc().get_owner() == player:
                                print(player_name, "owns this property. Yay!")
                            elif self._player_dict[player_name].get_loc().get_owner() is not None:
                                print(player_name, "had to pay", "$" + str(player.get_loc().get_rent()), "in rent to",
                                      player.get_loc().get_owner().get_name())
                                print(player_name, "now has $" + str(player_cash))

                    # Checks if player has either gone bankrupt or quit by the end of turn and prints if they have
                    if player_name not in self._player_dict:
                        print(player_name, "has been defeated!")

                    # Prints the winner if the game ended during this turn
                    if self.check_game_over() != "":
                        print("\nWe have a winner!")
                        print(self.check_game_over(), "\n")

            # If game is still going, print out the current active players and their cash
            if self.check_game_over() == "":
                print("\nThe following players are still in the game!")
                for player_name in self._player_dict:
                    print(player_name, "with:", "$" + str(self._player_dict[player_name].get_cash()))
                    game_history_dict[player_name].append((game_round, self._player_dict[player_name].get_cash()))
                game_round += 1

        print("Now that we have a winner, let's review the storied history of this game! Graphically!")
        for player_name in game_history_dict:

            # Iterate through the player data pairs for round/cash values to respective temp lists (for graphing)
            round_list = []
            cash_list = []

            # Creates a list of rounds and list of cash-on-hand for that round that correlate by index
            for pair in game_history_dict[player_name]:
                round_list.append(pair[0])
                cash_list.append(pair[1])

            # Produces a graph for each player to show their financial history over the course of the game
            pyplot.title("Player Financial History")
            pyplot.plot(round_list, cash_list, label=player_name)
        pyplot.xlabel("Round of the Game")
        pyplot.ylabel("Player Cash Reserves (in $) at End of Round")
        pyplot.legend(loc='upper left')
        pyplot.show()

        # Clear the board for new players - delete all players, resets player count to 0, and wipes ownership
        print("Clearing the board for the next game!")
        self._player_dict = {}
        for place in self._location_dict:
            self._location_dict[place].update_owner(None)
        self._player_count = 0


class Player:
    """
    Represents a boardgame player. Has data member to track the player's name, current location, cash,
    property holdings, and their player number (for potential use in an automated game loop).

    Class Interactions: This object contains all the information that must be directly associated with a player.
                        It is used by RealEstateGame objects to represent players. It is returned by the Property class
                        object's get_owner method and allows methods in a Property object to access all relevant
                        information about the owner of the property. The Property class is returned by the
                        Player object's get_location method, so that the Player object can access all information about
                        their current location on the board. Property objects are also stored in the Player
                        object's holdings list (and get/update holdings functions) so to access information and methods
                        for properties that the player owns, or is attempting to buy.

    Methods:    get_name, get_location, get_cash, get_holdings, get_player_num (for game loop only), update_cash,
                update_holdings, update_location, and loser
    """

    def __init__(self, name, start_cash, player_num=None):
        """
        Creates a new player object based on name, starting cash, and player number parameters.
        Holdings (property owned) are initialized as an empty list, and the player's location is initialized as None
        (The player will be moved to "Go" as part of the RealEstateGame's create_player method, since the player
        object has no context for any board locations until it becomes part of the actual game.)
        """

        self._name = name
        self._location = None
        self._cash = start_cash
        self._holdings = []
        self._player_num = player_num           # Used to enforce turn-order in the game loop

    def get_name(self):
        """Returns the player's name as a string."""
        return self._name

    def get_loc(self):
        """Returns the player's current location on the game board (as the location object)."""
        return self._location

    def get_cash(self):
        """Returns the player's current cash holdings."""
        return self._cash

    def get_holdings(self):
        """
        Returns a list of the player's current property holdings (as a list of objects). The items in this list are
        listed in the order that they were purchased.
        """
        return self._holdings

    def get_player_num(self):
        """Returns the player's number, which is used to determine turn order."""
        return self._player_num

    def update_cash(self, amount):
        """
        Adds or removes cash from the player's account, depending on if the argument is positive or negative.
        Based on amount parameter.
        """
        self._cash += amount

    def update_holdings(self, property_obj):
        """
        Adds or removes a property object from the player's holdings, based on an argument property object.
        """

        # Don't need to check for ownership, since that's handled by the buy function
        self._holdings.append(property_obj)
        return

    def update_location(self, location):
        """
        Updates the player's location (a location object keyed to its integer position on the game board)
        based on input parameter.
        """
        self._location = location
        return

    def loser(self):
        """
        If the player has lost the game, clears them as the owner of all their holdings and clears their holdings list.
        """
        for place in self._holdings:    # Updates the owner for all place objects in their holdings list
            place.update_owner(None)
        self._holdings = None           # Usage of None here to differentiate start/bankruptcy conditions
        return


class Property:
    """
    Represents a boardgame property location. Has data members to record the property's name, position on the
    game board, rent cost, purchase price, and the current owner's name.

    Class Interactions: This object contains all the information that must be directly associated with a property
                        location within a RealEstateGame object. It is returned by a Player object's get_location
                        method and allows methods in a Player object to access all relevant information about their
                        current position on the board. Property objects are also stored in Player objects' holdings list
                        (and get/update holdings functions) to access information and methods for properties that a
                        player owns, or is attempting to buy.

    Methods: get_name, get_position, get_rent, get_price, get_owner, update_cash, and update_owner
    """

    def __init__(self, name, position, rent):
        """
        Creates a new property based on name, location, and rent parameters.
        Name, location, and rent are derived from an argument received by the RealEstateGame class. Initial owner is
        set to None, until someone purchases it.
        """
        self._name = name
        self._position = position
        self._rent = rent
        self._price = 5 * self._rent
        self._owner = None

    def get_name(self):
        """Returns the property's name as a string."""
        return self._name

    def get_position(self):
        """Returns the property's position as an integer."""
        return self._position

    def get_rent(self):
        """Returns the property's rent price."""
        return self._rent

    def get_price(self):
        """Returns the property's purchase price (5x the cost of rent)."""
        return self._price

    def get_owner(self):
        """Returns the current property's owner's player object."""
        return self._owner

    def update_owner(self, owner):
        """Updates the property's current owner based on owner object parameter."""
        self._owner = owner


def setup_default_game(player_count):
    """
    Quickly sets up a game based on the parameter player count, using default amounts for rent and starting cash.
    Players names are assigned as Player 1, Player 2, etc. in order as they are created.
    Player number (for turn order) is assigned in the order the player is created. Early bird gets the worm!
    """

    # Creates the default game board
    default_game = RealEstateGame()
    print("Creating the Game Board...")
    default_rents = [50, 50, 50, 75, 75, 75, 100, 100, 100, 150, 150, 150, 200, 200, 200, 250, 250, 250, 300, 300,
                     300, 350, 350, 350]
    default_game.create_spaces(50, default_rents)

    # Creates the players
    for num in range(1, player_count + 1):
        player_name = "Player " + str(num)
        print("Creating", player_name)
        default_game.create_player(player_name, 1000)
    return default_game


# Try The Game Loop Here! Use manual=False to watch the game play itself, or use manual=True to play it for real!
game = setup_default_game(30)    # Integer parameter determines how many players the board will be set for
game.start_game(manual=False)    # Use manual=True to test manual gameplay with user prompts; False for autoplay

# Ideas to Expand Project:  Doomsday Card Deck class (random event each round from list of events), GUI for game,
#                           generalized attribute for non-rent classes for community-chest/jail type spaces
#                           (actually... you can't purchase 0 rent properties, so I think you can already do this;
#                           may just need to remove filter for 0 rent properties not being permitted, if it exists;
#                           maybe a method that says if not go and 0 dollars, it's an event location; new method
#                           that assigns rules to event locations that can be defined by a class, perhaps?)
#                           property upgrades (new class w/ different values depending on upgrade type),


# Method to init game itself, method to init gfx and put both into start_game
# pygame and tkinter libraries should suffice? how to implement bind?
# pygame has good gameplay widgets, but need tkinter for any real UI elements (like buttons, etc.)
