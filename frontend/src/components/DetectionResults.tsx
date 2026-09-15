import type { InferenceResponse } from "../types/detection";

interface DetectionResultsProps {
  result: InferenceResponse;
}

export function DetectionResults({ result }: DetectionResultsProps) {
  const complianceRate =
    result.total_detections === 0
      ? 1
      : (result.total_detections - result.total_violations) / result.total_detections;

  return (
    <section className="card">
      <h2>Latest result</h2>
      <div className="result-summary">
        <SummaryStat label="File" value={result.media_asset.original_filename} />
        <SummaryStat label="Type" value={result.media_asset.media_type} />
        <SummaryStat label="Frames analyzed" value={String(result.total_frames)} />
        <SummaryStat label="Detections" value={String(result.total_detections)} />
        <SummaryStat label="Violations" value={String(result.total_violations)} highlight={result.total_violations > 0} />
        <SummaryStat label="Compliance" value={`${(complianceRate * 100).toFixed(1)}%`} />
        <SummaryStat label="Processing time" value={`${result.processing_time_ms} ms`} />
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Class</th>
            <th>Confidence</th>
            <th>Frame</th>
            <th>Bounding box</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {result.detections.map((detection) => (
            <tr key={detection.id} className={detection.is_violation ? "row-violation" : undefined}>
              <td>{detection.class_name}</td>
              <td>{(detection.confidence * 100).toFixed(1)}%</td>
              <td>{detection.frame_index}</td>
              <td>
                [{detection.bbox_x_min.toFixed(0)}, {detection.bbox_y_min.toFixed(0)}, {detection.bbox_x_max.toFixed(0)},{" "}
                {detection.bbox_y_max.toFixed(0)}]
              </td>
              <td>{detection.is_violation ? "Violation" : "Compliant"}</td>
            </tr>
          ))}
          {result.detections.length === 0 && (
            <tr>
              <td colSpan={5} className="empty-row">
                No objects detected above the confidence threshold.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}

function SummaryStat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`summary-stat ${highlight ? "summary-stat-highlight" : ""}`}>
      <span className="summary-stat-label">{label}</span>
      <span className="summary-stat-value">{value}</span>
    </div>
  );
}
