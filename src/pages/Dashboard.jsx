import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/v1/alerts/history')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch alerts');
        return res.json();
      })
      .then((data) => {
        setAlerts(data.alerts || data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading alerts...</div>;
  if (error) return <div style={{color: 'red'}}>Error: {error}</div>;

  return (
    <div style={{maxWidth: '900px', margin: '2rem auto', padding: '2rem', background: '#fff', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.07)'}}>
      <h2 style={{marginBottom: '1.5rem'}}>Alert Dashboard</h2>
      {alerts.length === 0 ? (
        <div>No alerts found.</div>
      ) : (
        <table style={{width: '100%', borderCollapse: 'collapse'}}>
          <thead>
            <tr style={{background: '#f4f4f4'}}>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>ID</th>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>Type</th>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>Risk Score</th>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>Details</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.id} style={{borderBottom: '1px solid #eee'}}>
                <td style={{padding: '0.5rem'}}>{alert.id}</td>
                <td style={{padding: '0.5rem'}}>{alert.type || alert.alert_type}</td>
                <td style={{padding: '0.5rem'}}>{alert.risk_score}</td>
                <td style={{padding: '0.5rem'}}>
                  <Link to={`/case/${alert.id}`}>View</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Dashboard; 