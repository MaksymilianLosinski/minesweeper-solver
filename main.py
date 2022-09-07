import time
import pygame
import random
from queue import Queue
import threading
pygame.init()


WIDTH, HEIGHT = 680, 680
BG_COLOR = "black"
BOX_COLOR = "gray"
ROWS, COLS = 20, 20
MINES = 40
BOX_SIZE = (WIDTH/ROWS, HEIGHT/COLS)

#i = ROWS
#j = COLS

first_click = True
clickable = True


window = pygame.display.set_mode((WIDTH+1, HEIGHT+200))
window.fill(BG_COLOR)

bomb = pygame.image.load("img/bomb.png")
zero = pygame.image.load("img/0.png")
one = pygame.image.load("img/1.png")
two = pygame.image.load("img/2.png")
three = pygame.image.load("img/3.png")
four = pygame.image.load("img/4.png")
five = pygame.image.load("img/5.png")
six = pygame.image.load("img/6.png")
flaggy = pygame.image.load("img/flag.png")

font = pygame.font.SysFont(None, 40)
sans_font = pygame.font.SysFont("Comic Sans", 128)


pygame.draw.rect(window,"white",[1, HEIGHT+1, WIDTH-1, HEIGHT+199])

over_screen = pygame.Surface((WIDTH-1, HEIGHT-1), pygame.SRCALPHA)
def game_over():
        show_bombs()
        over_screen.fill((0, 0, 0, 164))
        window.blit(over_screen,(1,1))
        game = sans_font.render('Game', True, "black")
        over = sans_font.render('Over', True, "black")
        window.blit(game, ((WIDTH/2)-250, 150))
        window.blit(over, ((WIDTH/2), (HEIGHT/2)))
        global clickable
        clickable = False

def check_win():
        win = True
        for i in range(ROWS):
                for j in range(COLS):
                        if (i, j) in mines_placed:
                                continue
                        if revealed[i][j] == 1:
                                win = True
                        else:
                                win = False
                                break
                if win == False:
                        break
        return win

def new_game():
        global first_click, clickable
        first_click = True
        clickable = True
        global field, mine_field, revealed, mines_placed
        field = [[() for i in range(COLS)] for j in range(ROWS)] #pixel coordinates for each square
        mine_field = [[0 for i in range(COLS)] for j in range(ROWS)] # -1 for mines, 0 for empty, each number for each bomb nearby
        revealed = [[0 for i in range(COLS)] for j in range(ROWS)] # -1 for flag, 0 for not revealed, 1 for revealed
        mines_placed = [] #positions of bombs
        

        #initialize the field coords
        over_screen.fill((128, 128, 128, 0))
        for i in range(ROWS):
                for j in range(COLS):
                                pygame.draw.rect(window,BOX_COLOR,[BOX_SIZE[0]*i+1,BOX_SIZE[1]*j+1,BOX_SIZE[0]-1,BOX_SIZE[1]-1])
                                field[i][j] = (BOX_SIZE[0]*j+1,BOX_SIZE[1]*i+1)

        #place mines
        while len(mines_placed) < MINES:
                row = random.randrange(0, ROWS)
                col = random.randrange(0, COLS)
                pos = (col, row)

                if pos in mines_placed:
                        continue

                mines_placed.append(pos)
                # window.blit(bomb,field[i][j])

        #making list minefield
        for i in range(ROWS):
                for j in range(COLS):
                        neighbors = get_neighbors(i, j, ROWS, COLS)
                        count = 0
                        for cell in neighbors:
                                if cell in mines_placed:
                                        count += 1
                        mine_field[i][j] = count

        for i, j in mines_placed:
                #placing map on window and in 2d table
                mine_field[i][j] = -1

        #draw the field
        for i in field:
                for j in i:
                        pygame.draw.rect(window,BOX_COLOR,[j[0],j[1],BOX_SIZE[0]-1,BOX_SIZE[1]-1])
                        pass

