import "../styles/dashboard.css";

import DashboardNav from "../components/DashboardNav";
import { useEffect, useState } from "react";
import API from "../api/api";

export default function YourStrategies() {
  const token = localStorage.getItem("token");

  const strategyTemplates = {
    RSI_REVERSAL: {
      label: "RSI Reversal",
      buy_condition: "RSI < 30",
      sell_condition: "RSI > 70",
    },
    MACD_CROSSOVER: {
      label: "MACD Crossover",
      buy_condition: "MACD crosses above Signal",
      sell_condition: "MACD crosses below Signal",
    },
    MACD_TREND: {
      label: "MACD Trend",
      buy_condition: "MACD > Signal",
      sell_condition: "MACD < Signal",
    },
    EMA_TREND: {
      label: "EMA Trend",
      buy_condition: "Price > EMA20",
      sell_condition: "Price < EMA20",
    },
    RSI_EMA_COMBO: {
      label: "RSI + EMA Combo",
      buy_condition: "RSI < 30 AND Price > EMA20",
      sell_condition: "RSI > 70 AND Price < EMA20",
    },
  };

  const availableSymbols = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
  ];

  const [strategies, setStrategies] = useState([]);

  const [formData, setFormData] = useState({
    name: "",
    symbol: "BTCUSDT",
    timeframe: "",
    strategy_type: "",
    buy_condition: "",
    sell_condition: "",
  });

  const fetchStrategies = async () => {
    try {
      const response = await API.get(
        "/strategy/all",
        {
          params: {
            token,
          },
        }
      );

      setStrategies(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleStrategyTypeChange = (e) => {
    const selectedType = e.target.value;
    const template = strategyTemplates[selectedType];

    setFormData({
      ...formData,
      strategy_type: selectedType,
      buy_condition: template ? template.buy_condition : "",
      sell_condition: template ? template.sell_condition : "",
    });
  };

  const createStrategy = async (e) => {
    e.preventDefault();

    const strategyName =
      formData.name.trim() !== ""
        ? formData.name.trim()
        : `Strategy ${strategies.length + 1}`;

    const timeframe =
      formData.timeframe.trim() !== ""
        ? formData.timeframe.trim()
        : "1h";

    try {
      await API.post(
        "/strategy/create",
        {
          name: strategyName,
          symbol: formData.symbol,
          timeframe,
          strategy_type: formData.strategy_type,
          buy_condition: formData.buy_condition,
          sell_condition: formData.sell_condition,
          trigger_enabled: false,
          order_quantity: 1,
        },
        {
          params: {
            token,
          },
        }
      );

      alert("Strategy Created");

      setFormData({
        name: "",
        symbol: "BTCUSDT",
        timeframe: "",
        strategy_type: "",
        buy_condition: "",
        sell_condition: "",
      });

      fetchStrategies();
    } catch (error) {
      console.error(error);
      alert("Failed to create strategy");
    }
  };

  const updateTriggerSettings = async (
    strategyId,
    triggerEnabled,
    orderQuantity
  ) => {
    const finalQuantity =
      Number(orderQuantity) > 0 ? Number(orderQuantity) : 1;

    try {
      const response = await API.put(
        `/strategy/trigger/${strategyId}`,
        {},
        {
          params: {
            trigger_enabled: triggerEnabled,
            order_quantity: finalQuantity,
            token,
          },
        }
      );

      fetchStrategies();
    } catch (error) {
      console.error(error);
      alert("Failed to update trigger settings");
    }
  };

  const deleteStrategy = async (id) => {
    try {
      await API.delete(
        `/strategy/delete/${id}`,
        {
          params: {
            token,
          },
        }
      );

      fetchStrategies();
    } catch (error) {
      console.error(error);
      alert("Failed to delete strategy");
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Your Strategies</h1>

        <DashboardNav />
      </div>

      <div className="strategy-section">
        <h2>Create Strategy</h2>

        <form className="strategy-form" onSubmit={createStrategy}>
          <input
            type="text"
            name="name"
            placeholder="Strategy Name Optional"
            value={formData.name}
            onChange={handleChange}
          />

          <select
            name="strategy_type"
            value={formData.strategy_type}
            onChange={handleStrategyTypeChange}
            required
          >
            <option value="">Select Strategy</option>

            {Object.entries(strategyTemplates).map(([key, template]) => (
              <option key={key} value={key}>
                {template.label}
              </option>
            ))}
          </select>

          <select
            name="symbol"
            value={formData.symbol}
            onChange={handleChange}
            required
          >
            {availableSymbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>

          <input
            type="text"
            name="timeframe"
            placeholder="Timeframe Optional Default: 1h"
            value={formData.timeframe}
            onChange={handleChange}
          />

          <input
            type="text"
            value={formData.buy_condition}
            placeholder="Buy Condition"
            readOnly
          />

          <input
            type="text"
            value={formData.sell_condition}
            placeholder="Sell Condition"
            readOnly
          />

          <button type="submit">Create Strategy</button>
        </form>
      </div>

      <div className="saved-strategies-section">
        <h2>Saved Strategies</h2>

        {strategies.length === 0 ? (
          <p>No strategies found</p>
        ) : (
          strategies.map((strategy) => (
            <div key={strategy.id} className="strategy-card">
              <h3>{strategy.name}</h3>

              <p>
                <strong>Symbol:</strong> {strategy.symbol}
              </p>

              <p>
                <strong>Timeframe:</strong> {strategy.timeframe}
              </p>

              <p>
                <strong>Type:</strong> {strategy.strategy_type}
              </p>

              <p>
                <strong>Buy:</strong> {strategy.buy_condition}
              </p>

              <p>
                <strong>Sell:</strong> {strategy.sell_condition}
              </p>

              <p>
                <strong>Trigger:</strong>{" "}
                {strategy.trigger_enabled ? "Enabled" : "Disabled"}
              </p>

              <p>
                <strong>Order Quantity:</strong>{" "}
                {strategy.order_quantity || 1}
              </p>

              <p>
                <strong>Last Signal:</strong>{" "}
                {strategy.last_signal || "WAIT"}
              </p>

              <div className="trigger-box">
                <label>
                  <input
                    type="checkbox"
                    checked={strategy.trigger_enabled || false}
                    onChange={(e) =>
                      updateTriggerSettings(
                        strategy.id,
                        e.target.checked,
                        strategy.order_quantity || 1
                      )
                    }
                  />
                  Enable Trigger Order
                </label>

                <input
                  type="number"
                  min="0"
                  step="0.000001"
                  defaultValue={strategy.order_quantity || 1}
                  onBlur={(e) =>
                    updateTriggerSettings(
                      strategy.id,
                      strategy.trigger_enabled || false,
                      e.target.value
                    )
                  }
                />
              </div>

              <button
                className="delete-button"
                onClick={() => deleteStrategy(strategy.id)}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}