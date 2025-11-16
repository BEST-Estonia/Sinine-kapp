# src/screens/__init__.py
"""Screen modules for the Smart Cupboard application"""

from .base_screen import BaseScreen
from .main_menu import MainMenuScreen
from .card_scan import CardScanScreen
from .register_user import RegisterUserScreen
from .qr_scan import QRScanScreen
from .basket import BasketScreen
from .thank_you import ThankYouScreen
from .admin_main import AdminMainScreen
from .admin_users import AdminUsersScreen
from .admin_user_details import AdminUserDetailsScreen
from .admin_inventory import AdminInventoryScreen
from .admin_logs import AdminLogsScreen

__all__ = [
    'BaseScreen',
    'MainMenuScreen',
    'CardScanScreen', 
    'RegisterUserScreen',
    'QRScanScreen',
    'BasketScreen',
    'ThankYouScreen',
    'AdminMainScreen',
    'AdminUsersScreen',
    'AdminUserDetailsScreen',
    'AdminInventoryScreen',
    'AdminLogsScreen',
]
