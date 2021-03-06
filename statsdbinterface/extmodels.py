# -*- coding: utf-8 -*-

from flask import abort
from .database import db
from .dbmodels import Game, GamePlayer, GameServer, GameWeapon
from .modelutils import direct_to_dict, to_pagination
from . import redeclipse

import config


class Player:
    @staticmethod
    def handle_list():
        # Return a list of all player handles in the database.
        return [r[0] for r in
                GamePlayer.query.with_entities(GamePlayer.handle).filter(
                GamePlayer.handle != '').group_by(GamePlayer.handle).all()]

    @staticmethod
    def count():
        # Return the number of handles in the database.
        return GamePlayer.query.filter(
            GamePlayer.handle != '').group_by(GamePlayer.handle).count()

    @staticmethod
    def get_or_404(handle):
        # Return a Player for <handle> if <handle> exists, otherwise 404.
        handles = Player.handle_list()
        if handle in handles:
            return Player(handle)
        else:
            abort(404)

    @staticmethod
    def all(page=0, pagesize=None):
        # Return all players, with optional paging.
        filtered_handles = handles = Player.handle_list()
        # If pagesize is specified, only return page <page> from the list.
        if pagesize is not None:
            filtered_handles = handles[
                page * pagesize:page * pagesize + pagesize]
        return [Player(handle) for handle in filtered_handles]

    @classmethod
    def paginate(cls, page, per_page):
        return to_pagination(page, per_page, cls.all, cls.count)

    def __init__(self, handle):
        # Build a Player object from the database.
        self.handle = handle
        self.game_ids = [r[0] for r in GamePlayer.query.with_entities(
            GamePlayer.game_id).filter(GamePlayer.handle == self.handle).all()
            if Game.query.with_entities(Game.id).filter(
                Game.id == r[0]).scalar() is not None]

    def games(self, page=0, pagesize=None):
        # Return full Game objects from Player's game_ids.
        ids = (self.game_ids[page * pagesize:page * pagesize + pagesize]
               if pagesize is not None else self.game_ids)
        if not ids:
            return []
        return Game.query.filter(Game.id.in_(ids)).all()

    def games_paginate(self, page, per_page):
        return to_pagination(page, per_page, self.games,
                             lambda: len(self.game_ids))

    def weapons(self):
        ret = {}
        for weapon in redeclipse.versions.default.weaponlist:
            ret[weapon] = Weapon.from_player(weapon, self.handle)
        return ret

    def to_dict(self):
        return direct_to_dict(self, [
            "handle", "game_ids"
        ])


class Server:

    @staticmethod
    def handle_list():
        # Return a list of all server handles in the database.
        return [r[0] for r in
                GameServer.query.with_entities(GameServer.handle).filter(
                GameServer.handle != '').group_by(GameServer.handle).all()]

    @staticmethod
    def count():
        # Return the number of handles in the database.
        return GameServer.query.filter(
            GameServer.handle != '').group_by(GameServer.handle).count()

    @staticmethod
    def get_or_404(handle):
        # Return a Server for <handle> if <handle> exists, otherwise 404.
        handles = Server.handle_list()
        if handle in handles:
            return Server(handle)
        else:
            abort(404)

    @staticmethod
    def all(page=0, pagesize=None):
        # Return all servers, with optional paging.
        filtered_handles = handles = Server.handle_list()
        # If pagesize is specified, only return page <page> from the list.
        if pagesize is not None:
            filtered_handles = handles[
                page * pagesize:page * pagesize + pagesize]
        return [Server(handle) for handle in filtered_handles]

    @classmethod
    def paginate(cls, page, per_page):
        return to_pagination(page, per_page, cls.all, cls.count)

    def __init__(self, handle):
        # Build a Server object from the database.
        self.handle = handle
        self.game_ids = [r[0] for r in GameServer.query.with_entities(
            GameServer.game_id).filter(GameServer.handle == self.handle).all()
            if Game.query.with_entities(Game.id).filter(
                Game.id == r[0]).scalar() is not None]

    def games(self, page=0, pagesize=None):
        # Return full Game objects from Server's game_ids.
        ids = (self.game_ids[page * pagesize:page * pagesize + pagesize]
               if pagesize is not None else
               self.game_ids)
        if not ids:
            return []
        return Game.query.filter(Game.id.in_(ids)).all()

    def games_paginate(self, page, per_page):
        return to_pagination(page, per_page, self.games,
                             lambda: len(self.game_ids))

    def to_dict(self):
        return direct_to_dict(self, [
            "handle", "game_ids"
        ])


