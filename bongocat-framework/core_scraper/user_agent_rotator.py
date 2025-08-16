"""
User Agent Rotator - Manages user agent rotation to avoid detection
"""

import random
from typing import List, Dict


class UserAgentRotator:
    """Rotates user agents to avoid detection"""
    
    def __init__(self, custom_agents: List[str] = None):
        """Initialize with default and custom user agents"""
        self.default_agents = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Chrome on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            
            # Firefox on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            
            # Safari on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            
            # Chrome on Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Mobile Chrome
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        ]
        
        self.custom_agents = custom_agents or []
        self.all_agents = self.default_agents + self.custom_agents
        self.usage_stats = {}
        
        # Initialize usage stats
        for agent in self.all_agents:
            self.usage_stats[agent] = 0
    
    def get_random_agent(self) -> str:
        """Get random user agent"""
        agent = random.choice(self.all_agents)
        self.usage_stats[agent] += 1
        return agent
    
    def get_chrome_agent(self) -> str:
        """Get random Chrome user agent"""
        chrome_agents = [agent for agent in self.all_agents if 'Chrome' in agent and 'Edg' not in agent]
        if chrome_agents:
            agent = random.choice(chrome_agents)
            self.usage_stats[agent] += 1
            return agent
        return self.get_random_agent()
    
    def get_firefox_agent(self) -> str:
        """Get random Firefox user agent"""
        firefox_agents = [agent for agent in self.all_agents if 'Firefox' in agent]
        if firefox_agents:
            agent = random.choice(firefox_agents)
            self.usage_stats[agent] += 1
            return agent
        return self.get_random_agent()
    
    def get_safari_agent(self) -> str:
        """Get random Safari user agent"""
        safari_agents = [agent for agent in self.all_agents if 'Safari' in agent and 'Chrome' not in agent]
        if safari_agents:
            agent = random.choice(safari_agents)
            self.usage_stats[agent] += 1
            return agent
        return self.get_random_agent()
    
    def get_mobile_agent(self) -> str:
        """Get random mobile user agent"""
        mobile_agents = [agent for agent in self.all_agents if 'Mobile' in agent or 'Android' in agent or 'iPhone' in agent]
        if mobile_agents:
            agent = random.choice(mobile_agents)
            self.usage_stats[agent] += 1
            return agent
        return self.get_random_agent()
    
    def add_custom_agent(self, user_agent: str):
        """Add custom user agent"""
        if user_agent not in self.all_agents:
            self.custom_agents.append(user_agent)
            self.all_agents.append(user_agent)
            self.usage_stats[user_agent] = 0
    
    def remove_agent(self, user_agent: str):
        """Remove user agent from rotation"""
        if user_agent in self.custom_agents:
            self.custom_agents.remove(user_agent)
        if user_agent in self.all_agents:
            self.all_agents.remove(user_agent)
        if user_agent in self.usage_stats:
            del self.usage_stats[user_agent]
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            'total_agents': len(self.all_agents),
            'default_agents': len(self.default_agents),
            'custom_agents': len(self.custom_agents),
            'usage_stats': self.usage_stats,
            'most_used': max(self.usage_stats.items(), key=lambda x: x[1]) if self.usage_stats else None,
            'least_used': min(self.usage_stats.items(), key=lambda x: x[1]) if self.usage_stats else None
        }
    
    def reset_stats(self):
        """Reset usage statistics"""
        for agent in self.all_agents:
            self.usage_stats[agent] = 0