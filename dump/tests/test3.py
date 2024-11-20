# Kram testing site

index = 18

home_row = index // 8
home_col = index % 8

diamond_indices = []

diamond_indices.append(index)

# Loop through potential positions in the diamond range
for row_offset in range(-2, 3):   # Rows from -2 to +2 around home_row
    for col_offset in range(-2, 3):  # Columns from -2 to +2 around home_col
        # Calculate new position
        new_row = home_row + row_offset
        new_col = home_col + col_offset
        
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            # Check if the Manhattan distance is exactly 2
            if abs(row_offset) + abs(col_offset) == 2 or abs(row_offset) + abs(col_offset) == 1:
                # Convert (new_row, new_col) to 1D index
                diamond_indices.append(new_row * 8 + new_col)
        
print(diamond_indices)