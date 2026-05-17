import "../styles/dashboard.css";
import DashboardNav from "../components/DashboardNav";
import { useEffect, useState } from "react";
import API from "../api/api";
import { Link } from "react-router-dom";

export default function TradeHistory() {
  const [trades, setTrades] = useState([]);

  const token = localStorage.getItem("token");

  const fetchTrades = async () => {
    try {
      const response = await API.get(
        "/trade/all",
        {
          params: {
            token,
          },
        }
      );

      setTrades(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Trade History</h1>

        <DashboardNav />
      </div>

      {trades.length === 0 ? (
        <p>No trades found</p>
      ) : (
        trades.map((trade) => (
          <div key={trade.id} className="trade-card">
            <h3>{trade.side}</h3>

            <p><strong>Symbol:</strong> {trade.symbol}</p>
            <p><strong>Price:</strong> {trade.price}</p>
            <p><strong>Quantity:</strong> {trade.quantity}</p>
          </div>
        ))
      )}
    </div>
  );
}