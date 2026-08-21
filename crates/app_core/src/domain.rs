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

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Operation {
    pub ticker: String,
    pub op_type: OperationType,
    pub price: Money,
    pub quantity: Money,
    pub fee: Money,
    pub date: NaiveDate,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Price {
    pub ticker: String,
    pub date: NaiveDate,
    pub close: Money,
}

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
