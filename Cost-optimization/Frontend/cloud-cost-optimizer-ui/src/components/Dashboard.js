import React, { useEffect, useState } from 'react';
import { fetchCostData } from '../services/api';

const Dashboard: React.FC = () => {
  const [costData, setCostData] = useState([]);

  useEffect(() => {
    fetchCostData().then((response) => setCostData(response.data));
  }, []);

  return (
    <div>
      <h1>Cloud Cost Dashboard</h1>
      <pre>{JSON.stringify(costData, null, 2)}</pre>
    </div>
  );
};

export default Dashboard;

