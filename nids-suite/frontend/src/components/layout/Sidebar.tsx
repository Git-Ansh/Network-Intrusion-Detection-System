import React from 'react';
import { Link } from 'react-router-dom';

const Sidebar: React.FC = () => {
    return (
        <div className="flex flex-col h-full bg-gray-800 text-white p-4">
            <h2 className="text-lg font-bold mb-4">NIDS Suite</h2>
            <nav className="flex-1">
                <ul className="space-y-2">
                    <li>
                        <Link to="/dashboard" className="block p-2 hover:bg-gray-700 rounded">
                            Dashboard
                        </Link>
                    </li>
                    <li>
                        <Link to="/alerts" className="block p-2 hover:bg-gray-700 rounded">
                            Alerts
                        </Link>
                    </li>
                    <li>
                        <Link to="/network-map" className="block p-2 hover:bg-gray-700 rounded">
                            Network Map
                        </Link>
                    </li>
                    <li>
                        <Link to="/packet-explorer" className="block p-2 hover:bg-gray-700 rounded">
                            Packet Explorer
                        </Link>
                    </li>
                    <li>
                        <Link to="/settings" className="block p-2 hover:bg-gray-700 rounded">
                            Settings
                        </Link>
                    </li>
                </ul>
            </nav>
            <footer className="mt-auto">
                <p className="text-sm">© 2023 NIDS Suite</p>
            </footer>
        </div>
    );
};

export default Sidebar;