import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { dashboardAPI } from '../lib/api'
import { useAuthStore } from '../stores/authStore'
import {
  DocumentTextIcon,
  CurrencyDollarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  PlusIcon,
} from '@heroicons/react/24/outline'

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

function StatCard({ title, value, icon: Icon, iconBg, trend }) {
  return (
    <div className="stat-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 flex items-center gap-1 ${trend > 0 ? 'text-success-600' : 'text-danger-600'}`}>
              <ArrowTrendingUpIcon className={`w-4 h-4 ${trend < 0 ? 'rotate-180' : ''}`} />
              {Math.abs(trend)}% from last month
            </p>
          )}
        </div>
        <div className={`w-12 h-12 ${iconBg} rounded-xl flex items-center justify-center`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

function ActivityItem({ activity }) {
  const typeStyles = {
    invoice_created: 'bg-primary-100 text-primary-600',
    invoice_sent: 'bg-success-100 text-success-600',
    invoice_paid: 'bg-success-100 text-success-600',
    client_added: 'bg-slate-100 text-slate-600',
  }

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${typeStyles[activity.type] || 'bg-slate-100'}`}>
        <DocumentTextIcon className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-700">{activity.description}</p>
        <p className="text-xs text-slate-400 mt-0.5">
          {new Date(activity.timestamp).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  )
}

function OverdueInvoice({ invoice }) {
  const daysOverdue = Math.ceil(
    (new Date() - new Date(invoice.due_date)) / (1000 * 60 * 60 * 24)
  )

  return (
    <Link
      to={`/invoices/${invoice.id}`}
      className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors group"
    >
      <div>
        <p className="text-sm font-medium text-slate-700 group-hover:text-primary-600">
          {invoice.invoice_number}
        </p>
        <p className="text-xs text-slate-400">
          {invoice.clients?.name || 'Unknown Client'}
        </p>
      </div>
      <div className="text-right">
        <p className="text-sm font-semibold text-slate-900">
          {formatCurrency(invoice.total - invoice.amount_paid, invoice.currency)}
        </p>
        <p className="text-xs text-danger-600">
          {daysOverdue} days overdue
        </p>
      </div>
    </Link>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [activity, setActivity] = useState([])
  const [overdue, setOverdue] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const { organization } = useAuthStore()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsRes, activityRes, overdueRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getActivity(),
        dashboardAPI.getOverdue(),
      ])

      setStats(statsRes.data.data)
      setActivity(activityRes.data.data)
      setOverdue(overdueRes.data.data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-slate-200 rounded w-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-200 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  const currency = stats?.currency || organization?.currency || 'USD'

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-slate-900">
            Dashboard
          </h1>
          <p className="text-slate-500 mt-1">
            Welcome back! Here's your business overview.
          </p>
        </div>
        <Link to="/invoices/new" className="btn-primary">
          <PlusIcon className="w-5 h-5 mr-2" />
          New Invoice
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Invoices"
          value={stats?.total_invoices || 0}
          icon={DocumentTextIcon}
          iconBg="bg-primary-100 text-primary-600"
        />
        <StatCard
          title="Revenue"
          value={formatCurrency(stats?.total_revenue || 0, currency)}
          icon={CurrencyDollarIcon}
          iconBg="bg-success-100 text-success-600"
        />
        <StatCard
          title="Outstanding"
          value={formatCurrency(stats?.outstanding_amount || 0, currency)}
          icon={ClockIcon}
          iconBg="bg-warning-100 text-warning-600"
        />
        <StatCard
          title="Overdue"
          value={formatCurrency(stats?.overdue_amount || 0, currency)}
          icon={ExclamationTriangleIcon}
          iconBg="bg-danger-100 text-danger-600"
        />
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <p className="text-3xl font-bold text-slate-900">{stats?.draft_count || 0}</p>
          <p className="text-sm text-slate-500">Draft</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-3xl font-bold text-primary-600">{stats?.sent_count || 0}</p>
          <p className="text-sm text-slate-500">Sent</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-3xl font-bold text-success-600">{stats?.paid_count || 0}</p>
          <p className="text-sm text-slate-500">Paid</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-3xl font-bold text-danger-600">{stats?.overdue_count || 0}</p>
          <p className="text-sm text-slate-500">Overdue</p>
        </div>
      </div>

      {/* Activity & Overdue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="card">
          <div className="p-4 border-b border-slate-100">
            <h2 className="font-semibold text-slate-900">Recent Activity</h2>
          </div>
          <div className="p-2">
            {activity.length > 0 ? (
              activity.map((item) => (
                <ActivityItem key={item.id} activity={item} />
              ))
            ) : (
              <div className="p-6 text-center text-slate-500">
                No recent activity
              </div>
            )}
          </div>
        </div>

        {/* Overdue Invoices */}
        <div className="card">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="font-semibold text-slate-900">Overdue Invoices</h2>
            {overdue.length > 0 && (
              <span className="badge-overdue">{overdue.length}</span>
            )}
          </div>
          <div className="p-2">
            {overdue.length > 0 ? (
              overdue.slice(0, 5).map((invoice) => (
                <OverdueInvoice key={invoice.id} invoice={invoice} />
              ))
            ) : (
              <div className="p-6 text-center text-slate-500">
                <ExclamationTriangleIcon className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                No overdue invoices
              </div>
            )}
          </div>
          {overdue.length > 5 && (
            <div className="p-3 border-t border-slate-100">
              <Link
                to="/invoices?status=overdue"
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                View all {overdue.length} overdue invoices →
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

