import apiClient from "./apiClient";
import { getCurrentUsername } from "./userService";

export async function getMyPortfolios() {
  const username = getCurrentUsername();
  if (!username) {
    throw new Error("No current user. Please log in first.");
  }

  const response = await apiClient.get(`/portfolios/user/${username}`);
  return response.data;
}

export async function getPortfolioById(portfolioId) {
  const response = await apiClient.get(`/portfolios/${portfolioId}`);
  return response.data;
}

export async function createPortfolio({ name, description }) {
  const username = getCurrentUsername();
  if (!username) {
    throw new Error("No current user. Please log in first.");
  }

  const response = await apiClient.post("/portfolios/", {
    username,
    name,
    description,
  });
  return response.data;
}

export async function deletePortfolio(portfolioId) {
  const response = await apiClient.delete(`/portfolios/${portfolioId}`);
  return response.data;
}

export async function getPortfolioTransactions(portfolioId) {
  const response = await apiClient.get(`/portfolios/${portfolioId}/transactions`);
  return response.data;
}