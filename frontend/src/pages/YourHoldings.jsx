import "../styles/dashboard.css";

import { useEffect, useState } from "react";
import API from "../api/api";
import DashboardNav from "../components/DashboardNav";

export default function YourHoldings() {
  const token = localStorage.getItem("token");

  const [portfolio, setPortfolio] = useState({
    balance: 0,
    realized_pnl: 0,
    total_trades: 0,
    holdings: [],
  });

  const fetchPortfolio = async () => {
    try {
      const response = await API.get(
        "/portfolio/me",
        {
            params: {
            token,
            },
        }
        );

      setPortfolio(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Your Holdings</h1>

        <DashboardNav />
      </div>

      <div className="portfolio-grid">
        <div className="portfolio-card">
          <h3>Balance</h3>
          <h2>${portfolio.balance.toFixed(2)}</h2>
        </div>

        <div className="portfolio-card">
          <h3>Realized PnL</h3>
          <h2
            className={
              portfolio.realized_pnl >= 0 ? "profit" : "loss"
            }
          >
            ${portfolio.realized_pnl.toFixed(2)}
          </h2>
        </div>

        <div className="portfolio-card">
          <h3>Total Trades</h3>
          <h2>{portfolio.total_trades}</h2>
        </div>

        <div className="portfolio-card">
          <h3>Total Holdings</h3>
          <h2>{portfolio.holdings.length}</h2>
        </div>
      </div>

      <div className="holdings-section">
        <h2>Holdings</h2>

        {portfolio.holdings.length === 0 ? (
          <p>No holdings found</p>
        ) : (
          <div className="holdings-grid">
            {portfolio.holdings.map((holding) => (
              <div
                key={holding.symbol}
                className="holding-card"
              >
                <h3>{holding.symbol}</h3>

                <p>
                  <strong>Quantity:</strong>{" "}
                  {holding.quantity.toFixed(6)}
                </p>

                <p>
                  <strong>Average Price:</strong> $
                  {holding.average_price.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}