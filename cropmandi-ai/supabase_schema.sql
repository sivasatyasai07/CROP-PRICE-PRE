-- ============================================================================
-- CROP MANDI AI — SUPABASE DATABASE & STORAGE SCHEMA MIGRATION
-- ============================================================================

-- 1. Enable UUID Extension (standard in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 2. USER PROFILES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    preferred_language TEXT DEFAULT 'en',
    state TEXT,
    district TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.profiles;

-- Profiles RLS Policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Automatic Profile Creation Trigger on auth.users Signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, preferred_language, created_at, updated_at)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'preferred_language', 'en'),
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Automatic updated_at trigger function
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_profiles_updated ON public.profiles;
CREATE TRIGGER on_profiles_updated
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ============================================================================
-- 3. PRICE PREDICTION HISTORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.prediction_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    crop TEXT NOT NULL,
    state TEXT,
    district TEXT,
    market TEXT NOT NULL,
    current_price NUMERIC,
    predicted_price NUMERIC,
    min_price NUMERIC,
    max_price NUMERIC,
    trend TEXT,
    forecast_days INTEGER DEFAULT 7,
    prediction_date DATE DEFAULT CURRENT_DATE,
    model_name TEXT DEFAULT 'CatBoost Regressor',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for speedy retrieval by user and date
CREATE INDEX IF NOT EXISTS idx_prediction_history_user_id_created_at
    ON public.prediction_history (user_id, created_at DESC);

-- Enable RLS on prediction_history
ALTER TABLE public.prediction_history ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view their own predictions" ON public.prediction_history;
DROP POLICY IF EXISTS "Users can insert their own predictions" ON public.prediction_history;
DROP POLICY IF EXISTS "Users can delete their own predictions" ON public.prediction_history;

-- Prediction History RLS Policies
CREATE POLICY "Users can view their own predictions"
    ON public.prediction_history
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own predictions"
    ON public.prediction_history
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own predictions"
    ON public.prediction_history
    FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- 4. CROP DISEASE HISTORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.disease_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    image_url TEXT,
    crop TEXT,
    plant_part TEXT,
    health_status TEXT,
    disease_name TEXT,
    confidence NUMERIC,
    symptoms JSONB DEFAULT '[]'::jsonb,
    possible_causes JSONB DEFAULT '[]'::jsonb,
    management JSONB DEFAULT '[]'::jsonb,
    prevention JSONB DEFAULT '[]'::jsonb,
    risk_level TEXT,
    analysis_status TEXT DEFAULT 'completed',
    language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for speedy retrieval by user and date
CREATE INDEX IF NOT EXISTS idx_disease_history_user_id_created_at
    ON public.disease_history (user_id, created_at DESC);

-- Enable RLS on disease_history
ALTER TABLE public.disease_history ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view their own disease history" ON public.disease_history;
DROP POLICY IF EXISTS "Users can insert their own disease history" ON public.disease_history;
DROP POLICY IF EXISTS "Users can delete their own disease history" ON public.disease_history;

-- Disease History RLS Policies
CREATE POLICY "Users can view their own disease history"
    ON public.disease_history
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own disease history"
    ON public.disease_history
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own disease history"
    ON public.disease_history
    FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- 5. SUPABASE STORAGE BUCKET: disease-images
-- ============================================================================
-- Create bucket if it doesn't already exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'disease-images',
    'disease-images',
    true,
    10485760, -- 10MB limit
    ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Storage RLS Policies for disease-images
DROP POLICY IF EXISTS "Authenticated users can upload disease images to own folder" ON storage.objects;
DROP POLICY IF EXISTS "Anyone can view disease images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own disease images" ON storage.objects;

CREATE POLICY "Authenticated users can upload disease images to own folder"
    ON storage.objects
    FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'disease-images' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "Anyone can view disease images"
    ON storage.objects
    FOR SELECT
    USING (bucket_id = 'disease-images');

CREATE POLICY "Users can delete their own disease images"
    ON storage.objects
    FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'disease-images' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );
