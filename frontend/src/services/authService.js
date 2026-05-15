import { cognitoConfig } from "../config/cognito";

const ID_TOKEN_STORAGE_KEY = "kiwi_id_token";
const ACCESS_TOKEN_STORAGE_KEY = "kiwi_access_token";

export function buildLoginUrl() {
  const params = new URLSearchParams({
    client_id: cognitoConfig.clientId,
    response_type: "code",
    scope: cognitoConfig.scopes.join(" "),
    redirect_uri: cognitoConfig.redirectUri,
  });

  return `${cognitoConfig.domain}/oauth2/authorize?${params.toString()}`;
}

export async function exchangeCodeForTokens(code) {
  const tokenEndpoint = `${cognitoConfig.domain}/oauth2/token`;

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: cognitoConfig.clientId,
    code,
    redirect_uri: cognitoConfig.redirectUri,
  });

  const response = await fetch(tokenEndpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Token exchange failed: ${errorText}`);
  }

  return response.json();
}

export function saveTokens(tokens) {
  if (tokens.id_token) {
    localStorage.setItem(ID_TOKEN_STORAGE_KEY, tokens.id_token);
  }

  if (tokens.access_token) {
    localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, tokens.access_token);
  }
}

export function getIdToken() {
  return localStorage.getItem(ID_TOKEN_STORAGE_KEY);
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function isAuthenticated() {
  return Boolean(getIdToken());
}

export function clearTokens() {
  localStorage.removeItem(ID_TOKEN_STORAGE_KEY);
  localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function logout() {
  clearTokens();

  const params = new URLSearchParams({
    client_id: cognitoConfig.clientId,
    logout_uri: cognitoConfig.logoutUri,
  });

  window.location.href = `${cognitoConfig.domain}/logout?${params.toString()}`;
}