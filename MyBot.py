import hlt

from hlt import constants

from hlt.positionals import Direction

import random

import logging

""" <<<Game Begin>>> """

game = hlt.Game()

# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Tenyson")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
ship_states = {}
while True:
    game.update_frame()
    
    me = game.me
    game_map = game.game_map

    command_queue = []

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

    position_choices = []

    for ship in me.get_ships():

        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))
        if ship.id not in ship_states:
            ship_states[ship.id] = "collecting"

        position_options = ship.position.get_surrounding_cardinals() + [ship.position]

        # positon_dict will map the movement to the actual coordinate on the game map
        position_dict = {}
        # Actual movmentassociated with actual highlight
        halite_dict = {}

        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n]

        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount
            # ship will only go in this direction if no other ship plans to
            if position_dict[direction] not in position_choices:
                if direction == Direction.Still:    
                    halite_dict[direction] = halite_amount*3
                else:
                    halite_dict[direction] = halite_amount
            else:
                logging.info("Not moving\n")

        if ship_states[ship.id] == "depositing":
            move = game_map.naive_navigate(ship, me.shipyard.position)
            position_choices.append(position_dict[move])
            command_queue.append(ship.move(move))
            if move == Direction.Still:
                ship_states[ship.id] = "collecting"

          


        elif ship_states[ship.id] == "collecting":
                """ max(halite_dict, key=halite_dict.get) get the key with the highest value to decide which move to make"""
                directional_choice = max(halite_dict, key=halite_dict.get)
                position_choices.append(position_dict[directional_choice])
                command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice])))

                if ship.halite_amount > constants.MAX_HALITE * .95:
                    ship_states[ship.id] = "depositing"


    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    game.end_turn(command_queue)