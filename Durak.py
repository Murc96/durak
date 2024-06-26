import pygame
import random
from abc import ABC, abstractmethod
import logging
import os

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_size_x, screen_size_y = screen.get_size()
pygame.display.set_caption("Durak")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Constants
CARD_WIDTH = 100
CARD_HEIGHT = 150
STACK_GAP = 20
MAX_CARDS_IN_ROW = 8
BACKGROUND_IMAGE_PATH = os.path.join("images", "green-casino-poker-table-texture-game-background-free-vector.jpg")
BACK_OF_CARD_IMAGE_PATH = os.path.join("images", "back of the card.jpg")
SAVE_FILE_PATH = os.path.join("save", "save_data.txt")

# Utility Functions
def log_func_call(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Calling function {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Function {func.__name__} returned {result}")
        return result
    return wrapper

def is_defender(player):
    return player is defender

def check_win(deck):
    if len(deck.cards) == 0:
        for player in players:
            if player.num_cards_in_hand == 0:
                if players[1 - players.index(player)].num_cards_in_hand == 0:
                    print("Tie!")
                else:
                    print(f"{player.name} wins!")
                return True
    return False

def is_enabled(button):
    not_all_cards_defended = any(defender_card is None for defender_card in cards_to_display.values())
    for player in players:
        if player.is_visible():
            if is_defender(player):
                return button == "end_round_button" if not_all_cards_defended else button == "next_button"
            else:
                return button == "next_button" if not_all_cards_defended else button == "end_round_button"
    return False

def save_data(deck, player1, player2):
    with open(SAVE_FILE_PATH, "w") as file:
        cards_str = ", ".join(f"Card('{card.rank}', '{card.suit}')" for card in deck.cards) if deck.cards else "None"
        file.write(f"cards = [{cards_str}]\n")
        file.write(f"trump card = Card('{deck.trump_card.rank}', '{deck.trump_card.suit}')\n")
        file.write(f"trump card taken = {deck.trump_card_taken}\n")
        file.write(f"defender = {defender.name}\n")
        file.write(f"player1_visible = {player1.is_visible()}\n")
        
        attacker_cards_played_str = ", ".join(f"Card('{card.rank}', '{card.suit}')" for card in cards_to_display.keys()) if cards_to_display else "None"
        file.write(f"Attacker cards played = [{attacker_cards_played_str}]\n")
        
        defender_cards_played_str = ", ".join(f"Card('{card.rank}', '{card.suit}')" if card else "None" for card in cards_to_display.values()) if cards_to_display else "None"
        file.write(f"Defender cards played = [{defender_cards_played_str}]\n")
        
        player1_hand_str = ", ".join(f"Card('{card.rank}', '{card.suit}')" for card in player1._hand) if player1._hand else "None"
        file.write(f"Player 1 hand = [{player1_hand_str}]\n")
        
        player2_hand_str = ", ".join(f"Card('{card.rank}', '{card.suit}')" for card in player2._hand) if player2._hand else "None"
        file.write(f"Player 2 hand = [{player2_hand_str}]\n")
    
    print("Data saved")

def load_data(deck, player1, player2):
    with open(SAVE_FILE_PATH, "r") as file:
        lines = file.readlines()
    
    def extract_cards(line):
        return eval(line.replace("cards = [", "").replace("Attacker cards played = [", "").replace("Defender cards played = [", "").rstrip("]\n"))
    
    deck.cards = extract_cards(next(line for line in lines if "cards = " in line))
    deck.trump_card_taken = eval(next(line for line in lines if "trump card taken = " in line).replace("trump card taken = ", ""))
    deck.trump_card = eval(next(line for line in lines if "trump card = " in line).replace("trump card = ", "").rstrip("\n"))
    defender_line = next(line for line in lines if "defender = " in line).replace("defender = ", "").strip()
    global defender
    defender = player1 if defender_line == "player1" else player2
    
    player1._visible = eval(next(line for line in lines if "player1_visible = " in line).replace("player1_visible = ", ""))
    player2._visible = not player1._visible
    
    cards_to_display.clear()
    attacker_cards = extract_cards(next(line for line in lines if "Attacker cards played = " in line))
    defender_cards = extract_cards(next(line for line in lines if "Defender cards played = " in line))
    cards_to_display.update(dict(zip(attacker_cards, defender_cards)))
    
    player1._hand = extract_cards(next(line for line in lines if "Player 1 hand = " in line))
    player1.num_cards_in_hand = len(player1._hand)
    
    player2._hand = extract_cards(next(line for line in lines if "Player 2 hand = " in line))
    player2.num_cards_in_hand = len(player2._hand)

    player1.num_cards_played = sum(1 for card in cards_to_display.values() if card) if is_defender(player1) else sum(1 for card in cards_to_display.keys())

# Card and Deck Classes
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.rank_values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
                            "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        self.suit = suit
        self.image = pygame.transform.scale(pygame.image.load(
            os.path.join("images", f"{self.rank}_of_{self.suit}.png")).convert_alpha(), (CARD_WIDTH, CARD_HEIGHT))
        self.rect = self.image.get_rect()

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def draw(self, pos=None):
        if pos:
            screen.blit(self.image, pos)
        else:
            pos = self.rect.topleft
            screen.blit(self.image, pos)

    def set_top_left(self, pos):
        self.rect.topleft = pos

    def __gt__(self, other):
        return self.rank_values[self.rank] > self.rank_values[other.rank]

class TrumpCard(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit)

    def draw(self, pos=None):
        pass

class Cards:
    def __init__(self):
        self.rank = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
                     "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        self.suit = ("spades", "diamonds", "clubs", "hearts")
        self.cards = []

    def create_cards(self):
        for rank in self.rank:
            for suit in self.suit:
                self.cards.append(Card(rank, suit))
        return self.cards

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Deck(Cards, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__()
        self.create_cards()
        self.shuffle_deck()
        self.trump_card = self.get_trump_card()
        self.trump_card_taken = False

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def deal_cards(self, num_cards, hand):
        hand.extend(self.cards[:num_cards])
        if num_cards > len(self.cards) and not self.trump_card_taken:
            hand.append(self.trump_card)
            self.trump_card_taken = True
        self.cards = self.cards[num_cards:]
        return hand

    def get_trump_card(self):
        if self.cards:
            trump_card = self.cards.pop(0)
            trump_card.image = pygame.transform.scale(pygame.image.load(
                os.path.join("images", f"{trump_card.rank}_of_{trump_card.suit}.png")), (CARD_WIDTH, CARD_HEIGHT))
            return trump_card
        else:
            return None

# Player Classes
class AbstractPlayer(ABC):
    def __init__(self, deck):
        self.deck = deck
        self._hand = []
        self._visible = False
        self._dragging = False
        self._dragged_card = None
        self._original_index = None

    @abstractmethod
    def deal_hand(self, num_cards):
        pass

    def toggle_visibility(self):
        self._visible = not self._visible

    def is_visible(self):
        return self._visible

    def draw_hand(self, screen, offset, y_position):
        for i, card in enumerate(self._hand):
            card.set_top_left((i % MAX_CARDS_IN_ROW * (CARD_WIDTH + STACK_GAP) + offset, y_position + i // MAX_CARDS_IN_ROW * 35))
            card.draw()

    @abstractmethod
    def event_handler(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw_dragged_card(self):
        pass

class Player(AbstractPlayer):
    def __init__(self, deck, name, hand_position):
        super().__init__(deck)
        self.name = name
        self.hand_position = hand_position
        self.num_cards_played = 0
        self.num_cards_in_hand = 0
        global players
        players.append(self)

    card_to_defend = None

    def deal_hand(self, num_cards):
        self._hand = self.deck.deal_cards(num_cards, self._hand)
        self.num_cards_in_hand = len(self._hand)

    def event_handler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for card in self._hand:
                if card.rect.collidepoint(mouse_pos):
                    if not self._dragging:
                        self._dragging = True
                        self._dragged_card = card
                        self._original_index = self._hand.index(card)
                    break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                self._dragging = False
                if not is_defender(self):
                    self.handle_attack()
                else:
                    self.handle_defense()

    def handle_attack(self):
        global cards_to_display
        if self.num_cards_played == 0 or any(
                attacker_card.rank == self._dragged_card.rank for attacker_card in cards_to_display.keys()):
            card = self._hand.pop(self._original_index)
            cards_to_display[card] = None
            self.num_cards_played += 1
        self._dragged_card = None
        self._original_index = None

    def handle_defense(self):
        global cards_to_display
        opponent = players[1 - players.index(self)]
        self.card_to_defend = self.check_boundaries(opponent)
        if self.card_to_defend and cards_to_display[self.card_to_defend] is None and self.is_valid_move(self.deck, self._dragged_card):
            self._hand.pop(self._original_index)
            cards_to_display[self.card_to_defend] = self._dragged_card
            self.num_cards_played += 1
        self._dragged_card = None
        self._original_index = None

    def update(self):
        if self._dragging:
            mouse_pos = pygame.mouse.get_pos()
            self._dragged_card.rect.center = mouse_pos

    def draw_dragged_card(self):
        if self._dragging and self._dragged_card:
            self._dragged_card.draw()

    def draw_cards_to_display(self, screen, is_defender, opponent):
        if not is_defender:
            self.draw_attackers_played_cards(screen, self)
        else:
            self.draw_attackers_played_cards(screen, opponent)
        self.draw_defenders_played_cards()

    def draw_attackers_played_cards(self, screen, attacker):
        initial_x = screen.get_width() // 2 - ((attacker.num_cards_played - 1) * (CARD_WIDTH + STACK_GAP) // 2)
        initial_y = screen.get_height() // 2

        for i, card in enumerate(cards_to_display):
            card.rect.centerx = initial_x + i * (CARD_WIDTH + STACK_GAP)
            card.rect.centery = initial_y
            card.draw()

    def draw_defenders_played_cards(self):
        defender_card_offset_y = 40
        defender_cards_to_display = {k: v for k, v in cards_to_display.items() if v is not None}
        for attacker_card, defender_card in defender_cards_to_display.items():
            defender_card.rect.centerx = attacker_card.rect.centerx
            defender_card.rect.centery = attacker_card.rect.centery + defender_card_offset_y
            defender_card.draw()

    def check_boundaries(self, player):
        mouse_pos = pygame.mouse.get_pos()
        initial_x = screen.get_width() // 2 - ((player.num_cards_played - 1) * (CARD_WIDTH + STACK_GAP) // 2)
        initial_y = screen.get_height() // 2

        for i, card in enumerate(cards_to_display):
            if initial_x + i * (CARD_WIDTH + STACK_GAP) - CARD_WIDTH // 2 <= mouse_pos[0] <= initial_x + i * (CARD_WIDTH + STACK_GAP) + CARD_WIDTH // 2 and initial_y - CARD_HEIGHT // 2 <= mouse_pos[1] <= initial_y + CARD_HEIGHT // 2:
                return card
        return None

    @log_func_call
    def is_valid_move(self, deck, defender_card):
        attacker_card = self.card_to_defend
        if defender_card.suit == attacker_card.suit and defender_card > attacker_card:
            return True
        elif defender_card.suit == deck.trump_card.suit and attacker_card.suit != deck.trump_card.suit:
            return True
        return False

def main():
    # Set up images
    background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
    background_image = pygame.transform.scale(background_image, (screen_size_x, screen_size_y))
    back_of_card = pygame.image.load(BACK_OF_CARD_IMAGE_PATH)
    back_of_card = pygame.transform.scale(back_of_card, (CARD_WIDTH, CARD_HEIGHT))
    font = pygame.font.SysFont(None, 32)

    # Create buttons
    quit_button_rect = pygame.Rect((screen_size_x - 120, 20, 100, 40))
    quit_text = font.render("Quit", True, (255, 255, 255))
    next_button_rect = pygame.Rect((screen_size_x - 160, screen_size_y / 2 - 20, 140, 40))
    next_button_text = font.render("Next turn", True, (255, 255, 255))
    end_round_button_rect = pygame.Rect((screen_size_x - 160, screen_size_y / 2 + 30, 140, 40))
    end_round_button_text = font.render("End round", True, (255, 255, 255))

    global defender, players, cards_to_display
    players = []
    cards_to_display = {}

    # Create deck and players
    deck = Deck()
    player1 = Player(deck, "player1", (400, screen_size_y - 250))
    player1.toggle_visibility()
    player2 = Player(deck, "player2", (400, 100))
    defender = player2

    player1.deal_hand(6)
    player2.deal_hand(6)

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_data(deck, player1, player2)
                if event.key == pygame.K_l:
                    load_data(deck, player1, player2)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if quit_button_rect.collidepoint(event.pos):
                        run = False
                    elif next_button_rect.collidepoint(event.pos) and is_enabled("next_button"):
                        player1.toggle_visibility()
                        player2.toggle_visibility()
                    elif end_round_button_rect.collidepoint(event.pos) and is_enabled("end_round_button"):
                        handle_end_round(deck, player1, player2)

            player1.event_handler(event)
            player2.event_handler(event)

        # Draw screen
        screen.blit(background_image, (0, 0))
        if len(deck.cards) > 0:
            screen.blit(back_of_card, (50, 325))
            back_of_card_text = font.render(str(len(deck.cards)), True, (255, 255, 255))
            screen.blit(back_of_card_text, (85, 295))
            deck.trump_card.draw((180, 325))
        elif len(deck.cards) == 0 and not deck.trump_card_taken:
            deck.trump_card.draw((50, 325))

        pygame.draw.rect(screen, (255, 0, 0), quit_button_rect)
        screen.blit(quit_text, (screen_size_x - 110, 30))

        for player in players:
            if player.is_visible():
                opponent = players[1 - players.index(player)]
                if is_defender(player):
                    if is_enabled("end_round_button"):
                        end_round_button_text = font.render("Take cards", True, (255, 255, 255))
                        pygame.draw.rect(screen, (0, 0, 255), end_round_button_rect)
                        screen.blit(end_round_button_text, (screen_size_x - 150, screen_size_y / 2 + 40))
                    else:
                        pygame.draw.rect(screen, (0, 255, 0), next_button_rect)
                        screen.blit(next_button_text, (screen_size_x - 150, screen_size_y / 2 - 10))
                else:
                    if is_enabled("next_button"):
                        pygame.draw.rect(screen, (0, 255, 0), next_button_rect)
                        screen.blit(next_button_text, (screen_size_x - 150, screen_size_y / 2 - 10))
                    elif is_enabled("end_round_button"):
                        end_round_button_text = font.render("End round", True, (255, 255, 255))
                        pygame.draw.rect(screen, (0, 0, 255), end_round_button_rect)
                        screen.blit(end_round_button_text, (screen_size_x - 150, screen_size_y / 2 + 40))

                player.draw_hand(screen, player.hand_position[0], player.hand_position[1])
                player.draw_cards_to_display(screen, is_defender(player), opponent)
                player.update()
                player.draw_dragged_card()

        pygame.display.update()

    pygame.quit()

def handle_end_round(deck, player1, player2):
    global defender, cards_to_display
    player1.num_cards_in_hand = len(player1._hand)
    player2.num_cards_in_hand = len(player2._hand)
    button_clicked_by = next(player for player in players if player.is_visible())

    if not is_defender(button_clicked_by):
        undefended_cards = [card for card in cards_to_display.keys() if cards_to_display[card] is None]
        if not undefended_cards:
            defender = players[1 - players.index(defender)]
            player1.toggle_visibility()
            player2.toggle_visibility()
            cards_to_display.clear()
            player1.num_cards_played = 0
            player2.num_cards_played = 0
            if not check_win(deck):
                deal_additional_cards(player1, player2)
    else:
        undefended_cards = [card for card in cards_to_display.keys() if cards_to_display[card] is None]
        if undefended_cards:
            defender._hand.extend(undefended_cards + [card for card in cards_to_display.values() if card])
            defender.num_cards_in_hand = len(defender._hand)
            player1.toggle_visibility()
            player2.toggle_visibility()
            cards_to_display.clear()
            player1.num_cards_played = 0
            player2.num_cards_played = 0
            if not check_win(deck):
                deal_additional_cards(player1, player2)

def deal_additional_cards(player1, player2):
    if player1.num_cards_in_hand < 6:
        player1.deal_hand(6 - player1.num_cards_in_hand)
        player1.num_cards_in_hand = len(player1._hand)
    if player2.num_cards_in_hand < 6:
        player2.deal_hand(6 - player2.num_cards_in_hand)
        player2.num_cards_in_hand = len(player2._hand)

if __name__ == "__main__":
    main()

