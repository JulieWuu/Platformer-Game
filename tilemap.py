import json


class TileMap:
    def __init__(self, game, tile_size=48):
        self.game = game
        self.tile_size = tile_size
        self.tile_map = {}
        self.off_grid_tiles = []
        self.platforms = {}
        self.saws = {}

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.off_grid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.off_grid_tiles.remove(tile)

        for loc in self.tile_map.copy():
            tile = self.tile_map[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tile_map[loc]

        return matches.copy()

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tile_map': self.tile_map, 'tile_size': self.tile_size, 'off_grid': self.off_grid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tile_map = map_data['tile_map']
        self.tile_size = map_data['tile_size']
        self.off_grid_tiles = map_data['off_grid']
        self.platforms["start"] = (self.extract([('spawners', 2)], True))
        self.platforms["end"] = (self.extract([('spawners', 3)], True))
        self.saws["start"] = self.extract([('spawners', 4)], True)
        self.saws["end"] = self.extract([('spawners', 5)], True)

    def render(self, surf, offset=(0, 0)):
        for loc in self.tile_map:
            tile = self.tile_map[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0],
                                                                        tile['pos'][1] * self.tile_size - offset[1]))
        for tile in self.off_grid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0],
                                                                        tile['pos'][1] - offset[1]))
