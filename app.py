import sys
import math
import pydealer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QWidget
from PySide6.QtGui import QPixmap


def get_card_image_path(card, image_folder="./cards"):
    """Map PyDealer card to image path."""
    rank = card.value.lower().replace(" ", "_")
    suit = card.suit.lower().replace(" ", "_")
    return f"{image_folder}/{rank}_of_{suit}.png"


class BlackjackGame:
    def __init__(self, num_decks=1, num_players=1):
        self.num_decks = num_decks
        self.num_players = num_players
        self.deck = pydealer.Stack()

        for _ in range(num_decks):
            new_deck = pydealer.Deck()
            self.deck.add(new_deck.cards)

        self.deck.shuffle()

        self.player_hands = [pydealer.Stack() for _ in range(num_players)]
        self.dealer_hand = pydealer.Stack()

    def deal_initial_hands(self):
        """Deal initial cards to players and dealer."""
        for player_hand in self.player_hands:
            player_hand.add(self.deck.deal(2))
        self.dealer_hand.add(self.deck.deal(2))

    def hit(self, hand):
        """Add a card to a hand."""
        new_card = self.deck.deal(1)
        hand.add(new_card)

    def calculate_hand_value(self, hand):
        """Calculate value of a hand."""
        value = 0
        aces = 0
        for card in hand:
            if card.value.isdigit():
                value += int(card.value)
            elif card.value in ["Jack", "Queen", "King"]:
                value += 10
            elif card.value == "Ace":
                value += 11
                aces += 1
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_bust(self, hand):
        """Check if a hand has busted."""
        return self.calculate_hand_value(hand) > 21

    def dealer_should_hit(self):
        """Check if dealer should hit."""
        return self.calculate_hand_value(self.dealer_hand) < 17


