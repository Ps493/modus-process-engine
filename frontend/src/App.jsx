import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import ProcessList from "./pages/ProcessList.jsx";
import ProcessDetail from "./pages/ProcessDetail.jsx";
import AddProcess from "./pages/AddProcess.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">100-Process Intelligence Engine</div>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/processes">All Processes</NavLink>
          <NavLink to="/add">Add Process</NavLink>
        </nav>
      </header>
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/processes" element={<ProcessList />} />
          <Route path="/processes/:id" element={<ProcessDetail />} />
          <Route path="/add" element={<AddProcess />} />
        </Routes>
      </main>
    </div>
  );
}
