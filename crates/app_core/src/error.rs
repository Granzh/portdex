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
