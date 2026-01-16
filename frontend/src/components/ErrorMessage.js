import React from 'react';
import './ErrorMessage.css';

const ErrorMessage = ({ error, onRetry }) => {
  if (!error) return null;

  const getErrorMessage = (error) => {
    if (typeof error === 'string') return error;
    if (error.response?.data?.detail) return error.response.data.detail;
    if (error.response?.data?.message) return error.response.data.message;
    if (error.message) return error.message;
    return 'Noma\'lum xatolik yuz berdi';
  };

  return (
    <div className="error-message-container">
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <h3>Xatolik</h3>
        <p>{getErrorMessage(error)}</p>
        {onRetry && (
          <button className="retry-button" onClick={onRetry}>
            🔄 Qayta urinish
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
