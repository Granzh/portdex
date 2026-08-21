//! # Module for import config

use std::collections::HashMap;

use chrono::NaiveDate;
use serde::{Deserialize, Serialize};

use crate::error::LoaderError;

/// Struct for column mapping
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ColumnMapping {
    pub ticker: String,
    pub op_type: String,
    pub price: String,
    pub quantity: String,
    pub date: String,
    pub fee: String,
}

impl ColumnMapping {
    /// All expected headers as (logical name, config header) pairs.
    /// It is used for both index resolution and error messages.
    pub fn pairs(&self) -> [(&'static str, &str); 6] {
        [
            ("ticker", &self.ticker),
            ("op_type", &self.op_type),
            ("price", &self.price),
            ("quantity", &self.quantity),
            ("date", &self.date),
            ("fee", &self.fee),
        ]
    }
}

/// Date format is a strftime pattern, validated once upon config loading, rather than for every line.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DateFormat(String);

impl DateFormat {
    /// Create a new `DateFormat` and validate the format string.
    pub fn new(pattern: impl Into<String>) -> Result<Self, LoaderError> {
        let pattern = pattern.into();
        let probe = NaiveDate::from_ymd_opt(2024, 2, 28).expect("valid probe date");
        let rendered = probe.format(&pattern).to_string();

        match NaiveDate::parse_from_str(&rendered, &pattern) {
            Ok(parsed) if parsed == probe => Ok(Self(pattern)),
            _ => Err(LoaderError::BadDateFormat(pattern)),
        }
    }

    /// Parse a date string according to the validated format.
    ///
    /// # Errors
    ///
    /// Returns `LoaderError::ParseError` if the input string does not match the expected format.
    ///
    /// # Examples
    ///
    /// Successful parsing:
    /// ```
    /// use app_core::import_config::DateFormat;
    ///
    /// let valid_format = DateFormat::new("%Y-%m-%d").unwrap();
    /// let parsed = valid_format.parse("2024-12-12").unwrap(); // ok
    /// ```
    ///
    /// Example of a parsing error (will panic if unwrapped):
    /// ```rust,should_panic
    /// use app_core::import_config::DateFormat;
    ///
    /// let valid_format = DateFormat::new("%Y-%m-%d").unwrap();
    /// let parsed = valid_format.parse("2024.12.12").unwrap(); // panic!
    /// ```
    pub fn parse(&self, raw: &str) -> Result<NaiveDate, LoaderError> {
        NaiveDate::parse_from_str(raw.trim(), &self.0)
            .map_err(|e| LoaderError::ParseError(format!("date '{raw}': {e}")))
    }
}

/// Column indexes in file, validated once upon config loading.
pub struct ColumnIndex {
    pub ticker: usize,
    pub op_type: usize,
    pub price: usize,
    pub quantity: usize,
    pub date: usize,
    pub fee: usize,
}

impl ColumnIndex {
    /// Resolves ColumnMapping against the actual list of file headers.
    /// The general logic for xlsx/csv/Google Sheets is that each loader
    /// simply obtains a Vec<String> of headers in its own way and calls this function.
    pub fn resolve(headers: &[String], mapping: &ColumnMapping) -> Result<Self, LoaderError> {
        let index_of: HashMap<&str, usize> = headers
            .iter()
            .enumerate()
            .map(|(i, h)| (h.as_str(), i))
            .collect();

        let mut missing = Vec::new();
        let mut find = |wanted: &str| -> usize {
            match index_of.get(wanted) {
                Some(&i) => i,
                None => {
                    missing.push(wanted.to_string());
                    usize::MAX
                }
            }
        };

        let ticker = find(&mapping.ticker);
        let op_type = find(&mapping.op_type);
        let price = find(&mapping.price);
        let quantity = find(&mapping.quantity);
        let date = find(&mapping.date);
        let fee = find(&mapping.fee);

        if !missing.is_empty() {
            return Err(LoaderError::MissingColumn(missing.join(", ")));
        }

        Ok(Self {
            ticker,
            op_type,
            price,
            quantity,
            date,
            fee,
        })
    }
}
