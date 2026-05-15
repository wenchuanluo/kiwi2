import { jwtDecode } from "jwt-decode";
import { getIdToken } from "./authService";

export function getCurrentUsername() {
  const token = getIdToken();
  if (!token) {
    return null;
  }

  try {
    const claims = jwtDecode(token);
    return (
      claims["cognito:username"] ||
      claims.username ||
      claims.sub ||
      null
    );
  } catch (error) {
    console.error("Failed to decode JWT:", error);
    return null;
  }
}

export function isTokenExpired() {
  const token = getIdToken();
  if (!token) return true;

  try {
    const claims = jwtDecode(token);
    if (!claims.exp) return false;
    return claims.exp * 1000 < Date.now();
  } catch (error) {
    return true;
  }
}