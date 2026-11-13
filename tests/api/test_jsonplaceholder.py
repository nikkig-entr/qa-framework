"""API tests for JSONPlaceholder."""

import pytest

from qa_framework.api.models import Album, Comment, Photo, Post, Todo, User


@pytest.mark.api
class TestUsers:
    """Tests for /users endpoint."""

    async def test_get_users(self, api_client):
        """Test getting all users."""
        response = await api_client.get("/users", model=list[User])
        assert response.is_success
        assert response.data is not None
        assert len(response.data) == 10
        assert all(isinstance(u, User) for u in response.data)

    async def test_get_user_by_id(self, api_client):
        """Test getting a single user by ID."""
        response = await api_client.get("/users/1", model=User)
        assert response.is_success
        assert response.data is not None
        assert response.data.id == 1
        assert response.data.name == "Leanne Graham"
        assert response.data.username == "Bret"

    async def test_get_nonexistent_user(self, api_client):
        """Test getting non-existent user returns 404."""
        response = await api_client.get("/users/999", expected_status=[200, 404])
        assert response.status_code == 404


@pytest.mark.api
class TestPosts:
    """Tests for /posts endpoint."""

    async def test_get_posts(self, api_client):
        """Test getting all posts."""
        response = await api_client.get("/posts", model=list[Post])
        assert response.is_success
        assert response.data is not None
        assert len(response.data) == 100

    async def test_get_post_by_id(self, api_client):
        """Test getting a single post by ID."""
        response = await api_client.get("/posts/1", model=Post)
        assert response.is_success
        assert response.data is not None
        assert response.data.id == 1
        assert response.data.user_id == 1

    async def test_get_posts_by_user(self, api_client):
        """Test getting posts filtered by userId."""
        response = await api_client.get("/posts", params={"userId": 1}, model=list[Post])
        assert response.is_success
        assert response.data is not None
        assert all(p.user_id == 1 for p in response.data)
        assert len(response.data) == 10


@pytest.mark.api
class TestComments:
    """Tests for /comments endpoint."""

    async def test_get_comments(self, api_client):
        """Test getting all comments."""
        response = await api_client.get("/comments", model=list[Comment])
        assert response.is_success
        assert response.data is not None
        assert len(response.data) == 500

    async def test_get_comments_by_post(self, api_client):
        """Test getting comments filtered by postId."""
        response = await api_client.get("/comments", params={"postId": 1}, model=list[Comment])
        assert response.is_success
        assert response.data is not None
        assert all(c.post_id == 1 for c in response.data)
        assert len(response.data) == 5


@pytest.mark.api
class TestAlbums:
    """Tests for /albums endpoint."""

    async def test_get_albums(self, api_client):
        """Test getting all albums."""
        response = await api_client.get("/albums", model=list[Album])
        assert response.is_success
        assert response.data is not None
        assert len(response.data) == 100


@pytest.mark.api
class TestPhotos:
    """Tests for /photos endpoint."""

    async def test_get_photos(self, api_client):
        """Test getting all photos."""
        response = await api_client.get("/photos", model=list[Photo])
        assert response.is_success
        assert response.data is not None
        assert len(response.data) == 5000

    async def test_get_photos_by_album(self, api_client):
        """Test getting photos filtered by albumId."""
        response = await api_client.get("/photos", params={"albumId": 1}, model=list[Photo])
        assert response.is_success
        assert response.data is not None
        assert all(p.album_id == 1 for p in response.data)
        assert len(response.data) == 50


@pytest.mark.api
class TestTodos:
    """Tests for /todos endpoint."""

    async def test_get_todos(self, api_client):
        """Test getting all todos."""
        response = await api_client.get("/todos", model=list[Todo])
        assert response.is_success
        assert response.data is not None
        assert len(response.data) == 200

    async def test_get_completed_todos(self, api_client):
        """Test getting completed todos."""
        response = await api_client.get("/todos", params={"completed": "true"}, model=list[Todo])
        assert response.is_success
        assert response.data is not None
        assert all(t.completed for t in response.data)

    async def test_get_pending_todos(self, api_client):
        """Test getting pending todos."""
        response = await api_client.get("/todos", params={"completed": "false"}, model=list[Todo])
        assert response.is_success
        assert response.data is not None
        assert all(not t.completed for t in response.data)


@pytest.mark.api
class TestCreateOperations:
    """Tests for create operations (POST)."""

    async def test_create_post(self, api_client):
        """Test creating a new post."""
        new_post = {
            "title": "Test Post",
            "body": "This is a test post",
            "userId": 1,
        }
        response = await api_client.post("/posts", json=new_post, model=Post, expected_status=201)
        assert response.is_success
        assert response.data is not None
        assert response.data.title == "Test Post"
        assert response.data.body == "This is a test post"
        assert response.data.user_id == 1
        # JSONPlaceholder returns ID 101 for new posts
        assert response.data.id == 101

    async def test_create_comment(self, api_client):
        """Test creating a new comment."""
        new_comment = {
            "postId": 1,
            "name": "Test Comment",
            "email": "test@example.com",
            "body": "This is a test comment",
        }
        response = await api_client.post("/comments", json=new_comment, model=Comment, expected_status=201)
        assert response.is_success
        assert response.data is not None
        assert response.data.post_id == 1
        assert response.data.name == "Test Comment"


