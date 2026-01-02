import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { settingsAPI } from '../lib/api'
import { useAuthStore } from '../stores/authStore'
import {
  BuildingOfficeIcon,
  DocumentTextIcon,
  ReceiptPercentIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'

const tabs = [
  { id: 'company', name: 'Company', icon: BuildingOfficeIcon },
  { id: 'invoice', name: 'Invoice', icon: DocumentTextIcon },
  { id: 'taxes', name: 'Taxes', icon: ReceiptPercentIcon },
  { id: 'team', name: 'Team', icon: UserGroupIcon },
]

export default function Settings() {
  const { refreshUser } = useAuthStore()
  const [activeTab, setActiveTab] = useState('company')
  const [organization, setOrganization] = useState(null)
  const [taxes, setTaxes] = useState([])
  const [members, setMembers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm()

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setIsLoading(true)
    try {
      const [orgRes, taxesRes, membersRes] = await Promise.all([
        settingsAPI.getOrganization(),
        settingsAPI.getTaxes(),
        settingsAPI.getMembers(),
      ])

      setOrganization(orgRes.data.data)
      setTaxes(taxesRes.data.data)
      setMembers(membersRes.data.data)
      reset(orgRes.data.data)
    } catch (error) {
      console.error('Failed to load settings:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const onSubmit = async (data) => {
    setIsSaving(true)
    try {
      await settingsAPI.updateOrganization(data)
      toast.success('Settings saved!')
      refreshUser()
      reset(data)
    } catch (error) {
      toast.error('Failed to save settings')
    } finally {
      setIsSaving(false)
    }
  }

  const handleLogoUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      const response = await settingsAPI.uploadLogo(file)
      setOrganization({ ...organization, logo_url: response.data.data.logo_url })
      toast.success('Logo uploaded!')
    } catch (error) {
      toast.error('Failed to upload logo')
    }
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
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 mt-1">Manage your account and preferences</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-48 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'company' && (
            <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-6">
              <h2 className="font-semibold text-slate-900">Company Information</h2>

              {/* Logo */}
              <div>
                <label className="label">Company Logo</label>
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 bg-slate-100 rounded-xl flex items-center justify-center overflow-hidden">
                    {organization?.logo_url ? (
                      <img
                        src={organization.logo_url}
                        alt="Logo"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <BuildingOfficeIcon className="w-8 h-8 text-slate-400" />
                    )}
                  </div>
                  <div>
                    <label className="btn-secondary cursor-pointer">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleLogoUpload}
                        className="hidden"
                      />
                      Upload Logo
                    </label>
                    <p className="text-xs text-slate-500 mt-1">PNG, JPG up to 2MB</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="label">Company Name *</label>
                  <input
                    {...register('name', { required: true })}
                    className="input"
                  />
                </div>

                <div>
                  <label className="label">Email</label>
                  <input type="email" {...register('email')} className="input" />
                </div>

                <div>
                  <label className="label">Phone</label>
                  <input {...register('phone')} className="input" />
                </div>

                <div>
                  <label className="label">Website</label>
                  <input {...register('website')} className="input" />
                </div>

                <div>
                  <label className="label">Tax ID</label>
                  <input {...register('tax_id')} className="input" />
                </div>

                <div className="md:col-span-2">
                  <label className="label">Address</label>
                  <input {...register('address_line1')} className="input" />
                </div>

                <div>
                  <label className="label">City</label>
                  <input {...register('city')} className="input" />
                </div>

                <div>
                  <label className="label">State/Province</label>
                  <input {...register('state')} className="input" />
                </div>

                <div>
                  <label className="label">Postal Code</label>
                  <input {...register('postal_code')} className="input" />
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

                <div>
                  <label className="label">Currency</label>
                  <select {...register('currency')} className="input">
                    <option value="USD">USD - US Dollar</option>
                    <option value="EUR">EUR - Euro</option>
                    <option value="GBP">GBP - British Pound</option>
                    <option value="CAD">CAD - Canadian Dollar</option>
                    <option value="AUD">AUD - Australian Dollar</option>
                    <option value="INR">INR - Indian Rupee</option>
                  </select>
                </div>
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={isSaving || !isDirty}
                  className="btn-primary"
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'invoice' && (
            <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-6">
              <h2 className="font-semibold text-slate-900">Invoice Settings</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Invoice Number Prefix</label>
                  <input
                    {...register('invoice_prefix')}
                    className="input"
                    placeholder="INV"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Next invoice: {organization?.invoice_prefix || 'INV'}-{String(organization?.invoice_next_number || 1).padStart(4, '0')}
                  </p>
                </div>

                <div>
                  <label className="label">Default Payment Terms (days)</label>
                  <input
                    type="number"
                    {...register('default_payment_terms')}
                    className="input"
                  />
                </div>

                <div>
                  <label className="label">Default Tax Rate (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('default_tax_rate')}
                    className="input"
                  />
                </div>
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={isSaving || !isDirty}
                  className="btn-primary"
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'taxes' && (
            <div className="card p-6">
              <h2 className="font-semibold text-slate-900 mb-4">Tax Rates</h2>
              {taxes.length > 0 ? (
                <div className="space-y-2">
                  {taxes.map((tax) => (
                    <div
                      key={tax.id}
                      className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{tax.name}</p>
                        {tax.description && (
                          <p className="text-sm text-slate-500">{tax.description}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="font-medium">{tax.rate}%</span>
                        {tax.is_default && (
                          <span className="badge bg-primary-100 text-primary-700">Default</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500">No tax rates configured</p>
              )}
            </div>
          )}

          {activeTab === 'team' && (
            <div className="card p-6">
              <h2 className="font-semibold text-slate-900 mb-4">Team Members</h2>
              <div className="space-y-3">
                {members.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-700 font-medium">
                          {member.full_name?.charAt(0) || member.email.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium">{member.full_name || member.email}</p>
                        <p className="text-sm text-slate-500">{member.email}</p>
                      </div>
                    </div>
                    <span className={`badge ${
                      member.role === 'owner' ? 'bg-primary-100 text-primary-700' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {member.role}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

