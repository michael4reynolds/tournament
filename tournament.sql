-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;


CREATE TABLE players
(
  name TEXT NOT NULL,
  id   SERIAL PRIMARY KEY
);

CREATE TABLE matches
(
  winner INTEGER,
  loser  INTEGER,
  tie    BOOLEAN DEFAULT FALSE,
  id     SERIAL PRIMARY KEY
);

-- get total matches by player id
CREATE OR REPLACE VIEW v_played AS
  SELECT
    players.id,
    count(players.id) AS played
  FROM matches
    LEFT JOIN players
      ON matches.winner = players.id OR matches.loser = players.id
  GROUP BY players.id;

-- get total wins
CREATE OR REPLACE VIEW v_won AS
  SELECT
    players.id,
    count(matches.winner) AS wins
  FROM players
    LEFT JOIN matches ON players.id = matches.winner AND matches.tie = FALSE
  GROUP BY players.id;

-- Convenient access to player standings
CREATE OR REPLACE VIEW standings AS
  SELECT
    players.id,
    players.name,
    coalesce(v_won.wins, 0) as wins,
    coalesce(v_played.played, 0) as played
  FROM players
    LEFT JOIN v_played ON players.id = v_played.id
    LEFT JOIN v_won ON v_played.id = v_won.id
  ORDER BY v_won.wins DESC;
