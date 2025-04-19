import React, { useEffect, useState } from 'react';
import { ForceGraph2D } from 'react-force-graph';
import { fetchNetworkData } from '../../lib/api'; // Adjust the import path as necessary

const NetworkMap = () => {
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });

    useEffect(() => {
        const loadNetworkData = async () => {
            try {
                const data = await fetchNetworkData();
                setGraphData(data);
            } catch (error) {
                console.error('Error fetching network data:', error);
            }
        };

        loadNetworkData();
    }, []);

    return (
        <div className="network-map">
            <h2 className="text-xl font-bold mb-4">Network Map</h2>
            <ForceGraph2D
                graphData={graphData}
                nodeAutoColorBy="group"
                onNodeClick={(node) => alert(`Node: ${node.id}`)}
                width={window.innerWidth}
                height={window.innerHeight - 100}
            />
        </div>
    );
};

export default NetworkMap;