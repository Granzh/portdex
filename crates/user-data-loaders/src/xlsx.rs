use std::path::PathBuf;
use std::str::FromStr;

use calamine::{open_workbook_auto, Reader};
use rust_decimal::Decimal;

use app_core::{
    ColumnIndex, ColumnMapping, DateFormat, LoaderError, Operation, OperationType,
    UserStocksDataLoader,
};

pub struct XlsxLoader {
    path: PathBuf,
    mapping: ColumnMapping,
    date_format: DateFormat,
}

impl XlsxLoader {
    pub fn new(path: impl Into<PathBuf>, mapping: ColumnMapping, date_format: DateFormat) -> Self {
        Self {
            path: path.into(),
            mapping,
            date_format,
        }
    }
}

impl UserStocksDataLoader for XlsxLoader {
    fn read_current(&self) -> Result<Vec<Operation>, LoaderError> {
        let mut workbook = open_workbook_auto(&self.path)
            .map_err(|e| LoaderError::SourceUnavailable(e.to_string()))?;

        let sheet_name = workbook
            .sheet_names()
            .first()
            .cloned()
            .ok_or_else(|| LoaderError::ParseError("workbook has no sheets".into()))?;

        let range = workbook
            .worksheet_range(&sheet_name)
            .map_err(|e| LoaderError::ParseError(e.to_string()))?;

        let mut rows = range.rows();

        let header_row = rows
            .next()
            .ok_or_else(|| LoaderError::ParseError("empty sheet, no header row".into()))?;

        let headers: Vec<String> = header_row.iter().map(|c| c.to_string()).collect();

        let idx = ColumnIndex::resolve(&headers, &self.mapping)?;

        let mut result = Vec::new();
        for (row_num, row) in rows.enumerate() {
            let get = |i: usize| row.get(i).map(|c| c.to_string()).unwrap_or_default();

            let op_type = match get(idx.op_type).to_lowercase().as_str() {
                "buy" => OperationType::Buy,
                "sell" => OperationType::Sell,
                _ => continue, // skip rows with unknown operation type
            };

            result.push(Operation {
                ticker: get(idx.ticker),
                op_type,
                price: parse_decimal(&get(idx.price), row_num)?,
                quantity: parse_decimal(&get(idx.quantity), row_num)?,
                fee: parse_decimal(&get(idx.fee), row_num)?,
                date: self.date_format.parse(&get(idx.date))?,
            });
        }

        Ok(result)
    }
}

fn parse_decimal(raw: &str, row_num: usize) -> Result<Decimal, LoaderError> {
    Decimal::from_str(raw.trim().replace(',', ".").as_str())
        .map_err(|e| LoaderError::ParseError(format!("row {}: {e}", row_num + 2)))
}
