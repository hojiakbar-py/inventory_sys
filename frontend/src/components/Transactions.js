import React, { useState, useEffect } from 'react';
import { transactionAPI, productAPI, warehouseAPI } from '../api';

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    product: '',
    warehouse: '',
    transaction_type: 'IN',
    quantity: '',
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [transactionsRes, productsRes, warehousesRes] = await Promise.all([
        transactionAPI.getAll(),
        productAPI.getAll(),
        warehouseAPI.getAll()
      ]);

      setTransactions(transactionsRes.data.results || transactionsRes.data);
      setProducts(productsRes.data.results || productsRes.data);
      setWarehouses(warehousesRes.data.results || warehousesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await transactionAPI.create(formData);
      setFormData({
        product: '',
        warehouse: '',
        transaction_type: 'IN',
        quantity: '',
        notes: ''
      });
      setShowForm(false);
      loadData();
    } catch (error) {
      console.error('Saqlashda xatolik:', error);
      alert('Xatolik yuz berdi!');
    }
  };

  if (loading) {
    return <div className="loading">Yuklanmoqda...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Tranzaksiyalar</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Yopish' : '+ Yangi tranzaksiya'}
        </button>
      </div>

      {showForm && (
        <div className="form-container" style={{ marginBottom: '30px' }}>
          <h2>Yangi tranzaksiya</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Mahsulot *</label>
              <select
                name="product"
                value={formData.product}
                onChange={handleChange}
                required
              >
                <option value="">Mahsulotni tanlang</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.sku})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Ombor *</label>
              <select
                name="warehouse"
                value={formData.warehouse}
                onChange={handleChange}
                required
              >
                <option value="">Omborni tanlang</option>
                {warehouses.map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Tranzaksiya turi *</label>
              <select
                name="transaction_type"
                value={formData.transaction_type}
                onChange={handleChange}
                required
              >
                <option value="IN">Kirish</option>
                <option value="OUT">Chiqish</option>
                <option value="ADJUSTMENT">Tuzatish</option>
              </select>
            </div>

            <div className="form-group">
              <label>Miqdor *</label>
              <input
                type="number"
                name="quantity"
                value={formData.quantity}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Izoh</label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-success">
                Saqlash
              </button>
              <button
                type="button"
                className="btn btn-danger"
                onClick={() => setShowForm(false)}
              >
                Bekor qilish
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="data-table">
        <div className="table-header">
          <h2>Tranzaksiyalar ro'yxati</h2>
        </div>
        <table>
          <thead>
            <tr>
              <th>Mahsulot</th>
              <th>Ombor</th>
              <th>Turi</th>
              <th>Miqdor</th>
              <th>Izoh</th>
              <th>Sana</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length > 0 ? (
              transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.product_name}</td>
                  <td>{transaction.warehouse_name}</td>
                  <td>
                    <span className={`badge ${
                      transaction.transaction_type === 'IN' ? 'badge-success' :
                      transaction.transaction_type === 'OUT' ? 'badge-danger' :
                      'badge-warning'
                    }`}>
                      {transaction.transaction_type === 'IN' ? 'Kirish' :
                       transaction.transaction_type === 'OUT' ? 'Chiqish' : 'Tuzatish'}
                    </span>
                  </td>
                  <td>{transaction.quantity}</td>
                  <td>{transaction.notes || '-'}</td>
                  <td>{new Date(transaction.created_at).toLocaleString('uz-UZ')}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center' }}>
                  Tranzaksiyalar topilmadi
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Transactions;
