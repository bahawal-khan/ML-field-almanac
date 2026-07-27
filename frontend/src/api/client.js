import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

// Attach the JWT token (if present) to every outgoing request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If the token is invalid/expired, clear it so the app redirects to login
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
    return Promise.reject(error);
  }
);

export async function checkHealth() {
  const { data } = await client.get("/api/health");
  return data;
}

export async function registerUser({ username, email, password }) {
  const { data } = await client.post("/api/auth/register", { username, email, password });
  return data;
}

export async function loginUser({ email, password }) {
  const { data } = await client.post("/api/auth/login", { email, password });
  return data;
}

export async function fetchProfile() {
  const { data } = await client.get("/api/auth/profile");
  return data;
}

export async function predictCrop(payload) {
  const { data } = await client.post("/api/crop/predict", payload);
  return data;
}

export async function predictFertilizer(payload) {
  const { data } = await client.post("/api/fertilizer/predict", payload);
  return data;
}

export default client;
