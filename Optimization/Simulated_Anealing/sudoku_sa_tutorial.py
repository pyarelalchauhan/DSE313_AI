import numpy as np
import math
import random
import time
import os

# --- Terminal Colors & Emojis ---
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- Sudoku Core Logic ---

def print_sudoku(sudoku):
    """Prints the Sudoku board with nice formatting."""
    header = bcolors.OKCYAN + "      1 2 3   4 5 6   7 8 9" + bcolors.ENDC
    top_border = "    " + bcolors.OKCYAN + "┏" + "━"*23 + "┓" + bcolors.ENDC
    print(header)
    print(top_border)
    for i in range(9):
        if i in [3, 6]:
            sep = "    " + bcolors.OKCYAN + "┣" + "━"*7 + "╋" + "━"*7 + "╋" + "━"*7 + "┫" + bcolors.ENDC
            print(sep)
        line = f"  {bcolors.OKCYAN}{i+1} ┃{bcolors.ENDC} "
        for j in range(9):
            if j in [3, 6]: line += bcolors.OKCYAN + "┃ " + bcolors.ENDC
            val = str(sudoku[i, j]) if sudoku[i, j] != 0 else "."
            line += (bcolors.WARNING + val + bcolors.ENDC + " ") if sudoku[i, j] == 0 else (val + " ")
        print(line + bcolors.OKCYAN + "┃" + bcolors.ENDC)
    print("    " + bcolors.OKCYAN + "┗" + "━"*23 + "┛" + bcolors.ENDC)

def ascii_chart(history, width=40, height=5, label="Data", color=bcolors.OKGREEN):
    """Generates a simple ASCII sparkline-style graph for the terminal."""
    if not history: return ""
    
    # Downsample history to fit width
    if len(history) > width:
        indices = np.linspace(0, len(history) - 1, width, dtype=int)
        data = [history[i] for i in indices]
    else:
        data = history

    min_val, max_val = min(data), max(data)
    rng = max_val - min_val if max_val != min_val else 1
    
    chart = []
    for h in range(height, -1, -1):
        row = f"{bcolors.BOLD}{label:7} | {bcolors.ENDC}"
        threshold = min_val + (h / height) * rng
        for val in data:
            if val >= threshold:
                row += color + "█" + bcolors.ENDC
            else:
                row += " "
        chart.append(row)
    
    chart.append(" " * 10 + "┗" + "━" * len(data))
    return "\n".join(chart)

def calculate_errors(sudoku):
    errors = 0
    for i in range(9):
        errors += (9 - len(np.unique(sudoku[i, :])))
        errors += (9 - len(np.unique(sudoku[:, i])))
    return errors

def randomly_fill_blocks(sudoku):
    filled = np.copy(sudoku)
    fixed_mask = (sudoku != 0)
    for r_block in range(3):
        for c_block in range(3):
            r, c = r_block * 3, c_block * 3
            block = filled[r:r+3, c:c+3]
            existing = block[block != 0]
            missing = [v for v in range(1, 10) if v not in existing]
            random.shuffle(missing)
            for i in range(3):
                for j in range(3):
                    if not fixed_mask[r+i, c+j]:
                        filled[r+i, c+j] = missing.pop()
    return filled, fixed_mask

