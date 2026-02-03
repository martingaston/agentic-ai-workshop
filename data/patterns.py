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

    def generate(self, timestamp: datetime, difficulty: str = 'n/a') -> Dict[str, Any]:
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
            'difficulty_tier': 'n/a',
        }


class FakeAccountPatternGenerator(BasePatternGenerator):
    """Generates fake account abuse patterns with difficulty tiers."""

    def generate(self, timestamp: datetime, difficulty: str = 'easy') -> Dict[str, Any]:
        """
        Generate a fake account transaction record.

        Args:
            timestamp: Transaction timestamp
            difficulty: 'easy', 'medium', or 'hard' detection difficulty
        """
        # Account age varies by difficulty
        if difficulty == 'easy':
            # Very obvious fake account (0-3 days)
            account_age_days = random.randint(0, 3)
            email_domain = random.choice(TEMP_EMAIL_DOMAINS)
            email_verified = random.random() < 0.05  # 5% verified
            phone_verified = random.random() < 0.02  # 2% verified
            profile_complete = random.random() < 0.05  # 5% complete
            abuse_confidence = random.uniform(0.85, 0.98)
        elif difficulty == 'medium':
            # Somewhat sophisticated (3-7 days, sometimes legit email)
            account_age_days = random.randint(3, 7)
            email_domain = random.choice(TEMP_EMAIL_DOMAINS) if random.random() < 0.6 else random.choice(LEGITIMATE_EMAIL_DOMAINS)
            email_verified = random.random() < 0.3  # 30% verified
            phone_verified = random.random() < 0.15  # 15% verified
            profile_complete = random.random() < 0.2  # 20% complete
            abuse_confidence = random.uniform(0.65, 0.80)
        else:  # hard
            # Well-aged fake account (7-30 days, looks more legitimate)
            account_age_days = random.randint(7, 30)
            email_domain = random.choice(LEGITIMATE_EMAIL_DOMAINS)  # Looks legitimate
            email_verified = random.random() < 0.6  # 60% verified
            phone_verified = random.random() < 0.4  # 40% verified
            profile_complete = random.random() < 0.5  # 50% complete
            abuse_confidence = random.uniform(0.45, 0.65)

        account_created_date = timestamp - timedelta(days=account_age_days)

        # First purchase timing varies by difficulty
        if difficulty == 'easy':
            days_since_first_purchase = 0  # Immediate purchase
        elif difficulty == 'medium':
            days_since_first_purchase = random.randint(0, min(3, account_age_days))
        else:  # hard
            days_since_first_purchase = random.randint(3, min(14, account_age_days))

        # New accounts have few orders
        total_orders = random.randint(1, 3) if difficulty == 'easy' else random.randint(1, 5)

        # Geographic indicators
        country = random.choice(LOW_RISK_COUNTRIES + HIGH_RISK_COUNTRIES)
        ip_country = country
        card_country = random.choice(LOW_RISK_COUNTRIES)  # Often stolen cards from low-risk countries
        billing_country = card_country
        shipping_country = random.choice(LOW_RISK_COUNTRIES)

        # Order amount - varies widely
        order_amount = random.uniform(50.0, 500.0)

        # Session behavior varies by difficulty
        if difficulty == 'easy':
            session_duration = random.randint(30, 180)  # Very rushed
            cart_additions = random.randint(1, 3)
        elif difficulty == 'medium':
            session_duration = random.randint(120, 600)  # Somewhat normal
            cart_additions = random.randint(1, 5)
        else:  # hard
            session_duration = random.randint(180, 1200)  # Looks normal
            cart_additions = random.randint(1, 7)

        # Payment verification varies by difficulty
        if difficulty == 'easy':
            cvv_result = random.choices(['pass', 'fail', 'not_checked'], weights=[0.5, 0.3, 0.2])[0]
            avs_result = random.choices(['full_match', 'partial_match', 'no_match'], weights=[0.3, 0.3, 0.4])[0]
        elif difficulty == 'medium':
            cvv_result = random.choices(['pass', 'fail', 'not_checked'], weights=[0.7, 0.2, 0.1])[0]
            avs_result = random.choices(['full_match', 'partial_match', 'no_match'], weights=[0.5, 0.3, 0.2])[0]
        else:  # hard
            cvv_result = random.choices(['pass', 'not_checked'], weights=[0.9, 0.1])[0]  # Usually passes
            avs_result = random.choices(['full_match', 'partial_match'], weights=[0.7, 0.3])[0]

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
            'difficulty_tier': difficulty,
        }


