import pandas as pd
from textblob import TextBlob
import numpy as np
from datetime import datetime

class InterviewAnalytics:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'answer_lengths': [],
            'sentiment_scores': [],
            'keyword_matches': [],
            'technical_accuracy': []
        }
        
    def analyze_response(self, response, question, response_time):
        """Analyze a single response from the candidate"""
        # Response time analysis
        self.metrics['response_times'].append(response_time)
        
        # Answer length analysis
        self.metrics['answer_lengths'].append(len(response.split()))
        
        # Sentiment analysis
        blob = TextBlob(response)
        self.metrics['sentiment_scores'].append(blob.sentiment.polarity)
        
        # Keyword matching (based on question context)
        keywords = self._extract_keywords(question)
        matches = sum(1 for keyword in keywords if keyword.lower() in response.lower())
        self.metrics['keyword_matches'].append(matches / len(keywords) if keywords else 0)
        
        # Technical accuracy score (placeholder - can be enhanced with domain-specific logic)
        self.metrics['technical_accuracy'].append(self._assess_technical_accuracy(response, question))
    
    def _extract_keywords(self, question):
        """Extract important keywords from the question"""
        # This is a simple implementation - could be enhanced with NLP
        stop_words = set(['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        return [word for word in question.lower().split() if word not in stop_words]
    
    def _assess_technical_accuracy(self, response, question):
        """Assess technical accuracy of response"""
        # This is a placeholder implementation
        # Could be enhanced with domain-specific rules or ML models
        technical_keywords = {
            'programming': ['code', 'algorithm', 'function', 'class', 'method'],
            'database': ['sql', 'query', 'database', 'schema', 'table'],
            'web': ['html', 'css', 'javascript', 'api', 'http']
        }
        
        score = 0
        for category, keywords in technical_keywords.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in response.lower())
            score += matches
        
        return min(score / 5, 1.0)  # Normalize to 0-1
    
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        avg_metrics = {
            'average_response_time': np.mean(self.metrics['response_times']),
            'average_answer_length': np.mean(self.metrics['answer_lengths']),
            'average_sentiment': np.mean(self.metrics['sentiment_scores']),
            'keyword_match_rate': np.mean(self.metrics['keyword_matches']),
            'technical_accuracy': np.mean(self.metrics['technical_accuracy'])
        }
        
        report = {
            'summary': avg_metrics,
            'detailed_metrics': self.metrics,
            'recommendations': self._generate_recommendations(avg_metrics),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report
    
    def _generate_recommendations(self, metrics):
        """Generate personalized recommendations based on metrics"""
        recommendations = []
        
        if metrics['average_response_time'] > 30:  # If average response time > 30 seconds
            recommendations.append("Work on improving response time - try to answer more concisely")
            
        if metrics['average_sentiment'] < 0:
            recommendations.append("Try to maintain a more positive tone in responses")
            
        if metrics['keyword_match_rate'] < 0.5:
            recommendations.append("Focus on addressing key points in the questions more directly")
            
        if metrics['technical_accuracy'] < 0.7:
            recommendations.append("Review technical concepts - responses could be more detailed")
            
        return recommendations