def unstuck():
        global first_click, clickable, try_value, found
        tries = 0
        try_value = 0
        found = False      
        while clickable:
                if first_click:
                        break
                size = guess.qsize()
                time.sleep(0.2)
                if size == guess.qsize():
                        if tries == 3:
                                print("You're stuck")
                                guess_copy = []
                                for i in range(guess.qsize()):
                                        i, j = guess.get()
                                        guess_copy.append((i, j))
                                tries = 0
                                x = 0
                                while x < (len(guess_copy)):
                                        x += 1
                                        found = False
                                        if not clickable or first_click:
                                                break
                                        i, j = guess_copy[x]
                                        
                                        value = mine_field[i][j]
                                        if try_value == 9:
                                                if revealed[i][j] == 0:
                                                        print("Couldnt find more clues, clicking random tile")
                                                        mouse_click((field[i][j][0]+5,field[i][j][1]+5))
                                                        solve()
                                                        found = True
                                                        return()
                                        if revealed[i][j] == 0:
                                                continue
                                        if value == try_value and revealed[i][j] == 1:
                                                neighbors = get_neighbors(i, j, ROWS, COLS)
                                                for r, c in neighbors:
                                                        if revealed[r][c] == 0:
                                                                time.sleep(0.02)
                                                                print(f"Trying random {try_value}'s")
                                                                mouse_click((field[r][c][0]+5,field[r][c][1]+5))
                                                                solve()
                                                                found = True
                                                                return()

                                        if x == (len(guess_copy)-1):
                                                x = 0
                                                try_value += 1
                        tries += 1
                else:
                        tries = 0


def solve():
        global guess
        guess = Queue()
        for i in range(ROWS):
                for j in range(COLS):
                        guess.put((i, j))
        unstuck_bot = threading.Thread(target=unstuck, daemon=True)
        unstuck_bot.start()
        while not guess.empty():
                if not clickable or first_click:
                        break
                i, j = guess.get()
                if revealed[i][j]==-1:
                        continue
                if revealed[i][j]==0:
                        guess.put((i, j))
                        continue
                else:
                        value = mine_field[i][j]
                        if value == 0:
                                continue
                        neighbors = get_neighbors(i, j, ROWS, COLS)
                        hidden = 0
                        flagged = 0
                        global clicked
                        clicked = False
                        for r, c in neighbors:
                                if revealed[r][c] != 1:
                                        hidden += 1
                                if revealed[r][c] == -1:
                                        flagged += 1
                        if value == hidden:
                                for r,c in neighbors:
                                        if revealed[r][c] == 0:
                                                flag((field[r][c][0]+1,field[r][c][1]+1))
                                                continue
                        if value == flagged:
                                for r, c in neighbors:
                                        if revealed[r][c] == 0:
                                                mouse_click((field[r][c][0]+5,field[r][c][1]+5))
                                                guess.put((r, c))
                        else:
                                guess.put((i, j))
                                pass
                        time.sleep(0.02)
                        pygame.display.update()

        

def buttons(coords):
        x, y = coords
        if x > 20 and y > HEIGHT + 75 and x < 220 and y < HEIGHT + 125:
                new_game()
        if x > 240 and y > HEIGHT + 75 and x < 440 and y < HEIGHT + 125 and clickable:
                show_bombs()
        if x > 460 and y > HEIGHT + 75 and x < 660 and y < HEIGHT + 125 and clickable:
                solve()

def mouse_over(coords):
        x, y = coords
        if x > 20 and y > HEIGHT + 75 and x < 220 and y < HEIGHT + 125:
                pygame.draw.rect(window,"darkgreen",[20, HEIGHT+75, 200, 50])
                baton1 = font.render('New Game', True, "BLUE")
                window.blit(baton1, (50, HEIGHT+88))
        else:
                pygame.draw.rect(window,"green",[20, HEIGHT+75, 200, 50])
                baton1 = font.render('New Game', True, "BLUE")
                window.blit(baton1, (50, HEIGHT+88))
        if x > 240 and y > HEIGHT + 75 and x < 440 and y < HEIGHT + 125 and clickable:
                pygame.draw.rect(window,"darkgreen",[240, HEIGHT+75, 200, 50])
                baton2 = font.render('Show Bombs', True, "BLUE")
                window.blit(baton2, (250, HEIGHT+88))
        else:
                pygame.draw.rect(window,"green",[240, HEIGHT+75, 200, 50])
                baton2 = font.render('Show Bombs', True, "BLUE")
                window.blit(baton2, (250, HEIGHT+88))
        if x > 460 and y > HEIGHT + 75 and x < 660 and y < HEIGHT + 125 and clickable:
                pygame.draw.rect(window,"darkgreen",[460, HEIGHT+75, 200, 50])
                baton3 = font.render('Solve', True, "BLUE")
                window.blit(baton3, (525, HEIGHT+88))
        else:
                pygame.draw.rect(window,"green",[460, HEIGHT+75, 200, 50])
                baton3 = font.render('Solve', True, "BLUE")
                window.blit(baton3, (525, HEIGHT+88))

