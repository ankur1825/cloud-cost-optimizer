import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export const triggerScan = () => api.post('/scan');
export const fetchCostData = () => api.get('/cost-data');
export const getRecommendations = () => api.get('/recommendations');
