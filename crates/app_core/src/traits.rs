use chrono::NaiveDate;

use crate::domain::{Money, Operation, PortfolioSnapshot, Price, RowHash};
use crate::error::{CalcError, DbError, ExchangeError, LoaderError};

/// Import Batch ID - see app_core::reconcile
/// Batch is "shot of operation at the moment of certain import"
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct ImportBatchId(pub i64);

/// Append-only warehouse of operations and prices cache
/// Realization: SqliteDb, PostgresDb (crate 'db').
pub trait DatabaseInterface {
    /// Creates new batch for source (path/kind like in source_id) and make active
    /// The previous active batch for the same `source_id` ceases to be active but
    /// is not deleted - its rows remain in the tables as an audit trail, simply
    /// dropping out of default read operations
    fn create_import_batch(&self, source_id: &str) -> Result<ImportBatchId, DbError>;

    /// Current active batch of source, if an import for it has already taken place
    fn active_batch_id(&self, source_id: &str) -> Result<Option<ImportBatchId>, DbError>;

    /// Hashes of strings in concrete batch, if import for it has already taken place
    fn operations_in_batch_hashes(&self, batch: ImportBatchId) -> Result<Vec<RowHash>, DbError>;

    fn add_operations(&self, batch: ImportBatchId, ops: &[Operation]) -> Result<(), DbError>;

    fn read_operation(
        &self,
        ticker: Option<&str>,
        date_range: Option<(NaiveDate, NaiveDate)>,
    ) -> Result<Vec<Operation>, DbError>;

    fn add_price(&self, price: &Price) -> Result<(), DbError>;

    fn read_prices(&self, ticker: &str, date_range: Option<(NaiveDate, NaiveDate)>) -> Result<Vec<Price>, DbError>;
}


pub trait UserStockDateLoader {
    fn read_current(&self) -> Result<Vec<Operation>, LoaderError>;
}

pub trait ExchangeDataLoader {
    fn supports(&self, ticker: &str) -> bool;
    fn load_price_now(&self, ticker: &str) -> Result<Price, ExchangeError>;
    fn load_price_for_date(&self, ticker: &str, date: NaiveDate) -> Result<Price, ExchangeError>;
}

pub trait IndexCalculator {
    fn calc_index(&self, snapshot: &PortfolioSnapshot) -> Result<Money, CalcError>;
}
