import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { productsAPI } from '../../lib/api'
import { useAuthStore } from '../../stores/authStore'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  CubeIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

export default function Products() {
  const { organization } = useAuthStore()
  const [products, setProducts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [isSaving, setIsSaving] = useState(false)

  const currency = organization?.currency || 'USD'

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm()

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    setIsLoading(true)
    try {
      const response = await productsAPI.list({ per_page: 100 })
      setProducts(response.data.data.products)
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const openModal = (product = null) => {
    if (product) {
      setEditingProduct(product)
      reset(product)
    } else {
      setEditingProduct(null)
      reset({
        name: '',
        description: '',
        unit_price: '',
        unit: 'unit',
        tax_rate: 0,
        sku: '',
      })
    }
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingProduct(null)
    reset()
  }

  const onSubmit = async (data) => {
    setIsSaving(true)
    try {
      if (editingProduct) {
        await productsAPI.update(editingProduct.id, data)
        toast.success('Product updated!')
      } else {
        await productsAPI.create(data)
        toast.success('Product created!')
      }
      loadProducts()
      closeModal()
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Failed to save product'
      toast.error(message)
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async (product) => {
    if (!confirm(`Delete ${product.name}?`)) return

    try {
      await productsAPI.delete(product.id)
      toast.success('Product deleted')
      loadProducts()
    } catch (error) {
      toast.error('Failed to delete product')
    }
  }

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(search.toLowerCase()) ||
    product.sku?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-slate-900">Products & Services</h1>
          <p className="text-slate-500 mt-1">Manage your product catalog</p>
        </div>
        <button onClick={() => openModal()} className="btn-primary">
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Product
        </button>
      </div>

      {/* Search */}
      <div className="card p-4">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Products Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
          </div>
        ) : filteredProducts.length > 0 ? (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="table-header">Product</th>
                <th className="table-header">SKU</th>
                <th className="table-header text-right">Price</th>
                <th className="table-header text-right">Tax</th>
                <th className="table-header w-20"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredProducts.map((product) => (
                <tr key={product.id} className="hover:bg-slate-50 transition-colors">
                  <td className="table-cell">
                    <div>
                      <p className="font-medium text-slate-900">{product.name}</p>
                      {product.description && (
                        <p className="text-sm text-slate-500 truncate max-w-xs">
                          {product.description}
                        </p>
                      )}
                    </div>
                  </td>
                  <td className="table-cell text-slate-500">
                    {product.sku || '-'}
                  </td>
                  <td className="table-cell text-right font-medium">
                    {formatCurrency(product.unit_price, currency)}
                    <span className="text-slate-400 text-sm ml-1">/{product.unit}</span>
                  </td>
                  <td className="table-cell text-right text-slate-500">
                    {product.tax_rate}%
                  </td>
                  <td className="table-cell">
                    <div className="flex gap-1 justify-end">
                      <button
                        onClick={() => openModal(product)}
                        className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded"
                      >
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(product)}
                        className="p-1.5 text-slate-400 hover:text-danger-600 hover:bg-danger-50 rounded"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-12 text-center">
            <CubeIcon className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">No products yet</h3>
            <p className="text-slate-500 mb-6">Add products to use them in invoices.</p>
            <button onClick={() => openModal()} className="btn-primary">
              <PlusIcon className="w-5 h-5 mr-2" />
              Add Product
            </button>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-lg">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold">
                {editingProduct ? 'Edit Product' : 'Add Product'}
              </h2>
              <button onClick={closeModal} className="p-2 hover:bg-slate-100 rounded-lg">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="label">Product Name *</label>
                <input
                  {...register('name', { required: 'Name is required' })}
                  className={`input ${errors.name ? 'input-error' : ''}`}
                  placeholder="Web Design Service"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-danger-500">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="label">Description</label>
                <textarea
                  {...register('description')}
                  rows={2}
                  className="input"
                  placeholder="Brief description of the product or service"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Unit Price *</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('unit_price', { required: true, min: 0 })}
                    className="input"
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <label className="label">Unit</label>
                  <select {...register('unit')} className="input">
                    <option value="unit">Unit</option>
                    <option value="hour">Hour</option>
                    <option value="day">Day</option>
                    <option value="month">Month</option>
                    <option value="project">Project</option>
                    <option value="piece">Piece</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Tax Rate (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('tax_rate')}
                    className="input"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="label">SKU</label>
                  <input
                    {...register('sku')}
                    className="input"
                    placeholder="WDS-001"
                  />
                </div>
              </div>

              <div className="flex gap-3 justify-end pt-4">
                <button type="button" onClick={closeModal} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={isSaving} className="btn-primary">
                  {isSaving ? 'Saving...' : editingProduct ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

