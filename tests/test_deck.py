"""Tests unitaires pour core/deck.py."""

import pytest

from core.deck import (
    DECK_SIZE,
    JOKER_A,
    JOKER_B,
    card_bridge_value,
    card_to_string,
    card_value,
    create_deck,
    find_card,
)


class TestCreateDeck:
    def test_size(self) -> None:
        deck = create_deck()
        assert len(deck) == DECK_SIZE

    def test_all_unique(self) -> None:
        deck = create_deck()
        assert len(set(deck)) == DECK_SIZE

    def test_values_range(self) -> None:
        deck = create_deck()
        assert deck == tuple(range(1, 55))

    def test_is_tuple(self) -> None:
        deck = create_deck()
        assert isinstance(deck, tuple)


class TestCardToString:
    def test_ace_of_clubs(self) -> None:
        assert card_to_string(1) == "As de Trèfle"

    def test_king_of_clubs(self) -> None:
        assert card_to_string(13) == "Roi de Trèfle"

    def test_ace_of_diamonds(self) -> None:
        assert card_to_string(14) == "As de Carreau"

    def test_king_of_spades(self) -> None:
        assert card_to_string(52) == "Roi de Pique"

    def test_ten_of_hearts(self) -> None:
        assert card_to_string(36) == "10 de Cœur"

    def test_joker_a(self) -> None:
        assert card_to_string(JOKER_A) == "Joker Noir (A)"

    def test_joker_b(self) -> None:
        assert card_to_string(JOKER_B) == "Joker Rouge (B)"

    def test_invalid_card_raises(self) -> None:
        with pytest.raises(ValueError):
            card_to_string(0)
        with pytest.raises(ValueError):
            card_to_string(55)


class TestCardValue:
    def test_clubs_1_to_13(self) -> None:
        for i in range(1, 14):
            assert card_value(i) == i

    def test_diamonds_14_to_26(self) -> None:
        for i in range(14, 27):
            assert card_value(i) == i

    def test_hearts_27_to_39_wrap(self) -> None:
        for i in range(27, 40):
            assert card_value(i) == i - 26

    def test_spades_40_to_52_wrap(self) -> None:
        for i in range(40, 53):
            assert card_value(i) == i - 26

    def test_jokers_return_53(self) -> None:
        assert card_value(JOKER_A) == 53
        assert card_value(JOKER_B) == 53


class TestCardBridgeValue:
    def test_regular_cards_identity(self) -> None:
        for i in range(1, 53):
            assert card_bridge_value(i) == i

    def test_jokers_return_53(self) -> None:
        assert card_bridge_value(JOKER_A) == 53
        assert card_bridge_value(JOKER_B) == 53


class TestFindCard:
    def test_find_joker_a_in_standard_deck(self) -> None:
        deck = create_deck()
        assert find_card(deck, JOKER_A) == 52

    def test_find_joker_b_in_standard_deck(self) -> None:
        deck = create_deck()
        assert find_card(deck, JOKER_B) == 53

    def test_find_ace_of_clubs(self) -> None:
        deck = create_deck()
        assert find_card(deck, 1) == 0

    def test_find_king_of_spades(self) -> None:
        deck = create_deck()
        assert find_card(deck, 52) == 51
