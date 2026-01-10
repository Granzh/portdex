import pytest
from dataclasses import asdict
from portfolio.position import Position


class TestPosition:
    """Test cases for Position class"""

    def test_position_creation(self):
        """Test position creation with valid parameters"""
        position = Position(ticker="SBER", quantity=100, cash_flow=-5000.0)

        assert position.ticker == "SBER"
        assert position.quantity == 100
        assert position.cash_flow == -5000.0

    def test_position_zero_quantity(self):
        """Test position with zero quantity"""
        position = Position(ticker="GAZP", quantity=0, cash_flow=0.0)

        assert position.ticker == "GAZP"
        assert position.quantity == 0
        assert position.cash_flow == 0.0

    def test_position_negative_quantity(self):
        """Test position with negative quantity (short position)"""
        position = Position(ticker="SBER", quantity=-50, cash_flow=2500.0)

        assert position.ticker == "SBER"
        assert position.quantity == -50
        assert position.cash_flow == 2500.0

    def test_position_positive_cash_flow(self):
        """Test position with positive cash flow"""
        position = Position(ticker="GAZP", quantity=0, cash_flow=1500.0)

        assert position.cash_flow == 1500.0

    def test_position_large_values(self):
        """Test position with large values"""
        position = Position(ticker="SBER", quantity=1000000, cash_flow=-50000000.0)

        assert position.quantity == 1000000
        assert position.cash_flow == -50000000.0

    def test_position_asdict(self):
        """Test position conversion to dictionary"""
        position = Position(ticker="SBER", quantity=100, cash_flow=-5000.0)
        position_dict = asdict(position)

        expected = {"ticker": "SBER", "quantity": 100, "cash_flow": -5000.0}

        assert position_dict == expected

    def test_position_equality(self):
        """Test position equality comparison"""
        pos1 = Position(ticker="SBER", quantity=100, cash_flow=-5000.0)
        pos2 = Position(ticker="SBER", quantity=100, cash_flow=-5000.0)
        pos3 = Position(ticker="SBER", quantity=200, cash_flow=-10000.0)

        # Dataclasses implement equality by default
        assert pos1 == pos2
        assert pos1 != pos3

    def test_position_immutability_of_attributes(self):
        """Test that position attributes can be modified (dataclass is mutable)"""
        position = Position(ticker="SBER", quantity=100, cash_flow=-5000.0)

        # Dataclass fields are mutable by default
        position.quantity = 150
        position.cash_flow = -7500.0

        assert position.quantity == 150
        assert position.cash_flow == -7500.0

    def test_position_string_representation(self):
        """Test position string representation"""
        position = Position(ticker="SBER", quantity=100, cash_flow=-5000.0)
        str_repr = str(position)

        assert "SBER" in str_repr
        assert "100" in str_repr
        assert "-5000.0" in str_repr

    def test_position_repr(self):
        """Test position repr representation"""
        position = Position(ticker="GAZP", quantity=200, cash_flow=-8000.0)
        repr_str = repr(position)

        assert "Position" in repr_str
        assert "GAZP" in repr_str
        assert "200" in repr_str
        assert "-8000.0" in repr_str
