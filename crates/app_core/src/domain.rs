//! #Module with basic structures

use chrono::NaiveDate;
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};

pub type Money = Decimal;

/// OperationType
///
/// Note that fee included in Dividend, Buy, Sell
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum OperationType {
    Buy,
    Sell,
    Dividend,
}

impl OperationType {
    fn as_str(self) -> &'static str {
        match self {
            OperationType::Buy => "buy",
            OperationType::Sell => "sell",
            OperationType::Dividend => "fee",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct RowHash(pub [u8; 32]);

impl std::fmt::Display for RowHash {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", hex_encode(&self.0))
    }
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

/// Normalized row from user's table
/// Column mapping and parsing on UserStocksDataLoader level
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Operation {
    pub ticker: String,
    pub op_type: OperationType,
    pub price: Money,
    pub quantity: Money,
    pub fee: Money,
    pub date: NaiveDate,
}

impl Operation {
    pub fn content_hash(&self) -> RowHash {
        let canonical = format!(
            "{}|{}|{}|{}|{}|{}",
            self.ticker,
            self.op_type.as_str(),
            self.price.normalize(),
            self.quantity.normalize(),
            self.fee.normalize(),
            self.date,
        );
        RowHash(*blake3::hash(canonical.as_bytes()).as_bytes())
    }
}

/// Stock price on a concrete date
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Price {
    pub ticker: String,
    pub date: NaiveDate,
    pub close: Money,
}

/// Position on snapshot date
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    pub ticker: String,
    pub quantity: Money,
    pub avg_cost: Money,
    pub current_price: Money,
    pub fees_paid: Money,
}

impl Position {
    pub fn market_value(&self) -> Money {
        self.quantity * self.current_price
    }

    pub fn invested_value(&self) -> Money {
        self.quantity * self.avg_cost
    }
}

/// Portfolio snapshot as of a concrete date
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PortfolioSnapshot {
    pub date: NaiveDate,
    pub positions: Vec<Position>,
}

impl PortfolioSnapshot {
    /// Count total market value for current Snapshot
    pub fn total_market_value(&self) -> Money {
        self.positions.iter().map(Position::market_value).sum()
    }

    /// Count total invested money for current Snapshot
    pub fn total_invested(&self) -> Money {
        self.positions.iter().map(Position::invested_value).sum()
    }
}