class AccountTakeoverPatternGenerator(BasePatternGenerator):
    """Generates account takeover abuse patterns with difficulty tiers."""

    def generate(self, timestamp: datetime, difficulty: str = 'easy') -> Dict[str, Any]:
        """
        Generate an account takeover transaction record.

        Args:
            timestamp: Transaction timestamp
            difficulty: 'easy', 'medium', or 'hard' detection difficulty
        """
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

        # Login activity varies by difficulty
        if difficulty == 'easy':
            # Clear signs of takeover: many failed logins, password reset
            failed_login_attempts_24h = random.randint(5, 15)
            password_reset_count_30d = random.choices([1, 2], weights=[0.7, 0.3])[0]
            abuse_confidence = random.uniform(0.85, 0.97)
        elif difficulty == 'medium':
            # Some suspicious activity but not overwhelming
            failed_login_attempts_24h = random.randint(2, 6)
            password_reset_count_30d = random.choices([0, 1], weights=[0.5, 0.5])[0]
            abuse_confidence = random.uniform(0.65, 0.80)
        else:  # hard
            # Credential stuffing - no failed logins, looks like normal login
            failed_login_attempts_24h = 0  # Successful credential reuse
            password_reset_count_30d = 0
            abuse_confidence = random.uniform(0.45, 0.65)

        # Geographic patterns vary by difficulty
        original_country = random.choice(LOW_RISK_COUNTRIES)
        if difficulty == 'easy':
            # Clear geographic anomaly - high-risk country
            suspicious_country = random.choice(HIGH_RISK_COUNTRIES)
            vpn_detected = random.random() < 0.5
        elif difficulty == 'medium':
            # Different country but could be legitimate travel
            suspicious_country = random.choice(LOW_RISK_COUNTRIES)
            vpn_detected = random.random() < 0.4
        else:  # hard
            # Same country or VPN masking location
            suspicious_country = original_country if random.random() < 0.6 else random.choice(LOW_RISK_COUNTRIES)
            vpn_detected = random.random() < 0.2  # Less obvious

        ip_country = suspicious_country
        card_country = original_country
        billing_country = original_country

        # Shipping varies by difficulty
        if difficulty == 'easy':
            shipping_country = random.choice(HIGH_RISK_COUNTRIES + LOW_RISK_COUNTRIES)  # Often different
        elif difficulty == 'medium':
            shipping_country = suspicious_country if random.random() > 0.4 else original_country
        else:  # hard
            shipping_country = original_country if random.random() > 0.3 else suspicious_country

        # Order amount varies by difficulty
        historical_avg = random.uniform(40.0, 150.0)
        if difficulty == 'easy':
            order_amount = historical_avg * random.uniform(2.0, 4.0)  # Much higher
        elif difficulty == 'medium':
            order_amount = historical_avg * random.uniform(1.3, 2.5)  # Somewhat higher
        else:  # hard
            order_amount = historical_avg * random.uniform(0.9, 1.8)  # Close to normal

        # Session behavior varies by difficulty
        if difficulty == 'easy':
            session_duration = random.randint(60, 300)  # Very quick
            cart_additions = random.randint(1, 3)
        elif difficulty == 'medium':
            session_duration = random.randint(180, 600)  # Quick but not obviously
            cart_additions = random.randint(2, 5)
        else:  # hard
            session_duration = random.randint(300, 1200)  # More normal
            cart_additions = random.randint(2, 6)

        # Payment verification varies by difficulty
        if difficulty == 'easy':
            cvv_result = random.choices(['pass', 'fail', 'not_checked'], weights=[0.4, 0.4, 0.2])[0]
            avs_result = random.choices(['full_match', 'partial_match', 'no_match'], weights=[0.3, 0.3, 0.4])[0]
        elif difficulty == 'medium':
            cvv_result = random.choices(['pass', 'fail', 'not_checked'], weights=[0.6, 0.2, 0.2])[0]
            avs_result = random.choices(['full_match', 'partial_match', 'no_match'], weights=[0.5, 0.3, 0.2])[0]
        else:  # hard
            cvv_result = random.choices(['pass', 'not_checked'], weights=[0.85, 0.15])[0]
            avs_result = random.choices(['full_match', 'partial_match'], weights=[0.7, 0.3])[0]

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
            'device_id': self._generate_device_id(),
            'ip_address': self._generate_ip_address(suspicious_country),
            'ip_country': ip_country,
            'user_agent': random.choice(USER_AGENTS),
            'device_type': random.choice(DEVICE_TYPES),
            'new_device': True if difficulty == 'easy' else (random.random() < 0.7),
            'vpn_proxy_detected': vpn_detected,
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
            'high_risk_category': random.random() < 0.6 if difficulty == 'easy' else (random.random() < 0.4),
            'is_abuse': True,
            'abuse_type': 'account_takeover',
            'abuse_confidence': round(abuse_confidence, 2),
            'difficulty_tier': difficulty,
        }


