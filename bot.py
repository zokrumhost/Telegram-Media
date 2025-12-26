"""
Dharma Darshan Bot - Dharmik Media Group Access
Railway Deployment Version
Referral-based access to spiritual content
Author: Dharmik Team
Version: 2.5 (Railway Edition) - ORIGINAL MESSAGES VERSION
"""

import logging
import json
import os
import time
import shutil
import glob
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, ChatJoinRequestHandler
)
from telegram.error import BadRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================
CONFIG = {
    # 🔑 REQUIRED - Railway Environment Variables
    'BOT_TOKEN': os.environ.get('BOT_TOKEN'),
    'CHANNEL_ID': os.environ.get('CHANNEL_ID', "-1003375954970"),
    'ADMIN_USER_ID': os.environ.get('ADMIN_USER_ID'),
    
    # 🌟 DHARMIK SETTINGS
    'DHARMIK_CHANNEL_LINK': os.environ.get('DHARMIK_CHANNEL_LINK', "https://t.me/+gGCbM0pX7EA4NTg1"),
    'BOT_USERNAME': os.environ.get('BOT_USERNAME', "Interfaith_Gp_bot"),
    'REQUIRED_REFERRALS': int(os.environ.get('REQUIRED_REFERRALS', 3)),
    'REFERRAL_POINTS': int(os.environ.get('REFERRAL_POINTS', 1)),
    
    # ✨ SPIRITUAL EMOJIS
    'EMOJIS': {
        'om': '🕉️',
        'lotus': '🌸',
        'diya': '🪔',
        'temple': '🛕',
        'hands': '🙏',
        'star': '⭐',
        'medal': '🏅',
        'target': '🎯',
        'link': '🔗',
        'users': '👥',
        'celebration': '🎉',
        'bell': '🔔',
        'book': '📖',
        'video': '📹',
        'audio': '🎵',
        'lock': '🔒',
        'unlock': '🔓',
        'check': '✅',
        'warning': '⚠️',
        'admin': '👑',
        'home': '🏠',
        'refresh': '🔄',
        'share': '📱',
        'stats': '📊',
        'help': '❓',
        'channel': '📺',
        'gate': '🚪',
        'flower': '💮',
        'fire': '🔥',
        'heart': '💖',
        'gift': '🎁',
        'clock': '⏰',
        'trophy': '🏆',
        'message': '💬',
        'group': '👥',
        'bot': '🤖',
        'server': '🖥️'
    }
}
# ==================== CONFIG END ====================

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DharmikReferralBot:
    """Dharmik Media Group Access Bot - Secure Railway Version"""
    
    def __init__(self):
        self.config = CONFIG
        self.emoji = CONFIG['EMOJIS']
        
        # Railway-compatible storage paths
        if os.environ.get('RAILWAY_VOLUME_MOUNT_PATH'):
            self.data_dir = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH')
        else:
            self.data_dir = "data"
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.user_data_file = os.path.join(self.data_dir, "dharmik_users.json")
        self.backup_dir = os.path.join(self.data_dir, "backups")
        
        self.validate_config()
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        logger.info(f"{self.emoji['om']} Bot initialized: @{self.config['BOT_USERNAME']}")
        logger.info(f"{self.emoji['bot']} Running on Railway: {os.environ.get('RAILWAY_ENVIRONMENT', 'Local')}")
    
    def validate_config(self):
        """Validate configuration"""
        required = ['BOT_TOKEN', 'ADMIN_USER_ID']
        missing = []
        
        for key in required:
            if not self.config.get(key):
                missing.append(key)
        
        if missing:
            error_msg = f"{self.emoji['warning']} Missing required configuration: {', '.join(missing)}"
            print(f"\n{'='*60}")
            print(error_msg)
            print(f"{'='*60}")
            print(f"{self.emoji['help']} PLEASE SET THESE RAILWAY VARIABLES:")
            print(f"{'='*60}")
            for key in missing:
                print(f"• {key}")
            print(f"{'='*60}\n")
            
            logger.error(error_msg)
            raise ValueError("Missing required environment variables")
    
    def create_backup(self):
        """Create backup of user data"""
        try:
            if os.path.exists(self.user_data_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(self.backup_dir, f"users_{timestamp}.json")
                shutil.copy2(self.user_data_file, backup_path)
                
                backups = sorted(glob.glob(os.path.join(self.backup_dir, "users_*.json")))
                if len(backups) > 5:
                    for old_backup in backups[:-5]:
                        try:
                            os.remove(old_backup)
                        except:
                            pass
                logger.info(f"{self.emoji['check']} Backup created: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Backup error: {e}")
        return False
    
    def load_user_data(self):
        """Load user data from file"""
        if not os.path.exists(self.user_data_file):
            logger.info(f"{self.emoji['book']} Creating new user data file")
            return {}
        
        try:
            with open(self.user_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"{self.emoji['check']} Loaded {len(data)} users")
                return data
        except Exception as e:
            logger.error(f"Load error: {e}")
            return {}
    
    def save_user_data(self, data):
        """Save user data to file"""
        try:
            self.create_backup()
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"{self.emoji['check']} Saved {len(data)} users")
            return True
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False
    
    def get_referral_link(self, user_id):
        """Generate referral link for user"""
        username = self.config['BOT_USERNAME']
        if username and username.startswith('@'):
            username = username[1:]
        return f"https://t.me/{username}?start={user_id}"
    
    def escape_html(self, text):
        """Escape HTML special characters"""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;'))
    
    async def approve_channel_request(self, user_id, context: ContextTypes.DEFAULT_TYPE):
        """Approve user to Dharmik Channel"""
        try:
            await context.bot.approve_chat_join_request(self.config['CHANNEL_ID'], user_id)
            logger.info(f"{self.emoji['check']} Approved {user_id} to Dharmik Channel")
            return True
        except Exception as e:
            logger.error(f"Approve error: {e}")
            return False
    
    async def decline_channel_request(self, user_id, context: ContextTypes.DEFAULT_TYPE):
        """Decline user from channel"""
        try:
            await context.bot.decline_chat_join_request(self.config['CHANNEL_ID'], user_id)
            logger.info(f"{self.emoji['warning']} Declined {user_id}")
            return True
        except Exception as e:
            logger.error(f"Decline error: {e}")
            return False
    
    async def send_completion_message(self, user_id, context: ContextTypes.DEFAULT_TYPE):
        """Send beautiful completion message for Dharmik Channel"""
        try:
            # First message - Achievement (EXACT ORIGINAL MESSAGE)
            achievement_msg = (
                f"{self.emoji['om']} <b>CONGRATULATIONS! MISSION ACCOMPLISHED</b>\n\n"
                f"{self.emoji['celebration']} <b>You've successfully completed {self.config['REQUIRED_REFERRALS']} referrals!</b>\n\n"
                f"{self.emoji['medal']} <b>Your Achievement:</b>\n"
                f"• {self.emoji['users']} Referrals: {self.config['REQUIRED_REFERRALS']}/{self.config['REQUIRED_REFERRALS']}\n"
                f"• {self.emoji['check']} Status: <b>COMPLETED</b>\n"
                f"• {self.emoji['star']} Virtue Points: +{self.config['REFERRAL_POINTS']}\n\n"
                f"{self.emoji['bell']} <b>Dharmik Group Links Channel link is coming in the next message...</b>"
            )
            
            await context.bot.send_message(
                chat_id=int(user_id),
                text=achievement_msg,
                parse_mode='HTML'
            )
            
            # Wait 3 seconds for effect
            await asyncio.sleep(3)
            
            # Channel Access Message (EXACT ORIGINAL MESSAGE)
            channel_access_msg = (
                f"{self.emoji['gate']} <b>DHARMIK CHANNEL ACCESS GRANTED!</b>\n\n"
                f"{self.emoji['lotus']} <b>You now have access to \"Dharma Darshan\" Channel!</b>\n\n"
                f"{self.emoji['book']} <b>Dharmik Group Links Available in Channel:</b>\n"
                f"{self.emoji['unlock']} <b>Channel Link:</b>\n"
                f"{self.config['DHARMIK_CHANNEL_LINK']}\n\n"
                f"{self.emoji['fire']} <b>Instructions:</b>\n"
                f"1. Click the link above\n"
                f"2. Press \"Join\" button\n"
                f"3. You will be approved instantly\n\n"
                f"{self.emoji['heart']} <i>Thank you for Using This Bot</i>"
            )
            
            # Add BUTTON to second message
            keyboard = [
                [InlineKeyboardButton(
                    f"{self.emoji['temple']} Join Dharma Darshan Channel", 
                    url=self.config['DHARMIK_CHANNEL_LINK']
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=int(user_id),
                text=channel_access_msg,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            return True
        except Exception as e:
            logger.error(f"Completion message error: {e}")
            return False
    
    async def send_progress_update(self, user_id, new_count, context: ContextTypes.DEFAULT_TYPE):
        """Send progress update when user gets new referral (EXACT ORIGINAL MESSAGE)"""
        progress_msg = (
            f"{self.emoji['flower']} <b>NEW REFERRAL RECEIVED!</b>\n\n"
            f"{self.emoji['gift']} <b>+1 Virtue Point Earned!</b>\n\n"
            f"{self.emoji['target']} <b>Your Progress:</b>\n"
            f"• {self.emoji['users']} Referrals: {new_count}/{self.config['REQUIRED_REFERRALS']}\n"
            f"• {self.emoji['star']} Virtue Points: +1\n\n"
            f"{self.emoji['bell']} <b>Need {self.config['REQUIRED_REFERRALS'] - new_count} more referrals</b>\n\n"
            f"{self.emoji['heart']} <i>Keep Share And Support Us </i>"
        )
        
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=progress_msg,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Progress update error: {e}")
    
    # ==================== MAIN COMMANDS ====================
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = str(user.id)
        user_data = self.load_user_data()
        
        logger.info(f"{self.emoji['gate']} New user: {user_id} - {user.first_name}")
        
        # ✅ PROCESS REFERRAL
        if context.args and len(context.args) > 0:
            referrer_id = context.args[0]
            
            if (referrer_id.isdigit() and 
                referrer_id != user_id and 
                referrer_id in user_data):
                
                # Check if not already referred
                if 'referrals' not in user_data[referrer_id]:
                    user_data[referrer_id]['referrals'] = []
                
                if user_id not in user_data[referrer_id]['referrals']:
                    # Add referral
                    user_data[referrer_id]['referrals'].append(user_id)
                    
                    # Update points
                    user_data[referrer_id]['points'] = user_data[referrer_id].get('points', 0) + 1
                    
                    # Save data
                    self.save_user_data(user_data)
                    
                    # Get new count
                    new_count = len(user_data[referrer_id]['referrals'])
                    old_count = new_count - 1
                    
                    # Send notification if needed
                    if old_count < self.config['REQUIRED_REFERRALS']:
                        if new_count < self.config['REQUIRED_REFERRALS']:
                            # Progress update (for 1st and 2nd referral)
                            await self.send_progress_update(referrer_id, new_count, context)
                        
                        elif new_count == self.config['REQUIRED_REFERRALS']:
                            # Completion! (for 3rd referral) - TWO MESSAGES WITH BUTTON
                            await self.send_completion_message(referrer_id, context)
        
        # Register/update user
        if user_id not in user_data:
            user_data[user_id] = {
                'points': 0,
                'referrals': [],
                'first_name': user.first_name or "",
                'username': user.username or "",
                'joined_at': datetime.now().strftime("%d-%m-%Y %H:%M"),
                'last_activity': datetime.now().isoformat()
            }
        else:
            # Update last activity
            user_data[user_id]['last_activity'] = datetime.now().isoformat()
        
        self.save_user_data(user_data)
        
        user_info = user_data[user_id]
        referral_link = self.get_referral_link(user_id)
        
        # Welcome Message (EXACT ORIGINAL MESSAGE)
        welcome_text = (
            f"{self.emoji['om']} <b>WELCOME TO DHARMA DARSHAN BOT</b>\n\n"
            f"{self.emoji['hands']} <b>Hello {self.escape_html(user.first_name or 'Seeker')}!</b>\n\n"
            f"{self.emoji['book']} <b>This bot provides access to \"Dharma Darshan\" Channel where you'll find:</b>\n"
            f"• {self.emoji['video']} Daily Spiritual Discourses\n"
            f"• {self.emoji['star']} Virtue Points: {user_info['points']}\n"
            f"• {self.emoji['users']} Referrals: {len(user_info['referrals'])}/{self.config['REQUIRED_REFERRALS']}\n\n"
            f"{self.emoji['link']} <b>Your Referral Link:</b>\n"
            f"<code>{referral_link}</code>\n\n"
            f"{self.emoji['bell']} <b>How to Get Channel Access?</b>\n"
            f"1. {self.emoji['share']} Share above link with {self.config['REQUIRED_REFERRALS']} people\n"
            f"2. {self.emoji['check']} When they join, you get Virtue Points\n"
            f"3. {self.emoji['gate']} After {self.config['REQUIRED_REFERRALS']} referrals, get channel access\n\n"
            f"{self.emoji['heart']} <i> Share And Support Us  </i>"
        )
        
        share_url = f"https://t.me/share/url?url={referral_link}&text={self.emoji['om']} Join this bot for Dharmik Media Group Link"
        
        keyboard = [
            [InlineKeyboardButton(
                f"{self.emoji['share']} Share Link", 
                url=share_url
            )],
            [InlineKeyboardButton(
                f"{self.emoji['stats']} Check My Status", 
                callback_data="status"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user status (EXACT ORIGINAL MESSAGE)"""
        query = update.callback_query
        if query:
            await query.answer()
            user_id = str(query.from_user.id)
            message = query.message
        else:
            user_id = str(update.effective_user.id)
            message = update.message
        
        user_data = self.load_user_data()
        
        if user_id not in user_data:
            text = f"{self.emoji['warning']} Please use /start first"
            if query:
                await query.edit_message_text(text)
            else:
                await message.reply_text(text)
            return
        
        user_info = user_data[user_id]
        referral_count = len(user_info.get('referrals', []))
        referral_link = self.get_referral_link(user_id)
        
        status_text = (
            f"{self.emoji['om']} <b>YOUR SPIRITUAL JOURNEY</b>\n\n"
            f"{self.emoji['hands']} <b>Seeker:</b> {self.escape_html(user_info.get('first_name', 'Unknown'))}\n"
            f"{self.emoji['star']} <b>Virtue Points:</b> {user_info.get('points', 0)}\n"
            f"{self.emoji['users']} <b>Referrals:</b> {referral_count}/{self.config['REQUIRED_REFERRALS']} {'✅' if referral_count >= self.config['REQUIRED_REFERRALS'] else '⏳'}\n"
            f"{self.emoji['link']} <b>Your Link:</b> <code>{referral_link}</code>\n\n"
            f"{self.emoji['diya']} <b>Joined:</b> {user_info.get('joined_at', 'Unknown')}\n"
        )
        
        keyboard = []
        
        if referral_count >= self.config['REQUIRED_REFERRALS']:
            status_text += (
                f"\n{self.emoji['celebration']} <b>MISSION ACCOMPLISHED!</b>\n\n"
                f"{self.emoji['check']} <b>You've completed {self.config['REQUIRED_REFERRALS']} referrals!</b>\n"
                f"{self.emoji['gate']} <b>Now you can access Dharma Darshan Channel</b>\n\n"
                f"{self.emoji['bell']} If you didn't receive channel link, type /start again"
            )
            keyboard = [
                [InlineKeyboardButton(
                    f"{self.emoji['temple']} Dharma Media group Channel Links Channel", 
                    url=self.config['DHARMIK_CHANNEL_LINK']
                )],
                [InlineKeyboardButton(f"{self.emoji['refresh']} Refresh", callback_data="status")],
                [InlineKeyboardButton(f"{self.emoji['home']} Main Menu", callback_data="home")]
            ]
        else:
            needed = self.config['REQUIRED_REFERRALS'] - referral_count
            status_text += (
                f"\n{self.emoji['target']} <b>TOWARDS THE GOAL</b>\n\n"
                f"{self.emoji['bell']} <b>Need {needed} more referrals</b>\n"
                f"{self.emoji['heart']} <i>Keep spreading Dharmik Media </i>"
            )
            share_url = f"https://t.me/share/url?url={referral_link}&text={self.emoji['om']} Join for spiritual content!"
            keyboard = [
                [InlineKeyboardButton(
                    f"{self.emoji['share']} Share Link", 
                    url=share_url
                )],
                [InlineKeyboardButton(f"{self.emoji['refresh']} Refresh", callback_data="status")],
                [InlineKeyboardButton(f"{self.emoji['home']} Main Menu", callback_data="home")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if query:
                await query.edit_message_text(status_text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await message.reply_text(status_text, reply_markup=reply_markup, parse_mode='HTML')
        except BadRequest:
            if query:
                await query.answer(f"{self.emoji['check']} Updated!")
    
    async def home(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Return to home menu (EXACT ORIGINAL MESSAGE)"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_data = self.load_user_data()
        
        if user_id not in user_data:
            await query.edit_message_text(f"{self.emoji['warning']} Please use /start first")
            return
        
        user_info = user_data[user_id]
        referral_link = self.get_referral_link(user_id)
        
        home_text = (
            f"{self.emoji['om']} <b>DHARMA  BOT</b>\n\n"
            f"{self.emoji['book']} <b>Your Spiritual Journey Summary:</b>\n\n"
            f"{self.emoji['star']} <b>Virtue Points:</b> {user_info['points']}\n"
            f"{self.emoji['users']} <b>Referrals:</b> {len(user_info['referrals'])}/{self.config['REQUIRED_REFERRALS']}\n"
            f"{self.emoji['link']} <b>Your Link:</b> <code>{referral_link}</code>\n\n"
            f"{self.emoji['bell']} <b>Next Steps:</b>\n"
            f"1. {self.emoji['share']} Share your link\n"
            f"2. {self.emoji['check']} Complete {self.config['REQUIRED_REFERRALS']} referrals\n"
            f"3. {self.emoji['gate']} Get Dharma Group Link  Channel access\n\n"
            f"{self.emoji['heart']} <i>Every referral contributes to spreading Dharma!</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton(
                f"{self.emoji['share']} Share Link", 
                url=f"https://t.me/share/url?url={referral_link}&text={self.emoji['om']} Join for spiritual content!"
            )],
            [InlineKeyboardButton(f"{self.emoji['stats']} Check Status", callback_data="status")],
            [InlineKeyboardButton(f"{self.emoji['help']} Help", callback_data="help")]
        ]
        
        if len(user_info['referrals']) >= self.config['REQUIRED_REFERRALS']:
            keyboard.insert(1, [InlineKeyboardButton(
                f"{self.emoji['temple']} Dharma Darshan Channel", 
                url=self.config['DHARMIK_CHANNEL_LINK']
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(home_text, reply_markup=reply_markup, parse_mode='HTML')
        except BadRequest:
            await query.answer(f"{self.emoji['check']} Main Menu!")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information (EXACT ORIGINAL MESSAGE)"""
        query = update.callback_query
        if query:
            await query.answer()
            message = query.message
        else:
            message = update.message
        
        help_text = (
            f"{self.emoji['om']} <b>DHARMA BOT HELP</b>\n\n"
            f"{self.emoji['book']} <b>How This Bot Works?</b>\n\n"
            f"{self.emoji['check']} <b>Step 1:</b> Use /start to get your referral link\n"
            f"{self.emoji['share']} <b>Step 2:</b> Share link with {self.config['REQUIRED_REFERRALS']} people\n"
            f"{self.emoji['gift']} <b>Step 3:</b> When they join, you get Virtue Points\n"
            f"{self.emoji['gate']} <b>Step 4:</b> After {self.config['REQUIRED_REFERRALS']} referrals, get Dharma Group Links Channel access\n\n"
            f"{self.emoji['bell']} <b>Available Commands:</b>\n"
            f"• /start - Start bot & get referral link\n"
            f"• /status - Check your progress\n"
            f"• /help - This help message\n\n"
            f"{self.emoji['heart']} <b>Important Notes:</b>\n"
            f"• Each person can join only once using your link\n"
            f"• Self-referral is not allowed\n"
            f"• Channel access is auto-approved\n\n"
            f"{self.emoji['diya']} <i>Sharing This Bot!</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton(f"{self.emoji['home']} Main Menu", callback_data="home")],
            [InlineKeyboardButton(f"{self.emoji['stats']} Check Status", callback_data="status")],
            [InlineKeyboardButton(f"🚀 Get Started", callback_data="start_callback")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def start_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle start callback"""
        query = update.callback_query
        await query.answer(f"{self.emoji['bell']} Please type /start command!")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command to view statistics"""
        user_id = str(update.effective_user.id)
        
        if user_id != self.config['ADMIN_USER_ID']:
            await update.message.reply_text(f"{self.emoji['warning']} Admin only")
            return
        
        user_data = self.load_user_data()
        total_users = len(user_data)
        
        completed = 0
        total_refs = 0
        recent_users = 0
        
        for uid, info in user_data.items():
            refs = len(info.get('referrals', []))
            total_refs += refs
            if refs >= self.config['REQUIRED_REFERRALS']:
                completed += 1
            
            # Check recent activity (last 24 hours)
            last_activity = info.get('last_activity')
            if last_activity:
                try:
                    last_time = datetime.fromisoformat(last_activity)
                    if (datetime.now() - last_time).days < 1:
                        recent_users += 1
                except:
                    pass
        
        pending = total_users - completed
        
        stats = (
            f"{self.emoji['admin']} <b>ADMIN STATISTICS</b>\n\n"
            f"{self.emoji['users']} <b>Total Seekers:</b> {total_users}\n"
            f"{self.emoji['check']} <b>Completed Mission:</b> {completed}\n"
            f"{self.emoji['clock']} <b>In Progress:</b> {pending}\n"
            f"{self.emoji['link']} <b>Total Referrals:</b> {total_refs}\n"
            f"{self.emoji['message']} <b>Active (24h):</b> {recent_users}\n\n"
            f"{self.emoji['target']} <b>Target:</b> {self.config['REQUIRED_REFERRALS']} referrals per seeker\n"
            f"{self.emoji['temple']} <b>Channel:</b> Dharma Darshan\n"
            f"{self.emoji['bot']} <b>Bot:</b> @{self.config['BOT_USERNAME']}\n"
            f"{self.emoji['server']} <b>Server:</b> Railway\n\n"
            f"{self.emoji['diya']} <i>Dharma propagation work continues...</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton(f"{self.emoji['refresh']} Refresh Stats", callback_data="admin_refresh")],
            [InlineKeyboardButton(f"{self.emoji['home']} Main Menu", callback_data="home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(stats, reply_markup=reply_markup, parse_mode='HTML')
    
    async def admin_refresh(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Refresh admin stats"""
        query = update.callback_query
        await query.answer("Refreshing...")
        
        user_id = str(query.from_user.id)
        if user_id != self.config['ADMIN_USER_ID']:
            await query.message.edit_text(f"{self.emoji['warning']} Admin only")
            return
        
        await self.admin_command(update, context)
    
    async def handle_channel_join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Dharmik Channel join requests"""
        join_request = update.chat_join_request
        user_id = str(join_request.from_user.id)
        user_name = join_request.from_user.first_name or "User"
        
        logger.info(f"{self.emoji['gate']} Channel join request from {user_id} ({user_name})")
        
        user_data = self.load_user_data()
        
        if user_id in user_data:
            refs = len(user_data[user_id].get('referrals', []))
            
            if refs >= self.config['REQUIRED_REFERRALS']:
                success = await self.approve_channel_request(int(user_id), context)
                if success:
                    logger.info(f"{self.emoji['gate']} Approved {user_id} to Dharmik Channel (has {refs} refs)")
                    
                    try:
                        keyboard = [
                            [InlineKeyboardButton(
                                f"{self.emoji['temple']} Open Channel", 
                                url=self.config['DHARMIK_CHANNEL_LINK']
                            )]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await context.bot.send_message(
                            chat_id=int(user_id),
                            text=f"{self.emoji['celebration']} <b>Your channel access has been approved!</b>\n\n"
                                 f"{self.emoji['temple']} Welcome to Dharma Darshan Channel!\n\n"
                                 f"{self.emoji['heart']} <i>May your spiritual journey be blessed!</i>",
                            reply_markup=reply_markup,
                            parse_mode='HTML'
                        )
                    except:
                        pass
                else:
                    logger.error(f"{self.emoji['warning']} Failed to approve {user_id}")
            else:
                await self.decline_channel_request(int(user_id), context)
                needed = self.config['REQUIRED_REFERRALS'] - refs
                logger.info(f"{self.emoji['warning']} Declined {user_id} (needs {needed} more refs)")
                
                try:
                    await context.bot.send_message(
                        chat_id=int(user_id),
                        text=f"{self.emoji['warning']} <b>Channel Access Denied</b>\n\n"
                             f"{self.emoji['target']} You need {needed} more referrals to access the channel.\n"
                             f"{self.emoji['share']} Use /start to get your referral link and invite friends.\n\n"
                             f"{self.emoji['heart']} <i>Complete {self.config['REQUIRED_REFERRALS']} referrals for access!</i>",
                        parse_mode='HTML'
                    )
                except:
                    pass
        else:
            await self.decline_channel_request(int(user_id), context)
            logger.info(f"{self.emoji['warning']} Declined unknown user {user_id}")
            
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=f"{self.emoji['warning']} <b>You need to start the bot first!</b>\n\n"
                         f"{self.emoji['book']} Please use /start command with the bot.\n"
                         f"{self.emoji['share']} Then complete referrals to get channel access.",
                    parse_mode='HTML'
                )
            except:
                pass
    
    def setup_handlers(self, application):
        """Setup all bot handlers"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        
        application.add_handler(ChatJoinRequestHandler(
            self.handle_channel_join,
            chat_id=int(self.config['CHANNEL_ID'])
        ))
        
        application.add_handler(CallbackQueryHandler(self.status, pattern="^status$"))
        application.add_handler(CallbackQueryHandler(self.home, pattern="^home$"))
        application.add_handler(CallbackQueryHandler(self.help_command, pattern="^help$"))
        application.add_handler(CallbackQueryHandler(self.start_callback, pattern="^start_callback$"))
        application.add_handler(CallbackQueryHandler(self.admin_refresh, pattern="^admin_refresh$"))
    
    def run(self):
        """Start the Dharmik Bot on Railway"""
        self.validate_config()
        
        app = Application.builder() \
            .token(self.config['BOT_TOKEN']) \
            .read_timeout(30) \
            .write_timeout(30) \
            .connect_timeout(30) \
            .pool_timeout(30) \
            .build()
        
        self.setup_handlers(app)
        
        print(f"\n{'='*60}")
        print(f"{self.emoji['om']}  DHARMA DARSHAN BOT - RAILWAY EDITION  {self.emoji['om']}")
        print(f"{'='*60}")
        print(f"{self.emoji['bot']}  Bot: @{self.config['BOT_USERNAME']}")
        print(f"{self.emoji['target']}  Target: {self.config['REQUIRED_REFERRALS']} referrals")
        print(f"{self.emoji['temple']}  Channel: Dharma Darshan")
        print(f"{self.emoji['server']}  Server: Railway")
        print(f"{'='*60}")
        print(f"{self.emoji['check']}  Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'Development')}")
        print(f"{self.emoji['check']}  Data Directory: {self.data_dir}")
        print(f"{self.emoji['check']}  Users File: {self.user_data_file}")
        print(f"{'='*60}")
        print(f"{self.emoji['gate']}  Bot starting on Railway...")
        print(f"{'='*60}\n")
        
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )

def main():
    """Main function for Railway"""
    bot = DharmikReferralBot()
    bot.run()

if __name__ == '__main__':
    main()