import { buildLoginUrl } from "../services/authService";

function LoginPage() {
  const handleLogin = () => {
    window.location.href = buildLoginUrl();
  };

  return (
    <div className="login-page">
      <section className="login-hero">
        <div className="brand">
          <span className="brand-icon">🥝</span>
          <span className="brand-name">kiwi</span>
        </div>

        <h1>Smart portfolio management for modern investors.</h1>
        <p>
          Track your holdings, execute trades, and review every transaction in
          one place.
        </p>

        <ul>
          <li>Create and manage multiple portfolios</li>
          <li>Buy and sell securities instantly</li>
          <li>Review full transaction history</li>
        </ul>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div className="login-logo">🥝</div>
          <h2>Welcome back</h2>
          <p>Sign in with AWS Cognito to access your portfolio dashboard.</p>

          <button className="primary-button" onClick={handleLogin}>
            Sign in with Cognito
          </button>
        </div>
      </section>
    </div>
  );
}

export default LoginPage;