import React from 'react';
import { Header } from '../layout/Header';
import { Sidebar } from '../layout/Sidebar';

const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <div className="flex">
            <Sidebar />
            <div className="flex-1">
                <Header />
                <main className="p-4">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;