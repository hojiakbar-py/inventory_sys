import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import '../App.css';

function Profile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [userData, setUserData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    is_staff: false,
    is_superuser: false
  });
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // OTP state
  const [showOTPForm, setShowOTPForm] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [verifiedOtpCode, setVerifiedOtpCode] = useState('');
  const [otpData, setOtpData] = useState({
    otp_code: '',
    new_password: '',
    confirm_password: ''
  });
  const [otpLoading, setOtpLoading] = useState(false);

  const loadUserData = useCallback(async () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      const response = await api.get('/auth/me/');

      setUserData(response.data);
      setFormData({
        email: response.data.email,
        first_name: response.data.first_name,
        last_name: response.data.last_name
      });
    } catch (err) {
      console.error('Load user data error:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('authToken');
        navigate('/login');
      } else {
        setError('Foydalanuvchi ma\'lumotlarini yuklashda xatolik');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    loadUserData();
  }, [loadUserData]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setSuccess('');
  };


  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.patch('/auth/update-profile/', formData);

      setUserData(response.data);
      setSuccess('Ma\'lumotlar muvaffaqiyatli yangilandi!');
      setEditing(false);
    } catch (err) {
      console.error('Update error:', err);
      if (err.response?.data) {
        const errors = err.response.data;
        if (errors.email) {
          setError(`Email: ${errors.email[0]}`);
        } else {
          setError(errors.error || 'Ma\'lumotlarni yangilashda xatolik');
        }
      } else {
        setError('Server bilan bog\'lanishda xatolik');
      }
    } finally {
      setLoading(false);
    }
  };


  const handleRequestOTP = async () => {
    if (!userData.email) {
      setError('Email manzili kiritilmagan. Iltimos, avval email manzilini qo\'shing.');
      return;
    }

    setOtpLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/auth/request-password-change-otp/', {
        email: userData.email
      });

      setSuccess(response.data.message || 'OTP kod emailingizga yuborildi');
      setOtpSent(true);
    } catch (err) {
      console.error('Request OTP error:', err);
      setError(err.response?.data?.error || 'OTP so\'rashda xatolik yuz berdi');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleOTPChange = (e) => {
    setOtpData({
      ...otpData,
      [e.target.name]: e.target.value
    });
    setError('');
    setSuccess('');
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();

    if (!otpData.otp_code || otpData.otp_code.length !== 6) {
      setError('OTP kod 6 ta raqamdan iborat bo\'lishi kerak');
      return;
    }

    setOtpLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/auth/verify-otp/', {
        email: userData.email,
        otp_code: otpData.otp_code
      });

      if (response.data.verified) {
        setSuccess('OTP kod to\'g\'ri! Endi yangi parolni kiriting.');
        setVerifiedOtpCode(otpData.otp_code);
        setOtpVerified(true);
      }
    } catch (err) {
      console.error('Verify OTP error:', err);
      setError(err.response?.data?.error || 'Noto\'g\'ri yoki muddati o\'tgan OTP kod');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleOTPPasswordSubmit = async (e) => {
    e.preventDefault();

    if (otpData.new_password !== otpData.confirm_password) {
      setError('Parollar mos kelmayapti');
      return;
    }

    if (otpData.new_password.length < 8) {
      setError('Yangi parol kamida 8 ta belgidan iborat bo\'lishi kerak');
      return;
    }

    setOtpLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/auth/change-password-with-otp/', {
        email: userData.email,
        otp_code: verifiedOtpCode,
        new_password: otpData.new_password,
        confirm_password: otpData.confirm_password
      });

      setSuccess(response.data.message || 'Parol muvaffaqiyatli o\'zgartirildi!');
      setOtpData({ otp_code: '', new_password: '', confirm_password: '' });
      setOtpSent(false);
      setOtpVerified(false);
      setVerifiedOtpCode('');
      setShowOTPForm(false);

      // Auto logout after 2 seconds
      setTimeout(() => {
        handleLogout();
      }, 2000);
    } catch (err) {
      console.error('Change password with OTP error:', err);
      setError(err.response?.data?.error || 'Parolni o\'zgartirishda xatolik');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout/');
    } catch (err) {
      console.error('Logout error:', err);
    }

    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    navigate('/login');
  };

  if (loading && !userData.username) {
    return (
      <div className="loading-container">
        <div className="loading">Yuklanmoqda...</div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="page-header">
        <h1>👤 Foydalanuvchi Profili</h1>
        <button onClick={handleLogout} className="btn btn-danger">
          🚪 Chiqish
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          {success}
        </div>
      )}

      {/* User Info Card */}
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            {userData.first_name ? userData.first_name[0].toUpperCase() : userData.username[0].toUpperCase()}
          </div>
          <div className="profile-title">
            <h2>{userData.first_name} {userData.last_name || userData.username}</h2>
            <p className="profile-username">@{userData.username}</p>
            {userData.is_superuser && (
              <span className="badge badge-admin">👑 Admin</span>
            )}
            {userData.is_staff && !userData.is_superuser && (
              <span className="badge badge-staff">⭐ Xodim</span>
            )}
          </div>
        </div>

        {!editing ? (
          <div className="profile-info">
            <div className="info-row">
              <div className="info-label">Foydalanuvchi nomi:</div>
              <div className="info-value">{userData.username}</div>
            </div>
            <div className="info-row">
              <div className="info-label">Email:</div>
              <div className="info-value">{userData.email || 'Kiritilmagan'}</div>
            </div>
            <div className="info-row">
              <div className="info-label">Ism:</div>
              <div className="info-value">{userData.first_name || 'Kiritilmagan'}</div>
            </div>
            <div className="info-row">
              <div className="info-label">Familiya:</div>
              <div className="info-value">{userData.last_name || 'Kiritilmagan'}</div>
            </div>

            <div className="profile-actions">
              <button onClick={() => setEditing(true)} className="btn btn-primary">
                ✏️ Tahrirlash
              </button>
              <button
                onClick={() => {
                  setShowOTPForm(!showOTPForm);
                  setOtpSent(false);
                  setOtpVerified(false);
                  setVerifiedOtpCode('');
                  setOtpData({ otp_code: '', new_password: '', confirm_password: '' });
                  setError('');
                  setSuccess('');
                }}
                className="btn btn-warning"
              >
                🔒 Parolni O'zgartirish
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="profile-edit-form">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                className="form-control"
                value={formData.email}
                onChange={handleChange}
                placeholder="email@example.com"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Ism</label>
                <input
                  type="text"
                  name="first_name"
                  className="form-control"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="Ismingiz"
                />
              </div>

              <div className="form-group">
                <label>Familiya</label>
                <input
                  type="text"
                  name="last_name"
                  className="form-control"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="Familiyangiz"
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-success" disabled={loading}>
                {loading ? 'Saqlanmoqda...' : '✓ Saqlash'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setEditing(false);
                  setFormData({
                    email: userData.email,
                    first_name: userData.first_name,
                    last_name: userData.last_name
                  });
                  setError('');
                  setSuccess('');
                }}
              >
                ✗ Bekor qilish
              </button>
            </div>
          </form>
        )}
      </div>

      {/* OTP Password Change Form */}
      {showOTPForm && (
        <div className="profile-card">
          <h3>📧 Parolni O'zgartirish</h3>

          {/* Progress indicator */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '10px',
            marginBottom: '30px',
            padding: '20px'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: otpSent ? '#48bb78' : '#4299e1',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '18px'
            }}>
              {otpSent ? '✓' : '1'}
            </div>
            <div style={{
              width: '60px',
              height: '3px',
              background: otpSent ? '#48bb78' : '#cbd5e0'
            }}></div>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: otpVerified ? '#48bb78' : otpSent ? '#4299e1' : '#cbd5e0',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '18px'
            }}>
              {otpVerified ? '✓' : '2'}
            </div>
            <div style={{
              width: '60px',
              height: '3px',
              background: otpVerified ? '#48bb78' : '#cbd5e0'
            }}></div>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: otpVerified ? '#4299e1' : '#cbd5e0',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '18px'
            }}>
              3
            </div>
          </div>

          {/* Step labels */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-around',
            marginBottom: '30px',
            fontSize: '13px',
            color: '#718096'
          }}>
            <div style={{
              textAlign: 'center',
              fontWeight: otpSent ? 'normal' : 'bold',
              color: otpSent ? '#48bb78' : '#4299e1'
            }}>
              OTP yuborish
            </div>
            <div style={{
              textAlign: 'center',
              fontWeight: otpVerified ? 'normal' : otpSent ? 'bold' : 'normal',
              color: otpVerified ? '#48bb78' : otpSent ? '#4299e1' : '#718096'
            }}>
              OTP tekshirish
            </div>
            <div style={{
              textAlign: 'center',
              fontWeight: otpVerified ? 'bold' : 'normal',
              color: otpVerified ? '#4299e1' : '#718096'
            }}>
              Parol yangilash
            </div>
          </div>

          {/* Step 1: Send OTP */}
          {!otpSent ? (
            <div>
              <div style={{
                padding: '20px',
                background: '#f7fafc',
                borderRadius: '8px',
                textAlign: 'center',
                marginBottom: '20px'
              }}>
                <p style={{ fontSize: '16px', marginBottom: '10px' }}>
                  <strong>Email manzilingiz:</strong>
                </p>
                <p style={{
                  fontSize: '18px',
                  color: '#2d3748',
                  background: 'white',
                  padding: '10px',
                  borderRadius: '6px',
                  border: '2px solid #e2e8f0'
                }}>
                  {userData.email || 'Email kiritilmagan'}
                </p>
              </div>

              <button
                type="button"
                className="btn btn-primary"
                onClick={handleRequestOTP}
                disabled={otpLoading || !userData.email}
                style={{ width: '100%', fontSize: '16px', padding: '12px' }}
              >
                {otpLoading ? '📤 Yuborilmoqda...' : '📧 OTP Kod Yuborish'}
              </button>

              {!userData.email && (
                <p style={{
                  marginTop: '15px',
                  color: '#e53e3e',
                  textAlign: 'center',
                  fontSize: '14px'
                }}>
                  ⚠️ Email manzili kiritilmagan. Iltimos, avval profilingizga email qo'shing.
                </p>
              )}
            </div>
          ) : !otpVerified ? (
            /* Step 2: Verify OTP */
            <form onSubmit={handleVerifyOTP} className="password-form">
              <div className="form-group">
                <label>OTP Kod (6 raqam)</label>
                <input
                  type="text"
                  name="otp_code"
                  className="form-control"
                  value={otpData.otp_code}
                  onChange={handleOTPChange}
                  placeholder="123456"
                  maxLength="6"
                  pattern="\d{6}"
                  required
                  style={{
                    fontSize: '20px',
                    letterSpacing: '4px',
                    textAlign: 'center',
                    fontWeight: 'bold'
                  }}
                />
                <small style={{ color: '#718096', fontSize: '13px' }}>
                  Emailingizga yuborilgan 6 raqamli kodni kiriting
                </small>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-success" disabled={otpLoading}>
                  {otpLoading ? 'Tekshirilmoqda...' : '✓ Kodni Tekshirish'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setOtpSent(false);
                    setOtpData({ otp_code: '', new_password: '', confirm_password: '' });
                    setError('');
                    setSuccess('');
                  }}
                >
                  ← Orqaga
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowOTPForm(false);
                    setOtpSent(false);
                    setOtpVerified(false);
                    setVerifiedOtpCode('');
                    setOtpData({ otp_code: '', new_password: '', confirm_password: '' });
                    setError('');
                    setSuccess('');
                  }}
                >
                  ✗ Bekor qilish
                </button>
              </div>

              <div style={{
                marginTop: '15px',
                padding: '12px',
                background: '#fff3cd',
                border: '1px solid #ffc107',
                borderRadius: '6px',
                textAlign: 'center'
              }}>
                <small style={{ color: '#856404', fontSize: '13px' }}>
                  ⏰ OTP kod olmadingizmi? <button
                    type="button"
                    onClick={handleRequestOTP}
                    disabled={otpLoading}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#007bff',
                      textDecoration: 'underline',
                      cursor: 'pointer',
                      padding: '0',
                      font: 'inherit'
                    }}
                  >
                    Qayta yuborish
                  </button>
                </small>
              </div>
            </form>
          ) : (
            /* Step 3: Change Password */
            <form onSubmit={handleOTPPasswordSubmit} className="password-form">
              <div style={{
                padding: '15px',
                background: '#d4edda',
                border: '1px solid #c3e6cb',
                borderRadius: '8px',
                marginBottom: '20px',
                textAlign: 'center'
              }}>
                <p style={{ margin: '0', color: '#155724', fontSize: '14px' }}>
                  ✅ <strong>OTP kod tasdiqlandi!</strong> Endi yangi parolni kiriting.
                </p>
              </div>

              <div className="form-group">
                <label>Yangi parol</label>
                <input
                  type="password"
                  name="new_password"
                  className="form-control"
                  value={otpData.new_password}
                  onChange={handleOTPChange}
                  placeholder="Kamida 8 ta belgi"
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Yangi parolni tasdiqlash</label>
                <input
                  type="password"
                  name="confirm_password"
                  className="form-control"
                  value={otpData.confirm_password}
                  onChange={handleOTPChange}
                  placeholder="Yangi parolni qayta kiriting"
                  required
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-success" disabled={otpLoading}>
                  {otpLoading ? 'O\'zgartirilmoqda...' : '✓ Parolni O\'zgartirish'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowOTPForm(false);
                    setOtpSent(false);
                    setOtpVerified(false);
                    setVerifiedOtpCode('');
                    setOtpData({ otp_code: '', new_password: '', confirm_password: '' });
                    setError('');
                    setSuccess('');
                  }}
                >
                  ✗ Bekor qilish
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* User Stats */}
      <div className="profile-stats">
        <div className="stat-card">
          <div className="stat-icon">👤</div>
          <div className="stat-info">
            <div className="stat-value">{userData.is_superuser ? 'Superuser' : 'Oddiy foydalanuvchi'}</div>
            <div className="stat-label">Foydalanuvchi turi</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔐</div>
          <div className="stat-info">
            <div className="stat-value">Token Auth</div>
            <div className="stat-label">Autentifikatsiya</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">Faol</div>
            <div className="stat-label">Holat</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
