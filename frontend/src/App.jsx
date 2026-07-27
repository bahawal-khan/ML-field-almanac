import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CropRecommendation from "./pages/CropRecommendation";
import FertilizerRecommendation from "./pages/FertilizerRecommendation";
import "./App.css";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/crop"
            element={
              <ProtectedRoute>
                <CropRecommendation />
              </ProtectedRoute>
            }
          />
          <Route
            path="/fertilizer"
            element={
              <ProtectedRoute>
                <FertilizerRecommendation />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
