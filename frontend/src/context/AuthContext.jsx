import React, { createContext, useState, useEffect, useContext } from "react";
import { jwtDecode } from "jwt-decode";
import { api } from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const restoreAuth = async () => {
      const storedToken = localStorage.getItem("trippilot_token");
      if (!storedToken) {
        setLoading(false);
        return;
      }

      try {
        const decoded = jwtDecode(storedToken);
        const curTime = Date.now() / 1000;
        if (decoded.exp && decoded.exp <= curTime) {
          localStorage.removeItem("trippilot_token");
          setLoading(false);
          return;
        }

        setToken(storedToken);
        const userData = await api.get("/profile");
        setUser(userData);
      } catch (e) {
        localStorage.removeItem("trippilot_token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    restoreAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await api.post("/login", { email, password });
      localStorage.setItem("trippilot_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data.user;
    } catch (e) {
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      const data = await api.post("/register", { name, email, password });
      localStorage.setItem("trippilot_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data.user;
    } catch (e) {
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("trippilot_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