class PaymentFraudPatternGenerator(BasePatternGenerator):
    """Generates payment fraud patterns with difficulty tiers."""

    def generate(self, timestamp: datetime, difficulty: str = 'easy') -> Dict[str, Any]:
        """
        Generate a payment fraud transaction record.

        Args:
            timestamp: Transaction timestamp
            difficulty: 'easy', 'medium', or 'hard' detection difficulty
        """
        # Account age varies by difficulty
        if difficulty == 'easy':
            account_age_days = random.randint(1, 30)  # Newer accounts
            abuse_confidence = random.uniform(0.85, 0.97)
        elif difficulty == 'medium':
            account_age_days = random.randint(15, 90)  # Some history
            abuse_confidence = random.uniform(0.65, 0.80)
        else:  # hard
            account_age_days = random.randint(60, 180)  # Established accounts
            abuse_confidence = random.uniform(0.45, 0.65)
        account_created_date = timestamp - timedelta(days=account_age_days)

        days_since_first_purchase = random.randint(0, min(30, account_age_days))
        total_orders = random.randint(1, 10)

        # Verification varies by difficulty
        if difficulty == 'easy':
            email_verified = random.random() < 0.3
            phone_verified = random.random() < 0.2
            profile_complete = random.random() < 0.3
            email_domain = random.choice(TEMP_EMAIL_DOMAINS) if random.random() < 0.5 else random.choice(LEGITIMATE_EMAIL_DOMAINS)
        elif difficulty == 'medium':
            email_verified = random.random() < 0.6
            phone_verified = random.random() < 0.4
            profile_complete = random.random() < 0.5
            email_domain = random.choice(LEGITIMATE_EMAIL_DOMAINS)
        else:  # hard
            email_verified = random.random() < 0.8
            phone_verified = random.random() < 0.7
            profile_complete = random.random() < 0.7
            email_domain = random.choice(LEGITIMATE_EMAIL_DOMAINS)

        # Geographic mismatches vary by difficulty
        card_country = random.choice(LOW_RISK_COUNTRIES)
        if difficulty == 'easy':
            # Multiple clear mismatches
            ip_country = random.choice(HIGH_RISK_COUNTRIES)
            billing_country = random.choice([c for c in LOW_RISK_COUNTRIES if c != card_country])
            shipping_country = random.choice([c for c in LOW_RISK_COUNTRIES if c != card_country and c != billing_country])
        elif difficulty == 'medium':
            # One or two mismatches
            ip_country = random.choice(LOW_RISK_COUNTRIES + HIGH_RISK_COUNTRIES)
            billing_country = card_country if random.random() < 0.5 else random.choice(LOW_RISK_COUNTRIES)
            shipping_country = random.choice(LOW_RISK_COUNTRIES)
        else:  # hard
            # Only shipping mismatch (could be gift)
            ip_country = random.choice(LOW_RISK_COUNTRIES)
            billing_country = card_country
            shipping_country = random.choice(LOW_RISK_COUNTRIES) if random.random() < 0.7 else card_country

        # Order amount varies by difficulty
        if difficulty == 'easy':
            order_amount = random.uniform(500.0, 2000.0)  # Very high
        elif difficulty == 'medium':
            order_amount = random.uniform(200.0, 800.0)  # Moderate
        else:  # hard
            order_amount = random.uniform(100.0, 500.0)  # More normal

        # Session behavior
        session_duration = random.randint(60, 600)
        cart_additions = random.randint(1, 10)

        # Payment verification varies significantly by difficulty
        if difficulty == 'easy':
            cvv_result = random.choices(['pass', 'fail', 'not_checked'], weights=[0.2, 0.6, 0.2])[0]
            avs_result = random.choices(['full_match', 'partial_match', 'no_match'], weights=[0.2, 0.2, 0.6])[0]
            orders_24h = random.randint(3, 8)  # Multiple attempts
        elif difficulty == 'medium':
            cvv_result = random.choices(['pass', 'fail', 'not_checked'], weights=[0.5, 0.3, 0.2])[0]
            avs_result = random.choices(['full_match', 'partial_match', 'no_match'], weights=[0.4, 0.4, 0.2])[0]
            orders_24h = random.randint(1, 3)
        else:  # hard
            cvv_result = random.choices(['pass', 'not_checked'], weights=[0.85, 0.15])[0]
            avs_result = random.choices(['full_match', 'partial_match'], weights=[0.6, 0.4])[0]
            orders_24h = random.choices([0, 1], weights=[0.7, 0.3])[0]

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
            'high_risk_category': random.random() < (0.9 if difficulty == 'easy' else (0.6 if difficulty == 'medium' else 0.3)),
            'is_abuse': True,
            'abuse_type': 'payment_fraud',
            'abuse_confidence': round(abuse_confidence, 2),
            'difficulty_tier': difficulty,
        }


