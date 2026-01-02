import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { authAPI } from '../../lib/api'
import { ArrowLeftIcon, EnvelopeIcon } from '@heroicons/react/24/outline'

export default function ForgotPassword() {
  const [isLoading, setIsLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm()

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      await authAPI.requestPasswordReset(data.email)
      setEmailSent(true)
      toast.success('Reset link sent!')
    } catch (error) {
      // Don't reveal if email exists or not
      setEmailSent(true)
    } finally {
      setIsLoading(false)
    }
  }

  if (emailSent) {
    return (
      <div className="animate-fadeIn">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <EnvelopeIcon className="w-8 h-8 text-success-600" />
          </div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Check your email
          </h1>
          <p className="text-slate-400">
            We sent a password reset link to<br />
            <span className="text-white font-medium">{getValues('email')}</span>
          </p>
        </div>

        <div className="card p-8 text-center">
          <p className="text-slate-600 mb-6">
            Click the link in the email to reset your password.
            If you don't see it, check your spam folder.
          </p>
          <Link to="/login" className="btn-primary w-full py-3">
            Back to login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fadeIn">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-display font-bold text-white mb-2">
          Forgot password?
        </h1>
        <p className="text-slate-400">
          No worries, we'll send you reset instructions.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="card p-8 space-y-5">
        {/* Email */}
        <div>
          <label htmlFor="email" className="label">Email address</label>
          <input
            type="email"
            id="email"
            autoComplete="email"
            className={`input ${errors.email ? 'input-error' : ''}`}
            placeholder="you@company.com"
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address',
              },
            })}
          />
          {errors.email && (
            <p className="mt-1 text-sm text-danger-500">{errors.email.message}</p>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full py-3"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Sending...
            </span>
          ) : (
            'Send reset link'
          )}
        </button>
      </form>

      {/* Back to login */}
      <Link
        to="/login"
        className="mt-6 flex items-center justify-center gap-2 text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeftIcon className="w-4 h-4" />
        Back to login
      </Link>
    </div>
  )
}

