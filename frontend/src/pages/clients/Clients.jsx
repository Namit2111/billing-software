import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { clientsAPI } from '../../lib/api'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  UsersIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

export default function Clients() {
  const [clients, setClients] = useState([])
  const [meta, setMeta] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingClient, setEditingClient] = useState(null)
  const [isSaving, setIsSaving] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm()

  useEffect(() => {
    loadClients()
  }, [])

  const loadClients = async () => {
    setIsLoading(true)
    try {
      const response = await clientsAPI.list({ per_page: 50 })
      setClients(response.data.data.clients)
      setMeta(response.data.data.meta)
    } catch (error) {
      console.error('Failed to load clients:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const openModal = (client = null) => {
    if (client) {
      setEditingClient(client)
      reset(client)
    } else {
      setEditingClient(null)
      reset({
        name: '',
        email: '',
        company_name: '',
        phone: '',
        address_line1: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'US',
      })
    }
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingClient(null)
    reset()
  }

  const onSubmit = async (data) => {
    setIsSaving(true)
    try {
      if (editingClient) {
        await clientsAPI.update(editingClient.id, data)
        toast.success('Client updated!')
      } else {
        await clientsAPI.create(data)
        toast.success('Client created!')
      }
      loadClients()
      closeModal()
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Failed to save client'
      toast.error(message)
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async (client) => {
    if (!confirm(`Delete ${client.name}?`)) return

    try {
      await clientsAPI.delete(client.id)
      toast.success('Client deleted')
      loadClients()
    } catch (error) {
      toast.error('Failed to delete client')
    }
  }

  const filteredClients = clients.filter(client =>
    client.name.toLowerCase().includes(search.toLowerCase()) ||
    client.email?.toLowerCase().includes(search.toLowerCase()) ||
    client.company_name?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-slate-900">Clients</h1>
          <p className="text-slate-500 mt-1">Manage your clients</p>
        </div>
        <button onClick={() => openModal()} className="btn-primary">
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Client
        </button>
      </div>

      {/* Search */}
      <div className="card p-4">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Clients Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-40 bg-slate-200 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : filteredClients.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClients.map((client) => (
            <div key={client.id} className="card-hover p-6 group">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-700 font-semibold text-lg">
                      {client.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      {client.company_name || client.name}
                    </h3>
                    {client.company_name && (
                      <p className="text-sm text-slate-500">{client.name}</p>
                    )}
                  </div>
                </div>
                <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <button
                    onClick={() => openModal(client)}
                    className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(client)}
                    className="p-1.5 text-slate-400 hover:text-danger-600 hover:bg-danger-50 rounded"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="mt-4 space-y-1 text-sm text-slate-500">
                {client.email && <p>{client.email}</p>}
                {client.phone && <p>{client.phone}</p>}
                {client.city && (
                  <p>{[client.city, client.state].filter(Boolean).join(', ')}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center">
          <UsersIcon className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No clients yet</h3>
          <p className="text-slate-500 mb-6">Add your first client to get started.</p>
          <button onClick={() => openModal()} className="btn-primary">
            <PlusIcon className="w-5 h-5 mr-2" />
            Add Client
          </button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold">
                {editingClient ? 'Edit Client' : 'Add Client'}
              </h2>
              <button onClick={closeModal} className="p-2 hover:bg-slate-100 rounded-lg">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="label">Contact Name *</label>
                  <input
                    {...register('name', { required: 'Name is required' })}
                    className={`input ${errors.name ? 'input-error' : ''}`}
                    placeholder="John Doe"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-danger-500">{errors.name.message}</p>
                  )}
                </div>

                <div className="col-span-2">
                  <label className="label">Company Name</label>
                  <input
                    {...register('company_name')}
                    className="input"
                    placeholder="Acme Inc."
                  />
                </div>

                <div>
                  <label className="label">Email</label>
                  <input
                    type="email"
                    {...register('email')}
                    className="input"
                    placeholder="john@example.com"
                  />
                </div>

                <div>
                  <label className="label">Phone</label>
                  <input
                    {...register('phone')}
                    className="input"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>

                <div className="col-span-2">
                  <label className="label">Address</label>
                  <input
                    {...register('address_line1')}
                    className="input"
                    placeholder="123 Main St"
                  />
                </div>

                <div>
                  <label className="label">City</label>
                  <input
                    {...register('city')}
                    className="input"
                    placeholder="New York"
                  />
                </div>

                <div>
                  <label className="label">State/Province</label>
                  <input
                    {...register('state')}
                    className="input"
                    placeholder="NY"
                  />
                </div>

                <div>
                  <label className="label">Postal Code</label>
                  <input
                    {...register('postal_code')}
                    className="input"
                    placeholder="10001"
                  />
                </div>

                <div>
                  <label className="label">Country</label>
                  <select {...register('country')} className="input">
                    <option value="US">United States</option>
                    <option value="CA">Canada</option>
                    <option value="GB">United Kingdom</option>
                    <option value="AU">Australia</option>
                    <option value="IN">India</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3 justify-end pt-4">
                <button type="button" onClick={closeModal} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={isSaving} className="btn-primary">
                  {isSaving ? 'Saving...' : editingClient ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