class BlackjackWindow(QMainWindow):
    def __init__(self, num_players=1):
        super().__init__()
        self.setWindowTitle("Blackjack")
        self.setGeometry(100, 100, 1200, 800)

        self.num_players = num_players
        self.current_player_index = 0
        self.show_dealer_cards = False

        self.game = BlackjackGame(num_decks=2, num_players=num_players)

        # Set up the central widget and background color
        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet("QWidget { background-color: #228B22; }")  # Poker table green
        self.setCentralWidget(self.central_widget)

        # Dealer Label
        self.dealer_label = QLabel("Dealer", self.central_widget)
        self.dealer_label.setAlignment(Qt.AlignCenter)
        self.dealer_label.setGeometry(self.width() // 2 - 50, 50, 100, 30)

        # Current Player Label
        self.current_player_label = QLabel(self.central_widget)
        self.current_player_label.setAlignment(Qt.AlignCenter)
        self.current_player_label.setGeometry(self.width() // 2 - 150, 300, 300, 50)
        self.current_player_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")

        self.dealer_cards = []
        self.player_labels = []
        self.player_cards = [[] for _ in range(self.num_players)]

        for i in range(self.num_players):
            label = QLabel(f"Player {i + 1}", self.central_widget)
            label.setAlignment(Qt.AlignCenter)
            self.player_labels.append(label)

        # Buttons
        self.hit_button = QPushButton("Hit", self.central_widget)
        self.stand_button = QPushButton("Stand", self.central_widget)
        self.reset_button = QPushButton("Reset", self.central_widget)

        self.hit_button.clicked.connect(self.hit)
        self.stand_button.clicked.connect(self.stand)
        self.reset_button.clicked.connect(self.reset_game)

        # Position buttons
        self.hit_button.setGeometry(450, 700, 100, 40)
        self.stand_button.setGeometry(600, 700, 100, 40)
        self.reset_button.setGeometry(750, 700, 100, 40)

        # Reset button styles to default
        self.hit_button.setStyleSheet("QPushButton { background-color: #d6d6d6; border: 1px solid black; }")
        self.stand_button.setStyleSheet("QPushButton { background-color: #d6d6d6; border: 1px solid black; }")
        self.reset_button.setStyleSheet("QPushButton { background-color: #d6d6d6; border: 1px solid black; }")


        self.reset_game()


    def reset_game(self):
        """Reset the game to start a new round."""
        self.game = BlackjackGame(num_decks=2, num_players=self.num_players)
        self.game.deal_initial_hands()
        self.current_player_index = 0
        self.show_dealer_cards = False
        self.update_ui()

        # Check for Blackjack in initial hands
        for i, hand in enumerate(self.game.player_hands):
            if self.game.calculate_hand_value(hand) == 21:
                QMessageBox.information(self, "Blackjack!", f"Player {i + 1} got a Blackjack!")
                if i == self.current_player_index:  # If it's the current player's turn, skip it
                    self.next_player()

    def update_ui(self):
        """Update the GUI to reflect the current state of the game."""
        # Update the Current Player Label
        self.current_player_label.setText(f"Current Player: Player {self.current_player_index + 1}")

        # Clear existing dealer cards
        for card_label in self.dealer_cards:
            card_label.deleteLater()
        self.dealer_cards.clear()

        # Add dealer's cards
        center_x = self.width() // 2
        center_y = 100
        for j, card in enumerate(self.game.dealer_hand):
            card_image = QLabel(self.central_widget)
            if not self.show_dealer_cards and j == 1:
                card_image.setPixmap(QPixmap("./cards/back.png"))  # Back of the card
            else:
                card_image.setPixmap(QPixmap(get_card_image_path(card)))
            card_image.setFixedSize(100, 150)
            card_image.setScaledContents(True)
            card_image.setGeometry(center_x - 60 + j * 30, center_y, 100, 150)
            self.dealer_cards.append(card_image)
            card_image.show()

        # Layout players in a semi-circle
        radius = 400
        angle_increment = math.pi / (len(self.player_cards) + 1)
        for i, hand in enumerate(reversed(self.game.player_hands)):  # Reverse player order
            angle = angle_increment * (i + 1)
            player_x = center_x + int(radius * math.cos(angle))
            player_y = center_y + int(radius * math.sin(angle))

            self.player_labels[len(self.player_labels) - 1 - i].setGeometry(
                player_x - 50, player_y + 120, 100, 30
            )
            self.player_labels[len(self.player_labels) - 1 - i].show()

            for card_label in self.player_cards[len(self.player_cards) - 1 - i]:
                card_label.deleteLater()
            self.player_cards[len(self.player_cards) - 1 - i].clear()

            for j, card in enumerate(hand):
                card_image = QLabel(self.central_widget)
                card_image.setPixmap(QPixmap(get_card_image_path(card)))
                card_image.setFixedSize(100, 150)
                card_image.setScaledContents(True)
                card_image.setGeometry(player_x - 60 + j * 30, player_y - 100, 100, 150)
                self.player_cards[len(self.player_cards) - 1 - i].append(card_image)
                card_image.show()

    def hit(self):
        """Handle the 'Hit' action for the current player."""
        self.game.hit(self.game.player_hands[self.current_player_index])
        self.update_ui()

        # Check for Blackjack or Bust
        hand_value = self.game.calculate_hand_value(self.game.player_hands[self.current_player_index])
        if hand_value == 21:
            QMessageBox.information(
                self, "Blackjack!", f"Player {self.current_player_index + 1} got a Blackjack!"
            )
            self.next_player()  # Automatically end the player's turn
        elif self.game.is_bust(self.game.player_hands[self.current_player_index]):
            QMessageBox.information(
                self, "Game Over", f"Player {self.current_player_index + 1} busted!"
            )
            self.next_player()

    def stand(self):
        """Handle the 'Stand' action."""
        self.next_player()

    def next_player(self):
        """Move to the next player or dealer."""
        self.current_player_index += 1
        if self.current_player_index >= self.num_players:
            self.play_dealer_turn()
        else:
            self.update_ui()

    def play_dealer_turn(self):
        """Handle the dealer's turn."""
        self.show_dealer_cards = True  # Reveal all dealer cards
        while self.game.dealer_should_hit():
            self.game.hit(self.game.dealer_hand)
        self.update_ui()
        self.show_results()

    def show_results(self):
        """Determine and display the results."""
        dealer_value = self.game.calculate_hand_value(self.game.dealer_hand)
        results = []
        for i, hand in enumerate(self.game.player_hands):
            player_value = self.game.calculate_hand_value(hand)
            if self.game.is_bust(hand):
                results.append(f"Player {i + 1}: Busted!")
            elif dealer_value > 21 or player_value > dealer_value:
                results.append(f"Player {i + 1}: Won!")
            elif player_value == dealer_value:
                results.append(f"Player {i + 1}: Push!")
            else:
                results.append(f"Player {i + 1}: Lost!")
        QMessageBox.information(self, "Results", "\n".join(results))
        self.reset_game()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlackjackWindow(num_players=3)
    window.show()
    sys.exit(app.exec())