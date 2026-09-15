import { useEffect, useState } from "react";

import { ApiError, listDetections } from "../api/client";
import type { Detection } from "../types/detection";

const PAGE_SIZE = 10;

interface HistoryTableProps {
  refreshToken: number;
}

export function HistoryTable({ refreshToken }: HistoryTableProps) {
  const [items, setItems] = useState<Detection[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [classFilter, setClassFilter] = useState("");
  const [violationOnly, setViolationOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    setIsLoading(true);
    setError(null);

    listDetections({
      class_name: classFilter || undefined,
      is_violation: violationOnly ? true : undefined,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    })
      .then((response) => {
        if (!isActive) return;
        setItems(response.items);
        setTotal(response.total);
      })
      .catch((err) => {
        if (!isActive) return;
        setError(err instanceof ApiError ? err.message : "Failed to load detections.");
      })
      .finally(() => {
        if (isActive) setIsLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, [classFilter, violationOnly, page, refreshToken]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <section className="card">
      <h2>Detection history</h2>
      <div className="history-filters">
        <input
          type="text"
          placeholder="Filter by class name (e.g. NO-Hardhat)"
          value={classFilter}
          onChange={(event) => {
            setPage(0);
            setClassFilter(event.target.value);
          }}
        />
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={violationOnly}
            onChange={(event) => {
              setPage(0);
              setViolationOnly(event.target.checked);
            }}
          />
          Violations only
        </label>
      </div>

      {error && <p className="error-text">{error}</p>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Class</th>
            <th>Confidence</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((detection) => (
            <tr key={detection.id} className={detection.is_violation ? "row-violation" : undefined}>
              <td>{new Date(detection.created_at).toLocaleString()}</td>
              <td>{detection.class_name}</td>
              <td>{(detection.confidence * 100).toFixed(1)}%</td>
              <td>{detection.is_violation ? "Violation" : "Compliant"}</td>
            </tr>
          ))}
          {!isLoading && items.length === 0 && (
            <tr>
              <td colSpan={4} className="empty-row">
                No detections match the current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="pagination">
        <button disabled={page === 0} onClick={() => setPage((current) => current - 1)}>
          Previous
        </button>
        <span>
          Page {page + 1} of {totalPages} ({total} total)
        </span>
        <button disabled={page + 1 >= totalPages} onClick={() => setPage((current) => current + 1)}>
          Next
        </button>
      </div>
    </section>
  );
}
