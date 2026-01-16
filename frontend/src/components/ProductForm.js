import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productAPI, categoryAPI } from '../api';

function ProductForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    sku: '',
    description: '',
    unit: 'dona',
    price: '',
    min_stock_level: 10,
    image: null
  });

  useEffect(() => {
    loadCategories();
    if (id) {
      loadProduct();
    }
  }, [id]);

  const loadCategories = async () => {
    try {
      const response = await categoryAPI.getAll();
      setCategories(response.data.results || response.data);
    } catch (error) {
      console.error('Kategoriyalarni yuklashda xatolik:', error);
    }
  };

  const loadProduct = async () => {
    try {
      const response = await productAPI.get(id);
      setFormData({
        name: response.data.name,
        category: response.data.category || '',
        sku: response.data.sku,
        description: response.data.description || '',
        unit: response.data.unit,
        price: response.data.price,
        min_stock_level: response.data.min_stock_level,
        image: null
      });
    } catch (error) {
      console.error('Mahsulotni yuklashda xatolik:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'image') {
      setFormData({ ...formData, [name]: files[0] });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = new FormData();
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== '') {
          submitData.append(key, formData[key]);
        }
      });

      if (id) {
        await productAPI.update(id, submitData);
      } else {
        await productAPI.create(submitData);
      }

      navigate('/products');
    } catch (error) {
      console.error('Saqlashda xatolik:', error);
      alert('Xatolik yuz berdi!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>{id ? 'Mahsulotni tahrirlash' : 'Yangi mahsulot'}</h1>
      </div>

      <div className="form-container">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Mahsulot nomi *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>SKU kodi *</label>
            <input
              type="text"
              name="sku"
              value={formData.sku}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Kategoriya</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
            >
              <option value="">Kategoriyani tanlang</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Narx *</label>
            <input
              type="number"
              name="price"
              value={formData.price}
              onChange={handleChange}
              step="0.01"
              required
            />
          </div>

          <div className="form-group">
            <label>O'lchov birligi</label>
            <input
              type="text"
              name="unit"
              value={formData.unit}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Minimal zaxira darajasi</label>
            <input
              type="number"
              name="min_stock_level"
              value={formData.min_stock_level}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Tavsif</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Rasm</label>
            <input
              type="file"
              name="image"
              onChange={handleChange}
              accept="image/*"
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Saqlanmoqda...' : 'Saqlash'}
            </button>
            <button
              type="button"
              className="btn btn-danger"
              onClick={() => navigate('/products')}
            >
              Bekor qilish
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ProductForm;
