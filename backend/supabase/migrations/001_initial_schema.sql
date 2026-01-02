-- BillFlow Database Schema
-- Initial migration for V1

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    logo_url TEXT,
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'US',
    currency VARCHAR(3) DEFAULT 'USD',
    invoice_prefix VARCHAR(10) DEFAULT 'INV',
    invoice_next_number INTEGER DEFAULT 1,
    default_tax_rate DECIMAL(5,2) DEFAULT 0.00,
    default_payment_terms INTEGER DEFAULT 30,
    email VARCHAR(255),
    phone VARCHAR(30),
    website VARCHAR(255),
    tax_id VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users table (synced with Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('owner', 'member')),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Clients table
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(30),
    company_name VARCHAR(200),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'US',
    tax_id VARCHAR(50),
    currency VARCHAR(3) DEFAULT 'USD',
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    unit_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    unit VARCHAR(50) DEFAULT 'unit',
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    sku VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Invoices table
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    invoice_number VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')),
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    subtotal DECIMAL(12,2) DEFAULT 0.00,
    tax_total DECIMAL(12,2) DEFAULT 0.00,
    discount_total DECIMAL(12,2) DEFAULT 0.00,
    total DECIMAL(12,2) DEFAULT 0.00,
    amount_paid DECIMAL(12,2) DEFAULT 0.00,
    notes TEXT,
    terms TEXT,
    footer TEXT,
    pdf_url TEXT,
    sent_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    UNIQUE(organization_id, invoice_number)
);

-- Invoice items table
CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    description VARCHAR(500) NOT NULL,
    quantity DECIMAL(10,2) DEFAULT 1.00,
    unit_price DECIMAL(12,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Taxes table
CREATE TABLE taxes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    rate DECIMAL(5,2) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Email logs table
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')),
    provider_id VARCHAR(100),
    error_message TEXT,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX idx_clients_organization ON clients(organization_id);
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_products_organization ON products(organization_id);
CREATE INDEX idx_invoices_organization ON invoices(organization_id);
CREATE INDEX idx_invoices_client ON invoices(client_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_taxes_organization ON taxes(organization_id);
CREATE INDEX idx_email_logs_invoice ON email_logs(invoice_id);
CREATE INDEX idx_users_organization ON users(organization_id);

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE taxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;

-- Organizations policies
CREATE POLICY "Users can view their own organization"
    ON organizations FOR SELECT
    USING (id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Allow organization creation during registration"
    ON organizations FOR INSERT
    WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Owners can update their organization"
    ON organizations FOR UPDATE
    USING (id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role = 'owner'));

-- Users policies
CREATE POLICY "Users can view members in their organization"
    ON users FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id FROM users
            WHERE id = auth.uid() AND organization_id IS NOT NULL
        )
        OR id = auth.uid()
    );

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (id = auth.uid());

CREATE POLICY "Allow user creation during registration"
    ON users FOR INSERT
    WITH CHECK (id = auth.uid() OR auth.role() = 'service_role');

-- Clients policies
CREATE POLICY "Users can view clients in their organization"
    ON clients FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can create clients in their organization"
    ON clients FOR INSERT
    WITH CHECK (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can update clients in their organization"
    ON clients FOR UPDATE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can delete clients in their organization"
    ON clients FOR DELETE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

-- Products policies
CREATE POLICY "Users can view products in their organization"
    ON products FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can create products in their organization"
    ON products FOR INSERT
    WITH CHECK (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can update products in their organization"
    ON products FOR UPDATE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can delete products in their organization"
    ON products FOR DELETE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

-- Invoices policies
CREATE POLICY "Users can view invoices in their organization"
    ON invoices FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can create invoices in their organization"
    ON invoices FOR INSERT
    WITH CHECK (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can update invoices in their organization"
    ON invoices FOR UPDATE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can delete invoices in their organization"
    ON invoices FOR DELETE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

-- Invoice items policies
CREATE POLICY "Users can view invoice items for their invoices"
    ON invoice_items FOR SELECT
    USING (invoice_id IN (
        SELECT id FROM invoices WHERE organization_id IN (
            SELECT organization_id FROM users WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can create invoice items for their invoices"
    ON invoice_items FOR INSERT
    WITH CHECK (invoice_id IN (
        SELECT id FROM invoices WHERE organization_id IN (
            SELECT organization_id FROM users WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can update invoice items for their invoices"
    ON invoice_items FOR UPDATE
    USING (invoice_id IN (
        SELECT id FROM invoices WHERE organization_id IN (
            SELECT organization_id FROM users WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can delete invoice items for their invoices"
    ON invoice_items FOR DELETE
    USING (invoice_id IN (
        SELECT id FROM invoices WHERE organization_id IN (
            SELECT organization_id FROM users WHERE id = auth.uid()
        )
    ));

-- Taxes policies
CREATE POLICY "Users can view taxes in their organization"
    ON taxes FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Owners can manage taxes"
    ON taxes FOR ALL
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role = 'owner'));

-- Email logs policies
CREATE POLICY "Users can view email logs in their organization"
    ON email_logs FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can create email logs in their organization"
    ON email_logs FOR INSERT
    WITH CHECK (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

-- Functions and Triggers

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoice_items_updated_at
    BEFORE UPDATE ON invoice_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_taxes_updated_at
    BEFORE UPDATE ON taxes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_email_logs_updated_at
    BEFORE UPDATE ON email_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users to create public.users record
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Storage bucket for invoices
INSERT INTO storage.buckets (id, name, public)
VALUES ('invoices', 'invoices', true)
ON CONFLICT DO NOTHING;

-- Storage bucket for assets (logos)
INSERT INTO storage.buckets (id, name, public)
VALUES ('assets', 'assets', true)
ON CONFLICT DO NOTHING;

-- Storage policies
CREATE POLICY "Authenticated users can upload invoices"
    ON storage.objects FOR INSERT
    WITH CHECK (bucket_id = 'invoices' AND auth.role() = 'authenticated');

CREATE POLICY "Anyone can view invoice PDFs"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'invoices');

CREATE POLICY "Authenticated users can upload assets"
    ON storage.objects FOR INSERT
    WITH CHECK (bucket_id = 'assets' AND auth.role() = 'authenticated');

CREATE POLICY "Anyone can view assets"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'assets');

