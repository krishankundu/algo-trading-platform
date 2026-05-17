import "../styles/dashboard.css";
import DashboardNav from "../components/DashboardNav";
import { Link } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { RSI, EMA, MACD } from "technicalindicators";
import Chart from "react-apexcharts";
import axios from "axios";
import API from "../api/api";

export default function Dashboard() {
  const chartRef = useRef(null);

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

  const [user, setUser] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [trades, setTrades] = useState([]);
  const [orderQuantity, setOrderQuantity] = useState("");
  const [formData, setFormData] = useState({
    name: "",
    symbol: "BTCUSDT",
    timeframe: "",
    strategy_type: "",
    buy_condition: "",
    sell_condition: "",
  });
  const [dashboardStrategyType, setDashboardStrategyType] = useState("RSI_EMA_COMBO");
  const [selectedSymbol, setSelectedSymbol] = useState("BTCUSDT");
  const [price, setPrice] = useState(null);
  const [candles, setCandles] = useState([]);
  const [strategySignals, setStrategySignals] = useState([]);
  const [signal, setSignal] = useState("WAIT");
  const [rsiValue, setRsiValue] = useState(null);
  const [emaValue, setEmaValue] = useState(null);
  const [macdData, setMacdData] = useState([]);
  const [signalData, setSignalData] = useState([]);
  const [histogramData, setHistogramData] = useState([]);

  const [portfolio, setPortfolio] = useState({
    balance: 0,
    realized_pnl: 0,
    holdings: [],
    total_trades: 0,
  });

  const fetchUser = async () => {
    try {
      const response = await API.get(
        "/user/me",
        {
          params: {
            token,
          },
        }
      );

      setUser(response.data);
    } catch (error) {
      console.error(error);
    }
  };

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
  const fetchStrategySignals = async () => {
    try {
      const response = await API.get(
        "/signal/all",
        {
          params: {
            token,
          },
        }
      );

      setStrategySignals(response.data);

      fetchTrades();
      fetchPortfolio();
    } catch (error) {
      console.error(error);
    }
  };
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

  const fetchPrice = async () => {
    try {
      const response = await API.get(
        `/market/price/${selectedSymbol}`
      );

      setPrice(response.data.price);
    } catch (error) {
      console.error(error);
    }
  };

  const calculateSignalByStrategy = ({
    strategyType,
    latestRSI,
    latestPrice,
    latestEMA,
    latestMACD,
    latestMACDSignal,
    previousMACD,
    previousMACDSignal,
  }) => {
    if (strategyType === "RSI_REVERSAL") {
      if (latestRSI < 30) return "BUY";
      if (latestRSI > 70) return "SELL";
      return "WAIT";
    }

    if (strategyType === "MACD_CROSSOVER") {
      if (
        previousMACD <= previousMACDSignal &&
        latestMACD > latestMACDSignal
      ) {
        return "BUY";
      }

      if (
        previousMACD >= previousMACDSignal &&
        latestMACD < latestMACDSignal
      ) {
        return "SELL";
      }

      return "WAIT";
    }

  
    if (strategyType === "MACD_TREND") {
      if (latestMACD > latestMACDSignal) return "BUY";
      if (latestMACD < latestMACDSignal) return "SELL";
      return "WAIT";
    }

    if (strategyType === "EMA_TREND") {
      if (latestPrice > latestEMA) return "BUY";
      if (latestPrice < latestEMA) return "SELL";
      return "WAIT";
    }

    if (strategyType === "RSI_EMA_COMBO") {
      if (latestRSI < 30 && latestPrice > latestEMA) return "BUY";
      if (latestRSI > 70 && latestPrice < latestEMA) return "SELL";
      return "WAIT";
    }

    return "WAIT";
  };

  const fetchCandles = async () => {
    try {
      const response = await axios.get(
        "https://api.binance.com/api/v3/klines",
        {
          params: {
            symbol: selectedSymbol,
            interval: "1h",
            limit: 100,
          },
        }
      );

      const candleData = response.data;

      setCandles(candleData);

      const closes = candleData.map((candle) =>
        parseFloat(candle[4])
      );

      const rsi = RSI.calculate({
        values: closes,
        period: 14,
      });

      const ema = EMA.calculate({
        values: closes,
        period: 20,
      });

      const macd = MACD.calculate({
        values: closes,
        fastPeriod: 12,
        slowPeriod: 26,
        signalPeriod: 9,
        SimpleMAOscillator: false,
        SimpleMASignal: false,
      });

      setMacdData(
        macd.map((item, index) => ({
          x: index,
          y: item.MACD,
        }))
      );

      setSignalData(
        macd.map((item, index) => ({
          x: index,
          y: item.signal,
        }))
      );

      setHistogramData(
        macd.map((item, index) => ({
          x: index,
          y: item.histogram,
        }))
      );

      const latestRSI = rsi[rsi.length - 1];
      const latestEMA = ema[ema.length - 1];
      const latestPrice = closes[closes.length - 1];

      if (!latestRSI || !latestEMA || !latestPrice) {
        return;
      }

      setRsiValue(latestRSI.toFixed(2));
      setEmaValue(latestEMA.toFixed(2));

      const latestMACD = macd[macd.length - 1]?.MACD;
      const latestMACDSignal = macd[macd.length - 1]?.signal;

      const previousMACD = macd[macd.length - 2]?.MACD;
      const previousMACDSignal = macd[macd.length - 2]?.signal;

      const generatedSignal = calculateSignalByStrategy({
        strategyType: dashboardStrategyType,
        latestRSI,
        latestPrice,
        latestEMA,
        latestMACD,
        latestMACDSignal,
        previousMACD,
        previousMACDSignal,
      });

setSignal(generatedSignal);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchUser();
    fetchStrategies();
    fetchTrades();
    fetchPortfolio();
    fetchPrice();
    fetchCandles();
  }, []);

  useEffect(() => {
    setPrice(null);
    fetchPrice();
    fetchCandles();
  }, [selectedSymbol, dashboardStrategyType]);

  useEffect(() => {
    fetchStrategySignals();

    const interval = setInterval(() => {
      fetchStrategySignals();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/price/${selectedSymbol}`
    );

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPrice(data.price);
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket Closed");
    };

    return () => {
      if (
        socket.readyState === WebSocket.OPEN ||
        socket.readyState === WebSocket.CONNECTING
      ) {
        socket.close();
      }
    };
  }, [selectedSymbol]);

  useEffect(() => {
    if (!chartRef.current) return;

    chartRef.current.innerHTML = "";

    const container = document.createElement("div");

    container.className = "tradingview-widget-container__widget";

    container.style.height = "100%";
    container.style.width = "100%";

    chartRef.current.appendChild(container);

    const script = document.createElement("script");

    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";

    script.type = "text/javascript";
    script.async = true;

    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: `BINANCE:${selectedSymbol}`,
      interval: "60",
      timezone: "Etc/UTC",
      theme: "dark",
      style: "1",
      locale: "en",
      enable_publishing: false,
      allow_symbol_change: true,
      hide_top_toolbar: false,
      hide_legend: false,
      withdateranges: true,
    });

    chartRef.current.appendChild(script);

    return () => {
      if (chartRef.current) {
        chartRef.current.innerHTML = "";
      }
    };
  }, [selectedSymbol]);

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
      await axios.post(
        "http://127.0.0.1:8000/strategy/create",
        {
          name: strategyName,
          symbol: formData.symbol,
          timeframe,
          strategy_type: formData.strategy_type,
          buy_condition: formData.buy_condition,
          sell_condition: formData.sell_condition,
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

  const executeTrade = async (side) => {
    try {
      await API.post(
        "/trade/create",
        {},
        {
          params: {
            symbol: selectedSymbol,
            side,
            price,
            quantity: Number(orderQuantity) > 0 ? Number(orderQuantity) : 1,
            token,
          },
        }
      );

      fetchTrades();
      fetchPortfolio();

      alert(`${side} order executed`);
    } catch (error) {
      console.error(error);
      alert("Trade failed");
    }
  };

 
  const totalHoldingQuantity = portfolio.holdings.reduce(
    (total, item) => total + item.quantity,
    0
  );

  const estimatedHoldingValue = portfolio.holdings.reduce(
    (total, item) => {
      if (item.symbol === selectedSymbol) {
        return total + item.quantity * Number(price || 0);
      }

      return total + item.quantity * item.average_price;
    },
    0
  );

  const portfolioValue = portfolio.balance + estimatedHoldingValue;

  const pnl = portfolio.realized_pnl || 0;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Trading Dashboard</h1>

          <p className="dashboard-user">
            Welcome, {user ? user.username : "User"}
          </p>
        </div>

        <DashboardNav />
      </div>

      <div className="portfolio-grid">
        <div className="portfolio-card">
          <h3>Total Holdings</h3>
          <h2>{totalHoldingQuantity.toFixed(4)}</h2>
        </div>

        <div className="portfolio-card">
          <h3>Portfolio Value</h3>
          <h2>${portfolioValue.toFixed(2)}</h2>
        </div>

        <div className="portfolio-card">
          <h3>Realized PnL</h3>
          <h2 className={pnl >= 0 ? "profit" : "loss"}>
            ${pnl.toFixed(2)}
          </h2>
        </div>
      </div>

      <div className="market-section">
        <div className="market-header">
          <h2>Live Market Data</h2>

          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
          >
            {availableSymbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>
        </div>

        <h2 className="current-price">
          Current Price: ${price}
        </h2>

          <div className="signal-strategy-box">
            <label>Signal Strategy</label>

            <select
              value={dashboardStrategyType}
              onChange={(e) => setDashboardStrategyType(e.target.value)}
            >
              <option value="RSI_REVERSAL">RSI Reversal</option>
              <option value="MACD_CROSSOVER">MACD Crossover</option>
              <option value="MACD_TREND">MACD Trend</option>
              <option value="EMA_TREND">EMA Trend</option>
              <option value="RSI_EMA_COMBO">RSI + EMA Combo</option>
            </select>
          </div>

        <div className="indicator-grid">
          <div className="indicator-card">
            <h3>RSI</h3>
            <p>{rsiValue}</p>
          </div>

          <div className="indicator-card">
            <h3>EMA(20)</h3>
            <p>{emaValue}</p>
          </div>

          

          <div className="indicator-card">
            <h3>Signal</h3>
            <p
              className={
                signal === "BUY"
                  ? "profit"
                  : signal === "SELL"
                  ? "loss"
                  : ""
              }
            >
              {signal}
            </p>
          </div>
        </div>



        <div className="order-quantity-box">
          <label>Order Quantity</label>

          <input
            type="number"
            min="0"
            step="0.000001"
            placeholder="Default: 1"
            value={orderQuantity}
            onChange={(e) => setOrderQuantity(e.target.value)}
          />
        </div>

        <div className="trade-buttons">
          <button
            className="buy-button"
            onClick={() => executeTrade("BUY")}
          >
            BUY
          </button>

          <button
            className="sell-button"
            onClick={() => executeTrade("SELL")}
          >
            SELL
          </button>
        </div>

        <div className="tv-chart-wrapper">
          <div
            ref={chartRef}
            className="tradingview-widget-container"
          />
        </div>

        <div className="macd-section">
          <h2>MACD Indicator</h2>

          <Chart
            options={{
              chart: {
                id: "macd-chart",
                toolbar: {
                  show: false,
                },
                background: "transparent",
              },
              theme: {
                mode: "dark",
              },
              xaxis: {
                type: "numeric",
              },
              stroke: {
                width: [2, 2, 0],
              },
              plotOptions: {
                bar: {
                  columnWidth: "60%",
                },
              },
            }}
            series={[
              {
                name: "MACD",
                type: "line",
                data: macdData,
              },
              {
                name: "Signal",
                type: "line",
                data: signalData,
              },
              {
                name: "Histogram",
                type: "column",
                data: histogramData,
              },
            ]}
            type="line"
            height={350}
          />
        </div>
      </div>
    </div>
  );
}