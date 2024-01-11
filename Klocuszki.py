import pygame
import random

# Funkcje inicjalizujące i konfiguracyjne:
pygame.init()

# Stałe
GRID_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = 12, 23
SCREEN_WIDTH, SCREEN_HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE
PREVIEW_WIDTH, PREVIEW_HEIGHT = 8 * GRID_SIZE, 8 * GRID_SIZE
FPS = 60
MOVE_SPEED = 100  # Prędkość przesuwania w bok (ms)
FAST_FALL_SPEED = 50  # Przyspieszone opadanie

# Słownik prędkości opadania dla różnych poziomów (level: fall_speed)
LEVEL_SPEEDS = {
    1: 1000, 2: 700, 3: 600, 4: 500, 5: 400,
    6: 200, 7: 100, 8: 90, 9: 80, 10: 70
}

# Ustawienie początkowej prędkości opadania na prędkość pierwszego poziomu
FALL_SPEED = LEVEL_SPEEDS[1]

# Zmienne do śledzenia poziomu i usuniętych linii
current_level = 1
total_lines_cleared = 0

# Słowniki do śledzenia usunięć linii oraz najdłuższych combo
line_clears = {1: 0, 2: 0, 3: 0, 4: 0}
current_combo = {1: 0, 2: 0, 3: 0, 4: 0}
max_combo = {1: 0, 2: 0, 3: 0, 4: 0}
last_clear = None  # Zmienna do przechowywania informacji o ostatnim usunięciu

# Kolory
BLACK = (0, 0, 0)
WHITE = (245, 245, 245)
DARK_GREY = (30, 30, 30)  # Możesz dostosować te wartości do preferowanego koloru
COLORS = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 165, 0)]  # Zaktualizuj kolory klocków

# Definiowanie nowych kolorów zgodnie z obrazkiem
SCORE_COLOR = (255, 255, 0)  # żółty
LEVEL_COLOR = (0, 255, 0)    # zielony
COMBO_COLOR = (255, 165, 0)  # pomarańczowy
MAX_COMBO_COLOR = (255, 0, 0) # czerwony

# Ustawienia okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH + PREVIEW_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("KLOCUSZKI")

# Kształty Tetromino i ich kolory
TETROMINO_SHAPES = [
    ([[1, 1, 1, 1]], COLORS[0]),  # I
    ([[1, 1, 1], [0, 1, 0]], COLORS[1]),  # T
    ([[1, 1], [1, 1]], COLORS[2]),  # O
    ([[0, 1, 1], [1, 1, 0]], COLORS[3]),  # S
    ([[1, 1, 0], [0, 1, 1]], COLORS[4]),  # Z
    ([[1, 0, 0], [1, 1, 1]], COLORS[5]),  # J
    ([[0, 0, 1], [1, 1, 1]], COLORS[6])   # L
]

# Plansza
board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Zmienne dla punktacji
score = 0
score_per_line = [0, 100, 200, 300, 400]

# Funkcje rysujące:

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, DARK_GREY, rect, 1)

