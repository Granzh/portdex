use crate::{domain::Operation, error::DbError, traits::{DatabaseInterface, ImportBatchId}};

use std::collections::HashMap;
use crate::domain::{RowHash};

#[derive(Debug)]
pub enum ReconcileOutcome {
    /// hashes of file and active batch are same, nothing to do
    NoChange,
    Appended {batch: ImportBatchId, add: usize},
    FullReimport{ batch: ImportBatchId, total: usize},
}

pub struct ImportReconciler<'a, D: DatabaseInterface> {
    db: &'a D,
}

impl <'a, D:DatabaseInterface> ImportReconciler<'a, D> {
    pub fn new(db: &'a D) -> Self {
        Self {db}
    }

    pub fn reconcile(&self, source_id: &str, current: Vec<Operation>,) -> Result<ReconcileOutcome, DbError> {
        let active_batch = self.db.active_batch_id(source_id)?;

        let old_hashes = match active_batch {
            Some(b) => self.db.operations_in_batch_hashes(b)?,
            None => Vec::new(),
        };

        if old_hashes.is_empty() && current.is_empty() {
            return Ok(ReconcileOutcome::NoChange);
        }

        let old_counts = count_hashes(old_hashes.iter().copied());
        let new_counts = count_hashes(current.iter().map(Operation::content_hash));

        let needs_full_reimport = active_batch.is_none()
            || old_counts.iter().any(|(h, &old_c)| new_counts.get(h).copied().unwrap_or(0) < old_c);

        if needs_full_reimport {
            let batch = self.db.create_import_batch(source_id)?;
            self.db.add_operations(batch, &current)?;
            return Ok(ReconcileOutcome::FullReimport { batch, total: current.len() });
        }

        let batch = active_batch.expect("needs_full_reimport else true");
        let mut consumed: HashMap<RowHash, usize> = HashMap::new();
        let mut to_add = Vec::new();

        for op in current {
            let h = op.content_hash();
            let already_seen = old_counts.get(&h).copied().unwrap_or(0);
            let used = consumed.entry(h).or_insert(0);
            if *used < already_seen {
                *used += 1;
            } else {
                to_add.push(op);
            }
        }

        if to_add.is_empty() {
            return Ok(ReconcileOutcome::NoChange);
        }

        self.db.add_operations(batch, &to_add)?;
        Ok(ReconcileOutcome::Appended { batch, add: to_add.len() })
    }
}

fn count_hashes(hashes: impl Iterator<Item = RowHash>) -> HashMap<RowHash, usize> {
    let mut counts = HashMap::new();
    for h in hashes {
        *counts.entry(h).or_insert(0) += 1;
    }
    counts
}