class SuspiciousButLegitimatePatternGenerator(BasePatternGenerator):
    """
    Generates suspicious but legitimate transaction patterns.

    These are legitimate users whose behavior triggers fraud signals but are
    actually benign. Examples: VPN users, travelers, gift buyers, power shoppers.
    Creates the false positive zone where human review is needed.
    """

    def generate(self, timestamp: datetime, difficulty: str = 'n/a') -> Dict[str, Any]:
        """
        Generate a suspicious but legitimate transaction record.

        These patterns create the ambiguous zone (0.4-0.7 confidence) where
        models should be uncertain and trigger human review.
        """
        # Choose suspicious behavior type
        behavior_type = random.choice(['vpn_user', 'traveler', 'gift_buyer', 'power_shopper', 'expat'])

        # Established legitimate account
        account_age_days = random.randint(60, 730)
        account_created_date = timestamp - timedelta(days=account_age_days)
        days_since_first_purchase = random.randint(0, min(60, account_age_days - 10))
        total_orders = random.randint(5, 40)

        # Verified legitimate account
        email_verified = True
        phone_verified = random.random() > 0.2
        profile_complete = random.random() > 0.3
        email_domain = random.choice(LEGITIMATE_EMAIL_DOMAINS)

        # Base country
        home_country = random.choice(LOW_RISK_COUNTRIES)

        if behavior_type == 'vpn_user':
            # Privacy-conscious user always on VPN
            ip_country = random.choice(LOW_RISK_COUNTRIES + HIGH_RISK_COUNTRIES)
            card_country = home_country
            billing_country = home_country
            shipping_country = home_country
            vpn_proxy_detected = True
            new_device = random.random() < 0.2
            order_amount = random.uniform(30.0, 300.0)
            high_risk_items = random.random() < 0.3
            abuse_confidence = random.uniform(0.45, 0.65)

        elif behavior_type == 'traveler':
            # Legitimate user traveling/relocated
            ip_country = random.choice(LOW_RISK_COUNTRIES)  # Different country
            card_country = home_country
            billing_country = home_country
            shipping_country = random.choice([home_country, ip_country])  # Ship to hotel or home
            vpn_proxy_detected = random.random() < 0.3
            new_device = random.random() < 0.4  # Maybe new device
            order_amount = random.uniform(40.0, 400.0)
            high_risk_items = random.random() < 0.2
            abuse_confidence = random.uniform(0.40, 0.60)

        elif behavior_type == 'gift_buyer':
            # Buying gift for someone else
            ip_country = home_country
            card_country = home_country
            billing_country = home_country
            shipping_country = random.choice(LOW_RISK_COUNTRIES)  # Different shipping address
            vpn_proxy_detected = random.random() < 0.1
            new_device = random.random() < 0.15
            order_amount = random.uniform(50.0, 500.0)
            high_risk_items = random.random() < 0.4  # Electronics as gifts
            abuse_confidence = random.uniform(0.35, 0.55)

        elif behavior_type == 'power_shopper':
            # High-velocity legitimate user
            ip_country = home_country
            card_country = home_country
            billing_country = home_country
            shipping_country = home_country
            vpn_proxy_detected = random.random() < 0.15
            new_device = random.random() < 0.1
            order_amount = random.uniform(100.0, 800.0)
            high_risk_items = random.random() < 0.5
            abuse_confidence = random.uniform(0.40, 0.65)
            orders_24h = random.randint(2, 5)  # Many orders
            orders_7d = random.randint(5, 15)
        else:  # expat
            # Living abroad, shipping to foreign address regularly
            ip_country = random.choice(LOW_RISK_COUNTRIES)
            card_country = home_country
            billing_country = home_country
            shipping_country = ip_country  # Ships to current location
            vpn_proxy_detected = random.random() < 0.2
            new_device = random.random() < 0.2
            order_amount = random.uniform(40.0, 400.0)
            high_risk_items = random.random() < 0.25
            abuse_confidence = random.uniform(0.35, 0.60)

        # Set default velocity for non-power-shoppers
        if behavior_type != 'power_shopper':
            orders_24h = random.choices([0, 1], weights=[0.6, 0.4])[0]
            orders_7d = random.randint(1, 4)

        # Normal session behavior (legitimate users take time)
        session_duration = random.randint(180, 1800)
        cart_additions = random.randint(1, 6)

        # Clean payment verification (legitimate payment methods)
        cvv_result = random.choices(['pass', 'not_checked'], weights=[0.9, 0.1])[0]
        avs_result = random.choices(['full_match', 'partial_match'], weights=[0.8, 0.2])[0]

        # Historical average
        avg_order_value = random.uniform(50.0, 250.0)

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
            'failed_login_attempts_24h': random.choices([0, 1], weights=[0.95, 0.05])[0],
            'successful_logins_7d': random.randint(3, 15),
            'password_reset_count_30d': random.choices([0, 1], weights=[0.9, 0.1])[0],
            'device_id': self._generate_device_id(),
            'ip_address': self._generate_ip_address(ip_country),
            'ip_country': ip_country,
            'user_agent': random.choice([ua for ua in USER_AGENTS if 'Bot' not in ua and 'curl' not in ua]),
            'device_type': random.choice(DEVICE_TYPES),
            'new_device': new_device,
            'vpn_proxy_detected': vpn_proxy_detected,
            'payment_method': random.choices(PAYMENT_METHODS, weights=[0.5, 0.3, 0.15, 0.05])[0],
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
            'high_risk_category': high_risk_items,
            'is_abuse': False,  # Actually legitimate!
            'abuse_type': 'suspicious_but_legitimate',
            'abuse_confidence': round(abuse_confidence, 2),
            'difficulty_tier': 'n/a',  # Not fraud, so no difficulty tier
        }
