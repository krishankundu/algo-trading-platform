import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot,
  Brush,
} from "recharts";

function StockChart({ chartData }) {

  const crossoverPoints = chartData.filter(
    (item) => item.crossover
  );

  return (
    <div className="chart-card">

      <h2 className="section-title">
        MACD Indicator Analysis
      </h2>

      <ResponsiveContainer
        width="100%"
        height={520}
      >

        <LineChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 10,
            bottom: 20,
          }}
        >

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#1e293b"
          />

          <XAxis
            dataKey="date"
            tick={{ fill: "#94a3b8" }}
            minTickGap={40}
          />

          <YAxis
            tick={{ fill: "#94a3b8" }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "12px",
              color: "#fff",
            }}
          />

          <Line
            type="monotone"
            dataKey="macd"
            stroke="#2962ff"
            strokeWidth={3}
            dot={false}
            name="MACD"
          />

          <Line
            type="monotone"
            dataKey="signal_line"
            stroke="#ffb300"
            strokeWidth={3}
            dot={false}
            name="Signal Line"
          />

          {crossoverPoints.map((point, index) => (

            <ReferenceDot
              key={index}
              x={point.date}
              y={point.macd}
              r={7}
              fill={
                point.signal === "BUY"
                  ? "#00e676"
                  : "#ff5252"
              }
              stroke="#ffffff"
              strokeWidth={2}
            />
          ))}

          <Brush
            dataKey="date"
            height={35}
            stroke="#2962ff"
            travellerWidth={12}
          />

        </LineChart>

      </ResponsiveContainer>

    </div>
  );
}

export default StockChart;