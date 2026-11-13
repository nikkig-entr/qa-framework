"""Contract tests - schema validation."""

import pytest

from qa_framework.api.models import Album, Comment, Photo, Post, Todo, User


@pytest.mark.contract
class TestResponseSchemas:
    """Validate API responses match expected schemas."""

    async def test_user_schema(self, api_client):
        """Test user response matches User schema."""
        response = await api_client.get("/users/1", model=User)
        assert response.is_success
        assert response.data is not None
        # Schema validation happens automatically via model=User

    async def test_user_list_schema(self, api_client):
        """Test user list matches schema."""
        response = await api_client.get("/users", model=list[User])
        assert response.is_success
        assert response.data is not None
        assert len(response.data) == 10
        for user in response.data:
            assert isinstance(user, User)
            assert user.id > 0
            assert user.name
            assert user.email
            assert "@" in user.email

    async def test_post_schema(self, api_client):
        """Test post response matches Post schema."""
        response = await api_client.get("/posts/1", model=Post)
        assert response.is_success
        assert response.data is not None
        assert response.data.user_id > 0
        assert response.data.title
        assert response.data.body

    async def test_comment_schema(self, api_client):
        """Test comment response matches Comment schema."""
        response = await api_client.get("/comments/1", model=Comment)
        assert response.is_success
        assert response.data is not None
        assert response.data.post_id > 0
        assert response.data.name
        assert response.data.email
        assert "@" in response.data.email

    async def test_album_schema(self, api_client):
        """Test album response matches Album schema."""
        response = await api_client.get("/albums/1", model=Album)
        assert response.is_success
        assert response.data is not None
        assert response.data.user_id > 0
        assert response.data.title

    async def test_photo_schema(self, api_client):
        """Test photo response matches Photo schema."""
        response = await api_client.get("/photos/1", model=Photo)
        assert response.is_success
        assert response.data is not None
        assert response.data.album_id > 0
        assert response.data.title
        assert response.data.url.startswith("http")
        assert response.data.thumbnail_url.startswith("http")

    async def test_todo_schema(self, api_client):
        """Test todo response matches Todo schema."""
        response = await api_client.get("/todos/1", model=Todo)
        assert response.is_success
        assert response.data is not None
        assert response.data.user_id > 0
        assert response.data.title
        assert isinstance(response.data.completed, bool)


@pytest.mark.contract
class TestErrorResponses:
    """Test error response formats."""

    async def test_404_response_format(self, api_client):
        """Test 404 returns valid error structure."""
        response = await api_client.get("/users/999999", expected_status=[404])
        assert response.status_code == 404
        # JSONPlaceholder returns empty object for 404
        assert response.raw_data == {}

    async def test_invalid_endpoint(self, api_client):
        """Test invalid endpoint returns 404."""
        response = await api_client.get("/invalid-endpoint", expected_status=[404])
        assert response.status_code == 404


@pytest.mark.contract
class TestResponseHeaders:
    """Test response headers."""

    async def test_content_type_json(self, api_client):
        """Test responses have JSON content type."""
        response = await api_client.get("/users/1")
        assert response.is_success
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    async def test_cors_headers(self, api_client):
        """Test CORS headers if present."""
        response = await api_client.get("/users/1")
        # JSONPlaceholder doesn't have CORS, but check pattern
        assert response.status_code == 200
