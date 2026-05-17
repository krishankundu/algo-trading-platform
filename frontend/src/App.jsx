import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import RecentCandles from "./pages/RecentCandles";
import YourStrategies from "./pages/YourStrategies";
import TradeHistory from "./pages/TradeHistory";
import YourHoldings from "./pages/YourHoldings";

import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />

        <Route path="/login" element={<Login />} />

        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/recent-candles"
          element={
            <ProtectedRoute>
              <RecentCandles />
            </ProtectedRoute>
          }
        />

        <Route
          path="/strategies"
          element={
            <ProtectedRoute>
              <YourStrategies />
            </ProtectedRoute>
          }
        />

          <Route
            path="/holdings"
            element={
              <ProtectedRoute>
                <YourHoldings />
              </ProtectedRoute>
            }
          />

        <Route
          path="/trade-history"
          element={
            <ProtectedRoute>
              <TradeHistory />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;