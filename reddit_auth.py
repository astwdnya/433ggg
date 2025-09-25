import asyncio
import aiohttp
from aiohttp import web
import json
import os
import secrets
import urllib.parse
from datetime import datetime, timedelta

class RedditAuthManager:
    def __init__(self):
        # Reddit OAuth credentials - باید در .env تنظیم شوند
        from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
        self.client_id = REDDIT_CLIENT_ID or ''
        self.client_secret = REDDIT_CLIENT_SECRET or ''
        self.redirect_uri = 'http://localhost:8080/reddit/callback'
        self.user_sessions = {}  # {user_id: {token, refresh_token, expires_at}}
        self.pending_auth = {}   # {state: user_id}
        
    def generate_auth_url(self, user_id: int) -> str:
        """Generate Reddit OAuth URL for user authentication"""
        state = secrets.token_urlsafe(32)
        self.pending_auth[state] = user_id
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'state': state,
            'redirect_uri': self.redirect_uri,
            'duration': 'permanent',
            'scope': 'read'
        }
        
        auth_url = f"https://www.reddit.com/api/v1/authorize?{urllib.parse.urlencode(params)}"
        return auth_url
    
    async def handle_callback(self, request):
        """Handle Reddit OAuth callback"""
        try:
            code = request.query.get('code')
            state = request.query.get('state')
            error = request.query.get('error')
            
            if error:
                return web.Response(text=f"خطا در احراز هویت: {error}", status=400)
            
            if not code or not state:
                return web.Response(text="پارامترهای احراز هویت ناقص", status=400)
            
            if state not in self.pending_auth:
                return web.Response(text="درخواست احراز هویت نامعتبر", status=400)
            
            user_id = self.pending_auth.pop(state)
            
            # Exchange code for access token
            token_data = await self.exchange_code_for_token(code)
            if token_data:
                # Store user session
                expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                self.user_sessions[user_id] = {
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_at': expires_at,
                    'token_type': token_data.get('token_type', 'bearer')
                }
                
                return web.Response(text="""
                <!DOCTYPE html>
                <html dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <title>احراز هویت موفق</title>
                    <style>
                        body { font-family: Tahoma, Arial; text-align: center; padding: 50px; background: #f0f2f5; }
                        .success { background: #d4edda; color: #155724; padding: 20px; border-radius: 10px; max-width: 400px; margin: 0 auto; }
                        .icon { font-size: 48px; margin-bottom: 20px; }
                    </style>
                </head>
                <body>
                    <div class="success">
                        <div class="icon">✅</div>
                        <h2>احراز هویت موفق!</h2>
                        <p>حساب Reddit شما با موفقیت متصل شد.</p>
                        <p>حالا می‌توانید این صفحه را ببندید و به ربات برگردید.</p>
                    </div>
                    <script>
                        setTimeout(() => window.close(), 3000);
                    </script>
                </body>
                </html>
                """, content_type='text/html')
            else:
                return web.Response(text="خطا در دریافت توکن دسترسی", status=400)
                
        except Exception as e:
            print(f"❌ Error in Reddit callback: {e}")
            return web.Response(text=f"خطا در پردازش: {str(e)}", status=500)
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        try:
            token_url = 'https://www.reddit.com/api/v1/access_token'
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            headers = {'User-Agent': 'TelegramDownloadBot/1.0'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=data, auth=auth, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"❌ Token exchange failed: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error exchanging code for token: {e}")
            return None
    
    def is_user_authenticated(self, user_id: int) -> bool:
        """Check if user has valid Reddit authentication"""
        if user_id not in self.user_sessions:
            return False
        
        session = self.user_sessions[user_id]
        if datetime.now() >= session['expires_at']:
            # Token expired, try to refresh
            return False  # For now, require re-auth
        
        return True
    
    def get_user_token(self, user_id: int) -> str:
        """Get user's Reddit access token"""
        if not self.is_user_authenticated(user_id):
            return None
        
        return self.user_sessions[user_id]['access_token']
    
    async def make_authenticated_request(self, user_id: int, url: str, method='GET', **kwargs):
        """Make authenticated request to Reddit API"""
        token = self.get_user_token(user_id)
        if not token:
            return None
        
        headers = kwargs.get('headers', {})
        headers.update({
            'Authorization': f'Bearer {token}',
            'User-Agent': 'TelegramDownloadBot/1.0'
        })
        kwargs['headers'] = headers
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Reddit API request failed: {response.status}")
                    return None

# Global auth manager instance
reddit_auth = RedditAuthManager()

async def start_auth_server():
    """Start the authentication server"""
    app = web.Application()
    app.router.add_get('/reddit/callback', reddit_auth.handle_callback)
    
    # Health check endpoint
    async def health(request):
        return web.Response(text="Reddit Auth Server is running")
    
    app.router.add_get('/health', health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print("🔐 Reddit authentication server started on http://localhost:8080")
    return runner

if __name__ == "__main__":
    async def main():
        runner = await start_auth_server()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await runner.cleanup()
    
    asyncio.run(main())
