#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import argparse
import psycopg2


def connect():
    """Connect to the PostgreSQL database.
    Command line options for specifying the database(-d)
                                        the host(-t) or
                                        the user(-u)
    No options user default connnection: dbname=localhost
    Returns a database connection.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dbname', default='tournament',
                        help='specify database name')
    parser.add_argument('-t', '--host', help='specify database host')
    parser.add_argument('-u', '--user', help='specify database user')
    args = parser.parse_args()

    conn_string = 'dbname=' + args.dbname

    if args.host:
        conn_string += ' host=' + args.host

    if args.user:
        conn_string += ' user=' + args.user

    return psycopg2.connect(conn_string)


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches")

    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players")

    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()

    query = "SELECT count(*) FROM players"
    c.execute(query)

    count = c.fetchone()

    DB.close()
    return count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("insert into players values (%s) ", (name,))

    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()

    c.execute('SELECT * FROM standings')

    standings = [(row[0], row[1], row[2], row[3]) for row in c.fetchall()]

    DB.close()
    return standings


def reportMatch(winner, loser, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw:  boolean for guard if the players tied
    """
    DB = connect()

    c = DB.cursor()
    c.execute("insert into matches values ({}, {}, {})".
              format(winner, loser, draw))

    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    standings = playerStandings()
    pairs, l = [], len(standings)
    for i in range(0, l, 2):
        """
        p1: player 1
        p2: player 2
        """
        p1 = standings.pop(0)
        # allow for 'bye' to lowest unmatched player using arbitrary index
        p2 = standings.pop(0) if i < l - 1 else (-999, 'bye')

        add_match(p1, p2, pairs)

    return pairs


def add_match(p1, p2, pairs):
    """Add match in not in match set already

    Args:
        pairs: collection of already matched players
        p1: player 1
        p2: player 2
    """
    if already_matched(p1, p2, pairs):
        raise ValueError("Match already submitted")
    pairs.append((p1[0], p1[1], p2[0], p2[1]))


def already_matched(p1, p2, pairs):
    """Returns boolean describing if pairs to add have already been added

    Args:
        pairs: collection of already matched players
        p1: player 1
        p2: player 2
    """
    return (p1[0], p1[1], p2[0], p2[1]) in pairs or \
           (p2[0], p2[1], p1[0], p1[1]) in pairs
