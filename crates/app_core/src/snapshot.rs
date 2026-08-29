use std::collections::HashMap;

use crate::domain::{OperationType, Price};
use chrono::{NaiveDate, Utc};
use rust_decimal::Decimal;

use crate::{DatabaseInterface, ExchangeDataLoader, PortfolioSnapshot, Position, SnapshotError};

/// Build snapshot of portfolio on date of opererations + prices
pub struct PortfolioSnapshotBuilder<D: DatabaseInterface, E: ExchangeDataLoader> {
    db: D,
    exchange: E,
}

impl<D: DatabaseInterface, E: ExchangeDataLoader> PortfolioSnapshotBuilder<D, E> {
    pub fn new(db: D, exchange: E) -> Self {
        Self { db, exchange }
    }

    pub fn build_for_date(&self, date: NaiveDate) -> Result<PortfolioSnapshot, SnapshotError> {
        let ops = self
            .db
            .read_operations(None, Some((NaiveDate::MIN, date)))?;

        if ops.is_empty() {
            return Err(SnapshotError::NoOperationsBeforeDate(date.to_string()));
        }

        // TODO: change to FIFO/weighted average admission fee
        let mut agg: HashMap<String, (Decimal, Decimal, Decimal)> = HashMap::new();

        for op in &ops {
            let entry = agg.entry(op.ticker.clone()).or_insert((
                Decimal::ZERO,
                Decimal::ZERO,
                Decimal::ZERO,
            ));
            match op.op_type {
                OperationType::Buy => {
                    entry.0 += op.quantity;
                    entry.1 += op.price * op.quantity;
                    entry.2 += op.fee;
                }
                OperationType::Sell => {
                    entry.0 -= op.quantity;
                    entry.1 -= op.price * op.quantity;
                    entry.2 += op.fee;
                }
            }
        }

        let is_today = date == Utc::now().date_naive();
        let mut positions = Vec::with_capacity(agg.len());

        for (ticker, (qty, cost_sum, fees)) in agg {
            if qty <= Decimal::ZERO {
                continue;
            }

            let price: Price = if is_today {
                let p = self.exchange.load_price_now(&ticker)?;
                self.db.add_price(&p)?;
                p
            } else {
                self.db
                    .read_prices(&ticker, Some((date, date)))?
                    .into_iter()
                    .next()
                    .ok_or_else(|| SnapshotError::NoOperationsBeforeDate(date.to_string()))?
            };

            positions.push(Position {
                ticker,
                quantity: qty,
                avg_cost: cost_sum / qty,
                current_price: price.close,
                fees_paid: fees,
            });
        }

        Ok(PortfolioSnapshot { date, positions })
    }
}
