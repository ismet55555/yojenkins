import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../api/auth';

export default function NavBar() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">yojenkins</Link>
      </div>
      <div className="nav-links">
        <Link to="/">Dashboard</Link>
        <Link to="/jobs">Jobs</Link>
        <Link to="/folders">Folders</Link>
        <button onClick={handleLogout} className="nav-logout">Logout</button>
      </div>
    </nav>
  );
}
