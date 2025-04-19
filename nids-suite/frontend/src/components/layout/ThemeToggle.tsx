// filepath: /nids-suite/nids-suite/frontend/src/components/layout/ThemeToggle.tsx

import React, { useContext } from 'react';
import { ThemeContext } from '../../contexts/ThemeContext';

const ThemeToggle: React.FC = () => {
    const { theme, toggleTheme } = useContext(ThemeContext);

    return (
        <button
            onClick={toggleTheme}
            className={`p-2 rounded-md transition-colors duration-300 ${
                theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-gray-200 text-black'
            }`}
        >
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
    );
};

export default ThemeToggle;