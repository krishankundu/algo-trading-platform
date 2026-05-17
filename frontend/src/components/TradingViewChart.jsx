import { useEffect, useRef } from "react";

function TradingViewChart({ symbol }) {

  const container = useRef();

  useEffect(() => {

    container.current.innerHTML = "";

    const script = document.createElement("script");

    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";

    script.type = "text/javascript";

    script.async = true;

    script.innerHTML = JSON.stringify({

      autosize: true,

      symbol: symbol || "NASDAQ:AAPL",

      interval: "D",

      timezone: "Asia/Kolkata",

      theme: "dark",

      style: "1",

      locale: "en",

      enable_publishing: false,

      allow_symbol_change: true,

      hide_top_toolbar: false,

      hide_legend: true,

      hide_side_toolbar: false,

      save_image: false,

      details: false,

      hotlist: false,

      calendar: false,

      studies: [],

      withdateranges: true,

      support_host: "https://www.tradingview.com"
    });

    container.current.appendChild(script);

  }, [symbol]);

  return (

    <div
      style={{
        width: "100%",
        height: "70vh",
        minHeight: "500px",
        maxHeight: "900px",
        marginTop: "25px",
        borderRadius: "20px",
        overflow: "hidden",
        border: "1px solid rgba(255,255,255,0.08)",
        background: "#0b1220",
      }}
    >

      <div
        ref={container}
        style={{
          width: "100%",
          height: "100%",
        }}
      />

    </div>
  );
}

export default TradingViewChart;