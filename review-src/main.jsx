import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error('Root element not found. Please ensure there is a DOM element with id "root".');
} else {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    process.env.NODE_ENV === 'production' ? (
      <React.StrictMode>
        <App />
      </React.StrictMode>
    ) : (
      <App />
    )
  );
} 