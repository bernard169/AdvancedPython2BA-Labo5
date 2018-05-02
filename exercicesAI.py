#!/usr/bin/env python3
# tictactoe.py
# Author: Sébastien Combéfis
# Version: March 28, 2016

import argparse
import socket
import sys

import game

class FourInARowState (game.GameState):
    '''Class representing a state for the Tic-tac-toe game.'''
    def __init__(self, initialstate=[None] * 16):
        super().__init__(initialstate)
    
    def update(self, coord, player):
        state = self._state['visible']
        line, column = coord
        index = 4 * line + column
        if not (0 <= line <= 3 and 0 <= column <= 3):
            raise game.InvalidMoveException('The move is outside of the board')
        if state[index] is not None:
            raise game.InvalidMoveException('The specified cell is not empty')
        state[index] = player
    
    def _checkelems(self, state, elems):
        return state is not None and all(e == state for e in elems)
    
    def winner(self):
        state = self._state['visible']
        # Check horizontal and vertical lines
        for i in range(4):
            if self._checkelems(state[4 * i], [state[4 * i + e] for e in range(4)]):
                return state[4 * i]
            if self._checkelems(state[i], [state[4 * e + i] for e in range(4)]):
                return state[i]
        # Check diagonals
        if self._checkelems(state[0], [state[5 * e] for e in range(4)]):
            return state[0]
        if self._checkelems(state[3], [state[12 - 3 * e] for e in range(4)]):
            return state[3]
        return None if state.count(None) == 0 else -1
    
    def prettyprint(self):
        data = ['X' if e == 0 else 'O' if e == 1 else '_' for e in self._state['visible']]
        result = ''
        for i in range(4):
            result += '   {}\n'.format(' '.join(data[i * 4:i * 4 + 4]))
        print(result[:-1])


class FourInARowServer(game.GameServer):
    '''Class representing a server for the four in a row game.'''
    def __init__(self, verbose=False):
        super().__init__('Four in a row', 2, FourInARowState(), verbose=verbose)
    
    def applymove(self, move):
        try:
            index = int(move)
        except:
            raise game.InvalidMoveException('A valid move must be a stringified integer')
        else:
            self._state.update((index // 4, index % 4), self.currentplayer)


class FourInARowClient(game.GameClient):
    '''Class representing a client for the four in a row game.'''
    def __init__(self, name, server, verbose=False):
        super().__init__(server, FourInARowState, verbose=verbose)
        self.__name = name
    
    def _handle(self, message):
        pass
    
    def _nextmove(self, state):
        return str(state._state['visible'].index(None))


if __name__ == '__main__':
    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Four in a row game')
    subparsers = parser.add_subparsers(description='server client', help='Four in a row game components', dest='component')
    # Create the parser for the 'server' subcommand
    server_parser = subparsers.add_parser('server', help='launch a server')
    server_parser.add_argument('--host', help='hostname (default: localhost)', default='localhost')
    server_parser.add_argument('--port', help='port to listen on (default: 5000)', default=5000)
    server_parser.add_argument('--verbose', action='store_true')
    # Create the parser for the 'client' subcommand
    client_parser = subparsers.add_parser('client', help='launch a client')
    client_parser.add_argument('name', help='name of the player')
    client_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    client_parser.add_argument('--verbose', action='store_true')
    # Parse the arguments of sys.args
    args = parser.parse_args()
    if args.component == 'server':
        FourInARowServer(verbose=args.verbose).run()
    else:
        FourInARowClient(args.name, (args.host, args.port), verbose=args.verbose)