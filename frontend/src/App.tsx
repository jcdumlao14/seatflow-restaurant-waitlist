import {
  useEffect,
  useState,
} from "react";

import {
  addParty,
  callNext,
  cancelParty,
  clearToken,
  getMe,
  getStatistics,
  getToken,
  getWaitlist,
  login,
  noShowParty,
  register,
  seatParty,
  setToken,
  ApiError,
  type Statistics,
  type User,
  type WaitlistEntry,
} from "./api";

import "./App.css";


type AuthMode = "login" | "register";


const EMPTY_STATS: Statistics = {
  total: 0,
  waiting: 0,
  notified: 0,
  seated: 0,
  cancelled: 0,
  no_show: 0,
};


function App() {
  const [user, setUser] =
    useState<User | null>(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    const token = getToken();

    if (!token) {
      setLoading(false);
      return;
    }

    getMe()
      .then(setUser)
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-card">
          <div className="brand-mark">
            S
          </div>
          <h2>SeatFlow</h2>
          <p>
            Loading your workspace...
          </p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <AuthScreen
        onAuthenticated={(data) => {
          setToken(data.access_token);
          setUser(data.user);
        }}
      />
    );
  }

  return (
    <Dashboard
      user={user}
      onLogout={() => {
        clearToken();
        setUser(null);
      }}
    />
  );
}


function AuthScreen({
  onAuthenticated,
}: {
  onAuthenticated: (
    data: AuthResponseData,
  ) => void;
}) {
  const [mode, setMode] =
    useState<AuthMode>("login");

  const [restaurantName, setRestaurantName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function submit(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));
    setLoading(true);

    try {
      const data =
        mode === "login"
          ? await login(email, password)
          : await register(
              restaurantName,
              email,
              password,
            );

      onAuthenticated(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-hero">
        <div className="hero-content">
          <div className="brand">
            <div className="brand-mark">
              S
            </div>
            <span>SeatFlow</span>
          </div>

          <div className="hero-copy">
            <span className="eyebrow">
              Restaurant Operations
            </span>

            <h1>
              Turn waiting time into a better
              <span>
                guest experience.
              </span>
            </h1>

            <p>
              Manage your restaurant waitlist,
              track parties, and keep your team
              moving from one simple workspace.
            </p>
          </div>

          <div className="hero-points">
            <div>
              <strong>
                Live queue
              </strong>
              <span>
                Know who is waiting.
              </span>
            </div>

            <div>
              <strong>
                Team-ready
              </strong>
              <span>
                Owner, manager and staff roles.
              </span>
            </div>

            <div>
              <strong>
                SaaS-ready
              </strong>
              <span>
                Built for restaurant tenants.
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-card">
          <div className="mobile-brand">
            <div className="brand-mark">
              S
            </div>
            <span>SeatFlow</span>
          </div>

          <div className="auth-heading">
            <span className="eyebrow">
              {mode === "login"
                ? "Welcome back"
                : "Get started"}
            </span>

            <h2>
              {mode === "login"
                ? "Sign in to SeatFlow"
                : "Create your restaurant"}
            </h2>

            <p>
              {mode === "login"
                ? "Access your restaurant workspace."
                : "Create your restaurant workspace."}
            </p>
          </div>

          <div className="auth-tabs">
            <button
              className={
                mode === "login"
                  ? "active"
                  : ""
              }
              type="button"
              onClick={() => {
                setMode("login");
                setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));
              }}
            >
              Sign in
            </button>

            <button
              className={
                mode === "register"
                  ? "active"
                  : ""
              }
              type="button"
              onClick={() => {
                setMode("register");
                setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));
              }}
            >
              Register
            </button>
          </div>

          <form
            className="auth-form"
            onSubmit={submit}
          >
            {mode === "register" && (
              <label>
                Restaurant name
                <input
                  value={restaurantName}
                  onChange={(event) =>
                    setRestaurantName(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. Harbor Bistro"
                  minLength={2}
                  maxLength={150}
                  required
                />
              </label>
            )}

            <label>
              Email address
              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(
                    event.target.value,
                  )
                }
                placeholder="you@restaurant.com"
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value,
                  )
                }
                placeholder="Minimum 8 characters"
                minLength={8}
                required
              />
            </label>

            {error && (
              <div className="error-message">
                {typeof error === "string" ? error : JSON.stringify(error, null, 2)}
              </div>
            )}

            <button
              className="primary-button auth-submit"
              disabled={loading}
              type="submit"
            >
              {loading
                ? "Please wait..."
                : mode === "login"
                  ? "Sign in"
                  : "Create workspace"}
            </button>
          </form>

          <p className="auth-footer">
            JWT authentication Ã‚Â· Argon2 password
            hashing Ã‚Â· Multi-tenant architecture
          </p>
        </div>
      </section>
    </main>
  );
}