def draw_board():
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                color = COLORS[cell - 1]
                pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, BLACK, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_tetromino(tetromino, position, color):
    for y, row in enumerate(tetromino):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, (position[0] + x * GRID_SIZE, position[1] + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, BLACK, (position[0] + x * GRID_SIZE, position[1] + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_preview(tetromino, color):
    preview_x = SCREEN_WIDTH + (PREVIEW_WIDTH - len(tetromino[0]) * GRID_SIZE) // 2
    preview_y = 125  # Wysokość podpowiedzi klocka 
    draw_tetromino(tetromino, (preview_x, preview_y), color)

def rotate_tetromino(tetromino, position, direction=1):
    # Obrót tetromino
    if direction == 1:  # Obrót w prawo
        rotated = [list(row)[::-1] for row in zip(*tetromino)]
    else:  # Obrót w lewo
        rotated = [row for row in reversed(list(zip(*tetromino)))]

    # Sprawdź, czy obrócony klocek mieści się bez przesunięcia
    if valid_position(rotated, position):
        return rotated, position

    # Logika przesunięcia dla krawędzi
    for shift in range(4):
        shifted_position_left = (position[0] - shift * GRID_SIZE, position[1])
        shifted_position_right = (position[0] + shift * GRID_SIZE, position[1])
        if valid_position(rotated, shifted_position_left):
            return rotated, shifted_position_left
        elif valid_position(rotated, shifted_position_right):
            return rotated, shifted_position_right

    # Dodatkowa logika dla klocków przy prawej krawędzi
    if position[0] + len(rotated[0]) * GRID_SIZE > GRID_WIDTH * GRID_SIZE:
        # Oblicz, ile klocek wychodzi poza planszę
        overlap = position[0] + len(rotated[0]) * GRID_SIZE - GRID_WIDTH * GRID_SIZE

        # Przesuń klocek w lewo, aby przylegał do prawej krawędzi
        new_position = (position[0] - overlap, position[1])
        if valid_position(rotated, new_position):
            return rotated, new_position

    # Jeśli nie znaleziono ważnej pozycji, zwróć oryginalny klocek i pozycję
    return tetromino, position

def new_tetromino():
    return random.choice(TETROMINO_SHAPES)

def valid_position(tetromino, position):
    for y, row in enumerate(tetromino):
        for x, cell in enumerate(row):
            if cell:
                x_pos = position[0] // GRID_SIZE + x
                y_pos = position[1] // GRID_SIZE + y
                if x_pos < 0 or x_pos >= GRID_WIDTH or y_pos >= GRID_HEIGHT or (y_pos > 0 and board[y_pos][x_pos]):
                    return False
    return True

def place_tetromino(tetromino, position, color_index):
    for y, row in enumerate(tetromino):
        for x, cell in enumerate(row):
            if cell:
                board[position[1] // GRID_SIZE + y][position[0] // GRID_SIZE + x] = color_index

def clear_lines():
    global board, score, line_clears, current_combo, max_combo, last_clear, total_lines_cleared, current_level, fall_speed
    number_of_lines_cleared = 0

    new_board = [row for row in board if not all(row)]
    number_of_lines_cleared = len(board) - len(new_board)

    if number_of_lines_cleared > 0:
        line_clears[number_of_lines_cleared] += 1
        total_lines_cleared += number_of_lines_cleared  # Aktualizacja total_lines_cleared
        if last_clear == number_of_lines_cleared:
            # Zwiększ combo, jeśli ostatnie usunięcie było tej samej liczby linii
            current_combo[number_of_lines_cleared] += 1
        else:
            # Jeśli combo zostało przerwane inną liczbą linii, zresetuj tylko poprzednie combo
            if last_clear is not None:
                current_combo[last_clear] = 0
                if current_combo[last_clear] > max_combo[last_clear]:
                    max_combo[last_clear] = current_combo[last_clear]
            current_combo[number_of_lines_cleared] = 1
        last_clear = number_of_lines_cleared
    else:
        # Jeśli nie usunięto żadnych linii, nie resetuj combo
        pass  # Ten fragment jest teraz pusty, co oznacza brak akcji

        total_lines_cleared += number_of_lines_cleared

    # Zmiana poziomu, na przykład co 30 usuniętych linii
    if total_lines_cleared >= 30 * current_level:
        current_level += 1  # Zwiększenie poziomu
        fall_speed = LEVEL_SPEEDS.get(current_level, fall_speed)  # Aktualizacja prędkości opadania

        total_lines_cleared = 0  # Resetowanie licznika linii
        print(f"Total lines cleared: {total_lines_cleared}, Current level: {current_level}")  # Wydruk zmiany poziomu

    # Aktualizuj wynik
    score += score_per_line[number_of_lines_cleared] * current_combo.get(number_of_lines_cleared, 0)

    # Uaktualnienie planszy z nowymi pustymi liniami na górze
    board = [[0 for _ in range(GRID_WIDTH)] for _ in range(number_of_lines_cleared)] + new_board
    while len(board) < GRID_HEIGHT:
        board.insert(0, [0 for _ in range(GRID_WIDTH)])

    # Sprawdź, czy któreś z max_combo powinno zostać zaktualizowane
    for key, value in current_combo.items():
        if value > max_combo[key]:
            max_combo[key] = value
print(f"Total lines cleared: {total_lines_cleared}, Current level: {current_level}")

def draw_controls():
    font = pygame.font.Font(None, 24)
    controls_text = [
        "STRZAŁKI - RÓCH POZIOMY",
        "A i D - OBRÓT",
        "STRZAŁKA DÓŁ - SZYBKI OPAD",
        "R - RESET GRY",
        "P lub SPACJA - PAUZA GRY"
    ]

    # Ustawienia początkowej pozycji dla tekstu instrukcji
    start_y = 675  # Możesz dostosować tę wartość, aby pasowała do układu swojego interfejsu
    for text in controls_text:
        text_surface = font.render(text, True, (255, 255, 255))  # Biały kolor tekstu
        screen.blit(text_surface, (SCREEN_WIDTH + 20, start_y))  # Dostosuj współrzędną x zgodnie z potrzebą
        start_y += text_surface.get_height() + 8  # Odstęp między liniami

def draw_line_clear_stats():
    font = pygame.font.Font(None, 36)
    stats_y = 235  # Wysokość tekstu pod sugerowanym klockiem
    line_spacing = 5  # Odstęp między liniami w grupie
    group_spacing = 20  # Większy odstęp między grupami

    # Zdefiniuj kolory dla różnych linii statystyk
    SCORE_COLOR = (255, 255, 0)  # żółty
    LEVEL_COLOR = (0, 255, 0)    # zielony
    COMBO_COLOR = (255, 165, 0)  # pomarańczowy
    MAX_COMBO_COLOR = (255, 0, 0) # czerwony

    # Grupy wersów
    lines_stats = [
        (f"1 Line(s): {line_clears[1]}", LEVEL_COLOR),
        (f"2 Line(s): {line_clears[2]}", LEVEL_COLOR),
        (f"3 Line(s): {line_clears[3]}", LEVEL_COLOR),
        (f"4 Line(s): {line_clears[4]}", LEVEL_COLOR),
    ]

    combos_stats = [
        (f"1 Line Combo: {current_combo[1]}", COMBO_COLOR),
        (f"2 Line Combo: {current_combo[2]}", COMBO_COLOR),
        (f"3 Line Combo: {current_combo[3]}", COMBO_COLOR),
        (f"4 Line Combo: {current_combo[4]}", COMBO_COLOR),
    ]

    max_combos_stats = [
        (f"1 Line Max Combo: {max_combo[1]}", MAX_COMBO_COLOR),
        (f"2 Line Max Combo: {max_combo[2]}", MAX_COMBO_COLOR),
        (f"3 Line Max Combo: {max_combo[3]}", MAX_COMBO_COLOR),
        (f"4 Line Max Combo: {max_combo[4]}", MAX_COMBO_COLOR),
    ]

    # Obliczanie szerokości tekstu dla wyśrodkowania
    max_text_width = max(font.render(line[0], True, WHITE).get_width() for line in lines_stats + combos_stats + max_combos_stats)
    stats_x = SCREEN_WIDTH + (PREVIEW_WIDTH - max_text_width) // 2

    # Rysowanie linii statystyk
    def draw_stats_lines(stats, y_start):
        for line, color in stats:
            text_surface = font.render(line, True, color)
            centered_x = stats_x + (max_text_width - text_surface.get_width()) // 2
            screen.blit(text_surface, (centered_x, y_start))
            y_start += text_surface.get_height() + line_spacing
        return y_start

    # Rysuj każdą grupę statystyk
    stats_y = draw_stats_lines(lines_stats, stats_y)
    stats_y += group_spacing  # Dodajemy dodatkowy odstęp między grupami
    stats_y = draw_stats_lines(combos_stats, stats_y)
    stats_y += group_spacing
    draw_stats_lines(max_combos_stats, stats_y)

# Następnie wywołaj tę funkcję w głównej pętli gry.

def draw_score():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, SCORE_COLOR)
    # Możesz dostosować wartość y, aby przesunąć tekst wyżej na ekranie
    screen.blit(text, (SCREEN_WIDTH + 20, 30))  # x pozostaje bez zmian, y jest teraz bliżej górnej krawędzi ekranu

# Funkcje zakończenia gry:
    
def game_over():
    font = pygame.font.Font(None, 72)
    text = font.render("Game Over", True, MAX_COMBO_COLOR)    
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

    font_small = pygame.font.Font(None, 36)
    restart_text = font_small.render("Press 'R' to Restart, 'Q' to Quit", True, LEVEL_COLOR)
    restart_text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_text_rect)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Zakończenie gry
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    return True  # Restart gry
                if event.key == pygame.K_q:
                    return False  # Zakończenie gry

# Resetowanie gry

def reset_game():
    global board, score, line_clears, current_combo, max_combo, last_clear
    global current_tetromino, current_color, next_tetromino, next_color
    global position_x, position_y, fall_speed, move_left_time, move_right_time

    # Inicjalizacja position_x i position_y
    position_x, position_y = SCREEN_WIDTH // 2 - GRID_SIZE, 0
    
    # Resetowanie planszy
    board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    # Resetowanie punktacji i statystyk
    score = 0
    line_clears = {1: 0, 2: 0, 3: 0, 4: 0}
    current_combo = {1: 0, 2: 0, 3: 0, 4: 0}
    max_combo = {1: 0, 2: 0, 3: 0, 4: 0}
    last_clear = None

    # Resetowanie klocków
    current_tetromino, current_color = new_tetromino()
    next_tetromino, next_color = new_tetromino()

    # Resetowanie pozycji i prędkości
    position_x, position_y = SCREEN_WIDTH // 2 - GRID_SIZE, 0
    fall_speed = FALL_SPEED
    move_left_time = 0
    move_right_time = 0

def draw_level():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Level: {current_level}", True, LEVEL_COLOR)
    # Ustaw tekst "Level" tuż pod tekstem "Score"
    screen.blit(text, (SCREEN_WIDTH + 20, 70))  # Dostosuj współrzędną y zgodnie z potrzebą

# Główna pętla gry:
    
def main():
    global score, current_tetromino, current_color, next_tetromino, next_color
    global current_level, position_x, position_y, left_pressed, right_pressed
    global rotate_direction, fall_speed
    reset_game()

    is_paused = False
    is_fast_falling = False
    clock = pygame.time.Clock()
    running = True
    last_fall_time = pygame.time.get_ticks()
    move_left_time = 0
    move_right_time = 0
    rotate_direction = 0

    left_pressed = False
    right_pressed = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                elif event.key == pygame.K_r:
                    reset_game()  # Resetowanie gry
                    current_tetromino, current_color = new_tetromino()
                    next_tetromino, next_color = new_tetromino()
                    position_x, position_y = SCREEN_WIDTH // 2 - GRID_SIZE, 0
                elif event.key == pygame.K_LEFT:
                    left_pressed = True
                elif event.key == pygame.K_RIGHT:
                    right_pressed = True
                elif event.key == pygame.K_DOWN:
                    is_fast_falling = True
                elif event.key == ord('d'):
                    rotate_direction = 1  # Obrót w prawo
                elif event.key == ord('a'):
                    rotate_direction = -1  # Obrót w lewo
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    is_fast_falling = False
                if event.key == pygame.K_LEFT:
                    left_pressed = False
                if event.key == pygame.K_RIGHT:
                    right_pressed = False
                if event.key in [pygame.K_UP, ord('a'), ord('d')]:
                    rotate_direction = 0

        current_time = pygame.time.get_ticks()

        if not is_paused:
            fall_speed = FAST_FALL_SPEED if is_fast_falling else LEVEL_SPEEDS[current_level]
            if current_time - last_fall_time > fall_speed:
                new_position_y = position_y + GRID_SIZE
                if valid_position(current_tetromino, (position_x, new_position_y)):
                    position_y = new_position_y
                    last_fall_time = current_time
                else:
                    place_tetromino(current_tetromino, (position_x, position_y), COLORS.index(current_color) + 1)
                    clear_lines()
                    current_tetromino, current_color = next_tetromino, next_color
                    next_tetromino, next_color = new_tetromino()
                    position_x, position_y = SCREEN_WIDTH // 2 - GRID_SIZE, 0

                    if not valid_position(current_tetromino, (position_x, position_y)):
                        running = game_over()  # Restart gry lub wyjście
                        if running:
                            reset_game()
                            current_tetromino, current_color = new_tetromino()
                            next_tetromino, next_color = new_tetromino()
                            position_x, position_y = SCREEN_WIDTH // 2 - GRID_SIZE, 0
                        continue

            if rotate_direction != 0:
                rotated_tetromino, new_position = rotate_tetromino(current_tetromino, (position_x, position_y), rotate_direction)
                if valid_position(rotated_tetromino, new_position):
                    current_tetromino = rotated_tetromino
                    position_x, position_y = new_position
                rotate_direction = 0

            if left_pressed:
                if current_time - move_left_time > MOVE_SPEED:
                    new_position_x = position_x - GRID_SIZE
                    if valid_position(current_tetromino, (new_position_x, position_y)):
                        position_x = new_position_x
                        move_left_time = current_time

            if right_pressed:
                if current_time - move_right_time > MOVE_SPEED:
                    new_position_x = position_x + GRID_SIZE
                    if valid_position(current_tetromino, (new_position_x, position_y)):
                        position_x = new_position_x
                        move_right_time = current_time

        screen.fill(BLACK)  # Wypełnienie ekranu kolorem
        draw_grid()
        draw_board()
        draw_tetromino(current_tetromino, (position_x, position_y), current_color)
        draw_preview(next_tetromino, next_color)
        draw_score()  # Rysowanie wyniku
        draw_level()  # Rysowanie poziomu
        draw_controls() # Wywołanie opisu
        draw_line_clear_stats()  # Rysowanie statystyk
        pygame.display.update()  # Aktualizacja wyświetlanego obrazu
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()