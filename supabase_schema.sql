-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable Row Level Security
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

-- OD Requests table
CREATE TABLE IF NOT EXISTS od_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES auth.users(id),
    student_name TEXT NOT NULL,
    student_email TEXT NOT NULL,
    event_name TEXT NOT NULL,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    document_url TEXT,
    status TEXT DEFAULT 'pending',
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    od_request_id UUID NOT NULL REFERENCES od_requests(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name TEXT NOT NULL,
    user_role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Teacher notifications table
CREATE TABLE IF NOT EXISTS teacher_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Row Level Security Policies

-- OD Requests Policies
ALTER TABLE od_requests ENABLE ROW LEVEL SECURITY;

-- Everyone can read OD requests they have access to
CREATE POLICY "Students can view their own OD requests" 
    ON od_requests FOR SELECT 
    USING ((auth.uid() = student_id) OR 
           (auth.jwt() ->> 'user_metadata')::jsonb ->> 'role' = 'teacher');

-- Students can insert their own OD requests
CREATE POLICY "Students can insert their own OD requests" 
    ON od_requests FOR INSERT 
    WITH CHECK (auth.uid() = student_id);

-- Only teachers can update OD requests
CREATE POLICY "Teachers can update OD requests" 
    ON od_requests FOR UPDATE 
    USING ((auth.jwt() ->> 'user_metadata')::jsonb ->> 'role' = 'teacher');

-- Comments Policies
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- Everyone can read comments for OD requests they have access to
CREATE POLICY "Users can view comments for their OD requests" 
    ON comments FOR SELECT 
    USING (
        EXISTS (
            SELECT 1 FROM od_requests
            WHERE od_requests.id = comments.od_request_id
            AND ((od_requests.student_id = auth.uid()) OR 
                (auth.jwt() ->> 'user_metadata')::jsonb ->> 'role' = 'teacher')
        )
    );

-- Users can insert their own comments
CREATE POLICY "Users can insert their own comments" 
    ON comments FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Only the author can update their comments
CREATE POLICY "Users can update their own comments" 
    ON comments FOR UPDATE 
    USING (auth.uid() = user_id);

-- Teacher notifications Policies
ALTER TABLE teacher_notifications ENABLE ROW LEVEL SECURITY;

-- Only teachers can read notification settings
CREATE POLICY "Only teachers can read notification settings" 
    ON teacher_notifications FOR SELECT 
    USING ((auth.jwt() ->> 'user_metadata')::jsonb ->> 'role' = 'teacher');

-- Only teachers can modify notification settings
CREATE POLICY "Only teachers can modify notification settings" 
    ON teacher_notifications FOR INSERT 
    WITH CHECK ((auth.jwt() ->> 'user_metadata')::jsonb ->> 'role' = 'teacher');

-- Function to handle user profile creation after signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- If the new user is a teacher, add them to teacher_notifications
    IF (NEW.raw_user_meta_data->>'role' = 'teacher') THEN
        INSERT INTO public.teacher_notifications (email)
        VALUES (NEW.email);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call the function after a new user is created
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
