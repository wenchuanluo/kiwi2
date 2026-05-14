import { Link } from "react-router-dom";

function PortfolioCard({ portfolio, onDelete, isDeleting }) {
  const handleDeleteClick = (event) => {
    event.preventDefault();
    event.stopPropagation();

    const confirmed = window.confirm(
      `Delete portfolio "${portfolio.name}"? This cannot be undone.`
    );
    if (confirmed) {
      onDelete(portfolio.id);
    }
  };

  return (
    <Link to={`/portfolios/${portfolio.id}`} className="portfolio-card-link">
      <div className="portfolio-card">
        <div className="portfolio-card-body">
          <h3 className="portfolio-card-title">{portfolio.name}</h3>
          <p className="portfolio-card-description">{portfolio.description}</p>
          <p className="portfolio-card-meta">
            Holdings: {portfolio.investments_count ?? 0}
          </p>
        </div>

        <div className="portfolio-card-actions">
          <button
            className="danger-button"
            onClick={handleDeleteClick}
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </Link>
  );
}

export default PortfolioCard;