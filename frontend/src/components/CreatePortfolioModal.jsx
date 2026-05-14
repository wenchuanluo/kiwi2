import { useState } from "react";
import { createPortfolio } from "../services/portfolioService";

function CreatePortfolioModal({ isOpen, onClose, onCreated }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) {
    return null;
  }

  const resetForm = () => {
    setName("");
    setDescription("");
    setError(null);
    setSubmitting(false);
  };

  const handleClose = () => {
    if (submitting) return;
    resetForm();
    onClose();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    if (!name.trim() || !description.trim()) {
      setError("Name and description are required.");
      return;
    }

    setSubmitting(true);
    try {
      await createPortfolio({
        name: name.trim(),
        description: description.trim(),
      });
      resetForm();
      onCreated();
      onClose();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to create portfolio."
      );
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create Portfolio</h2>
          <button
            className="modal-close"
            onClick={handleClose}
            disabled={submitting}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <label className="form-field">
            <span className="form-label">Name</span>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Tech Stocks"
              disabled={submitting}
              autoFocus
            />
          </label>

          <label className="form-field">
            <span className="form-label">Description</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What is this portfolio for?"
              rows={3}
              disabled={submitting}
            />
          </label>

          {error && <p className="error-text">{error}</p>}

          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={handleClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {submitting ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreatePortfolioModal;