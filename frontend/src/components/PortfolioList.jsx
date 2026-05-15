import { useEffect, useState } from "react";
import {
  getMyPortfolios,
  deletePortfolio,
} from "../services/portfolioService";
import PortfolioCard from "./PortfolioCard";

function PortfolioList({ refreshSignal }) {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const loadPortfolios = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMyPortfolios();
      setPortfolios(data);
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Failed to load portfolios."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolios();
  }, [refreshSignal]);

  const handleDelete = async (portfolioId) => {
    setDeletingId(portfolioId);
    setError(null);
    try {
      await deletePortfolio(portfolioId);
      await loadPortfolios();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to delete portfolio."
      );
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return <p className="muted">Loading portfolios...</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (portfolios.length === 0) {
    return (
      <p className="muted">
        You have no portfolios yet. Click "Create Portfolio" to get started.
      </p>
    );
  }

  return (
    <div className="portfolio-grid">
      {portfolios.map((portfolio) => (
        <PortfolioCard
          key={portfolio.id}
          portfolio={portfolio}
          onDelete={handleDelete}
          isDeleting={deletingId === portfolio.id}
        />
      ))}
    </div>
  );
}

export default PortfolioList;