type AuthResponseData = {
  access_token: string;
  user: User;
};


function Dashboard({
  user,
  onLogout,
}: {
  user: User;
  onLogout: () => void;
}) {
  const [entries, setEntries] =
    useState<WaitlistEntry[]>([]);

  const [stats, setStats] =
    useState<Statistics>(EMPTY_STATS);

  const [customerName, setCustomerName] =
    useState("");

  const [phone, setPhone] =
    useState("");

  const [partySize, setPartySize] =
    useState(2);

  const [loading, setLoading] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  async function refresh() {
    try {
      const [queue, statistics] =
        await Promise.all([
          getWaitlist(),
          getStatistics(),
        ]);

      setEntries(queue);
      setStats(statistics);
      setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));
    } catch (err) {
      if (
        err instanceof ApiError &&
        err.status === 401
      ) {
        onLogout();
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load dashboard.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  function notify(message: string) {
    setSuccess(message);
    setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));

    window.setTimeout(() => {
      setSuccess("");
    }, 2500);
  }

  async function handleAddParty(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));
    setSuccess("");
    setSubmitting(true);

    try {
      await addParty(
        customerName.trim(),
        phone.trim(),
        partySize,
      );

      setCustomerName("");
      setPhone("");
      setPartySize(2);

      await refresh();

      notify(
        "Party added to the waitlist.",
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to add party.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCallNext() {
    setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));

    try {
      const entry = await callNext();

      notify(
        `${entry.customer_name} has been called.`,
      );

      await refresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to call next party.",
      );
    }
  }

  async function handleStatus(
    entry: WaitlistEntry,
    action:
      | "seat"
      | "cancel"
      | "no-show",
  ) {
    setError(typeof "" === "string" ? "" : JSON.stringify("", null, 2));

    try {
      if (action === "seat") {
        await seatParty(entry.id);

        notify(
          `${entry.customer_name} has been seated.`,
        );
      }

      if (action === "cancel") {
        await cancelParty(entry.id);

        notify(
          `${entry.customer_name} was cancelled.`,
        );
      }

      if (action === "no-show") {
        await noShowParty(entry.id);

        notify(
          `${entry.customer_name} marked as no-show.`,
        );
      }

      await refresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update party.",
      );
    }
  }

  const activeEntries =
    entries.filter(
      (entry) =>
        entry.status === "waiting" ||
        entry.status === "notified",
    );

  const historyEntries =
    entries
      .filter(
        (entry) =>
          entry.status !== "waiting" &&
          entry.status !== "notified",
      )
      .slice()
      .reverse()
      .slice(0, 8);

  return (
    <div className="dashboard-shell">
      <header className="topbar">
        <div className="topbar-brand">
          <div className="brand-mark">
            S
          </div>

          <div>
            <strong>SeatFlow</strong>
            <span>
              Restaurant Waitlist
            </span>
          </div>
        </div>

        <div className="topbar-user">
          <div className="user-meta">
            <strong>{user.email}</strong>

            <span>
              {user.role.toUpperCase()}
            </span>
          </div>

          <button
            className="logout-button"
            onClick={onLogout}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard">
        <section className="dashboard-heading">
          <div>
            <span className="eyebrow">
              Restaurant workspace
            </span>

            <h1>
              Waitlist Dashboard
            </h1>

            <p>
              Manage today's guest queue from
              one place.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={refresh}
          >
            Refresh
          </button>
        </section>

        {error && (
          <div className="alert error-message">
            {typeof error === "string" ? error : JSON.stringify(error, null, 2)}
          </div>
        )}

        {success && (
          <div className="alert success-message">
            {success}
          </div>
        )}

        <section className="stats-grid">
          <StatCard
            label="Waiting"
            value={stats.waiting}
            emphasis
          />

          <StatCard
            label="Called"
            value={stats.notified}
          />

          <StatCard
            label="Seated"
            value={stats.seated}
          />

          <StatCard
            label="Completed"
            value={
              stats.seated +
              stats.cancelled +
              stats.no_show
            }
          />

          <StatCard
            label="Total"
            value={stats.total}
          />
        </section>

        <section className="workspace-grid">
          <div className="panel add-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">
                  New guest
                </span>

                <h2>
                  Add to waitlist
                </h2>
              </div>
            </div>

            <form
              className="party-form"
              onSubmit={handleAddParty}
            >
              <label>
                Customer name
                <input
                  value={customerName}
                  onChange={(event) =>
                    setCustomerName(
                      event.target.value,
                    )
                  }
                  placeholder="Customer name"
                  required
                />
              </label>

              <label>
                Phone
                <input
                  value={phone}
                  onChange={(event) =>
                    setPhone(
                      event.target.value,
                    )
                  }
                  placeholder="+63 9XX XXX XXXX"
                  required
                />
              </label>

              <label>
                Party size
                <input
                  type="number"
                  min={1}
                  max={50}
                  value={partySize}
                  onChange={(event) =>
                    setPartySize(
                      Number(
                        event.target.value,
                      ),
                    )
                  }
                  required
                />
              </label>

              <button
                className="primary-button"
                disabled={submitting}
                type="submit"
              >
                {submitting
                  ? "Adding..."
                  : "Add Party"}
              </button>
            </form>

            <div className="next-action">
              <div>
                <span>
                  Queue action
                </span>

                <strong>
                  {stats.waiting} parties waiting
                </strong>
              </div>

              <button
                className="call-button"
                disabled={
                  stats.waiting === 0
                }
                onClick={handleCallNext}
              >
                Call Next
              </button>
            </div>
          </div>

          <div className="panel queue-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">
                  Live queue
                </span>

                <h2>
                  Current waitlist
                </h2>
              </div>

              <span className="queue-count">
                {activeEntries.length} active
              </span>
            </div>

            {loading ? (
              <div className="empty-state">
                Loading queue...
              </div>
            ) : activeEntries.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">
                  Ã¢Å“â€œ
                </div>

                <strong>
                  No active parties
                </strong>

                <span>
                  The waitlist is currently clear.
                </span>
              </div>
            ) : (
              <div className="queue-list">
                {activeEntries.map(
                  (entry, index) => (
                    <QueueRow
                      key={entry.id}
                      entry={entry}
                      position={index + 1}
                      onStatus={
                        handleStatus
                      }
                    />
                  ),
                )}
              </div>
            )}
          </div>
        </section>

        <section className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">
                Queue history
              </span>

              <h2>
                Recent activity
              </h2>
            </div>
          </div>

          {historyEntries.length === 0 ? (
            <div className="empty-state">
              No completed activity yet.
            </div>
          ) : (
            <div className="history-table">
              <div className="history-header">
                <span>Customer</span>
                <span>Party</span>
                <span>Status</span>
                <span>Wait</span>
              </div>

              {historyEntries.map(
                (entry) => (
                  <div
                    className="history-row"
                    key={entry.id}
                  >
                    <strong>
                      {entry.customer_name}
                    </strong>

                    <span>
                      {entry.party_size} guest
                      {entry.party_size !== 1
                        ? "s"
                        : ""}
                    </span>

                    <StatusBadge
                      status={entry.status}
                    />

                    <span>
                      {entry.estimated_wait_minutes} min
                    </span>
                  </div>
                ),
              )}
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <span>SeatFlow</span>

        <span>
          Tenant #{user.restaurant_id}
        </span>

        <span>
          {user.role} workspace
        </span>
      </footer>
    </div>
  );
}


