import requests
import random
import string

def generate_user_agent():
    """Generate a random User-Agent string."""
    iphone_models = ['iPhone11,8', 'iPhone10,6', 'iPhone12,1', 'iPhone12,3', 'iPhone12,5']
    ios_versions = ['12_3_1', '13_3_1', '14_4_1', '13_5_1', '14_0_1', '15_0_2']
    locales = ['en_US']
    instagram_versions = ['105.0.0.11.118', '110.0.0.16.119', '113.0.0.39.122']

    iphone = random.choice(iphone_models)
    ios = random.choice(ios_versions)
    locale = random.choice(locales)
    instagram = random.choice(instagram_versions)

    return (
        f'Mozilla/5.0 (iPhone; CPU iPhone OS {ios} like Mac OS X) '
        f'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 '
        f'Instagram {instagram} ({iphone}; iOS {ios}; {locale}; scale=2.00; 828x1792)'
    )

def generate_random_cookies():
    """Generate random cookies for the session."""
    cookie_keys = ['sessionid', 'csrftoken', 'mid', 'ig_did', 'shbid', 'rur', 'shbts', 'ds_user_id', 'urlgen']
    return {key: ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32)) for key in cookie_keys}

def create_session(proxy=None):
    """Create a session with optional proxy and custom headers."""
    session = requests.Session()

    # Set custom headers
    session.headers.update({
        'User-Agent': generate_user_agent(),
        'Referer': 'https://www.instagram.com/',
        'X-Requested-With': 'XMLHttpRequest'
    })

    # Update cookies
    session.cookies.update(generate_random_cookies())

    # Add proxy if provided
    if proxy:
        proxy_host, proxy_port, proxy_username, proxy_password = proxy.split(':')
        proxy_url = f"socks5://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
        session.proxies.update({
            "http": proxy_url,
            "https": proxy_url
        })

    return session

def check_headers(proxy=None):
    """Send a request to httpbin.org/headers and print the response."""
    session = create_session(proxy)
    url = 'https://httpbin.org/headers'
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Headers sent to httpbin.org:")
        print(response.json())  # Print the headers returned by httpbin
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    # Example proxy: "199.233.238.6:6326:joker1:112112112ffF"
    proxy = input("Enter proxy (or leave blank for no proxy): ").strip()
    proxy = proxy if proxy else None  # Use proxy only if provided
    check_headers(proxy)

if __name__ == '__main__':
    main()

