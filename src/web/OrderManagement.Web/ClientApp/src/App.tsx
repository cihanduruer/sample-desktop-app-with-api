import { useEffect, useState } from "react";

// ============================================================================
// TEACHING ARTIFACT - one giant component, intentionally bad React.
// Planted problems:
//   * Hard-coded API base URL (breaks once the SPA is served from the BFF origin).
//   * `any` types everywhere; no shared models.
//   * fetch() in useEffect with no cleanup, no error handling, no loading guards.
//   * Auth token stored in localStorage (XSS-exfiltratable).
//   * Everything is one component; no memoization; inline styles.
//   * Totals recomputed inline on every render.
// ============================================================================

// BAD: hard-coded, environment-agnostic URL.
const API = "http://localhost:5080/api";

export default function App() {
  const [orders, setOrders] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin");
  const [message, setMessage] = useState("");
  const [dashboard, setDashboard] = useState("");
  const [newStatus, setNewStatus] = useState("SHIPPED");
  const [selectedId, setSelectedId] = useState<any>(null);

  // BAD: no dependency array hygiene, no cleanup, no abort controller.
  useEffect(() => {
    fetch(API + "/orders")
      .then((r) => r.json())
      .then((d) => setOrders(d));
    fetch(API + "/products")
      .then((r) => r.json())
      .then((d) => setProducts(d));
  }, []);

  // BAD: async with no try/catch; ignores HTTP status; trusts response shape.
  function login() {
    fetch(API + "/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ Email: email, Password: password }),
    })
      .then((r) => r.json())
      .then((d: any) => {
        // BAD: token in localStorage; also dumps user object into the page.
        localStorage.setItem("token", d.token);
        setMessage("Logged in: " + JSON.stringify(d.user));
      });
  }

  function refresh() {
    fetch(API + "/orders")
      .then((r) => r.json())
      .then((d) => setOrders(d));
  }

  // BAD: blocks nothing on the UI, but the BFF endpoint is deliberately slow and
  // there is no loading indicator, so the button just appears frozen.
  function loadDashboard() {
    setMessage("Loading dashboard (slow)...");
    fetch(API + "/dashboard")
      .then((r) => r.text())
      .then((html) => {
        setDashboard(html);
        setMessage("Dashboard loaded");
      });
  }

  function updateStatus() {
    if (selectedId == null) {
      // BAD: alert() for control flow.
      alert("select an order first");
      return;
    }
    fetch(API + "/orders/" + selectedId + "/status", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ Status: newStatus }),
    })
      .then((r) => r.json())
      .then(() => refresh());
  }

  // BAD: recomputed on every render with no memoization.
  let grandTotal = 0;
  for (let i = 0; i < orders.length; i++) {
    grandTotal = grandTotal + orders[i].total;
  }

  return (
    <div style={{ padding: 20, maxWidth: 1000, margin: "0 auto" }}>
      <h1 style={{ color: "#333" }}>Order Management (Web)</h1>

      {/* Login row. BAD: password rendered as text input; creds in state. */}
      <div style={{ marginBottom: 12 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
          style={{ marginLeft: 6 }}
        />
        <button onClick={login} style={{ marginLeft: 6 }}>
          Login
        </button>
        <span style={{ marginLeft: 12, color: "green" }}>{message}</span>
      </div>

      <div style={{ marginBottom: 12 }}>
        <button onClick={refresh}>Refresh Orders</button>
        <input
          value={newStatus}
          onChange={(e) => setNewStatus(e.target.value)}
          style={{ marginLeft: 12, width: 120 }}
        />
        <button onClick={updateStatus} style={{ marginLeft: 6 }}>
          Update Status
        </button>
        <button onClick={loadDashboard} style={{ marginLeft: 6 }}>
          Load Dashboard (slow)
        </button>
      </div>

      <h3>Orders (grand total: ${grandTotal})</h3>
      <table style={{ width: "100%", background: "white" }}>
        <thead>
          <tr>
            <th>Id</th>
            <th>Customer</th>
            <th>Email</th>
            <th>Status</th>
            <th>Items</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {/* BAD: array index as key; whole row clickable via inline handler. */}
          {orders.map((o: any, idx: number) => (
            <tr
              key={idx}
              onClick={() => setSelectedId(o.id)}
              style={{ background: selectedId === o.id ? "#def" : "white", cursor: "pointer" }}
            >
              <td>{o.id}</td>
              <td>{o.customer_name}</td>
              <td>{o.customerEmail}</td>
              <td>{o.status}</td>
              <td>{o.item_count}</td>
              <td>{o.total}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Products</h3>
      <ul>
        {products.map((p: any, idx: number) => (
          <li key={idx}>
            {p.name} - ${p.price} ({p.stock} in stock)
          </li>
        ))}
      </ul>

      {/* BAD: raw HTML from the BFF injected via dangerouslySetInnerHTML (XSS). */}
      <h3>Dashboard</h3>
      <div dangerouslySetInnerHTML={{ __html: dashboard }} />
    </div>
  );
}
