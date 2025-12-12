import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://cqrpbiepyeypbkizwacu.supabase.co";
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxcnBiaWVweWV5cGJraXp3YWN1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3MDA0MTksImV4cCI6MjA3MTI3NjQxOX0.Iyy2W5tw0-40sQdRfFJTfwYij4iUl8-KoUlg39u7kOE";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
