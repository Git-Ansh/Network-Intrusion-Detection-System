import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
    return (
        <header className="bg-gray-800 text-white p-4 flex justify-between items-center">
            <div className="text-lg font-bold">
                <Link to="/">NIDS Suite</Link>
            </div>
            <nav>
                <ul className="flex space-x-4">
                    <li>
                        <Link to="/dashboard" className="hover:underline">Dashboard</Link>
                    </li>
                    <li>
                        <Link to="/alerts" className="hover:underline">Alerts</Link>
                    </li>
                    <li>
                        <Link to="/network-map" className="hover:underline">Network Map</Link>
                    </li>
                    <li>
                        <Link to="/packet-explorer" className="hover:underline">Packet Explorer</Link>
                    </li>
                    <li>
                        <Link to="/settings" className="hover:underline">Settings</Link>
                    </li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;