#!/usr/bin/env python3
"""
ELM369 JMR0824197846902 - Enforcement Automation System
Validates language, geographic, and timezone restrictions
Location: Kokomo, Indiana USA 46902
Timestamp: 2026-03-30T14:42:00-05:00 (America/Indiana/Knox)
"""

import json
import logging
import pytz
from datetime import datetime
from typing import Dict, Tuple, List
import geoip2.database
import requests

# Configuration
CONFIG = {
    "ALLOWED_LANGUAGE": "en-US",
    "ALLOWED_COUNTRY": "US",
    "ALLOWED_STATE": "Indiana",
    "ALLOWED_CITY": "Kokomo",
    "ALLOWED_POSTAL_CODE": "46902",
    "REFERENCE_LATITUDE": 40.4831,
    "REFERENCE_LONGITUDE": -86.1637,
    "TIMEZONE": "America/Indiana/Knox",
    "MAX_LOCATION_VARIANCE_MILES": 50  # Within 50 miles of Kokomo
}

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/elm369/enforcement.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LocationValidator:
    """Validates geographic location against Kokomo, Indiana reference point"""
    
    @staticmethod
    def distance_between_coordinates(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in miles between two coordinates using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3956  # Radius of earth in miles
        return c * r
    
    @staticmethod
    def validate_ip_geolocation(ip_address: str) -> Tuple[bool, Dict]:
        """Validate IP address is from USA"""
        try:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
            data = response.json()
            
            timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
            
            if data.get('country_code') != CONFIG["ALLOWED_COUNTRY"]:
                logger.warning(f"[{timestamp}] IP geolocation failed - Country: {data.get('country_code')} at {data.get('city')}, {data.get('region_code')}")
                return False, {
                    "reason": "non_usa_ip",
                    "country": data.get('country_code'),
                    "city": data.get('city'),
                    "region": data.get('region_code'),
                    "timestamp": timestamp
                }
            
            logger.info(f"[{timestamp}] IP geolocation valid - {data.get('city')}, {data.get('region_code')}")
            return True, data
        except Exception as e:
            logger.error(f"IP geolocation check failed: {str(e)}")
            return False, {"reason": "geoip_error", "error": str(e)}
    
    @staticmethod
    def validate_gps_coordinates(latitude: float, longitude: float) -> Tuple[bool, Dict]:
        """Validate GPS coordinates are within acceptable range of Kokomo, IN"""
        distance = LocationValidator.distance_between_coordinates(
            CONFIG["REFERENCE_LATITUDE"],
            CONFIG["REFERENCE_LONGITUDE"],
            latitude,
            longitude
        )
        
        timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
        
        if distance <= CONFIG["MAX_LOCATION_VARIANCE_MILES"]:
            logger.info(f"[{timestamp}] GPS coordinates valid - Distance from Kokomo: {distance:.2f} miles")
            return True, {"distance_miles": distance, "timestamp": timestamp}
        else:
            logger.warning(f"[{timestamp}] GPS coordinates invalid - Distance from Kokomo: {distance:.2f} miles (max: {CONFIG['MAX_LOCATION_VARIANCE_MILES']})")
            return False, {"reason": "location_too_far", "distance_miles": distance, "timestamp": timestamp}


class LanguageValidator:
    """Validates language preferences are en-US only"""
    
    @staticmethod
    def validate_accept_language_header(accept_language: str) -> Tuple[bool, Dict]:
        """Validate Accept-Language header contains en-US"""
        timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
        
        if not accept_language:
            logger.warning(f"[{timestamp}] Missing Accept-Language header")
            return False, {"reason": "missing_header", "timestamp": timestamp}
        
        # Parse language header
        languages = [lang.split(';')[0].strip() for lang in accept_language.split(',')]
        
        # Check if en-US is present
        for lang in languages:
            if 'en-us' in lang.lower() or lang.lower() == 'en':
                logger.info(f"[{timestamp}] Accept-Language header valid: {accept_language}")
                return True, {"languages": languages, "timestamp": timestamp}
        
        logger.warning(f"[{timestamp}] Accept-Language header invalid - Missing en-US: {accept_language}")
        return False, {"reason": "non_english_us", "languages": languages, "timestamp": timestamp}
    
    @staticmethod
    def validate_device_locale(device_locale: str) -> Tuple[bool, Dict]:
        """Validate device locale is en-US"""
        timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
        
        if device_locale.lower() == 'en-us' or device_locale.lower() == 'en_us':
            logger.info(f"[{timestamp}] Device locale valid: {device_locale}")
            return True, {"locale": device_locale, "timestamp": timestamp}
        
        logger.warning(f"[{timestamp}] Device locale invalid: {device_locale}")
        return False, {"reason": "invalid_locale", "locale": device_locale, "timestamp": timestamp}
    
    @staticmethod
    def validate_text_encoding(text: str) -> Tuple[bool, Dict]:
        """Validate text contains only ASCII characters"""
        timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
        
        try:
            text.encode('ascii')
            logger.info(f"[{timestamp}] Text encoding valid - ASCII only")
            return True, {"encoding": "ascii", "timestamp": timestamp}
        except UnicodeEncodeError:
            logger.warning(f"[{timestamp}] Text encoding invalid - Contains non-ASCII characters")
            return False, {"reason": "non_ascii_text", "timestamp": timestamp}


class TimezoneValidator:
    """Validates timezone is America/Indiana/Knox"""
    
    @staticmethod
    def validate_timezone(timezone_str: str) -> Tuple[bool, Dict]:
        """Validate timezone setting"""
        timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
        
        if timezone_str == CONFIG["TIMEZONE"]:
            logger.info(f"[{timestamp}] Timezone valid: {timezone_str}")
            return True, {"timezone": timezone_str, "timestamp": timestamp}
        
        logger.warning(f"[{timestamp}] Timezone invalid: {timezone_str} (required: {CONFIG['TIMEZONE']})")
        return False, {"reason": "invalid_timezone", "timezone": timezone_str, "required": CONFIG["TIMEZONE"], "timestamp": timestamp}
    
    @staticmethod
    def validate_ntp_sync() -> Tuple[bool, Dict]:
        """Validate system time is NTP synchronized"""
        timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
        
        try:
            # Check NTP sync status
            import subprocess
            result = subprocess.run(['timedatectl', 'status'], capture_output=True, text=True)
            
            if 'synchronized: yes' in result.stdout or 'System synchronized: yes' in result.stdout:
                logger.info(f"[{timestamp}] NTP synchronization valid")
                return True, {"ntp_synced": True, "timestamp": timestamp}
            else:
                logger.warning(f"[{timestamp}] NTP synchronization failed")
                return False, {"reason": "ntp_not_synced", "timestamp": timestamp}
        except Exception as e:
            logger.error(f"NTP check failed: {str(e)}")
            return False, {"reason": "ntp_check_error", "error": str(e), "timestamp": timestamp}


class AccessEnforcer:
    """Main access control enforcer"""
    
    def __init__(self):
        self.location_validator = LocationValidator()
        self.language_validator = LanguageValidator()
        self.timezone_validator = TimezoneValidator()
    
    def validate_access(self, request_data: Dict) -> Tuple[bool, Dict]:
        """
        Comprehensive access validation
        
        Args:
            request_data: {
                'ip_address': str,
                'accept_language': str,
                'device_locale': str,
                'timezone': str,
                'latitude': float (optional),
                'longitude': float (optional)
            }
        
        Returns:
            (bool, Dict) - Access granted/denied with details
        """
        timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
        results = {
            "timestamp": timestamp,
            "location": CONFIG["ALLOWED_CITY"] + ", " + CONFIG["ALLOWED_STATE"] + " " + CONFIG["ALLOWED_POSTAL_CODE"],
            "validations": {},
            "access_granted": True,
            "errors": []
        }
        
        # 1. Validate IP Geolocation
        ip_valid, ip_data = self.location_validator.validate_ip_geolocation(request_data.get('ip_address', ''))
        results["validations"]["ip_geolocation"] = ip_valid
        if not ip_valid:
            results["access_granted"] = False
            results["errors"].append(ip_data)
        
        # 2. Validate Accept-Language Header
        lang_valid, lang_data = self.language_validator.validate_accept_language_header(
            request_data.get('accept_language', '')
        )
        results["validations"]["accept_language"] = lang_valid
        if not lang_valid:
            results["access_granted"] = False
            results["errors"].append(lang_data)
        
        # 3. Validate Device Locale
        locale_valid, locale_data = self.language_validator.validate_device_locale(
            request_data.get('device_locale', '')
        )
        results["validations"]["device_locale"] = locale_valid
        if not locale_valid:
            results["access_granted"] = False
            results["errors"].append(locale_data)
        
        # 4. Validate Timezone
        tz_valid, tz_data = self.timezone_validator.validate_timezone(request_data.get('timezone', ''))
        results["validations"]["timezone"] = tz_valid
        if not tz_valid:
            results["access_granted"] = False
            results["errors"].append(tz_data)
        
        # 5. Validate GPS Coordinates (if provided)
        if 'latitude' in request_data and 'longitude' in request_data:
            gps_valid, gps_data = self.location_validator.validate_gps_coordinates(
                request_data.get('latitude'),
                request_data.get('longitude')
            )
            results["validations"]["gps_coordinates"] = gps_valid
            if not gps_valid:
                results["access_granted"] = False
                results["errors"].append(gps_data)
        
        # 6. Validate NTP Sync
        ntp_valid, ntp_data = self.timezone_validator.validate_ntp_sync()
        results["validations"]["ntp_sync"] = ntp_valid
        if not ntp_valid:
            results["access_granted"] = False
            results["errors"].append(ntp_data)
        
        # Log final decision
        if results["access_granted"]:
            logger.info(f"[{timestamp}] ACCESS GRANTED - All validations passed")
        else:
            logger.warning(f"[{timestamp}] ACCESS DENIED - {len(results['errors'])} validation(s) failed")
        
        return results["access_granted"], results
    
    def log_access_attempt(self, request_data: Dict, result: Dict, database_path: str):
        """Log access attempt to database"""
        try:
            import sqlite3
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO elm369_access_logs 
                (timestamp, ip_address, accept_language, device_locale, timezone, 
                 latitude, longitude, access_granted, validations, errors)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result["timestamp"],
                request_data.get('ip_address', 'unknown'),
                request_data.get('accept_language', 'unknown'),
                request_data.get('device_locale', 'unknown'),
                request_data.get('timezone', 'unknown'),
                request_data.get('latitude'),
                request_data.get('longitude'),
                result["access_granted"],
                json.dumps(result["validations"]),
                json.dumps(result["errors"])
            ))
            
            conn.commit()
            conn.close()
            
            timestamp = datetime.now(pytz.timezone(CONFIG["TIMEZONE"])).isoformat()
            logger.info(f"[{timestamp}] Access attempt logged to database")
        except Exception as e:
            logger.error(f"Failed to log access attempt: {str(e)}")


if __name__ == "__main__":
    enforcer = AccessEnforcer()
    
    # Example test case
    test_request = {
        'ip_address': '68.107.28.84',  # USA IP
        'accept_language': 'en-US,en;q=0.9',
        'device_locale': 'en-US',
        'timezone': 'America/Indiana/Knox',
        'latitude': 40.4831,
        'longitude': -86.1637
    }
    
    access_granted, result = enforcer.validate_access(test_request)
    print(json.dumps(result, indent=2))
