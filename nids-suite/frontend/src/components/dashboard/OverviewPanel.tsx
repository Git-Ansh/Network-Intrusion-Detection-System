import React from 'react';

const OverviewPanel: React.FC = () => {
    const [metrics, setMetrics] = React.useState({
        packetsPerSecond: 0,
        anomalyRate: 0,
        cpuUsage: 0,
        memoryUsage: 0,
    });

    React.useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                setMetrics(data);
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        };

        const intervalId = setInterval(fetchMetrics, 5000); // Fetch metrics every 5 seconds
        fetchMetrics(); // Initial fetch

        return () => clearInterval(intervalId); // Cleanup on unmount
    }, []);

    return (
        <div className="overview-panel">
            <h2 className="text-lg font-semibold">Overview</h2>
            <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="metric">
                    <h3 className="text-sm">Packets/Sec</h3>
                    <p className="text-xl">{metrics.packetsPerSecond}</p>
                </div>
                <div className="metric">
                    <h3 className="text-sm">Anomaly Rate</h3>
                    <p className="text-xl">{metrics.anomalyRate}%</p>
                </div>
                <div className="metric">
                    <h3 className="text-sm">CPU Usage</h3>
                    <p className="text-xl">{metrics.cpuUsage}%</p>
                </div>
                <div className="metric">
                    <h3 className="text-sm">Memory Usage</h3>
                    <p className="text-xl">{metrics.memoryUsage}%</p>
                </div>
            </div>
        </div>
    );
};

export default OverviewPanel;