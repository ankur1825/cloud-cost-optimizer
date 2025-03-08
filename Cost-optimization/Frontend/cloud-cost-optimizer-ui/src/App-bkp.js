import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import CostChart from "./components/CostChart";
import Alerts from "./components/Alerts";
import React from 'react';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CostChart />} />
        <Route path="/alerts" element={<Alerts />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <div className="App">
      <h1>Cloud Cost Optimizer</h1>
    </div>
  );
}

export default App;

