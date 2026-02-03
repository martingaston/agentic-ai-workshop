"""
Pattern generators for different abuse types in ecommerce transactions.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any
from faker import Faker

from schema import (
    TEMP_EMAIL_DOMAINS,
    LEGITIMATE_EMAIL_DOMAINS,
    HIGH_RISK_COUNTRIES,
    LOW_RISK_COUNTRIES,
    DEVICE_TYPES,
    PAYMENT_METHODS,
    USER_AGENTS,
    ALL_CARD_BINS,
)

fake = Faker()


class BasePatternGenerator:
    """Base class for pattern generation with common utilities."""

    def __init__(self, seed: int | None = None):
        """Initialize generator with optional seed for reproducibility."""
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
        self.fake = Faker()

    def _generate_ip_address(self, country: str | None = None) -> str:
        """Generate a realistic IP address."""
        # Anonymized IP format
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.xxx.xxx"

    def _generate_device_id(self) -> str:
        """Generate a unique device identifier."""
        return f"DEV_{self.fake.hexify(text='^^^^^^^^', upper=True)}"

    def _generate_transaction_id(self, timestamp: datetime) -> str:
        """Generate a unique transaction identifier."""
        date_str = timestamp.strftime('%Y%m%d')
        random_suffix = self.fake.hexify(text='^^^^^^', upper=True)
        return f"TXN_{date_str}_{random_suffix}"

    def _generate_user_id(self) -> str:
        """Generate a unique user identifier."""
        return f"USER_{random.randint(10000, 999999)}"


class LegitimatePatternGenerator(BasePatternGenerator):
    """Generates legitimate transaction patterns."""

    def generate(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate a legitimate transaction record."""
        # Account created 30-365 days ago
        account_age_days = random.randint(30, 365)
        account_created_date = timestamp - timedelta(days=account_age_days)

        # First purchase typically within first 30 days of account creation
        days_since_first_purchase = random.randint(0, min(30, account_age_days))

        # Established users have more orders
        total_orders = random.randint(1, 50)

        # Normal velocity
        orders_24h = random.choices([0, 1], weights=[0.8, 0.2])[0]
        orders_7d = random.randint(0, 5)

        # Verified accounts
        email_verified = random.random() > 0.1  # 90% verified
        phone_verified = random.random() > 0.2  # 80% verified
        profile_complete = random.random() > 0.3  # 70% complete

        # Low-risk email domain
        email_domain = random.choice(LEGITIMATE_EMAIL_DOMAINS)

        # Consistent geographic location
        country = random.choice(LOW_RISK_COUNTRIES)
        ip_country = country
        card_country = country if random.random() > 0.1 else random.choice(LOW_RISK_COUNTRIES)
        billing_country = country
        shipping_country = country if random.random() > 0.05 else random.choice(LOW_RISK_COUNTRIES)

        # Normal order amounts
        avg_order_value = random.uniform(30.0, 200.0)
        order_amount = random.gauss(avg_order_value, avg_order_value * 0.3)
        order_amount = max(10.0, order_amount)

        # Normal session behavior
        session_duration = random.randint(120, 1800)  # 2-30 minutes
        cart_additions = random.randint(1, 5)

        # Clean payment verification
        cvv_result = random.choices(
            ['pass', 'not_checked'],
            weights=[0.9, 0.1]
        )[0]
        avs_result = random.choices(
            ['full_match', 'partial_match'],
            weights=[0.85, 0.15]
        )[0]

        return {
            'transaction_id': self._generate_transaction_id(timestamp),
            'timestamp': timestamp,
            'user_id': self._generate_user_id(),
            'order_amount': round(order_amount, 2),
            'currency': 'USD',
            'account_created_date': account_created_date,
            'account_age_days': account_age_days,
            'email_domain': email_domain,
            'phone_verified': phone_verified,
            'email_verified': email_verified,
            'profile_complete': profile_complete,
            'failed_login_attempts_24h': 0 if random.random() > 0.05 else random.randint(1, 2),
            'successful_logins_7d': random.randint(3, 20),
            'password_reset_count_30d': 0 if random.random() > 0.1 else 1,
            'device_id': self._generate_device_id(),
            'ip_address': self._generate_ip_address(country),
            'ip_country': ip_country,
            'user_agent': random.choice([ua for ua in USER_AGENTS if 'Bot' not in ua and 'curl' not in ua]),
            'device_type': random.choice(DEVICE_TYPES),
            'new_device': random.random() < 0.15,  # 15% new device
            'vpn_proxy_detected': random.random() < 0.05,  # 5% VPN usage
            'payment_method': random.choices(
                PAYMENT_METHODS,
                weights=[0.5, 0.3, 0.15, 0.05]  # Credit card most common
            )[0],
            'card_bin': random.choice(ALL_CARD_BINS),
            'card_country': card_country,
            'billing_country': billing_country,
            'shipping_country': shipping_country,
            'billing_shipping_match': billing_country == shipping_country,
            'cvv_check_result': cvv_result,
            'avs_result': avs_result,
            'payment_processor_response': 'approved',
            'days_since_account_first_purchase': days_since_first_purchase,
            'total_orders_lifetime': total_orders,
            'orders_last_24h': orders_24h,
            'orders_last_7d': orders_7d,
            'avg_order_value': round(avg_order_value, 2),
            'session_duration_seconds': session_duration,
            'cart_additions_session': cart_additions,
            'high_risk_category': random.random() < 0.2,  # 20% high-risk items
            'is_abuse': False,
            'abuse_type': 'legitimate',
            'abuse_confidence': 0.0,
        }


class FakeAccountPatternGenerator(BasePatternGenerator):
    """Generates fake account abuse patterns."""

    def generate(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate a fake account transaction record."""
        # Very new accounts (0-3 days)
        account_age_days = random.randint(0, 3)
        account_created_date = timestamp - timedelta(days=account_age_days)

        # First purchase immediately or very soon after creation
        days_since_first_purchase = 0 if random.random() > 0.3 else account_age_days

        # New accounts have few orders
        total_orders = random.randint(1, 3)

        # Temporary email domain
        email_domain = random.choice(TEMP_EMAIL_DOMAINS)

        # Not verified
        email_verified = random.random() < 0.1  # 10% verified
        phone_verified = random.random() < 0.05  # 5% verified
        profile_complete = random.random() < 0.1  # 10% complete

        # Geographic indicators
        country = random.choice(LOW_RISK_COUNTRIES + HIGH_RISK_COUNTRIES)
        ip_country = country
        card_country = random.choice(LOW_RISK_COUNTRIES)  # Often stolen cards from low-risk countries
        billing_country = card_country
        shipping_country = random.choice(LOW_RISK_COUNTRIES)

        # Order amount - varies widely
        order_amount = random.uniform(50.0, 500.0)

        # Rushed behavior
        session_duration = random.randint(30, 180)  # 30 seconds to 3 minutes
        cart_additions = random.randint(1, 3)

        # Payment verification
        cvv_result = random.choices(
            ['pass', 'fail', 'not_checked'],
            weights=[0.6, 0.2, 0.2]
        )[0]
        avs_result = random.choices(
            ['full_match', 'partial_match', 'no_match'],
            weights=[0.4, 0.3, 0.3]
        )[0]

        # Abuse confidence
        abuse_confidence = random.uniform(0.7, 0.95)

        return {
            'transaction_id': self._generate_transaction_id(timestamp),
            'timestamp': timestamp,
            'user_id': self._generate_user_id(),
            'order_amount': round(order_amount, 2),
            'currency': 'USD',
            'account_created_date': account_created_date,
            'account_age_days': account_age_days,
            'email_domain': email_domain,
            'phone_verified': phone_verified,
            'email_verified': email_verified,
            'profile_complete': profile_complete,
            'failed_login_attempts_24h': 0,  # No failed logins for new accounts
            'successful_logins_7d': random.randint(1, 5),
            'password_reset_count_30d': 0,
            'device_id': self._generate_device_id(),
            'ip_address': self._generate_ip_address(country),
            'ip_country': ip_country,
            'user_agent': random.choice(USER_AGENTS),
            'device_type': random.choice(DEVICE_TYPES),
            'new_device': True,  # Always new device for new account
            'vpn_proxy_detected': random.random() < 0.3,  # 30% VPN usage
            'payment_method': random.choices(
                PAYMENT_METHODS,
                weights=[0.6, 0.2, 0.15, 0.05]
            )[0],
            'card_bin': random.choice(ALL_CARD_BINS),
            'card_country': card_country,
            'billing_country': billing_country,
            'shipping_country': shipping_country,
            'billing_shipping_match': random.random() < 0.4,  # 40% match
            'cvv_check_result': cvv_result,
            'avs_result': avs_result,
            'payment_processor_response': random.choices(
                ['approved', 'suspected_fraud'],
                weights=[0.7, 0.3]
            )[0],
            'days_since_account_first_purchase': days_since_first_purchase,
            'total_orders_lifetime': total_orders,
            'orders_last_24h': random.randint(1, 3),
            'orders_last_7d': total_orders,
            'avg_order_value': round(order_amount, 2),
            'session_duration_seconds': session_duration,
            'cart_additions_session': cart_additions,
            'high_risk_category': random.random() < 0.5,  # 50% high-risk items
            'is_abuse': True,
            'abuse_type': 'fake_account',
            'abuse_confidence': round(abuse_confidence, 2),
        }


class AccountTakeoverPatternGenerator(BasePatternGenerator):
    """Generates account takeover abuse patterns."""

    def generate(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate an account takeover transaction record."""
        # Older, established accounts
        account_age_days = random.randint(90, 730)  # 3 months to 2 years
        account_created_date = timestamp - timedelta(days=account_age_days)

        # Account has history
        total_orders = random.randint(5, 50)
        days_since_first_purchase = random.randint(30, account_age_days - 30)

        # Verified legitimate account
        email_verified = True
        phone_verified = random.random() > 0.3
        profile_complete = random.random() > 0.2

        # Legitimate email domain
        email_domain = random.choice(LEGITIMATE_EMAIL_DOMAINS)

        # Suspicious login activity
        failed_login_attempts_24h = random.randint(3, 15)
        password_reset_count_30d = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]

        # Geographic anomaly - account from one country, transaction from another
        original_country = random.choice(LOW_RISK_COUNTRIES)
        suspicious_country = random.choice(HIGH_RISK_COUNTRIES + LOW_RISK_COUNTRIES)
        ip_country = suspicious_country

        # Shipping changed to different location
        card_country = original_country
        billing_country = original_country
        shipping_country = suspicious_country if random.random() > 0.3 else random.choice(LOW_RISK_COUNTRIES)

        # Higher than average order amount
        historical_avg = random.uniform(40.0, 150.0)
        order_amount = historical_avg * random.uniform(1.5, 4.0)  # 1.5x to 4x higher

        # Quick checkout (attacker knows what they want)
        session_duration = random.randint(60, 300)  # 1-5 minutes
        cart_additions = random.randint(1, 3)

        # Payment verification
        cvv_result = random.choices(
            ['pass', 'fail', 'not_checked'],
            weights=[0.5, 0.3, 0.2]
        )[0]
        avs_result = random.choices(
            ['full_match', 'partial_match', 'no_match'],
            weights=[0.3, 0.4, 0.3]
        )[0]

        abuse_confidence = random.uniform(0.75, 0.95)

        return {
            'transaction_id': self._generate_transaction_id(timestamp),
            'timestamp': timestamp,
            'user_id': self._generate_user_id(),
            'order_amount': round(order_amount, 2),
            'currency': 'USD',
            'account_created_date': account_created_date,
            'account_age_days': account_age_days,
            'email_domain': email_domain,
            'phone_verified': phone_verified,
            'email_verified': email_verified,
            'profile_complete': profile_complete,
            'failed_login_attempts_24h': failed_login_attempts_24h,
            'successful_logins_7d': random.randint(1, 3),
            'password_reset_count_30d': password_reset_count_30d,
            'device_id': self._generate_device_id(),  # New device
            'ip_address': self._generate_ip_address(suspicious_country),
            'ip_country': ip_country,
            'user_agent': random.choice(USER_AGENTS),
            'device_type': random.choice(DEVICE_TYPES),
            'new_device': True,  # Attacker using different device
            'vpn_proxy_detected': random.random() < 0.4,  # 40% VPN usage
            'payment_method': random.choices(
                PAYMENT_METHODS,
                weights=[0.5, 0.3, 0.15, 0.05]
            )[0],
            'card_bin': random.choice(ALL_CARD_BINS),
            'card_country': card_country,
            'billing_country': billing_country,
            'shipping_country': shipping_country,
            'billing_shipping_match': billing_country == shipping_country,
            'cvv_check_result': cvv_result,
            'avs_result': avs_result,
            'payment_processor_response': random.choices(
                ['approved', 'suspected_fraud'],
                weights=[0.6, 0.4]
            )[0],
            'days_since_account_first_purchase': days_since_first_purchase,
            'total_orders_lifetime': total_orders,
            'orders_last_24h': random.randint(1, 2),
            'orders_last_7d': random.randint(1, 3),
            'avg_order_value': round(historical_avg, 2),
            'session_duration_seconds': session_duration,
            'cart_additions_session': cart_additions,
            'high_risk_category': random.random() < 0.6,  # 60% high-risk items
            'is_abuse': True,
            'abuse_type': 'account_takeover',
            'abuse_confidence': round(abuse_confidence, 2),
        }


