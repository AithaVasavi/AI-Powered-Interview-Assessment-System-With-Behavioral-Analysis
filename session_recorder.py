import json
from datetime import datetime
import os

class InterviewRecorder:
    def __init__(self, base_dir="interview_sessions"):
        self.base_dir = base_dir
        self.current_session = None
        self.session_data = None
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Create the base directory if it doesn't exist"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            os.makedirs(os.path.join(self.base_dir, "recordings"))
    
    def start_session(self, username):
        """Start a new interview session"""
        self.current_session = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_data = {
            'username': username,
            'start_time': datetime.now().isoformat(),
            'interactions': [],
            'resume_text': '',
            'model_used': '',
            'end_time': None,
            'analytics': None
        }
    
    def record_interaction(self, role, content, timestamp=None):
        """Record a single interaction in the session"""
        if not self.session_data:
            raise ValueError("No active session")
            
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        interaction = {
            'role': role,
            'content': content,
            'timestamp': timestamp
        }
        
        self.session_data['interactions'].append(interaction)
    
    def set_resume_text(self, resume_text):
        """Store the resume text used in the session"""
        if self.session_data:
            self.session_data['resume_text'] = resume_text
    
    def set_model_used(self, model_name):
        """Store the AI model used in the session"""
        if self.session_data:
            self.session_data['model_used'] = model_name
    
    def add_analytics(self, analytics_data):
        """Add analytics data to the session"""
        if self.session_data:
            self.session_data['analytics'] = analytics_data
    
    def end_session(self):
        """End the current session and save it to disk"""
        if not self.session_data:
            raise ValueError("No active session")
            
        self.session_data['end_time'] = datetime.now().isoformat()
        
        # Save session to file
        filename = os.path.join(self.base_dir, "recordings", f"{self.current_session}.json")
        with open(filename, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        session_id = self.current_session
        self.current_session = None
        self.session_data = None
        
        return session_id
    
    def load_session(self, session_id):
        """Load a previous session"""
        filename = os.path.join(self.base_dir, "recordings", f"{session_id}.json")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Session {session_id} not found")
            
        with open(filename, 'r') as f:
            return json.load(f)
    
    def list_sessions(self, username=None):
        """List all recorded sessions, optionally filtered by username"""
        sessions = []
        recordings_dir = os.path.join(self.base_dir, "recordings")
        
        for filename in os.listdir(recordings_dir):
            if filename.endswith('.json'):
                with open(os.path.join(recordings_dir, filename), 'r') as f:
                    session_data = json.load(f)
                    if username is None or session_data['username'] == username:
                        sessions.append({
                            'session_id': filename[:-5],  # Remove .json
                            'start_time': session_data['start_time'],
                            'end_time': session_data['end_time'],
                            'username': session_data['username'],
                            'model_used': session_data['model_used']
                        })
        
        return sorted(sessions, key=lambda x: x['start_time'], reverse=True)