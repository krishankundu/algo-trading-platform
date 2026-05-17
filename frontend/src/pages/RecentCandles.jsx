import "../styles/dashboard.css";
import DashboardNav from "../components/DashboardNav";
import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

export default function RecentCandles() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [candles, setCandles] = useState([]);

  const fetchCandles = async () => {
    try {
      const response = await axios.get(
        "https://api.binance.com/api/v3/klines",
        {
          params: {
            symbol,
            interval: "1h",
            limit: 100,
          },
        }
      );

      setCandles(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchCandles();
  }, [symbol]);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Recent Candles</h1>

        <DashboardNav />
      </div>

      <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
        <option value="BTCUSDT">BTCUSDT</option>
        <option value="ETHUSDT">ETHUSDT</option>
        <option value="BNBUSDT">BNBUSDT</option>
        <option value="SOLUSDT">SOLUSDT</option>
        <option value="XRPUSDT">XRPUSDT</option>
        <option value="ADAUSDT">ADAUSDT</option>
      </select>

      <div className="candles-grid">
        {candles.slice(-24).reverse().map((candle, index) => (
          <div key={index} className="candle-card">
            <p><strong>Open:</strong> {parseFloat(candle[1]).toFixed(2)}</p>
            <p><strong>High:</strong> {parseFloat(candle[2]).toFixed(2)}</p>
            <p><strong>Low:</strong> {parseFloat(candle[3]).toFixed(2)}</p>
            <p><strong>Close:</strong> {parseFloat(candle[4]).toFixed(2)}</p>
            <p><strong>Volume:</strong> {parseFloat(candle[5]).toFixed(2)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}