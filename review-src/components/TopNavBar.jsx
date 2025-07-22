import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const TopNavBar = () => {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;
  return (
    <nav style={{backgroundColor: '#1a1a2e', padding: '1rem 2rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', position: 'sticky', top: 0, zIndex: 1000}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto'}}>
        <Link to='/' style={{textDecoration: 'none', color: '#fff', fontSize: '1.5rem', fontWeight: 'bold'}}>
          <span style={{color: '#00d4ff'}}>KOR</span><span style={{color: '#fff'}}>.AI</span>
        </Link>
        <div style={{display: 'flex', gap: '2rem', alignItems: 'center'}}>
          <Link to='/' style={{textDecoration: 'none', color: isActive('/') ? '#00d4ff' : '#fff', padding: '0.5rem 1rem', borderRadius: '4px'}}>Dashboard</Link>
          <Link to='/alerts' style={{textDecoration: 'none', color: isActive('/alerts') ? '#00d4ff' : '#fff', padding: '0.5rem 1rem', borderRadius: '4px'}}>Alerts</Link>
          <Link to='/models' style={{textDecoration: 'none', color: isActive('/models') ? '#00d4ff' : '#fff', padding: '0.5rem 1rem', borderRadius: '4px'}}>Models</Link>
        </div>
      </div>
    </nav>
  );
};
export default TopNavBar; 