-- SQL Seed Data for Supabase --

-- Insert initial roles
INSERT INTO roles (name) VALUES ('Viewer'), ('Analyst'), ('Admin');

-- Insert initial users
INSERT INTO users (email, password, role_id) VALUES 
('admin@example.com', 'hashed_password_for_admin', 3),
('analyst@example.com', 'hashed_password_for_analyst', 2),
('viewer@example.com', 'hashed_password_for_viewer', 1);

-- Insert initial alert types
INSERT INTO alert_types (name) VALUES 
('Malware Detection'), 
('Unauthorized Access'), 
('Data Exfiltration');

-- Insert initial settings
INSERT INTO settings (key, value) VALUES 
('alert_threshold', '5'),
('log_retention_days', '14');

-- Insert initial feature set
INSERT INTO features (name, description) VALUES 
('ip.ttl', 'Time to live in IP header'),
('tcp.flags.syn', 'SYN flag in TCP header'),
('payload_len', 'Length of the payload'); 

-- Insert initial flow summaries
INSERT INTO flow_summaries (flow_id, src_ip, dst_ip, src_port, dst_port, protocol, start_time, end_time, bytes, packets, state) VALUES 
('flow1', '192.168.1.1', '192.168.1.2', 12345, 80, 'TCP', 1620000000000, 1620003600000, 1000, 10, 'completed'),
('flow2', '192.168.1.3', '192.168.1.4', 54321, 443, 'TCP', 1620000000000, 1620003600000, 2000, 20, 'completed'); 

-- Note: Replace 'hashed_password_for_*' with actual hashed passwords for security.