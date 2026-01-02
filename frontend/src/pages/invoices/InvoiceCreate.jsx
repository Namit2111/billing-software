import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm, useFieldArray } from 'react-hook-form'
import toast from 'react-hot-toast'
import { invoicesAPI, clientsAPI, productsAPI, settingsAPI } from '../../lib/api'
import {
  PlusIcon,
  TrashIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline'

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

export default function InvoiceCreate() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  
  const [clients, setClients] = useState([])
  const [products, setProducts] = useState([])
  const [organization, setOrganization] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      client_id: '',
      issue_date: new Date().toISOString().split('T')[0],
      due_date: '',
      notes: '',
      terms: '',
      items: [{ description: '', quantity: 1, unit_price: 0, tax_rate: 0 }],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  })

  const watchItems = watch('items')
  const currency = organization?.currency || 'USD'

  // Calculate totals
  const subtotal = watchItems?.reduce((sum, item) => {
    return sum + (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)
  }, 0) || 0

  const taxTotal = watchItems?.reduce((sum, item) => {
    const itemSubtotal = (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)
    return sum + itemSubtotal * ((parseFloat(item.tax_rate) || 0) / 100)
  }, 0) || 0

  const total = subtotal + taxTotal

  useEffect(() => {
    loadInitialData()
  }, [id])

  const loadInitialData = async () => {
    setIsLoading(true)
    try {
      const [clientsRes, productsRes, orgRes] = await Promise.all([
        clientsAPI.list({ per_page: 100 }),
        productsAPI.list({ per_page: 100 }),
        settingsAPI.getOrganization(),
      ])

      setClients(clientsRes.data.data.clients)
      setProducts(productsRes.data.data.products)
      setOrganization(orgRes.data.data)

      // Set default due date based on payment terms
      const paymentTerms = orgRes.data.data.default_payment_terms || 30
      const dueDate = new Date()
      dueDate.setDate(dueDate.getDate() + paymentTerms)
      setValue('due_date', dueDate.toISOString().split('T')[0])

      // Load invoice if editing
      if (id) {
        const invoiceRes = await invoicesAPI.get(id)
        const invoice = invoiceRes.data.data
        
        reset({
          client_id: invoice.client_id,
          issue_date: invoice.issue_date,
          due_date: invoice.due_date,
          notes: invoice.notes || '',
          terms: invoice.terms || '',
          items: invoice.items.map(item => ({
            description: item.description,
            quantity: item.quantity,
            unit_price: item.unit_price,
            tax_rate: item.tax_rate,
            product_id: item.product_id,
          })),
        })
      }
    } catch (error) {
      console.error('Failed to load data:', error)
      toast.error('Failed to load data')
    } finally {
      setIsLoading(false)
    }
  }

  const onSubmit = async (data) => {
    if (data.items.length === 0) {
      toast.error('Please add at least one line item')
      return
    }

    setIsSaving(true)
    try {
      if (isEdit) {
        await invoicesAPI.update(id, data)
        toast.success('Invoice updated!')
      } else {
        const response = await invoicesAPI.create(data)
        toast.success('Invoice created!')
        navigate(`/invoices/${response.data.data.id}`)
        return
      }
      navigate('/invoices')
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Failed to save invoice'
      toast.error(message)
    } finally {
      setIsSaving(false)
    }
  }

  const addProductItem = (product) => {
    append({
      product_id: product.id,
      description: product.name,
      quantity: 1,
      unit_price: product.unit_price,
      tax_rate: product.tax_rate,
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  return (
    <div className="animate-fadeIn">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate('/invoices')}
          className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <ArrowLeftIcon className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-display font-bold text-slate-900">
            {isEdit ? 'Edit Invoice' : 'New Invoice'}
          </h1>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Client Selection */}
            <div className="card p-6">
              <h2 className="font-semibold text-slate-900 mb-4">Client</h2>
              <select
                {...register('client_id', { required: 'Please select a client' })}
                className={`input ${errors.client_id ? 'input-error' : ''}`}
              >
                <option value="">Select a client</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.company_name || client.name} ({client.email})
                  </option>
                ))}
              </select>
              {errors.client_id && (
                <p className="mt-1 text-sm text-danger-500">{errors.client_id.message}</p>
              )}
            </div>

            {/* Dates */}
            <div className="card p-6">
              <h2 className="font-semibold text-slate-900 mb-4">Dates</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Issue Date</label>
                  <input
                    type="date"
                    {...register('issue_date', { required: true })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Due Date</label>
                  <input
                    type="date"
                    {...register('due_date', { required: true })}
                    className="input"
                  />
                </div>
              </div>
            </div>

            {/* Line Items */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-slate-900">Line Items</h2>
                {products.length > 0 && (
                  <div className="relative group">
                    <button
                      type="button"
                      className="btn-secondary text-sm"
                    >
                      Add from Products
                    </button>
                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-slate-200 py-2 hidden group-hover:block z-10">
                      {products.slice(0, 10).map((product) => (
                        <button
                          key={product.id}
                          type="button"
                          onClick={() => addProductItem(product)}
                          className="w-full text-left px-4 py-2 text-sm hover:bg-slate-50"
                        >
                          <span className="font-medium">{product.name}</span>
                          <span className="text-slate-500 ml-2">
                            {formatCurrency(product.unit_price, currency)}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                {fields.map((field, index) => (
                  <div key={field.id} className="grid grid-cols-12 gap-3 items-start">
                    <div className="col-span-5">
                      <input
                        {...register(`items.${index}.description`, { required: true })}
                        placeholder="Description"
                        className="input"
                      />
                    </div>
                    <div className="col-span-2">
                      <input
                        type="number"
                        step="0.01"
                        {...register(`items.${index}.quantity`, { required: true, min: 0.01 })}
                        placeholder="Qty"
                        className="input"
                      />
                    </div>
                    <div className="col-span-2">
                      <input
                        type="number"
                        step="0.01"
                        {...register(`items.${index}.unit_price`, { required: true, min: 0 })}
                        placeholder="Price"
                        className="input"
                      />
                    </div>
                    <div className="col-span-2">
                      <input
                        type="number"
                        step="0.01"
                        {...register(`items.${index}.tax_rate`)}
                        placeholder="Tax %"
                        className="input"
                      />
                    </div>
                    <div className="col-span-1 flex justify-center">
                      {fields.length > 1 && (
                        <button
                          type="button"
                          onClick={() => remove(index)}
                          className="p-2 text-slate-400 hover:text-danger-500 transition-colors"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <button
                type="button"
                onClick={() => append({ description: '', quantity: 1, unit_price: 0, tax_rate: 0 })}
                className="mt-4 flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium text-sm"
              >
                <PlusIcon className="w-4 h-4" />
                Add Line Item
              </button>
            </div>

            {/* Notes */}
            <div className="card p-6">
              <h2 className="font-semibold text-slate-900 mb-4">Notes & Terms</h2>
              <div className="space-y-4">
                <div>
                  <label className="label">Notes (visible to client)</label>
                  <textarea
                    {...register('notes')}
                    rows={3}
                    className="input"
                    placeholder="Thank you for your business!"
                  />
                </div>
                <div>
                  <label className="label">Terms & Conditions</label>
                  <textarea
                    {...register('terms')}
                    rows={3}
                    className="input"
                    placeholder="Payment is due within 30 days..."
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar - Preview & Actions */}
          <div className="space-y-6">
            {/* Summary */}
            <div className="card p-6 sticky top-6">
              <h2 className="font-semibold text-slate-900 mb-4">Summary</h2>
              
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Subtotal</span>
                  <span className="font-medium">{formatCurrency(subtotal, currency)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Tax</span>
                  <span className="font-medium">{formatCurrency(taxTotal, currency)}</span>
                </div>
                <div className="border-t border-slate-200 pt-3">
                  <div className="flex justify-between">
                    <span className="font-semibold text-slate-900">Total</span>
                    <span className="text-xl font-bold text-primary-600">
                      {formatCurrency(total, currency)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="btn-primary w-full py-3"
                >
                  {isSaving ? 'Saving...' : isEdit ? 'Update Invoice' : 'Create Invoice'}
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/invoices')}
                  className="btn-secondary w-full"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  )
}

