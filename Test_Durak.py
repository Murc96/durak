import unittest
from Durak import Player
from Durak import Deck


class TestPlayer(unittest.TestCase):
    def setUp(self):
        deck = Deck()
        self.player1 = Player(deck, "Player 1", (0, 0))
        self.player2 = Player(deck, "Player 2", (0, 0))

    def test_deal_hand(self):
        self.player1.deal_hand(6)
        self.player2.deal_hand(6)
        self.assertEqual(len(self.player1._hand), 6)
        self.assertEqual(len(self.player2._hand), 6)

    def test_player_name(self):
        self.assertEqual(self.player1.name, "Player 1")
        self.assertEqual(self.player2.name, "Player 2")
        self.assertEqual(self.player1.name, "Player 2")

    def test_loaded_data(self):
        with open("save_data.txt", "r") as file:
            lines = file.readlines()

            cards_line = next(
                (line for line in lines if "cards = " in line), None)
            self.assertIsNone(cards_line)

            trump_card_taken_line = next(
                (line for line in lines if "trump card taken = " in line), None)
            self.assertIsNone(trump_card_taken_line)

            trump_card_line = next(
                (line for line in lines if "trump card = " in line), None)
            self.assertIsNone(trump_card_line)

            defender_line = next(
                (line for line in lines if "defender = " in line), None)
            self.assertIsNone(defender_line)

            player1_visible_line = next(
                (line for line in lines if "player1_visible = " in line), None)
            self.assertIsNone(player1_visible_line)

            attacker_cards_played_line = next(
                (line for line in lines if "Attacker cards played = " in line), None)
            self.assertIsNone(attacker_cards_played_line)

            defender_cards_played_line = next(
                (line for line in lines if "Defender cards played = " in line), None)
            self.assertIsNone(defender_cards_played_line)

            player1_hand_line = next(
                (line for line in lines if "Player 1 hand = " in line), None)
            self.assertIsNone(player1_hand_line)

            player2_hand_line = next(
                (line for line in lines if "Player 2 hand = " in line), None)
            self.assertIsNone(player2_hand_line)


if __name__ == '__main__':
    unittest.main()