function StatCard({
  label,
  value,
  emphasis = false,
}: {
  label: string;
  value: number;
  emphasis?: boolean;
}) {
  return (
    <div
      className={
        emphasis
          ? "stat-card emphasis"
          : "stat-card"
      }
    >
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}


function QueueRow({
  entry,
  position,
  onStatus,
}: {
  entry: WaitlistEntry;
  position: number;
  onStatus: (
    entry: WaitlistEntry,
    action:
      | "seat"
      | "cancel"
      | "no-show",
  ) => void;
}) {
  return (
    <article className="queue-row">
      <div className="queue-position">
        {position}
      </div>

      <div className="queue-person">
        <strong>
          {entry.customer_name}
        </strong>

        <span>
          {entry.phone} - {entry.party_size} guest
          {entry.party_size !== 1
            ? "s"
            : ""}
        </span>
      </div>

      <div className="queue-wait">
        <strong>
          {entry.estimated_wait_minutes} min
        </strong>

        <span>
          estimated
        </span>
      </div>

      <StatusBadge
        status={entry.status}
      />

      <div className="queue-actions">
        <button
          className="small-button success"
          onClick={() =>
            onStatus(
              entry,
              "seat",
            )
          }
        >
          Seat
        </button>

        <button
          className="small-button muted"
          onClick={() =>
            onStatus(
              entry,
              "cancel",
            )
          }
        >
          Cancel
        </button>

        <button
          className="small-button danger"
          onClick={() =>
            onStatus(
              entry,
              "no-show",
            )
          }
        >
          No-show
        </button>
      </div>
    </article>
  );
}


function StatusBadge({
  status,
}: {
  status: string;
}) {
  const labels: Record<
    string,
    string
  > = {
    waiting: "Waiting",
    notified: "Called",
    seated: "Seated",
    cancelled: "Cancelled",
    no_show: "No-show",
  };

  return (
    <span
      className={`status-badge status-${status}`}
    >
      {labels[status] || status}
    </span>
  );
}


export default App;


