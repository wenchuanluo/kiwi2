import { logout } from "../services/authService";

function Dashboard() {
  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <h1>Kiwi Dashboard</h1>
          <p>You are signed in successfully.</p>
        </div>

        <button className="secondary-button" onClick={logout}>
          Log out
        </button>
      </header>

      <main className="dashboard-content">
        <div className="placeholder-card">
          <h2>Portfolio management will be implemented next.</h2>
          <p>
            The authentication flow is working. Next, we will connect this page
            to the Flask backend API.
          </p>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;