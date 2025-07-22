import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

const CaseDetail = () => {
  const { id } = useParams();
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/v1/alerts/history')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch alert');
        return res.json();
      })
      .then((data) => {
        const found = (data.alerts || data).find((a) => String(a.id) === String(id));
        if (!found) throw new Error('Alert not found');
        setAlert(found);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div>Loading case details...</div>;
  if (error) return <div style={{color: 'red'}}>Error: {error}</div>;

  return (
    <div style={{maxWidth: '700px', margin: '2rem auto', padding: '2rem', background: '#fff', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.07)'}}>
      <h2>Case Detail</h2>
      <div style={{marginBottom: '1rem'}}>
        <Link to="/">&larr; Back to Dashboard</Link>
      </div>
      <div style={{padding: '1rem', background: '#f9f9f9', borderRadius: '6px'}}>
        {Object.entries(alert).map(([key, value]) => (
          <div key={key} style={{marginBottom: '0.5rem'}}>
            <strong>{key}:</strong> {String(value)}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CaseDetail; 