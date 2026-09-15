# Frontend Dashboard

A React and TypeScript single page application that consumes the backend API: upload media, view the latest detection result, browse a searchable history table, and monitor compliance trends through charts.

## Stack

- React 18 with TypeScript, built with Vite.
- [axios](https://axios-http.com/) for API calls.
- [recharts](https://recharts.org/) for the bar and line charts.
- Plain CSS (`src/styles/index.css`), no UI framework dependency, to keep the bundle small and the styling easy to audit.

## Structure

```
src/
  api/client.ts          Axios instance and typed API calls
  types/detection.ts      TypeScript types mirroring the backend Pydantic schemas
  components/
    UploadPanel.tsx        File upload, calls /inference/image or /inference/video
    DetectionResults.tsx    Shows the result of the most recent upload
    HistoryTable.tsx        Searchable, paginated table backed by /detections
    StatsCharts.tsx         KPI cards and charts backed by /stats/summary and /stats/timeseries
    Layout.tsx               Header, footer, page shell
  pages/Dashboard.tsx      Composes the components above into the main view
```

## Configuration

Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to the backend's base URL. When running through Docker Compose this is left as the relative path `/api/v1`, since nginx proxies API requests to the backend container (see [nginx.conf](nginx.conf)).

## Running locally without Docker

```
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and expects the backend to be reachable at the URL configured in `.env` (CORS is enabled on the backend for `http://localhost:5173` by default).

## Building for production

```
npm run build
npm run preview
```

## Linting

```
npm run lint
```
