import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { exchangeCodeForTokens, saveTokens } from "../services/authService";

function CallbackPage() {
  const navigate = useNavigate();
  const [message, setMessage] = useState("Completing sign in...");
  const hasHandled = useRef(false);

  useEffect(() => {
    if (hasHandled.current) return;
    hasHandled.current = true;

    async function handleCallback() {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");

        if (!code) {
          throw new Error("Authorization code is missing from callback URL.");
        }

        const tokens = await exchangeCodeForTokens(code);
        saveTokens(tokens);

        navigate("/dashboard");
      } catch (error) {
        console.error("Authentication failed");
        setMessage("Sign in failed. Redirecting to login page...");
        setTimeout(() => navigate("/"), 2000);
      }
    }

    handleCallback();
  }, [navigate]);

  return (
    <div className="center-page">
      <div className="status-card">
        <h2>{message}</h2>
      </div>
    </div>
  );
}

export default CallbackPage;