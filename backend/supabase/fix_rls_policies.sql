-- Fix RLS Policies for BillFlow
-- Run this in Supabase SQL Editor to fix the infinite recursion issue

-- ============================================
-- DISABLE RLS (Recommended for Development)
-- Using IF EXISTS to avoid errors on missing tables
-- ============================================

-- Disable RLS on all tables that exist
DO $$ 
BEGIN
    -- Disable RLS on each table if it exists
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'organizations') THEN
        ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'users') THEN
        ALTER TABLE users DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'clients') THEN
        ALTER TABLE clients DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'products') THEN
        ALTER TABLE products DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'invoices') THEN
        ALTER TABLE invoices DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'invoice_items') THEN
        ALTER TABLE invoice_items DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'taxes') THEN
        ALTER TABLE taxes DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'email_logs') THEN
        ALTER TABLE email_logs DISABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'audit_logs') THEN
        ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- Drop all existing problematic policies
DROP POLICY IF EXISTS "Users can view members in their organization" ON users;
DROP POLICY IF EXISTS "Allow user creation during registration" ON users;
DROP POLICY IF EXISTS "Users can view their own organization" ON organizations;
DROP POLICY IF EXISTS "Allow organization creation during registration" ON organizations;
DROP POLICY IF EXISTS "Owners can update their organization" ON organizations;
DROP POLICY IF EXISTS "Owners can delete their organization" ON organizations;

-- Success message
SELECT 'RLS policies have been disabled successfully!' as status;