class PaymentFraudPatternGenerator(BasePatternGenerator):
    """Generates payment fraud patterns."""

    def generate(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate a payment fraud transaction record."""
        # Account age varies - can be new or established
        account_age_days = random.randint(1, 180)
        account_created_date = timestamp - timedelta(days=account_age_days)

        days_since_first_purchase = random.randint(0, min(30, account_age_days))
        total_orders = random.randint(1, 10)

        # Mixed verification status
        email_verified = random.random() > 0.4
        phone_verified = random.random() > 0.6
        profile_complete = random.random() > 0.5

        # Choose email domain - 60% legitimate, 40% temporary
        if random.random() < 0.6:
            email_domain = random.choice(LEGITIMATE_EMAIL_DOMAINS)
        else:
            email_domain = random.choice(TEMP_EMAIL_DOMAINS)

        # Geographic mismatches - key fraud indicator
        ip_country = random.choice(LOW_RISK_COUNTRIES + HIGH_RISK_COUNTRIES)
        card_country = random.choice(LOW_RISK_COUNTRIES)  # Stolen cards often from low-risk countries
        billing_country = random.choice(LOW_RISK_COUNTRIES + HIGH_RISK_COUNTRIES)
        shipping_country = random.choice(LOW_RISK_COUNTRIES)

        # Ensure mismatches
        if random.random() > 0.3:  # 70% have mismatches
            billing_country = random.choice([c for c in LOW_RISK_COUNTRIES if c != card_country])

        # High-value orders with high-risk items
        order_amount = random.uniform(200.0, 2000.0)

        # Session behavior
        session_duration = random.randint(60, 600)
        cart_additions = random.randint(1, 10)

        # Failed payment verification - strong fraud signal
        cvv_result = random.choices(
            ['pass', 'fail', 'not_checked'],
            weights=[0.3, 0.5, 0.2]
        )[0]
        avs_result = random.choices(
            ['full_match', 'partial_match', 'no_match'],
            weights=[0.2, 0.3, 0.5]
        )[0]

        # Multiple payment attempts (card testing)
        orders_24h = random.randint(1, 8)

        abuse_confidence = random.uniform(0.7, 0.98)

        return {
            'transaction_id': self._generate_transaction_id(timestamp),
            'timestamp': timestamp,
            'user_id': self._generate_user_id(),
            'order_amount': round(order_amount, 2),
            'currency': 'USD',
            'account_created_date': account_created_date,
            'account_age_days': account_age_days,
            'email_domain': email_domain,
            'phone_verified': phone_verified,
            'email_verified': email_verified,
            'profile_complete': profile_complete,
            'failed_login_attempts_24h': random.randint(0, 3),
            'successful_logins_7d': random.randint(1, 10),
            'password_reset_count_30d': random.choices([0, 1], weights=[0.8, 0.2])[0],
            'device_id': self._generate_device_id(),
            'ip_address': self._generate_ip_address(ip_country),
            'ip_country': ip_country,
            'user_agent': random.choice(USER_AGENTS),
            'device_type': random.choice(DEVICE_TYPES),
            'new_device': random.random() < 0.5,
            'vpn_proxy_detected': random.random() < 0.35,  # 35% VPN usage
            'payment_method': random.choices(
                PAYMENT_METHODS,
                weights=[0.7, 0.2, 0.08, 0.02]  # Mostly cards for fraud
            )[0],
            'card_bin': random.choice(ALL_CARD_BINS),
            'card_country': card_country,
            'billing_country': billing_country,
            'shipping_country': shipping_country,
            'billing_shipping_match': billing_country == shipping_country,
            'cvv_check_result': cvv_result,
            'avs_result': avs_result,
            'payment_processor_response': random.choices(
                ['approved', 'declined', 'suspected_fraud'],
                weights=[0.5, 0.2, 0.3]
            )[0],
            'days_since_account_first_purchase': days_since_first_purchase,
            'total_orders_lifetime': total_orders,
            'orders_last_24h': orders_24h,
            'orders_last_7d': random.randint(orders_24h, orders_24h + 5),
            'avg_order_value': round(order_amount * random.uniform(0.7, 1.3), 2),
            'session_duration_seconds': session_duration,
            'cart_additions_session': cart_additions,
            'high_risk_category': random.random() < 0.8,  # 80% high-risk items (electronics, gift cards)
            'is_abuse': True,
            'abuse_type': 'payment_fraud',
            'abuse_confidence': round(abuse_confidence, 2),
        }
