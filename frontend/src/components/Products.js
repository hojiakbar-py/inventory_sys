import React, { useState, useEffect } from 'react';
import { productAPI, categoryAPI } from '../api';
import { Link } from 'react-router-dom';

function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  useEffect(() => {
    loadData();
  }, [searchTerm, selectedCategory]);

  const loadData = async () => {
    try {
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedCategory) params.category = selectedCategory;

      const [productsRes, categoriesRes] = await Promise.all([
        productAPI.getAll(params),
        categoryAPI.getAll()
      ]);

      setProducts(productsRes.data.results || productsRes.data);
      setCategories(categoriesRes.data.results || categoriesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Mahsulotni o\'chirmoqchimisiz?')) {
      try {
        await productAPI.delete(id);
        loadData();
      } catch (error) {
        console.error('O\'chirishda xatolik:', error);
      }
    }
  };

  if (loading) {
    return <div className="loading">Yuklanmoqda...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Mahsulotlar</h1>
        <Link to="/products/new" className="btn btn-primary">
          + Yangi mahsulot
        </Link>
      </div>

      <div className="data-table">
        <div className="table-header">
          <h2>Mahsulotlar ro'yxati</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              className="search-bar"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">Barcha kategoriyalar</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            <input
              type="text"
              className="search-bar"
              placeholder="Qidirish..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>Nomi</th>
              <th>Kategoriya</th>
              <th>Narx</th>
              <th>Birlik</th>
              <th>Zaxira</th>
              <th>Holat</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            {products.length > 0 ? (
              products.map((product) => (
                <tr key={product.id}>
                  <td>{product.sku}</td>
                  <td>{product.name}</td>
                  <td>{product.category_name || 'N/A'}</td>
                  <td>{product.price} so'm</td>
                  <td>{product.unit}</td>
                  <td>{product.total_stock}</td>
                  <td>
                    {product.low_stock ? (
                      <span className="badge badge-danger">Kam</span>
                    ) : (
                      <span className="badge badge-success">Yetarli</span>
                    )}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <Link to={`/products/${product.id}`} className="btn btn-primary">
                        Ko'rish
                      </Link>
                      <Link to={`/products/edit/${product.id}`} className="btn btn-warning">
                        Tahrirlash
                      </Link>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDelete(product.id)}
                      >
                        O'chirish
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center' }}>
                  Mahsulotlar topilmadi
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Products;
