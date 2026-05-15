import { useState } from "react";
import { logout } from "../services/authService";
import { getCurrentUsername } from "../services/userService";
import PortfolioList from "./PortfolioList";
import CreatePortfolioModal from "./CreatePortfolioModal";

function Dashboard() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [refreshSignal, setRefreshSignal] = useState(0);
  const currentUser = getCurrentUsername();

  const handleCreated = () => {
    setRefreshSignal((prev) => prev + 1);
  };

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <h1>Kiwi Dashboard</h1>
          <p>
            Signed in as <strong>{currentUser}</strong>
          </p>
        </div>

        <button className="secondary-button" onClick={logout}>
          Log out
        </button>
      </header>

      <main className="dashboard-content">
        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>My Portfolios</h2>
            <button
              className="primary-button"
              onClick={() => setIsCreateOpen(true)}
            >
              + Create Portfolio
            </button>
          </div>
          <PortfolioList refreshSignal={refreshSignal} />
        </div>
      </main>

      <CreatePortfolioModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreated={handleCreated}
      />
    </div>
  );
}

export default Dashboard;