import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Import the new App component

const rootElement = document.getElementById('root');
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App /> {/* Render the imported App component */}
    </React.StrictMode>
  );
} else {
  console.error("Failed to find the root element. Ensure your public/index.html has a div with id='root'.");
}
