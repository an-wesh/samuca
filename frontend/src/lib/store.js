import { create } from "zustand";

export const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem("user") || "null"),
  token: localStorage.getItem("token"),
  setAuth: (user, token) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    set({ user, token });
  },
  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    set({ user: null, token: null });
  },
}));

export const useMarketStore = create((set) => ({
  currentSymbol: "BTCUSD",
  timeframe: "1h",
  setSymbol: (currentSymbol) => set({ currentSymbol }),
  setTimeframe: (timeframe) => set({ timeframe }),
}));
