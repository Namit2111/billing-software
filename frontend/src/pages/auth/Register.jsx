import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useAuthStore } from '../../stores/authStore'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'

export default function Register() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { register: registerUser } = useAuthStore()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        full_name: data.fullName,
        company_name: data.companyName,
      })
      toast.success('Account created successfully!')
      navigate('/dashboard')
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Registration failed'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="animate-fadeIn">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-display font-bold text-white mb-2">
          Create your account
        </h1>
        <p className="text-slate-400">
          Start managing your invoices in minutes
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="card p-8 space-y-5">
        {/* Full Name */}
        <div>
          <label htmlFor="fullName" className="label">Full name</label>
          <input
            type="text"
            id="fullName"
            autoComplete="name"
            className={`input ${errors.fullName ? 'input-error' : ''}`}
            placeholder="John Doe"
            {...register('fullName', {
              required: 'Full name is required',
              minLength: {
                value: 2,
                message: 'Name must be at least 2 characters',
              },
            })}
          />
          {errors.fullName && (
            <p className="mt-1 text-sm text-danger-500">{errors.fullName.message}</p>
          )}
        </div>

        {/* Company Name */}
        <div>
          <label htmlFor="companyName" className="label">
            Company name
          </label>
          <input
            type="text"
            id="companyName"
            autoComplete="organization"
            className={`input ${errors.companyName ? 'input-error' : ''}`}
            placeholder="Acme Inc."
            {...register('companyName', {
              required: 'Company name is required',
              minLength: {
                value: 2,
                message: 'Company name must be at least 2 characters',
              },
            })}
          />
          {errors.companyName && (
            <p className="mt-1 text-sm text-danger-500">{errors.companyName.message}</p>
          )}
        </div>

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

        {/* Password */}
        <div>
          <label htmlFor="password" className="label">Password</label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="new-password"
              className={`input pr-10 ${errors.password ? 'input-error' : ''}`}
              placeholder="••••••••"
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters',
                },
              })}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              {showPassword ? (
                <EyeSlashIcon className="w-5 h-5" />
              ) : (
                <EyeIcon className="w-5 h-5" />
              )}
            </button>
          </div>
          {errors.password && (
            <p className="mt-1 text-sm text-danger-500">{errors.password.message}</p>
          )}
          <p className="mt-1 text-xs text-slate-500">
            Must be at least 8 characters
          </p>
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
              Creating account...
            </span>
          ) : (
            'Create account'
          )}
        </button>

        {/* Terms */}
        <p className="text-xs text-slate-500 text-center">
          By creating an account, you agree to our{' '}
          <a href="#" className="text-primary-600 hover:underline">Terms of Service</a>
          {' '}and{' '}
          <a href="#" className="text-primary-600 hover:underline">Privacy Policy</a>
        </p>
      </form>

      {/* Sign in link */}
      <p className="mt-6 text-center text-slate-400">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
          Sign in
        </Link>
      </p>
    </div>
  )
}

