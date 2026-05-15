import { useEffect, useState } from "react";
import { getPortfolioTransactions } from "../services/portfolioService";

function TransactionHistory({ portfolioId, refreshSignal }) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const loadTransactions = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPortfolioTransactions(portfolioId);
        if (!cancelled) {
          setTransactions(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              err.message ||
              "Failed to load transactions."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadTransactions();

    return () => {
      cancelled = true;
    };
  }, [portfolioId, refreshSignal]);

  if (loading) {
    return <p className="muted">Loading transactions...</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (transactions.length === 0) {
    return (
      <p className="muted">
        No transactions yet. Once you place a buy or sell order, it will
        appear here.
      </p>
    );
  }

  const sortedTransactions = [...transactions].sort(
    (a, b) => new Date(b.date_time) - new Date(a.date_time)
  );

  return (
    <table className="transactions-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Ticker</th>
          <th>Type</th>
          <th>Quantity</th>
          <th>Price</th>
        </tr>
      </thead>
      <tbody>
        {sortedTransactions.map((tx) => (
          <tr key={tx.transaction_id}>
            <td>{formatDateTime(tx.date_time)}</td>
            <td className="ticker">{tx.ticker}</td>
            <td>
              <span
                className={
                  tx.transaction_type === "BUY"
                    ? "tag tag-buy"
                    : "tag tag-sell"
                }
              >
                {tx.transaction_type}
              </span>
            </td>
            <td>{tx.quantity}</td>
            <td>${Number(tx.price).toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function formatDateTime(isoString) {
  try {
    const date = new Date(isoString);
    return date.toLocaleString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}

export default TransactionHistory;