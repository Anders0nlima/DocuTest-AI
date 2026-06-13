import axios from "axios";

export const apiClient = axios.create({
  // Pointing directly to our FastAPI backend default local port
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});
