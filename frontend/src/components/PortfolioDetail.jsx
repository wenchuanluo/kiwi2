import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getPortfolioById } from "../services/portfolioService";
import BuyForm from "./BuyForm";
import SellForm from "./SellForm";
import TransactionHistory from "./TransactionHistory";

function PortfolioDetail() {
  const { id } = useParams();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshSignal, setRefreshSignal] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const loadPortfolio = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPortfolioById(id);
        if (!cancelled) {
          setPortfolio(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              err.message ||
              "Failed to load portfolio."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadPortfolio();

    return () => {
      cancelled = true;
    };
  }, [id, refreshSignal]);

  const handleTradeCompleted = () => {
    setRefreshSignal((prev) => prev + 1);
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <header className="dashboard-header">
          <Link to="/dashboard" className="back-link">
            ← Back to Dashboard
          </Link>
        </header>
        <main className="dashboard-content">
          <p className="muted">Loading portfolio...</p>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <header className="dashboard-header">
          <Link to="/dashboard" className="back-link">
            ← Back to Dashboard
          </Link>
        </header>
        <main className="dashboard-content">
          <p className="error-text">{error}</p>
        </main>
      </div>
    );
  }

  if (!portfolio) {
    return null;
  }

  const role = portfolio.my_role;
  const canTrade = role === "owner" || role === "manager";

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <Link to="/dashboard" className="back-link">
            ← Back to Dashboard
          </Link>
          <div className="portfolio-title-row">
            <h1>{portfolio.name}</h1>
            <RoleBadge role={role} />
          </div>
          <p>{portfolio.description}</p>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Holdings</h2>
          </div>

          {portfolio.investments.length === 0 ? (
            <p className="muted">
              {canTrade
                ? "No holdings yet. Use the Buy form below to purchase your first shares."
                : "No holdings yet."}
            </p>
          ) : (
            <table className="holdings-table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Quantity</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.investments.map((investment) => (
                  <tr key={investment.ticker}>
                    <td className="ticker">{investment.ticker}</td>
                    <td>{investment.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {canTrade ? (
          <div className="trade-grid">
            <div className="dashboard-section">
              <BuyForm
                portfolioId={portfolio.id}
                onTradeCompleted={handleTradeCompleted}
              />
            </div>

            <div className="dashboard-section">
              <SellForm
                portfolioId={portfolio.id}
                holdings={portfolio.investments}
                onTradeCompleted={handleTradeCompleted}
              />
            </div>
          </div>
        ) : (
          <div className="dashboard-section">
            <p className="muted">
              You have <strong>view-only access</strong> to this portfolio.
              Trading actions are not available.
            </p>
          </div>
        )}

        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Transaction History</h2>
          </div>
          <TransactionHistory
            portfolioId={portfolio.id}
            refreshSignal={refreshSignal}
          />
        </div>
      </main>
    </div>
  );
}

function RoleBadge({ role }) {
  if (!role || role === "none") return null;

  const className = `role-badge role-${role}`;
  const label = role.charAt(0).toUpperCase() + role.slice(1);
  return <span className={className}>{label}</span>;
}

export default PortfolioDetail;