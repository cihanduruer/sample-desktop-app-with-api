import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

// BAD: no error boundary, no StrictMode, non-null assertion on getElementById.
ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
