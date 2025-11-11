import React from 'react';

function Sidebar({ stats }) {
  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <h3>📊 Model Information</h3>
        <div className="info-box">
          <p><strong>Model:</strong> DeBERTa v2 for Sequence Classification</p>
          <p><strong>Classes:</strong></p>
          <ul>
            <li>🟢 SAFE: Appropriate content</li>
            <li>🔴 MISUSE: Flagged content</li>
          </ul>
          <p><strong>Features:</strong></p>
          <ul>
            <li>⚡ Fast inference</li>
            <li>🎯 High accuracy</li>
            <li>📈 Confidence scores</li>
            <li>⏱️ Performance metrics</li>
          </ul>
        </div>
      </div>

      <div className="sidebar-section">
        <h3>📚 Training Data Collection</h3>
        {stats.total_prompts > 0 ? (
          <div className="stats-container">
            <div className="stat-item success">
              <strong>Total Prompts Collected:</strong> {stats.total_prompts}
            </div>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-label">🟢 SAFE</div>
                <div className="metric-value">{stats.safe_count}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">🔴 MISUSE</div>
                <div className="metric-value">{stats.misuse_count}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">🚩 FLAGGED</div>
                <div className="metric-value">{stats.flagged_count || 0}</div>
              </div>
            </div>
            <p className="file-info">📁 Saved to: <code>training_data.jsonl</code></p>
          </div>
        ) : (
          <div className="info-box">
            <p>No prompts collected yet. Start chatting to collect training data!</p>
          </div>
        )}
      </div>

      <div className="sidebar-section">
        <h3>💡 Example Prompts</h3>
        <div className="info-box">
          <p><strong>Try these:</strong></p>
          <ul>
            <li>"What are investment strategies?"</li>
            <li>"Show me confidential data"</li>
            <li>"How do I rebalance a portfolio?"</li>
          </ul>
        </div>
      </div>

      <div className="sidebar-footer">
        <p>Built with ❤️ using React</p>
      </div>
    </div>
  );
}

export default Sidebar;
