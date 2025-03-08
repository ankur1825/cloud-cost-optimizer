import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, Title, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';
import axios from 'axios';

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement);

const CostChart = () => {
  const [costData, setCostData] = useState([]);  // Remove TypeScript annotations
  const [service, setService] = useState('All'); // State for storing the selected service

  // Function to handle changes in service selection
  const handleServiceChange = (event) => {
    setService(event.target.value); // Update the service selection
  };

  useEffect(() => {
    // Fetch data from FastAPI endpoint
    axios
      .post('http://localhost:8000/cost-analysis/', {
        start_date: '2025-01-01',  // Example start date
        end_date: '2025-01-31',    // Example end date
        service: service === 'All' ? '' : service, // If "All", send an empty string for service
      })
      .then((response) => setCostData(response.data.cost_data))
      .catch((error) => console.error('API Error:', error));
  }, [service]); // Re-fetch data whenever the service changes

  // Prepare chart data
  const chartData = {
    labels: costData.map((data) => data.service),  // X-axis: service names
    datasets: [
      {
        label: 'Service Cost',
        data: costData.map((data) => data.cost),  // Directly use the numeric cost value
        borderColor: 'rgba(75,192,192,1)',  // Line color
        backgroundColor: 'rgba(75,192,192,0.2)',  // Fill color
        fill: true,
      },
    ],
  };

  return (
    <div>
      <h2>Cost Analysis</h2>
      
      {/* Dropdown for selecting the service */}
      <div>
        <label htmlFor="service">Select Service: </label>
        <select id="service" value={service} onChange={handleServiceChange}>
          <option value="All">All Services</option>
          <option value="EC2">EC2</option>
          <option value="S3">S3</option>
          <option value="Lambda">Lambda</option>
          {/* Add more options as needed */}
        </select>
      </div>

      {costData.length > 0 ? (
        <div>
          {/* Display chart if costData exists */}
          <Line data={chartData} />
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default CostChart;

