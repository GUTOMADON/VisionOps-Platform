import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-title">
          <span className="app-header-logo">VisionOps</span>
          <span className="app-header-subtitle">Safety Monitoring Platform</span>
        </div>
        <a
          className="app-header-link"
          href="https://github.com/gutomadon/VisionOps-Platform"
          target="_blank"
          rel="noreferrer"
        >
          View on GitHub
        </a>
      </header>
      <main className="app-main">{children}</main>
      <footer className="app-footer">
        VisionOps Platform - end to end computer vision monitoring reference project.
      </footer>
    </div>
  );
}
