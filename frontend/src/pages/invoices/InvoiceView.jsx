import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { invoicesAPI } from '../../lib/api'
import {
  ArrowLeftIcon,
  PencilIcon,
  PaperAirplaneIcon,
  CheckCircleIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline'

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'long',
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
    <span className={`${styles[status] || 'badge-draft'} text-sm px-3 py-1`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default function InvoiceView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [invoice, setInvoice] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showSendModal, setShowSendModal] = useState(false)
  const [showPayModal, setShowPayModal] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [isMarking, setIsMarking] = useState(false)

  useEffect(() => {
    loadInvoice()
  }, [id])

  const loadInvoice = async () => {
    try {
      const response = await invoicesAPI.get(id)
      setInvoice(response.data.data)
    } catch (error) {
      toast.error('Failed to load invoice')
      navigate('/invoices')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSend = async () => {
    setIsSending(true)
    try {
      await invoicesAPI.send(id, { attach_pdf: true })
      toast.success('Invoice sent successfully!')
      loadInvoice()
      setShowSendModal(false)
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Failed to send invoice'
      toast.error(message)
    } finally {
      setIsSending(false)
    }
  }

  const handleMarkPaid = async () => {
    setIsMarking(true)
    try {
      await invoicesAPI.markPaid(id, {})
      toast.success('Invoice marked as paid!')
      loadInvoice()
      setShowPayModal(false)
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Failed to mark as paid'
      toast.error(message)
    } finally {
      setIsMarking(false)
    }
  }

  const handleDownloadPdf = async () => {
    try {
      const response = await invoicesAPI.downloadPdf(id)
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `invoice-${invoice.invoice_number}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      toast.error('Failed to download PDF')
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this invoice?')) return

    try {
      await invoicesAPI.delete(id)
      toast.success('Invoice deleted')
      navigate('/invoices')
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Failed to delete invoice'
      toast.error(message)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (!invoice) return null

  const client = invoice.client || {}

  return (
    <div className="animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/invoices')}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-display font-bold text-slate-900">
                {invoice.invoice_number}
              </h1>
              <StatusBadge status={invoice.status} />
            </div>
            <p className="text-slate-500 mt-1">
              {client.company_name || client.name}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {invoice.status === 'draft' && (
            <>
              <Link
                to={`/invoices/${id}/edit`}
                className="btn-secondary"
              >
                <PencilIcon className="w-4 h-4 mr-2" />
                Edit
              </Link>
              <button
                onClick={() => setShowSendModal(true)}
                className="btn-primary"
              >
                <PaperAirplaneIcon className="w-4 h-4 mr-2" />
                Send Invoice
              </button>
            </>
          )}
          {(invoice.status === 'sent' || invoice.status === 'overdue') && (
            <>
              <button
                onClick={() => setShowSendModal(true)}
                className="btn-secondary"
              >
                <EnvelopeIcon className="w-4 h-4 mr-2" />
                Resend
              </button>
              <button
                onClick={() => setShowPayModal(true)}
                className="btn-success"
              >
                <CheckCircleIcon className="w-4 h-4 mr-2" />
                Mark as Paid
              </button>
            </>
          )}
          <button onClick={handleDownloadPdf} className="btn-secondary">
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Download PDF
          </button>
          {invoice.status === 'draft' && (
            <button onClick={handleDelete} className="btn-ghost text-danger-600">
              <TrashIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Invoice Preview */}
      <div className="card p-8 max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-3xl font-display font-bold text-primary-600">INVOICE</h2>
            <p className="text-slate-500 mt-1">{invoice.invoice_number}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-500">Issue Date</p>
            <p className="font-medium">{formatDate(invoice.issue_date)}</p>
            <p className="text-sm text-slate-500 mt-2">Due Date</p>
            <p className="font-medium">{formatDate(invoice.due_date)}</p>
          </div>
        </div>

        {/* Bill To */}
        <div className="mb-8">
          <p className="text-sm font-medium text-slate-500 mb-2">BILL TO</p>
          <p className="font-semibold text-lg">{client.company_name || client.name}</p>
          {client.name && client.company_name && (
            <p className="text-slate-600">{client.name}</p>
          )}
          {client.address_line1 && <p className="text-slate-600">{client.address_line1}</p>}
          {client.city && (
            <p className="text-slate-600">
              {[client.city, client.state, client.postal_code].filter(Boolean).join(', ')}
            </p>
          )}
          {client.email && <p className="text-slate-600">{client.email}</p>}
        </div>

        {/* Line Items */}
        <div className="border rounded-lg overflow-hidden mb-8">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-50 border-b">
                <th className="text-left px-4 py-3 text-sm font-semibold text-slate-600">Description</th>
                <th className="text-right px-4 py-3 text-sm font-semibold text-slate-600 w-20">Qty</th>
                <th className="text-right px-4 py-3 text-sm font-semibold text-slate-600 w-28">Price</th>
                <th className="text-right px-4 py-3 text-sm font-semibold text-slate-600 w-20">Tax</th>
                <th className="text-right px-4 py-3 text-sm font-semibold text-slate-600 w-28">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {invoice.items?.map((item, index) => (
                <tr key={index}>
                  <td className="px-4 py-3">{item.description}</td>
                  <td className="px-4 py-3 text-right">{item.quantity}</td>
                  <td className="px-4 py-3 text-right">
                    {formatCurrency(item.unit_price, invoice.currency)}
                  </td>
                  <td className="px-4 py-3 text-right">{item.tax_rate}%</td>
                  <td className="px-4 py-3 text-right font-medium">
                    {formatCurrency(item.total, invoice.currency)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Totals */}
        <div className="flex justify-end">
          <div className="w-64 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Subtotal</span>
              <span>{formatCurrency(invoice.subtotal, invoice.currency)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Tax</span>
              <span>{formatCurrency(invoice.tax_total, invoice.currency)}</span>
            </div>
            <div className="border-t pt-2 flex justify-between">
              <span className="font-semibold">Total</span>
              <span className="text-xl font-bold text-primary-600">
                {formatCurrency(invoice.total, invoice.currency)}
              </span>
            </div>
            {invoice.amount_paid > 0 && (
              <>
                <div className="flex justify-between text-sm text-success-600">
                  <span>Paid</span>
                  <span>-{formatCurrency(invoice.amount_paid, invoice.currency)}</span>
                </div>
                <div className="flex justify-between font-semibold">
                  <span>Balance Due</span>
                  <span>{formatCurrency(invoice.balance_due, invoice.currency)}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Notes */}
        {invoice.notes && (
          <div className="mt-8 pt-6 border-t">
            <p className="text-sm font-medium text-slate-500 mb-2">Notes</p>
            <p className="text-slate-600 whitespace-pre-wrap">{invoice.notes}</p>
          </div>
        )}

        {invoice.terms && (
          <div className="mt-4">
            <p className="text-sm font-medium text-slate-500 mb-2">Terms & Conditions</p>
            <p className="text-slate-600 whitespace-pre-wrap text-sm">{invoice.terms}</p>
          </div>
        )}
      </div>

      {/* Send Modal */}
      {showSendModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md m-4">
            <h3 className="text-lg font-semibold mb-4">Send Invoice</h3>
            <p className="text-slate-600 mb-4">
              This will send the invoice to <strong>{client.email}</strong>
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowSendModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSend}
                disabled={isSending}
                className="btn-primary"
              >
                {isSending ? 'Sending...' : 'Send Invoice'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Mark Paid Modal */}
      {showPayModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md m-4">
            <h3 className="text-lg font-semibold mb-4">Mark as Paid</h3>
            <p className="text-slate-600 mb-4">
              Mark this invoice as fully paid?
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowPayModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleMarkPaid}
                disabled={isMarking}
                className="btn-success"
              >
                {isMarking ? 'Processing...' : 'Mark as Paid'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