def solve_with_terminal_viz(puzzle):
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{bcolors.HEADER}{bcolors.BOLD}🌡️ TERMINAL SA SUDOKU SOLVER 🌡️{bcolors.ENDC}\n")
    
    # --- STEP 1: PRINT INITIAL PUZZLE ---
    print(f"{bcolors.OKBLUE}{bcolors.BOLD}Step 1: Initial Sudoku Puzzle (Unsolved){bcolors.ENDC}")
    print_sudoku(puzzle)
    time.sleep(1.5)

    # --- STEP 2: RANDOMLY FILL BLOCKS ---
    current_board, fixed_mask = randomly_fill_blocks(puzzle)
    print(f"\n{bcolors.OKBLUE}{bcolors.BOLD}Step 2: After Randomly Filling 3x3 Blocks{bcolors.ENDC}")
    print(f"(Note: Each 3x3 block is now valid, but Rows/Cols have conflicts)")
    print_sudoku(current_board)
    score = calculate_errors(current_board)
    print(f"Initial Conflicts (Cost): {bcolors.FAIL}{score}{bcolors.ENDC}")
    time.sleep(2.0)

    # --- STEP 3: ANNEALING ---
    # Parameters & History
    sigma = 1.0           # Initial Temperature
    decreaseFactor = 0.99 # Exponential Cooling
    stuckCount = 0
    
    cost_history = []
    sigma_history = []
    
    max_epochs = 2000
    iterations = 100
    
    best_score = score
    best_board = np.copy(current_board)

    print(f"\n{bcolors.OKGREEN}Starting Annealing Process...{bcolors.ENDC}")
    time.sleep(1)

    last_move_status = "N/A"
    accepted_moves = 0
    rejected_moves = 0

    for epoch in range(max_epochs):
        previousScore = score
        
        for i in range(iterations):
            # Pick a block and swap two non-fixed cells
            br, bc = random.randint(0, 2) * 3, random.randint(0, 2) * 3
            cells = [[br+r, bc+c] for r in range(3) for c in range(3) if not fixed_mask[br+r, bc+c]]
            if len(cells) < 2: continue
            
            c1, c2 = random.sample(cells, 2)
            
            # Swap
            current_board[c1[0], c1[1]], current_board[c2[0], c2[1]] = \
                current_board[c2[0], c2[1]], current_board[c1[0], c1[1]]
            
            new_score = calculate_errors(current_board)
            delta_e = new_score - score
            
            if delta_e <= 0 or (sigma > 0 and random.random() < math.exp(-delta_e / sigma)):
                score = new_score
                accepted_moves += 1
                last_move_status = f"{bcolors.OKGREEN}ACCEPTED{bcolors.ENDC}"
                if score < best_score:
                    best_score = score
                    best_board = np.copy(current_board)
            else:
                # Revert
                current_board[c1[0], c1[1]], current_board[c2[0], c2[1]] = \
                    current_board[c2[0], c2[1]], current_board[c1[0], c1[1]]
                rejected_moves += 1
                last_move_status = f"{bcolors.FAIL}REJECTED{bcolors.ENDC}"
            
            if best_score == 0: break
        
        cost_history.append(score)
        sigma_history.append(sigma)
        
        # --- COOLING SCHEDULE ---
        sigma *= decreaseFactor
        
        # Adaptive Reheating
        if score >= previousScore: stuckCount += 1
        else: stuckCount = 0
        
        if stuckCount > 80:
            sigma += 2
            stuckCount = 0

        # UI Update
        if True: 
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"{bcolors.HEADER}Epoch: {epoch} | Best Score Found: {bcolors.OKGREEN}{best_score}{bcolors.ENDC}")
            print(f"{bcolors.BOLD}Current Cost: {bcolors.FAIL}{score}{bcolors.ENDC} | Current Temp: {bcolors.OKCYAN}{sigma:.6f}{bcolors.ENDC}")
            print(f"Last Move: {last_move_status} | Accepted: {accepted_moves} | Rejected: {rejected_moves}")
            
            print(ascii_chart(cost_history, label="COST", color=bcolors.FAIL))
            print(ascii_chart(sigma_history, label="TEMP", color=bcolors.OKCYAN))
            
            print_sudoku(current_board)
            time.sleep(0.2)

        if best_score == 0: break

    if best_score == 0:
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}✨ SUCCESS! SOLUTION FOUND! ✨{bcolors.ENDC}")
    else:
        print(f"\n{bcolors.FAIL}Stopped at Epoch {epoch}. Best Score: {best_score}{bcolors.ENDC}")

if __name__ == "__main__":
    puzzle = np.array([
        [0, 9, 4, 0, 0, 6, 0, 3, 2],
        [5, 7, 0, 0, 2, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 5, 0, 8, 0],
        [9, 0, 7, 8, 0, 0, 6, 0, 5],
        [0, 0, 6, 0, 9, 0, 3, 0, 0],
        [8, 3, 0, 0, 0, 7, 0, 1, 0],
        [0, 0, 5, 0, 0, 0, 0, 0, 1],
        [0, 2, 0, 1, 5, 0, 4, 6, 7],
        [7, 0, 0, 6, 0, 0, 2, 0, 3]
    ])
    solve_with_terminal_viz(puzzle)
