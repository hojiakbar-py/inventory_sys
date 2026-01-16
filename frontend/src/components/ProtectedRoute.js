import React from 'react';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('authToken');

  if (!token) {
    // Token yo'q bo'lsa, login page'ga yo'naltirish
    return <Navigate to="/login" replace />;
  }

  // Token bor bo'lsa, componentni ko'rsatish
  return children;
}

export default ProtectedRoute;
