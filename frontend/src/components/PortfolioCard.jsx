import { Link } from "react-router-dom";

function PortfolioCard({ portfolio, onDelete, isDeleting }) {
  const isOwner = portfolio.my_role === "owner";

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
          <div className="portfolio-card-header">
            <h3 className="portfolio-card-title">{portfolio.name}</h3>
            <RoleBadge role={portfolio.my_role} />
          </div>
          <p className="portfolio-card-description">{portfolio.description}</p>
          <p className="portfolio-card-meta">
            Holdings: {portfolio.investments_count ?? 0}
          </p>
        </div>

        {isOwner && (
          <div className="portfolio-card-actions">
            <button
              className="danger-button"
              onClick={handleDeleteClick}
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </button>
          </div>
        )}
      </div>
    </Link>
  );
}

function RoleBadge({ role }) {
  if (!role || role === "none") return null;

  const className = `role-badge role-${role}`;
  const label = role.charAt(0).toUpperCase() + role.slice(1);
  return <span className={className}>{label}</span>;
}

export default PortfolioCard;