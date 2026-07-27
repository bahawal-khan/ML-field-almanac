import { Link, useNavigate } from "react-router-dom";
import { Sprout, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar__brand">
        <Sprout size={22} strokeWidth={2.2} />
        <span>Field Almanac</span>
      </Link>

      <div className="navbar__links">
        {isAuthenticated ? (
          <>
            <Link to="/crop">Crop</Link>
            <Link to="/fertilizer">Fertilizer</Link>
            <span className="navbar__user">{user?.email}</span>
            <button className="navbar__logout" onClick={handleLogout}>
              <LogOut size={15} />
              Sign out
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Sign in</Link>
            <Link to="/register" className="navbar__cta">
              Create account
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
