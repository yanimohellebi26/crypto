"""Tests unitaires pour les 5 opérations de core/solitaire.py."""

from core.deck import JOKER_A, JOKER_B, create_deck
from core.solitaire import (
    count_cut,
    move_joker_a,
    move_joker_b,
    read_output,
    solitaire_step,
    triple_cut,
)




class TestMoveJokerA:
    def test_normal_position(self) -> None:
        deck = (1, 2, 53, 3, 4)
        result = move_joker_a(deck)
        assert result == (1, 2, 3, 53, 4)

    def test_last_position_wraps_to_second(self) -> None:
        """Piège #1 : dernière position → index 1 (pas 0)."""
        deck = (1, 2, 3, 4, 53)
        result = move_joker_a(deck)
        assert result == (1, 53, 2, 3, 4)

    def test_first_position(self) -> None:
        deck = (53, 1, 2, 3, 4)
        result = move_joker_a(deck)
        assert result == (1, 53, 2, 3, 4)

    def test_standard_deck_first_step(self) -> None:
        """Schneier : paquet initial, A échange avec B."""
        deck = create_deck()
        result = move_joker_a(deck)
        assert result[52] == JOKER_B
        assert result[53] == JOKER_A

    def test_does_not_mutate_original(self) -> None:
        deck = (1, 2, 53, 3, 4)
        original = deck
        move_joker_a(deck)
        assert deck is original
        assert deck == (1, 2, 53, 3, 4)



class TestMoveJokerB:
    def test_normal_position(self) -> None:
        deck = (1, 54, 2, 3, 4, 5)
        result = move_joker_b(deck)
        assert result == (1, 2, 3, 54, 4, 5)

    def test_last_position_wraps_to_third(self) -> None:
        """Piège #2a : dernière position → index 2."""
        deck = (1, 2, 3, 4, 54)
        result = move_joker_b(deck)
        assert result == (1, 2, 54, 3, 4)

    def test_second_to_last_wraps_to_second(self) -> None:
        """Piège #2b : avant-dernière → index 1."""
        deck = (1, 2, 3, 54, 4)
        result = move_joker_b(deck)
        assert result == (1, 54, 2, 3, 4)

    def test_first_position(self) -> None:
        deck = (54, 1, 2, 3, 4, 5)
        result = move_joker_b(deck)
        assert result == (1, 2, 54, 3, 4, 5)

    def test_schneier_example_adjacent_jokers(self) -> None:
        """Schneier : 3 A B 8 9 6 → step1: 3 B A 8 9 6 → step2: 3 A 8 B 9 6."""
        after_step1 = (3, 54, 53, 8, 9, 6)  # A already moved
        result = move_joker_b(after_step1)
        assert result == (3, 53, 8, 54, 9, 6)

    def test_does_not_mutate_original(self) -> None:
        deck = (1, 54, 2, 3, 4, 5)
        original = deck
        move_joker_b(deck)
        assert deck is original



class TestTripleCut:
    def test_normal(self) -> None:
        """Exemple de Schneier : 2 4 6 B 5 8 7 1 A 3 9."""
        deck = (2, 4, 6, 54, 5, 8, 7, 1, 53, 3, 9)
        result = triple_cut(deck)
        assert result == (3, 9, 54, 5, 8, 7, 1, 53, 2, 4, 6)

    def test_joker_at_top(self) -> None:
        """Premier joker en 1ère position → segment du dessus vide."""
        deck = (54, 5, 8, 7, 1, 53, 3, 9)
        result = triple_cut(deck)
        assert result == (3, 9, 54, 5, 8, 7, 1, 53)

    def test_joker_at_bottom(self) -> None:
        """Second joker en dernière position → segment du dessous vide."""
        deck = (3, 9, 54, 5, 8, 7, 1, 53)
        result = triple_cut(deck)
        assert result == (54, 5, 8, 7, 1, 53, 3, 9)

    def test_both_jokers_at_ends(self) -> None:
        """Les deux jokers aux extrémités → pas de changement."""
        deck = (54, 5, 8, 7, 1, 53)
        result = triple_cut(deck)
        assert result == (54, 5, 8, 7, 1, 53)

    def test_jokers_adjacent(self) -> None:
        deck = (1, 2, 53, 54, 3, 4)
        result = triple_cut(deck)
        assert result == (3, 4, 53, 54, 1, 2)

    def test_jokers_adjacent_reversed(self) -> None:
        deck = (1, 2, 54, 53, 3, 4)
        result = triple_cut(deck)
        assert result == (3, 4, 54, 53, 1, 2)



class TestCountCut:
    def test_normal(self) -> None:
        deck = (5, 3, 1, 4, 2)
        result = count_cut(deck)
        # Last card = 2, bridge_value = 2 → take 2 from top: [5, 3]
        assert result == (1, 4, 5, 3, 2)

    def test_joker_last_no_change(self) -> None:
        """Piège : si la dernière carte est un joker → paquet inchangé."""
        deck = create_deck()  # se termine par 54 (Joker B)
        result = count_cut(deck)
        assert result == deck

    def test_schneier_example(self) -> None:
        """Schneier sample 1, step 4 : [B 2 3..52 A 1] → [2 3..52 A B 1]."""
        deck = (54,) + tuple(range(2, 53)) + (53, 1)
        result = count_cut(deck)
        expected = tuple(range(2, 53)) + (53, 54, 1)
        assert result == expected

    def test_last_card_does_not_move(self) -> None:
        """Piège #4 : la dernière carte ne bouge JAMAIS."""
        deck = (5, 3, 1, 4, 2)
        result = count_cut(deck)
        assert result[-1] == deck[-1]



class TestReadOutput:
    def test_normal(self) -> None:
        # Top card = 4 → bridge_value = 4 → deck[4] = 5 → card_value(5) = 5
        deck = (4, 1, 2, 3, 5, 6, 7)
        assert read_output(deck) == 5

    def test_joker_output_returns_none(self) -> None:
        """Piège #5 : si sortie = joker → None (il faut recommencer)."""
        # Top card = 4 → bridge_value = 4 → deck[4] = 53 (Joker A) → None
        deck = (4, 1, 2, 3, 53, 6, 7)
        assert read_output(deck) is None

    def test_does_not_modify_deck(self) -> None:
        """Piège #6 : opération 5 ne modifie PAS le paquet."""
        deck = (4, 1, 2, 3, 5, 6, 7)
        original = deck
        read_output(deck)
        assert deck is original
        assert deck == (4, 1, 2, 3, 5, 6, 7)

    def test_high_card_value_wraps_to_1_through_26(self) -> None:
        # card 40 → card_value(40) = 14
        deck = (1, 40) + tuple(range(2, 40)) + (41, 42)
        output = read_output(deck)
        assert output == 14

    def test_schneier_first_output(self) -> None:
        """Schneier : après step 4, deck = [2,3,...,52,A,B,1] → top=2, deck[2]=4."""
        deck = tuple(range(2, 53)) + (53, 54, 1)
        output = read_output(deck)
        assert output == 4


class TestSolitaireStep:
    def test_first_output_unkeyed(self) -> None:
        """Premier cycle du paquet standard → sortie = 4."""
        deck = create_deck()
        new_deck, output = solitaire_step(deck)
        assert output == 4
        assert len(new_deck) == 54
        assert len(set(new_deck)) == 54

    def test_deck_integrity_over_many_steps(self) -> None:
        """Après 50 cycles, toujours 54 cartes uniques."""
        deck = create_deck()
        for _ in range(50):
            deck, _ = solitaire_step(deck)
            assert len(deck) == 54
            assert len(set(deck)) == 54
