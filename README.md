# Algo Trading Platform

A full-stack algorithmic trading simulation platform built with FastAPI, React, PostgreSQL, and real-time market data.  
The system allows users to register, log in, view live crypto market data, create trading strategies, simulate paper trades, manage holdings, and track trade history.

## Live Demo

Frontend: https://algo-trading-platform-theta.vercel.app  
Backend API Docs: https://algo-trading-backend-dvwt.onrender.com/docs

## GitHub Repository

https://github.com/krishankundu/algo-trading-platform

---

## Project Overview

This project is designed as a trading dashboard and paper-trading system where users can:

- Register and log in securely
- View live market prices
- View candlestick data
- Analyze indicators such as RSI, EMA, and MACD
- Create predefined trading strategies
- Enable trigger-based strategy execution
- Execute manual paper trades
- Track holdings
- View trade history
- Monitor portfolio balance and realized profit/loss

The platform does not place real trades. It is a simulated paper-trading system for educational and demonstration purposes.

---

## Tech Stack

### Frontend

- React
- Vite
- React Router
- Axios
- ApexCharts
- TradingView Widget
- CSS

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Python
- yfinance
- pandas
- ta

### Deployment

- Frontend: Vercel
- Backend: Render
- Database: Render PostgreSQL

---

## Main Features

### 1. Authentication

Users can:

- Register
- Log in
- Access protected routes
- Log out

Authentication is handled using JWT tokens.

---

### 2. Trading Dashboard

The dashboard displays:

- Logged-in username
- Portfolio balance
- Realized PnL
- Live market price
- RSI value
- EMA value
- MACD chart
- TradingView chart
- Manual BUY/SELL order panel

---

### 3. Market Data

The backend provides market data endpoints such as:

```txt
GET /market/price/{symbol}
GET /market/candles/{symbol}