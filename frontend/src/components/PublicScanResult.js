import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { qrScanAPI } from '../api';

function PublicScanResult() {
    const { qrData } = useParams();
    const navigate = useNavigate();
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await qrScanAPI.scan(decodeURIComponent(qrData));
                setResult(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Skaner xatolik:', err);
                setError(err.response?.data?.error || 'Ma\'lumot topilmadi');
                setLoading(false);
            }
        };

        if (qrData) {
            fetchData();
        }
    }, [qrData]);

    if (loading) return <div style={{ padding: '20px', textAlign: 'center' }}>Yuklanmoqda...</div>;

    if (error) return (
        <div style={{ padding: '20px', textAlign: 'center', color: 'red' }}>
            <h3>Xatolik</h3>
            <p>{error}</p>
            <button onClick={() => navigate('/qr-scanner')} className="btn btn-primary">Qayta skanerlash</button>
        </div>
    );

    if (!result) return null;

    // Render logic copied/adapted from QRScanner.js specifically for result display
    return (
        <div className="container" style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
            <button
                onClick={() => navigate('/qr-scanner')}
                className="btn btn-secondary"
                style={{ marginBottom: '20px' }}
            >
                ← Ortga
            </button>

            <h2>
                {result.type === 'equipment' ? '🖥️ Qurilma Ma\'lumotlari' : '👤 Hodim Ma\'lumotlari'}
            </h2>

            {/* Copy the display logic from QRScanner.js result section here */}
            {/* ... */}
            {/* I will reuse the logic I just wrote in QRScanner.js but ensure it works here */}

            {result.type === 'equipment' && (
                <div>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '20px',
                        marginBottom: '20px'
                    }}>
                        <div style={{
                            backgroundColor: '#f5f5f5',
                            padding: '15px',
                            borderRadius: '8px',
                            border: '2px solid #e0e0e0'
                        }}>
                            <h4 style={{ color: '#1976d2', marginBottom: '10px', fontSize: '1.1rem' }}>
                                📋 Asosiy Ma'lumotlar
                            </h4>
                            <p style={{ marginBottom: '8px' }}>
                                <strong>Nomi:</strong><br />{result.data.name}
                            </p>
                            <p style={{ marginBottom: '8px' }}>
                                <strong>Inventar #:</strong><br />{result.data.inventory_number}
                            </p>
                            <p style={{ marginBottom: '8px' }}>
                                <strong>Seriya #:</strong><br />{result.data.serial_number || 'N/A'}
                            </p>
                            <p style={{ marginBottom: '8px' }}>
                                <strong>Kategoriya:</strong><br />{result.data.category_name || 'N/A'}
                            </p>
                        </div>
                        {/* ... Add other sections similarly ... */}
                    </div>
                    {/* ... */}
                </div>
            )}

            {result.type === 'employee' && (
                <div>
                    {/* Employee display logic */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '20px',
                        marginBottom: '20px'
                    }}>
                        <div style={{
                            backgroundColor: '#f5f5f5',
                            padding: '15px',
                            borderRadius: '8px',
                            border: '2px solid #e0e0e0'
                        }}>
                            <h4 style={{ color: '#1976d2', marginBottom: '10px', fontSize: '1.1rem' }}>
                                👤 Shaxsiy Ma'lumotlar
                            </h4>
                            <p style={{ marginBottom: '8px' }}>
                                <strong>F.I.O:</strong><br />{result.data.full_name}
                            </p>
                            <p style={{ marginBottom: '8px' }}>
                                <strong>Hodim ID:</strong><br />{result.data.employee_id}
                            </p>
                            <p style={{ marginBottom: '8px' }}>
                                <strong>Lavozim:</strong><br />{result.data.position}
                            </p>
                            <p style={{ marginBottom: 0 }}>
                                <strong>Bo'lim:</strong><br />{result.data.department_name || 'N/A'}
                            </p>
                        </div>
                        {/* ... */}
                    </div>

                    {/* Detailed Equipment Table */}
                    {result.current_equipment && result.current_equipment.length > 0 && (
                        <div style={{
                            backgroundColor: '#e3f2fd',
                            padding: '15px',
                            borderRadius: '8px',
                            marginTop: '20px',
                            border: '2px solid #2196f3'
                        }}>
                            <h3 style={{ color: '#1565c0', marginBottom: '15px' }}>
                                💻 Joriy Qurilmalar ({result.current_equipment.length})
                            </h3>
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', minWidth: '800px', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ backgroundColor: '#bbdefb' }}>
                                            <th style={{ padding: '10px', textAlign: 'left' }}>Inventar #</th>
                                            <th style={{ padding: '10px', textAlign: 'left' }}>Nomi</th>
                                            <th style={{ padding: '10px', textAlign: 'left' }}>Kategoriya</th>
                                            <th style={{ padding: '10px', textAlign: 'left' }}>Holat</th>
                                            <th style={{ padding: '10px', textAlign: 'left' }}>Tayinlangan</th>
                                            <th style={{ padding: '10px', textAlign: 'left' }}>Qaytarish</th>
                                            <th style={{ padding: '10px', textAlign: 'left' }}>Muddat</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {result.current_equipment.map((eq, index) => {
                                            const isOverdue = eq.is_overdue;
                                            const rowStyle = isOverdue ? { backgroundColor: '#ffebee' } : { borderBottom: '1px solid #90caf9' };

                                            return (
                                                <tr key={index} style={rowStyle}>
                                                    <td style={{ padding: '10px' }}>{eq.inventory_number}</td>
                                                    <td style={{ padding: '10px' }}>{eq.name}</td>
                                                    <td style={{ padding: '10px' }}>{eq.category || '-'}</td>
                                                    <td style={{ padding: '10px' }}>
                                                        <div>
                                                            <span style={{ fontWeight: 'bold' }}>{eq.status}</span>
                                                            {eq.condition && <div style={{ fontSize: '0.85em', color: '#666' }}>{eq.condition}</div>}
                                                        </div>
                                                    </td>
                                                    <td style={{ padding: '10px' }}>{new Date(eq.assigned_date).toLocaleDateString('uz-UZ')}</td>
                                                    <td style={{ padding: '10px' }}>
                                                        {eq.expected_return_date ? (
                                                            <span style={{ color: isOverdue ? '#d32f2f' : 'inherit', fontWeight: isOverdue ? 'bold' : 'normal' }}>
                                                                {new Date(eq.expected_return_date).toLocaleDateString('uz-UZ')}
                                                                {isOverdue && <div style={{ fontSize: '0.8em', color: '#d32f2f' }}>Muddat o'tgan!</div>}
                                                            </span>
                                                        ) : (
                                                            <span style={{ color: '#666', fontStyle: 'italic' }}>Belgilanmagan</span>
                                                        )}
                                                    </td>
                                                    <td style={{ padding: '10px' }}>
                                                        <span style={{
                                                            padding: '3px 8px',
                                                            borderRadius: '12px',
                                                            backgroundColor: isOverdue ? '#d32f2f' : '#2196f3',
                                                            color: 'white',
                                                            fontWeight: 'bold',
                                                            fontSize: '0.85rem'
                                                        }}>
                                                            {eq.days_assigned} kun
                                                        </span>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default PublicScanResult;
