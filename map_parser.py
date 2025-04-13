import struct
import numpy as np

def prepare_wfc_input(map_path, map_width=None, map_height=None, is_large_map=False):
    # TANIBO (2.35) is a small map, and Vertania is a large map, so be careful when you set is_large_map! 
    with open(map_path, 'rb') as f:
        # Determine header size
        header_size = 32 if is_large_map else 28
        
        # Read header and get dimensions
        header = f.read(header_size)
        org_columns, org_rows = struct.unpack('<II', header[:8])
        
        # Use manual dimensions if provided
        if map_width and map_height:
            org_columns, org_rows = map_width, map_height
        
        print(f"Processing {org_columns}x{org_rows} map with {header_size}-byte header")

        # Read all tile data
        f.seek(header_size)
        rom_ids = np.frombuffer(f.read(), dtype='<u2')
        
        # Convert tiles and track movable blocks
        movable_ids = set()
        unique_ids_set = set()
        
        def convert_tile(tile):
            """Convert raw tile value to final ID, tracking movable blocks"""
            if tile >= 0x2E00:  # Movable block threshold - all the tile that shos as extremely large in its metadata means it is being added with a flag representing is is moveable.
                converted = tile - 11264 - 1024
                movable_ids.add(converted)
                unique_ids_set.add(converted)
                return converted
            elif tile >= 1024:
                converted = tile - 1024
                unique_ids_set.add(converted)
                return converted
            unique_ids_set.add(tile)
            return tile # Normal tiles
        
        tile_ids = np.array([convert_tile(t) for t in rom_ids])
        
        # Reshape to 2D grid with error handling
        try:
            wfc_grid = tile_ids.reshape(org_rows, org_columns)
        except ValueError as e:
            print(f"Error reshaping array: {e}")
            print(f"Expected {org_rows*org_columns} tiles, got {len(tile_ids)}")
            raise
        
        return wfc_grid, org_rows, org_columns, sorted(movable_ids), sorted(unique_ids_set)

# Usage:
#wfc_array, rows, cols, movable_ids, unique_ids_set = prepare_wfc_input("VERTANIA-WALD (1.0).map", None, None, True)

#print("\nFinal tile array:")
#print(wfc_array)
#print(f"\nMovable block IDs: {movable_ids}")  # Now shows as plain integers
#print(f"\nMap dimensions: {rows} rows × {cols} columns")
#print(f"\nAll IDS(Unique): {unique_ids_set}")
