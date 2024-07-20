import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test the home page."""
    rv = client.get('/')
    assert b'Enter search term' in rv.data

def test_sql_injection(client):
    """Test submitting a SQL injection attack."""
    rv = client.post('/', data=dict(search_term="' OR 1=1--"))
    assert b'SQL injection attack detected' in rv.data

def test_xss_attack(client):
    """Test submitting an XSS attack."""
    rv = client.post('/', data=dict(search_term='<script>alert("XSS")</script>'))
    assert b'XSS attack detected' in rv.data

def test_valid_search(client):
    """Test submitting a valid search term."""
    rv = client.post('/', data=dict(search_term='valid search term'))
    assert b'Your search term: valid search term' in rv.data
