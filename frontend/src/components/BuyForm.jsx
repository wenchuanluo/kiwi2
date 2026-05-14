import { useState } from "react";
import { executeBuy } from "../services/tradeService";

function BuyForm({ portfolioId, onTradeCompleted }) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!ticker.trim()) {
      setError("Ticker is required.");
      return;
    }

    const numericQuantity = Number(quantity);
    if (!Number.isInteger(numericQuantity) || numericQuantity <= 0) {
      setError("Quantity must be a positive integer.");
      return;
    }

    setSubmitting(true);
    try {
      await executeBuy({
        portfolioId,
        ticker,
        quantity: numericQuantity,
      });
      setSuccessMessage(
        `Bought ${numericQuantity} share(s) of ${ticker.toUpperCase().trim()}.`
      );
      setTicker("");
      setQuantity("");
      onTradeCompleted();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to execute buy order."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="trade-form">
      <h3>Buy</h3>

      <div className="trade-form-row">
        <label className="form-field">
          <span className="form-label">Ticker</span>
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="e.g. AAPL"
            disabled={submitting}
          />
        </label>

        <label className="form-field">
          <span className="form-label">Quantity</span>
          <input
            type="number"
            min="1"
            step="1"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="e.g. 10"
            disabled={submitting}
          />
        </label>
      </div>

      {error && <p className="error-text">{error}</p>}
      {successMessage && <p className="success-text">{successMessage}</p>}

      <button type="submit" className="primary-button" disabled={submitting}>
        {submitting ? "Placing order..." : "Buy"}
      </button>
    </form>
  );
}

export default BuyForm;