import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { supabase } from '../../lib/supabase';
import { useAuth } from '../../contexts/AuthContext';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const history = useHistory();
    const { setUser } = useAuth();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const { user, error } = await supabase.auth.signIn({
                email,
                password,
            });

            if (error) throw error;

            setUser(user);
            history.push('/dashboard');
        } catch (error) {
            setError(error.message);
        }
    };

    return (
        <div className="flex items-center justify-center h-screen">
            <form onSubmit={handleLogin} className="bg-white p-6 rounded shadow-md w-96">
                <h2 className="text-2xl mb-4">Login</h2>
                {error && <p className="text-red-500 mb-4">{error}</p>}
                <div className="mb-4">
                    <label className="block mb-2" htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="border rounded w-full p-2"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-2" htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="border rounded w-full p-2"
                        required
                    />
                </div>
                <button type="submit" className="bg-blue-500 text-white rounded w-full p-2">Login</button>
            </form>
        </div>
    );
};

export default LoginPage;