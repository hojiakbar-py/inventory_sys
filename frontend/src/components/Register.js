import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../App.css';

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const validateForm = () => {
    if (!formData.username || !formData.email || !formData.password || !formData.password2) {
      setError('Barcha majburiy maydonlarni to\'ldiring');
      return false;
    }

    if (formData.username.length < 3) {
      setError('Foydalanuvchi nomi kamida 3 ta belgidan iborat bo\'lishi kerak');
      return false;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Email manzil noto\'g\'ri formatda');
      return false;
    }

    if (formData.password.length < 8) {
      setError('Parol kamida 8 ta belgidan iborat bo\'lishi kerak');
      return false;
    }

    if (formData.password !== formData.password2) {
      setError('Parollar mos kelmayapti');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const { password2, ...registerData } = formData;
      const response = await axios.post(`${API_BASE_URL}/auth/register/`, registerData);

      // Auto login after registration
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
        localStorage.setItem('username', formData.username);
        navigate('/');
      } else {
        // If no token returned, redirect to login
        navigate('/login');
      }
    } catch (err) {
      console.error('Register error:', err);
      if (err.response?.data) {
        const errors = err.response.data;
        if (errors.username) {
          setError(`Foydalanuvchi nomi: ${errors.username[0]}`);
        } else if (errors.email) {
          setError(`Email: ${errors.email[0]}`);
        } else if (errors.password) {
          setError(`Parol: ${errors.password[0]}`);
        } else {
          setError(errors.error || 'Ro\'yxatdan o\'tishda xatolik yuz berdi');
        }
      } else {
        setError('Server bilan bog\'lanishda xatolik yuz berdi');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-header">
          <h1>📝 Ro'yxatdan O'tish</h1>
          <p>Inventar boshqaruv tizimi</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-message" style={{
              padding: '15px',
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              borderRadius: '8px',
              color: '#c33',
              marginBottom: '20px'
            }}>
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Foydalanuvchi nomi *</label>
            <input
              type="text"
              id="username"
              name="username"
              className="form-control"
              value={formData.username}
              onChange={handleChange}
              placeholder="Kamida 3 ta belgi"
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              className="form-control"
              value={formData.email}
              onChange={handleChange}
              placeholder="example@company.uz"
              disabled={loading}
              autoComplete="email"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">Ism</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                className="form-control"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="Ismingiz"
                disabled={loading}
                autoComplete="given-name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="last_name">Familiya</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                className="form-control"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Familiyangiz"
                disabled={loading}
                autoComplete="family-name"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Parol *</label>
            <input
              type="password"
              id="password"
              name="password"
              className="form-control"
              value={formData.password}
              onChange={handleChange}
              placeholder="Kamida 8 ta belgi"
              disabled={loading}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password2">Parolni tasdiqlash *</label>
            <input
              type="password"
              id="password2"
              name="password2"
              className="form-control"
              value={formData.password2}
              onChange={handleChange}
              placeholder="Parolni qayta kiriting"
              disabled={loading}
              autoComplete="new-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-success btn-block"
            disabled={loading}
            style={{ width: '100%', marginTop: '20px' }}
          >
            {loading ? 'Yuklanmoqda...' : 'Ro\'yxatdan O\'tish'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Hisobingiz bormi?{' '}
            <button
              onClick={() => navigate('/login')}
              className="link-button"
              style={{
                background: 'none',
                border: 'none',
                color: '#667eea',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              Kirish
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;
