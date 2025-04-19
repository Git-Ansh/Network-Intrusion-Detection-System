import React from 'react';

interface AlertItemProps {
    alert: {
        id: string;
        timestamp: string;
        severity: 'low' | 'medium' | 'high';
        message: string;
    };
}

const AlertItem: React.FC<AlertItemProps> = ({ alert }) => {
    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'low':
                return 'bg-green-100 text-green-800';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800';
            case 'high':
                return 'bg-red-100 text-red-800';
            default:
                return '';
        }
    };

    return (
        <div className={`p-4 rounded-md shadow-md ${getSeverityColor(alert.severity)}`}>
            <h3 className="font-bold">{alert.timestamp}</h3>
            <p>{alert.message}</p>
        </div>
    );
};

export default AlertItem;