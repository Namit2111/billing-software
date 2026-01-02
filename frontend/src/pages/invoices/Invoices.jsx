import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { invoicesAPI } from '../../lib/api'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function StatusBadge({ status }) {
  const styles = {
    draft: 'badge-draft',
    sent: 'badge-sent',
    paid: 'badge-paid',
    overdue: 'badge-overdue',
    cancelled: 'badge bg-slate-100 text-slate-500',
  }

  return (
    <span className={styles[status] || 'badge-draft'}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default function Invoices() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [invoices, setInvoices] = useState([])
  const [meta, setMeta] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')

  const statusFilter = searchParams.get('status') || ''
  const page = parseInt(searchParams.get('page') || '1')

  useEffect(() => {
    loadInvoices()
  }, [statusFilter, page])

  const loadInvoices = async () => {
    setIsLoading(true)
    try {
      const response = await invoicesAPI.list({
        status: statusFilter || undefined,
        page,
        per_page: 20,
      })
      setInvoices(response.data.data.invoices)
      setMeta(response.data.data.meta)
    } catch (error) {
      console.error('Failed to load invoices:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleStatusFilter = (status) => {
    if (status) {
      setSearchParams({ status })
    } else {
      setSearchParams({})
    }
  }

  const statuses = ['', 'draft', 'sent', 'paid', 'overdue']

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-slate-900">Invoices</h1>
          <p className="text-slate-500 mt-1">Manage your invoices</p>
        </div>
        <Link to="/invoices/new" className="btn-primary">
          <PlusIcon className="w-5 h-5 mr-2" />
          New Invoice
        </Link>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search invoices..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Status Filter */}
          <div className="flex gap-2">
            {statuses.map((status) => (
              <button
                key={status || 'all'}
                onClick={() => handleStatusFilter(status)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === status
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {status ? status.charAt(0).toUpperCase() + status.slice(1) : 'All'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
          </div>
        ) : invoices.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="table-header">Invoice</th>
                  <th className="table-header">Client</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Issue Date</th>
                  <th className="table-header">Due Date</th>
                  <th className="table-header text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {invoices.map((invoice) => (
                  <tr
                    key={invoice.id}
                    className="hover:bg-slate-50 transition-colors"
                  >
                    <td className="table-cell">
                      <Link
                        to={`/invoices/${invoice.id}`}
                        className="font-medium text-primary-600 hover:text-primary-700"
                      >
                        {invoice.invoice_number}
                      </Link>
                    </td>
                    <td className="table-cell">
                      {invoice.client_name || 'Unknown'}
                    </td>
                    <td className="table-cell">
                      <StatusBadge status={invoice.status} />
                    </td>
                    <td className="table-cell text-slate-500">
                      {formatDate(invoice.issue_date)}
                    </td>
                    <td className="table-cell text-slate-500">
                      {formatDate(invoice.due_date)}
                    </td>
                    <td className="table-cell text-right font-medium">
                      {formatCurrency(invoice.total, invoice.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center">
            <DocumentTextIcon className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">No invoices yet</h3>
            <p className="text-slate-500 mb-6">Create your first invoice to get started.</p>
            <Link to="/invoices/new" className="btn-primary">
              <PlusIcon className="w-5 h-5 mr-2" />
              Create Invoice
            </Link>
          </div>
        )}

        {/* Pagination */}
        {meta.total_pages > 1 && (
          <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing {(page - 1) * meta.per_page + 1} to{' '}
              {Math.min(page * meta.per_page, meta.total)} of {meta.total} invoices
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setSearchParams({ status: statusFilter, page: page - 1 })}
                disabled={!meta.has_prev}
                className="btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setSearchParams({ status: statusFilter, page: page + 1 })}
                disabled={!meta.has_next}
                className="btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

