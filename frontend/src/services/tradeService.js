import apiClient from "./apiClient";

export async function executeBuy({ portfolioId, ticker, quantity }) {
  const response = await apiClient.post("/trade/buy", {
    portfolio_id: portfolioId,
    ticker: ticker.toUpperCase().trim(),
    quantity,
  });
  return response.data;
}

export async function executeSell({ portfolioId, ticker, quantity }) {
  const response = await apiClient.post("/trade/sell", {
    portfolio_id: portfolioId,
    ticker: ticker.toUpperCase().trim(),
    quantity,
  });
  return response.data;
}