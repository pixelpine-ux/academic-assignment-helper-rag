/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from 'react';
import { auth } from '../services/api';

const AuthContext = createContext(null);

const getInitialUser = () => {
  return auth.isAuthenticated() ? { authenticated: true } : null;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(getInitialUser);

  const login = async (email, password) => {
    const data = await auth.login(email, password);
    setUser({ authenticated: true, email });
    return data;
  };

  const logout = () => {
    auth.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
