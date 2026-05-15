
export const cognitoConfig = {
  domain: import.meta.env.VITE_COGNITO_DOMAIN,
  clientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
  redirectUri: import.meta.env.VITE_REDIRECT_URI,
  logoutUri: import.meta.env.VITE_LOGOUT_URI,
  scopes: ["openid", "email", "profile"],
};

export const backendConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL,
};