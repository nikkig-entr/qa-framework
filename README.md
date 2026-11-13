# QA Automation Framework

Senior-level test automation framework built with **Playwright**, **pytest**, **httpx**, and **SQLAlchemy**. Designed for scalable, maintainable, and reliable test automation.

## Features

- **UI Testing**: Playwright with Page Object Model, Page Factory, retry logic
- **API Testing**: Async httpx client with validation, mocking (respx), retry
- **Contract Testing**: Schema validation, consumer-driven contracts
- **Database Testing**: Async SQLAlchemy with repository pattern, testcontainers
- **Parallel Execution**: pytest-xdist with load-balanced distribution
- **Flaky Handling**: Automatic retries with exponential backoff
- **Rich Reporting**: HTML reports + Allure with screenshots/traces
- **CI/CD Ready**: GitHub Actions workflow with matrix testing
- **Docker Support**: Multi-stage builds, docker-compose for local dev
- **Type Safety**: Full mypy compliance, pydantic models
- **Code Quality**: Ruff linting, pre-commit hooks

## Quick Start

### Prerequisites

- Python 3.11+
- Git
- Docker (optional, for databases)

### Installation

```bash
# Clone and enter
git clone <your-repo>
cd qa-framework

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -U pip
pip install -e ".[dev]"

# Install Playwright browsers
playwright install --with-deps

# Copy environment config
cp .env.example .env
```

### Run Tests

```bash
# All tests (parallel)
pytest -n auto

# UI tests only
pytest tests/ui -v -n 2

# API tests only
pytest tests/api -v -n auto

# With HTML report
pytest --html=reports/report.html --self-contained-html

# With Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

### Docker

```bash
# Run all tests in container
docker compose --profile test up --build

# Interactive development
docker compose --profile dev up -d
docker compose exec qa-dev bash

# With databases
docker compose --profile all up --build
```

## Project Structure

```
qa-framework/
├── src/qa_framework/          # Framework source
│   ├── config.py              # Pydantic settings
│   ├── logging.py             # Structured logging
│   ├── ui/                    # UI testing
│   │   ├── base_page.py       # Base Page Object
│   │   ├── page_factory.py    # Page Factory
│   │   └── pages/             # Page Objects
│   ├── api/                   # API testing
│   │   ├── client.py          # Async API Client
│   │   └── models.py          # Pydantic models
│   └── db/                    # Database testing
│       ├── session.py         # Async session manager
│       └── repository.py      # Repository pattern
├── tests/
│   ├── conftest.py            # Pytest fixtures
│   ├── ui/                    # UI tests
│   ├── api/                   # API tests
│   ├── contract/              # Contract tests
│   └── db/                    # Database tests
├── config/                    # Config files
├── docker/                    # Docker files
├── .github/workflows/         # CI/CD
├── pyproject.toml             # Project config
└── README.md
```

## Writing Tests

### UI Test Example

```python
# tests/ui/test_login.py
import pytest
from qa_framework.ui.pages import LoginPage

@pytest.mark.ui
class TestLogin:
    async def test_valid_login(self, page, page_factory, test_user):
        login_page = page_factory.get(LoginPage)
        await login_page.navigate()
        await login_page.login(test_user["username"], test_user["password"])
        await login_page.assert_login_success()
```

### API Test Example

```python
# tests/api/test_users.py
import pytest
from qa_framework.api.models import User

@pytest.mark.api
class TestUsers:
    async def test_get_user(self, api_client):
        response = await api_client.get("/users/1", model=User)
        assert response.is_success
        assert response.data.id == 1
        assert response.data.username == "Bret"
```

### Page Object Example

```python
# src/qa_framework/ui/pages/dashboard_page.py
from playwright.async_api import Locator
from ..base_page import BasePage

class DashboardPage(BasePage):
    url_path = "/dashboard"

    @property
    def welcome_message(self) -> Locator:
        return self.get_by_test_id("welcome")

    @property
    def logout_button(self) -> Locator:
        return self.get_by_role("button", name="Logout")

    async def assert_logged_in(self, username: str) -> "DashboardPage":
        await self.expect_contains_text(self.welcome_message, username)
        await self.expect_visible(self.logout_button)
        return self
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER_NAME` | chromium | Browser: chromium, firefox, webkit |
| `BROWSER_HEADLESS` | true | Headless mode |
| `API_BASE_URL` | jsonplaceholder | API base URL |
| `TEST_PARALLEL_WORKERS` | 0 (auto) | Parallel workers |
| `TEST_RERUNS` | 2 | Retry failed tests |

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

- **Lint**: Ruff + MyPy
- **API Tests**: Parallel, HTML + Allure reports
- **UI Tests**: Chromium + Firefox, screenshots on failure
- **Contract Tests**: Schema validation
- **Allure Report**: Combined report from all test types

## Best Practices

1. **Page Objects**: Encapsulate selectors and actions, return `self` for chaining
2. **Fixtures**: Use `page_factory` for page objects, `api_client` for API
3. **Assertions**: Use `expect_*` methods from `BasePage` for auto-retry
4. **Data**: Use `faker` for test data, fixtures for common scenarios
5. **Parallel**: Tests must be independent; use unique data per test
6. **Flaky**: Mark with `@pytest.mark.flaky`, fix root cause ASAP

## Extending

### Add New Page Object

```python
# src/qa_framework/ui/pages/new_page.py
from playwright.async_api import Locator
from ..base_page import BasePage

class NewPage(BasePage):
    url_path = "/new-page"

    @property
    def submit_button(self) -> Locator:
        return self.get_by_role("button", name="Submit")
```

Register in `src/qa_framework/ui/pages/__init__.py`.

### Add New API Model

```python
# src/qa_framework/api/models.py
class NewResource(BaseSchema):
    id: int
    name: str
    created_at: datetime
```

Use in tests: `model=NewResource` or `model=list[NewResource]`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright browsers missing | `playwright install --with-deps` |
| Port conflicts | Check docker-compose ports |
| Flaky UI tests | Increase `TEST_RERUNS`, add explicit waits |
| Slow tests | Use `-n auto`, profile with `--durations=10` |
| Import errors | Ensure `pip install -e .` ran |

## License

MIT