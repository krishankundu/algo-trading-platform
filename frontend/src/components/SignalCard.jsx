function SignalCard({ signal }) {

  const getColor = () => {

    if (signal === "BUY") {
      return "#00C853";
    }

    if (signal === "SELL") {
      return "#D50000";
    }

    return "#FFD600";
  };

  return (

    <div
      style={{
        background: "#1e293b",
        padding: "20px",
        borderRadius: "12px",
        marginBottom: "20px",
        display: "inline-block",
      }}
    >

      <h3
        style={{
          color: "#94a3b8",
        }}
      >
        Current Signal
      </h3>

      <h1
        style={{
          color: getColor(),
          marginTop: "10px",
        }}
      >
        {signal}
      </h1>

    </div>
  );
}

export default SignalCard;