// frontend/src/components/AlertsFeed/AlertsFeed.jsx

import React, { useState, useEffect } from 'react';
import './AlertsFeed.css';

const AlertsFeed = ({ wsUrl }) => {
  const [alerts, setAlerts] = useState([]);
  const [wsConnection, setWsConnection] = useState(null);

  useEffect(() => {
    // Establish WebSocket connection for real-time alerts
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('[*] WebSocket connection established for alerts');
      setWsConnection(ws);
    };

    ws.onmessage = (event) => {
      try {
        const alert = JSON.parse(event.data);
        setAlerts(prevAlerts => [
          {
            ...alert,
            id: Date.now() + Math.random(),
            timestamp: new Date().toLocaleTimeString()
          },
          ...prevAlerts.slice(0, 49) // Keep only last 50 alerts
        ]);
      } catch (error) {
        console.error('Error parsing alert data:', error);
      }
    };

    ws.onclose = () => {
      console.log('[*] WebSocket connection closed');
      setWsConnection(null);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [wsUrl]);

  const getAlertClass = (type) => {
    switch (type) {
      case 'ML_Anomaly':
        return 'alert-ml';
      case 'CentralityShift':
        return 'alert-centrality';
      case 'TrafficClusterOutlier':
        return 'alert-cluster';
      default:
        return 'alert-default';
    }
  };

  const clearAlerts = () => {
    setAlerts([]);
  };

  return (
    <div className="alerts-feed">
      <div className="alerts-header">
        <h3>Security Alerts</h3>
        <div className="alerts-controls">
          <span className={`status ${wsConnection ? 'connected' : 'disconnected'}`}>
            {wsConnection ? '● Connected' : '● Disconnected'}
          </span>
          <button onClick={clearAlerts} className="clear-button">
            Clear
          </button>
        </div>
      </div>
      
      <div className="alerts-list">
        {alerts.length === 0 ? (
          <div className="no-alerts">No alerts detected</div>
        ) : (
          alerts.map(alert => (
            <div key={alert.id} className={`alert-item ${getAlertClass(alert.type)}`}>
              <div className="alert-header">
                <span className="alert-type">{alert.type}</span>
                <span className="alert-time">{alert.timestamp}</span>
              </div>
              <div className="alert-message">{alert.message}</div>
              {alert.node && (
                <div className="alert-node">Node: {alert.node}</div>
              )}
              {alert.details && (
                <div className="alert-details">
                  <small>
                    {alert.details.src_addr && `${alert.details.src_addr}:${alert.details.src_port}`}
                    {alert.details.dst_addr && ` → ${alert.details.dst_addr}:${alert.details.dst_port}`}
                  </small>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsFeed;