def mouse_click(coords):
        global clickable
        if clickable:
                y, x = get_pos(coords)
                if not revealed[y][x] == -1:
                        if mine_field[y][x]==-1:
                                game_over()
                        else:
                                revealed[y][x] = 1
                                reveal((y, x), mine_field)
                                uncover(y, x, mine_field)
        
        if check_win() and clickable:
                over_screen.fill((0, 0, 0, 164))
                window.blit(over_screen,(1,1))
                game = sans_font.render('You', True, "black")
                over = sans_font.render('Won', True, "black")
                window.blit(game, ((WIDTH/2)-250, 150))
                window.blit(over, ((WIDTH/2), (HEIGHT/2))) 
                clickable = False

        

def flag(coords):
        y, x = get_pos(coords)

        if revealed[y][x] == 0:
                window.blit(flaggy, field[y][x])
                revealed[y][x] = -1
        elif revealed[y][x] == -1:
                pygame.draw.rect(window,BOX_COLOR,[field[y][x][0],field[y][x][1],BOX_SIZE[0]-1,BOX_SIZE[1]-1])
                revealed[y][x] = 0
def get_pos(coords):
        global field
        for i in field:
                for j in i:
                        if coords[0] > j[0] and coords[1] > j[1]:
                                if coords[0] - BOX_SIZE[0] < j[0] and coords[1] - BOX_SIZE[1] < j[1]:
                                        x = i.index(j)
                                        y = field.index(i)
                                        return((y, x))
                                        
def show_bombs():
        for y, x in mines_placed:
                window.blit(bomb, field[y][x])


def reveal(pos, mine_field):
        y, x = pos

        
        if mine_field[y][x]==0:
                pygame.draw.rect(window,"white",[field[y][x][0],field[y][x][1],BOX_SIZE[0]-1,BOX_SIZE[1]-1])
        if mine_field[y][x]==1:
                window.blit(one, field[y][x])
        if mine_field[y][x]==2:
                window.blit(two, field[y][x])
        if mine_field[y][x]==3:
                window.blit(three, field[y][x])
        if mine_field[y][x]==4:
                window.blit(four, field[y][x])
        if mine_field[y][x]==5:
                window.blit(five, field[y][x])
        if mine_field[y][x]==6:
                window.blit(six, field[y][x])

def get_neighbors(row, col, rows, cols):
        neighbors = []

        if row > 0:
                neighbors.append((row - 1, col))
        if row < rows -1:
                neighbors.append((row + 1, col))
        if col > 0:
                neighbors.append((row, col - 1))
        if col < cols -1:
                neighbors.append((row, col + 1))

        if row > 0 and col > 0:
                neighbors.append((row - 1, col - 1))
        if row < rows -1 and col < cols -1:
                neighbors.append((row + 1, col + 1))
        if row < rows - 1 and col > 0:
                neighbors.append((row + 1, col - 1))
        if row > 0 and col < cols - 1:
                neighbors.append((row - 1, col + 1))
        return neighbors

def uncover(row, col, mine_field):
        q = Queue()
        q.put((row, col))
        visited = set()

        if first_click:
                while not q.empty():
                        current = q.get()

                        neighbors = get_neighbors(*current, ROWS, COLS)
                        
                        for r, c in neighbors:
                                if (r, c) in visited:
                                        continue
                                value = mine_field[r][c]
                                if value != -1:
                                        revealed[r][c] = 1
                                reveal((r, c), mine_field)
                                
                                if value == 0:
                                        q.put((r, c))
                                visited.add((r,c))
        else:
                if mine_field[row][col] == 0:
                        while not q.empty():
                                current = q.get()

                                neighbors = get_neighbors(*current, ROWS, COLS)
                                
                                for r, c in neighbors:
                                        if (r, c) in visited:
                                                continue
                                        value = mine_field[r][c]
                                        if value != -1:
                                                revealed[r][c] = 1
                                        reveal((r, c), mine_field)

                                        if value == 0:
                                                q.put((r, c))
                                        visited.add((r,c))


new_game()
pygame.display.update()
run = True

while run:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                        try:
                                if mouse[1] > HEIGHT:
                                        buttons(mouse)
                                else:
                                        if event.button == 1:
                                                mouse_click(mouse)
                                                if first_click:
                                                        first_click = False
                                        if event.button == 3:
                                                flag(mouse)
                        except TypeError:
                                print("Wrong mouse position")
                        

        
        mouse = pygame.mouse.get_pos()
        mouse_over(mouse)
        pygame.display.update()
        