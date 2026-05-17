import { Link, useLocation, useNavigate } from "react-router-dom";

export default function DashboardNav() {
  const location = useLocation();
  const navigate = useNavigate();

  const links = [
    {
      label: "Dashboard",
      path: "/dashboard",
    },
    {
      label: "Recent Candles",
      path: "/recent-candles",
    },
    {
      label: "Your Strategies",
      path: "/strategies",
    },
    {
      label: "Your Holdings",
      path: "/holdings",
    },
    {
      label: "Trade History",
      path: "/trade-history",
    },
  ];

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="dashboard-links">
      {links.map((link) => {
        const isActive = location.pathname === link.path;

        if (isActive) {
          return (
            <span
              key={link.path}
              className="dashboard-link disabled-link"
            >
              {link.label}
            </span>
          );
        }

        return (
          <Link
            key={link.path}
            to={link.path}
            className="dashboard-link"
          >
            {link.label}
          </Link>
        );
      })}

      <button
        type="button"
        className="logout-button"
        onClick={handleLogout}
      >
        Logout
      </button>
    </div>
  );
}