// frontend/src/pages/Dashboard/Dashboard.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NetworkGraph from '../../components/NetworkGraph/NetworkGraph';
import AlertsFeed from '../../components/AlertsFeed/AlertsFeed';
import './Dashboard.css';

const Dashboard = ({ onLogout }) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    nodeCount: 0,
    edgeCount: 0,
    lastUpdate: null
  });

  // Fetch graph data periodically
  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/graph');
        setGraphData(response.data);
        setStats({
          nodeCount: response.data.nodes.length,
          edgeCount: response.data.links.length,
          lastUpdate: new Date().toLocaleTimeString()
        });
        setError('');
      } catch (error) {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          onLogout();
        } else {
          setError('Failed to fetch graph data');
          console.error('Error fetching graph data:', error);
        }
      } finally {
        setIsLoading(false);
      }
    };

    // Initial fetch
    fetchGraphData();

    // Set up periodic updates every 5 seconds
    const interval = setInterval(fetchGraphData, 5000);

    return () => clearInterval(interval);
  }, [onLogout]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    delete axios.defaults.headers.common['Authorization'];
    onLogout();
  };

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading NIDS Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>NIDS Dashboard</h1>
          <div className="stats">
            <span className="stat-item">Nodes: {stats.nodeCount}</span>
            <span className="stat-item">Edges: {stats.edgeCount}</span>
            <span className="stat-item">Last Update: {stats.lastUpdate}</span>
          </div>
        </div>
        <div className="header-right">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <main className="dashboard-content">
        <div className="graph-section">
          <div className="section-header">
            <h2>Network Graph</h2>
            <div className="graph-controls">
              <span className="graph-status">
                {graphData.nodes.length > 0 ? '● Active' : '● No Data'}
              </span>
            </div>
          </div>
          <NetworkGraph 
            graphData={graphData} 
            width={800} 
            height={600} 
          />
        </div>

        <div className="alerts-section">
          <AlertsFeed wsUrl="ws://localhost:8000/ws/alerts" />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