class Map:
    @staticmethod
    def map_list():
        # Return a list of all map names in the database.
        return [r[0] for r in
                Game.query.with_entities(Game.map).group_by(Game.map).all()]

    @staticmethod
    def count():
        # Return the number of maps in the database.
        return Game.query.with_entities(Game.map).group_by(Game.map).count()

    @staticmethod
    def get_or_404(name):
        # Return a Map for <name> if <name> exists, otherwise 404.
        names = Map.map_list()
        if name in names:
            return Map(name)
        else:
            abort(404)

    def all(page=0, pagesize=None):
        # Return all m, with optional paging.
        filtered_names = names = Map.map_list()
        # If pagesize is specified, only return page <page> from the list.
        if pagesize is not None:
            filtered_names = names[
                page * pagesize:page * pagesize + pagesize]
        return [Map(name) for name in filtered_names]

    @classmethod
    def paginate(cls, page, per_page):
        return to_pagination(page, per_page, cls.all, cls.count)

    def __init__(self, name):
        # Build a Map object from the database.
        self.name = name
        self.game_ids = [
            r[0] for r in
            Game.query.with_entities(Game.id).filter(
                Game.map == self.name
            ).all()
        ]

    def games(self, page=0, pagesize=None):
        # Return full Game objects from Map's game_ids.
        ids = (self.game_ids[page * pagesize:page * pagesize + pagesize]
               if pagesize is not None else
               self.game_ids)
        if not ids:
            return []
        return Game.query.filter(Game.id.in_(ids)).all()

    def games_paginate(self, page, per_page):
        return to_pagination(page, per_page, self.games,
                             lambda: len(self.game_ids))

    def topraces(self):
        # Return a dictionary of the top race times.
        return [
            {
                "game_id": r[0],
                "handle": r[1],
                "name": r[2],
                "score": r[3],
            }
            for r in
            (
                GamePlayer.query
                # We only need some information.
                .with_entities(
                    GamePlayer.game_id, GamePlayer.handle,
                    GamePlayer.name, GamePlayer.score
                )
                # Only games from this map.
                .filter(GamePlayer.game_id.in_(self.game_ids))
                # Only timed race.
                .filter(db.func.re_mode(GamePlayer.game_id, 'race'))
                .filter(db.func.re_mut(GamePlayer.game_id, 'timed'))
                # Scores of 0 indicate the race was never completed.
                .filter(GamePlayer.score > 0)
                # Get only the best score from each handle.
                .group_by(GamePlayer.handle)
                .having(db.func.min(GamePlayer.score))
                # Finally: order, limit, and fetch.
                .order_by(GamePlayer.score.asc())
                .limit(config.API_HIGHSCORE_RESULTS)
                .all()
            )
        ]

    def to_dict(self):
        return direct_to_dict(self, [
            "name", "game_ids"
        ], {
            "topraces": self.topraces(),
        })


class Weapon:

    columns = ["timewielded", "timeloadout",
               "damage1", "frags1", "hits1", "flakhits1",
               "shots1", "flakshots1",
               "damage2", "frags2", "hits2", "flakhits2",
               "shots2", "flakshots2",
               ]

    @staticmethod
    def weapon_list():
        # Return a list of all default weapon names.
        return redeclipse.versions.default.weaponlist

    @staticmethod
    def count():
        # Return the number of default weapons.
        return len(Weapon.weapon_list())

    @staticmethod
    def finish_query(name, query):
        weapon = Weapon(name)
        qret = query.with_entities(*[
            db.func.sum(getattr(GameWeapon, c))
            for c in Weapon.columns]).all()[0]
        for c in Weapon.columns:
            setattr(weapon, c, qret[Weapon.columns.index(c)])
        return weapon

    @staticmethod
    def from_player(weapon, player):
        return Weapon.finish_query(weapon, GameWeapon.query.filter(
            GameWeapon.weapon == weapon).filter(
                GameWeapon.playerhandle == player))

    @staticmethod
    def from_game(weapon, game):
        return Weapon.finish_query(weapon, GameWeapon.query.filter(
            GameWeapon.weapon == weapon).filter(
                GameWeapon.game_id == game))

    @staticmethod
    def from_game_player(weapon, game, player):
        return Weapon.finish_query(weapon, GameWeapon.query.filter(
            GameWeapon.weapon == weapon).filter(
                GameWeapon.game_id == game).filter(
                GameWeapon.playerhandle == player))

    @staticmethod
    def from_weapon(weapon):
        return Weapon.finish_query(weapon, GameWeapon.query.filter(
            GameWeapon.weapon == weapon))

    @staticmethod
    def get_or_404(name):
        names = Weapon.weapon_list()
        if name in names:
            return Weapon.from_weapon(name)
        else:
            abort(404)

    @staticmethod
    def all():
        return [Weapon.from_weapon(n) for n in Weapon.weapon_list()]

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return direct_to_dict(self, [
            "name"
        ] + Weapon.columns)
