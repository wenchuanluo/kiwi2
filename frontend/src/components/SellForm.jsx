import { useState } from "react";
import { executeSell } from "../services/tradeService";

function SellForm({ portfolioId, holdings, onTradeCompleted }) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  if (holdings.length === 0) {
    return (
      <div className="trade-form">
        <h3>Sell</h3>
        <p className="muted">
          No holdings to sell. Buy some shares first.
        </p>
      </div>
    );
  }

  const selectedHolding = holdings.find((h) => h.ticker === ticker);
  const maxQuantity = selectedHolding ? selectedHolding.quantity : null;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!ticker) {
      setError("Please select a holding to sell.");
      return;
    }

    const numericQuantity = Number(quantity);
    if (!Number.isInteger(numericQuantity) || numericQuantity <= 0) {
      setError("Quantity must be a positive integer.");
      return;
    }

    if (maxQuantity !== null && numericQuantity > maxQuantity) {
      setError(`You only have ${maxQuantity} share(s) of ${ticker}.`);
      return;
    }

    setSubmitting(true);
    try {
      await executeSell({
        portfolioId,
        ticker,
        quantity: numericQuantity,
      });
      setSuccessMessage(
        `Sold ${numericQuantity} share(s) of ${ticker}.`
      );
      setTicker("");
      setQuantity("");
      onTradeCompleted();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to execute sell order."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="trade-form">
      <h3>Sell</h3>

      <div className="trade-form-row">
        <label className="form-field">
          <span className="form-label">Holding</span>
          <select
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            disabled={submitting}
          >
            <option value="">Select a holding...</option>
            {holdings.map((h) => (
              <option key={h.ticker} value={h.ticker}>
                {h.ticker} ({h.quantity} share{h.quantity === 1 ? "" : "s"})
              </option>
            ))}
          </select>
        </label>

        <label className="form-field">
          <span className="form-label">
            Quantity {maxQuantity !== null && `(max ${maxQuantity})`}
          </span>
          <input
            type="number"
            min="1"
            step="1"
            max={maxQuantity ?? undefined}
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="e.g. 5"
            disabled={submitting}
          />
        </label>
      </div>

      {error && <p className="error-text">{error}</p>}
      {successMessage && <p className="success-text">{successMessage}</p>}

      <button type="submit" className="primary-button" disabled={submitting}>
        {submitting ? "Placing order..." : "Sell"}
      </button>
    </form>
  );
}

export default SellForm;