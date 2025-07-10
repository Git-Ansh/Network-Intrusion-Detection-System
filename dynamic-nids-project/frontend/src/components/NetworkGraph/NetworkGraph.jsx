// frontend/src/components/NetworkGraph/NetworkGraph.jsx

import React, { useState, useEffect, useRef, useMemo } from 'react';
import * as d3 from 'd3';
import './NetworkGraph.css';

const NetworkGraph = ({ graphData, width, height }) => {
  const svgRef = useRef();
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);

  // Memoize the simulation setup to avoid re-creating it on every render
  const simulation = useMemo(() => {
    return d3.forceSimulation()
      .force('link', d3.forceLink().id(d => d.id).distance(50))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(20));
  }, [width, height]);

  // Update simulation when data changes
  useEffect(() => {
    if (!graphData || !graphData.nodes || !graphData.links) return;

    const newNodes = graphData.nodes.map(node => ({ ...node }));
    const newLinks = graphData.links.map(link => ({ ...link }));

    setNodes(newNodes);
    setLinks(newLinks);

    simulation.nodes(newNodes);
    simulation.force('link').links(newLinks);
    simulation.alpha(1).restart();

    // Set up the simulation tick handler
    simulation.on('tick', () => {
      setNodes([...newNodes]);
      setLinks([...newLinks]);
    });
  }, [graphData, simulation]);

  // D3 rendering logic
  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    // Create links
    const linkElements = svg.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke-width', d => Math.sqrt(d.weight || 1));

    // Create nodes
    const nodeElements = svg.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', 8)
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add labels
    const labelElements = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .attr('class', 'node-label')
      .text(d => d.id)
      .attr('dy', -12);

    // Update positions on tick
    const updatePositions = () => {
      linkElements
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      nodeElements
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      labelElements
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    };

    simulation.on('tick', updatePositions);

    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

  }, [nodes, links, simulation]);

  return (
    <div className="network-graph-container">
      <svg
        ref={svgRef}
        className="network-graph"
        width={width}
        height={height}
      />
    </div>
  );
};

export default NetworkGraph;
