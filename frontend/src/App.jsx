import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, ShoppingCart, User, TrendingUp, Gift } from 'lucide-react'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [users, setUsers] = useState([])
  const [products, setProducts] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('dashboard')

  useEffect(() => {
    fetchUsers()
    fetchProducts()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users?limit=50`)
      setUsers(response.data)
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/products?limit=50`)
      setProducts(response.data)
    } catch (error) {
      console.error('Error fetching products:', error)
    }
  }

  const getRecommendations = async (userId) => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/recommendations/${userId}`)
      setRecommendations(response.data.recommendations || [])
      setSelectedUser(users.find(u => u.id === userId))
    } catch (error) {
      console.error('Error fetching recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateData = async () => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE_URL}/generate-data`)
      await fetchUsers()
      await fetchProducts()
      alert('Sample data generated successfully!')
    } catch (error) {
      console.error('Error generating data:', error)
      alert('Error generating data')
    } finally {
      setLoading(false)
    }
  }

  const Dashboard = () => (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <User className="w-8 h-8 text-blue-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold">Total Users</h3>
              <p className="text-2xl font-bold text-blue-600">{users.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <ShoppingCart className="w-8 h-8 text-green-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold">Total Products</h3>
              <p className="text-2xl font-bold text-green-600">{products.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-purple-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold">Recommendations</h3>
              <p className="text-2xl font-bold text-purple-600">{recommendations.length}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <button
            onClick={generateData}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Sample Data'}
          </button>
        </div>
      </div>
    </div>
  )

  const UsersTab = () => (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Users</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {users.map((user) => (
          <div key={user.id} className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="font-semibold text-lg">{user.name}</h3>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-500">Age: {user.age} | {user.gender}</p>
            <p className="text-sm text-gray-500">Persona: {user.persona_type}</p>
            <p className="text-sm text-gray-500">
              Purchases: {user.total_purchases} | Spent: ${user.total_spent}
            </p>
            <button
              onClick={() => getRecommendations(user.id)}
              className="mt-2 bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
            >
              Get Recommendations
            </button>
          </div>
        ))}
      </div>
    </div>
  )

  const ProductsTab = () => (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Products</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((product) => (
          <div key={product.id} className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="font-semibold text-lg">{product.name}</h3>
            <p className="text-gray-600">{product.brand}</p>
            <p className="text-sm text-gray-500">Category: {product.category}</p>
            <p className="text-lg font-bold text-green-600">${product.price}</p>
            <div className="flex items-center mt-2">
              <span className="text-yellow-500">★</span>
              <span className="ml-1 text-sm">{product.rating}/5</span>
              <span className="ml-2 text-sm text-gray-500">({product.review_count} reviews)</span>
            </div>
            {product.discount_percentage > 0 && (
              <div className="mt-2">
                <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                  {product.discount_percentage}% OFF
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )

  const RecommendationsTab = () => (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Recommendations</h2>
      
      {selectedUser && (
        <div className="bg-blue-50 p-4 rounded-lg mb-6">
          <h3 className="font-semibold">Recommendations for: {selectedUser.name}</h3>
          <p className="text-sm text-gray-600">Persona: {selectedUser.persona_type}</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4">Loading recommendations...</p>
        </div>
      ) : recommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendations.map((rec, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-lg">{rec.product.name}</h3>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  Score: {rec.score.toFixed(2)}
                </span>
              </div>
              <p className="text-gray-600">{rec.product.brand}</p>
              <p className="text-sm text-gray-500">Category: {rec.product.category}</p>
              <p className="text-lg font-bold text-green-600">${rec.product.price}</p>
              <div className="flex items-center mt-2">
                <span className="text-yellow-500">★</span>
                <span className="ml-1 text-sm">{rec.product.rating}/5</span>
              </div>
              {rec.product.discount_percentage > 0 && (
                <div className="mt-2">
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                    <Gift className="w-4 h-4 inline mr-1" />
                    {rec.product.discount_percentage}% OFF
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <Search className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p>Select a user to see their recommendations</p>
        </div>
      )}
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-800">Recommendation Engine</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'dashboard' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('users')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'users' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Users
              </button>
              <button
                onClick={() => setActiveTab('products')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'products' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Products
              </button>
              <button
                onClick={() => setActiveTab('recommendations')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'recommendations' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Recommendations
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'products' && <ProductsTab />}
        {activeTab === 'recommendations' && <RecommendationsTab />}
      </main>
    </div>
  )
}

export default App
