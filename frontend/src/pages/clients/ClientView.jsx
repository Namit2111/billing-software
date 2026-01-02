import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { clientsAPI, invoicesAPI } from '../../lib/api'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

export default function ClientView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [client, setClient] = useState(null)
  const [invoices, setInvoices] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadClient()
  }, [id])

  const loadClient = async () => {
    try {
      const [clientRes, invoicesRes] = await Promise.all([
        clientsAPI.get(id),
        invoicesAPI.list({ client_id: id }),
      ])
      setClient(clientRes.data.data)
      setInvoices(invoicesRes.data.data.invoices)
    } catch (error) {
      navigate('/clients')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (!client) return null

  return (
    <div className="animate-fadeIn">
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate('/clients')}
          className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <ArrowLeftIcon className="w-5 h-5" />
        </button>
        <h1 className="text-2xl font-display font-bold text-slate-900">
          {client.company_name || client.name}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card p-6">
          <h2 className="font-semibold text-slate-900 mb-4">Contact Info</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Name</dt>
              <dd className="font-medium">{client.name}</dd>
            </div>
            {client.email && (
              <div>
                <dt className="text-slate-500">Email</dt>
                <dd className="font-medium">{client.email}</dd>
              </div>
            )}
            {client.phone && (
              <div>
                <dt className="text-slate-500">Phone</dt>
                <dd className="font-medium">{client.phone}</dd>
              </div>
            )}
          </dl>
        </div>

        <div className="lg:col-span-2 card p-6">
          <h2 className="font-semibold text-slate-900 mb-4">Recent Invoices</h2>
          {invoices.length > 0 ? (
            <div className="space-y-2">
              {invoices.map((invoice) => (
                <div
                  key={invoice.id}
                  className="flex items-center justify-between p-3 hover:bg-slate-50 rounded-lg cursor-pointer"
                  onClick={() => navigate(`/invoices/${invoice.id}`)}
                >
                  <span className="font-medium text-primary-600">{invoice.invoice_number}</span>
                  <span className="text-slate-500">{invoice.status}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500">No invoices yet</p>
          )}
        </div>
      </div>
    </div>
  )
}

