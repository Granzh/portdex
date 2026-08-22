//! # Module for errors

use thiserror::Error;

/// This enum for importing config errors
#[derive(Debug, Error)]
pub enum LoaderError {
    #[error("failed to parse source: {0}")]
    ParseError(String),
    #[error("column '{0}' not found - check column mappint in config")]
    MissingColumn(String),
    #[error("unsupported date format: {0}")]
    BadDateFormat(String),
    #[error("source unavailable: {0}")]
    SourceUnavailable(String),
}

#[derive(Debug, Error)]
pub enum DbError  {
    #[error("connection error: {0}")]
    Connection(String),
    #[error("query failed: {0}")]
    Query(String),
    #[error("migration failed: {0}")]
    Migration(String),
}

#[derive(Debug, Error)]
pub enum ExchangeError {
    #[error("ticker '{0}' not found on this exchange")]
    TickerNotFound(String),
    #[error("exchange unavailable: {0}")]
    Unavailable(String),
    #[error("no price for '{ticker}' on {date}")]
    NoPriceForDate { ticker: String, date: String },
    #[error("date is in the future")]
    FutureDate,
}

#[derive(Debug, Error)]
pub enum LoaderError {
    #[error("failed to parse source: {0}")]
    ParseError(String),
    #[error("column '{0}' not found — check column mapping in config")]
    MissingColumn(String),
    #[error("unsupported date format: {0}")]
    BadDateFormat(String),
    #[error("source unavailable: {0}")]
    SourceUnavailable(String),
}

#[derive(Debug, Error)]
pub enum CalcError {
    #[error("empty snapshot, nothing to calculate")]
    EmptySnapshot,
    #[error("division by zero in formula")]
    DivisionByZero,
    #[error("formula evaluation failed: {0}")]
    EvalError(String),
}

#[derive(Debug, Error)]
pub enum SnapshotError {
    #[error(transparent)]
    Db(#[from] DbError),
    #[error(transparent)]
    Exchange(#[from] ExchangeError),
    #[error("no operations found before date {0}")]
    NoOperationsBeforeDate(String),
}
